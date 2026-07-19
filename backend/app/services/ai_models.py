"""
AI Models Service
Handles RoBERTa and CLIP model loading and inference
"""

import os
import logging
from typing import Tuple, Dict, List
import numpy as np
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    CLIPProcessor,
    CLIPModel
)
import torch
from PIL import Image
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

# Global model instances
roberta_model = None
roberta_tokenizer = None
clip_model = None
clip_processor = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class AIModels:
    """Handles AI model operations"""
    
    @staticmethod
    async def initialize_models():
        """Initialize RoBERTa and CLIP models"""
        global roberta_model, roberta_tokenizer, clip_model, clip_processor
        
        mock_ai_models = os.getenv("MOCK_AI_MODELS", "false").lower() == "true"
        if mock_ai_models:
            logger.warning("MOCK_AI_MODELS is set to true. Skipping loading of heavy PyTorch models to save RAM.")
            return
            
        try:
            logger.info("[bold yellow]Initializing AI models...[/bold yellow]")
            
            # Load RoBERTa model
            model_name = os.getenv("MODEL_NAME", "hamzab/roberta-fake-news-classification")
            logger.info(f"Loading RoBERTa model: [cyan]{model_name}[/cyan]")
            
            roberta_tokenizer = AutoTokenizer.from_pretrained(model_name)
            # Load specialized model—it normally has 2 labels (Fake, Real)
            roberta_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            roberta_model = roberta_model.to(device)
            roberta_model.eval()
            
            # Load CLIP model
            clip_model_name = os.getenv("CLIP_MODEL", "openai/clip-vit-base-patch32")
            logger.info(f"Loading CLIP model: [cyan]{clip_model_name}[/cyan]")
            
            clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
            clip_model = CLIPModel.from_pretrained(clip_model_name)
            clip_model = clip_model.to(device)
            clip_model.eval()
            
            logger.info("[bold green]AI models initialized successfully[/bold green]")
            
        except Exception as e:
            logger.error(f"[bold red]Failed to initialize AI models:[/bold red] {e}")
            raise
    
    @staticmethod
    def analyze_text(headline: str) -> Tuple[str, float]:
        """
        Analyze headline using fine-tuned RoBERTa
        Returns: (prediction, confidence)
        """
        try:
            mock_ai_models = os.getenv("MOCK_AI_MODELS", "false").lower() == "true"
            if mock_ai_models or roberta_model is None or roberta_tokenizer is None:
                # Mock analysis logic for fast testing/low-memory environments
                headline_lower = headline.lower()
                if any(word in headline_lower for word in ["breaking", "shocking", "unbelievable", "secret", "exposed", "miracle", "fake"]):
                    prediction = "Fake"
                    confidence = 0.88
                elif len(headline) % 3 == 0:
                    prediction = "Misleading"
                    confidence = 0.68
                else:
                    prediction = "Real"
                    confidence = 0.94
                return prediction, confidence

            inputs = roberta_tokenizer(
                headline,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(device)
            
            with torch.no_grad():
                outputs = roberta_model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                
                # hamzab/roberta-fake-news-classification mapping:
                # LABEL_0: Fake, LABEL_1: Real
                fake_prob = probabilities[0][0].item()
                real_prob = probabilities[0][1].item()
                
            # Logic for "Misleading": if the difference is very small, it's uncertain/misleading
            diff = abs(real_prob - fake_prob)
            if diff < 0.15: # Slightly more sensitive threshold
                prediction = "Misleading"
                # Use a combined confidence for misleading (capped at 75% for misleading)
                confidence = 0.55 + (diff / 0.3) * 0.2
            elif fake_prob > real_prob:
                prediction = "Fake"
                confidence = fake_prob
            else:
                prediction = "Real"
                confidence = real_prob
            
            # Calibration: avoid 100% or absolute certainty in AI outputs
            confidence = min(0.985, float(confidence))
            
            return prediction, confidence
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return "Misleading", 0.5
    
    @staticmethod
    def analyze_image_text_similarity(image_url: str, headline: str) -> float:
        """
        Analyze image-text similarity using CLIP cosine similarity
        Returns: similarity score (0-1)
        """
        try:
            mock_ai_models = os.getenv("MOCK_AI_MODELS", "false").lower() == "true"
            if mock_ai_models or clip_model is None or clip_processor is None:
                # Mock similarity (e.g. based on deterministic seed to stay stable for same inputs)
                import random
                random.seed(len(headline) + len(image_url))
                return round(random.uniform(0.65, 0.95), 2)

            # Download image with user-agent to avoid blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(image_url, timeout=10, headers=headers)
            response.raise_for_status() # Raise error for bad status
            
            image = Image.open(BytesIO(response.content)).convert("RGB")
            
            # Prepare inputs
            inputs = clip_processor(
                text=[headline],
                images=image,
                return_tensors="pt",
                padding=True
            ).to(device)
            
            with torch.no_grad():
                # Get embeddings
                image_features = clip_model.get_image_features(pixel_values=inputs['pixel_values'])
                text_features = clip_model.get_text_features(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'])
                
                # Normalize features
                image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
                text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
                
                # Calculate cosine similarity
                similarity = (image_features @ text_features.T).item()
                
            # Logit calibration: CLIP values are often compressed
            # We map the 0.05-0.35 raw cosine similarity to 0-1 range
            if similarity < 0.05:
                final_similarity = 0.0
            elif similarity < 0.25:
                # Linear map [0.05, 0.25] -> [0.05, 0.75]
                final_similarity = 0.05 + (similarity - 0.05) * 3.5
            else:
                # Linear map [0.25, 0.4+] -> [0.75, 0.98]
                final_similarity = min(0.98, 0.75 + (similarity - 0.25) * 1.5)

            return float(final_similarity)
            
        except Exception as e:
            logger.error(f"Error analyzing image-text similarity: {e}")
            return 0.0
    
    @staticmethod
    def generate_explanation(headline: str, prediction: str, confidence: float) -> str:
        """
        Generate explanation for the prediction
        """
        confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
        
        explanations = {
            "Fake": f"This headline appears to be fabricated or contains false information. "
                   f"Our analysis with {confidence_level} confidence suggests the claim is not supported by reliable sources.",
            "Real": f"This headline appears to be factually accurate based on our analysis. "
                   f"The claim is supported with {confidence_level} confidence by available evidence.",
            "Misleading": f"This headline contains partially true information but may be presented in a misleading context. "
                         f"With {confidence_level} confidence, we found that the claim lacks complete accuracy or context."
        }
        
        return explanations.get(prediction, "Unable to determine the accuracy of this headline.")


class TextAnalyzer:
    """Specialized text analysis"""
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        # Filter common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are'}
        keywords = [w for w in words if w not in common_words and len(w) > 3]
        return list(set(keywords))[:10]
    
    @staticmethod
    def calculate_text_complexity(text: str) -> float:
        """Calculate text complexity score (0-1)"""
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        # Normalize to 0-1
        complexity = min(avg_word_length / 10, 1.0)
        return complexity


class ImageAnalyzer:
    """Specialized image analysis"""
    
    @staticmethod
    def validate_image_url(url: str) -> bool:
        """Validate if image URL is accessible"""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def get_image_metadata(image_url: str) -> Dict:
        """Get image metadata"""
        try:
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content))
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "size_mb": len(response.content) / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Error getting image metadata: {e}")
            return {}
