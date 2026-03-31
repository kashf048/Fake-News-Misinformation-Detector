"""
Fact Check Service
Integrates with Google Fact Check API
"""

import os
import logging
import aiohttp
from typing import List, Dict, Tuple
from app.schemas.analysis import FactCheck

logger = logging.getLogger(__name__)

GOOGLE_FACT_CHECK_API = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


class FactCheckService:
    """Handles fact-checking operations"""
    
    @staticmethod
    async def search_fact_checks(headline: str, max_results: int = 3) -> List[FactCheck]:
        """
        Search for fact-checks related to the headline
        """
        api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
        
        if not api_key:
            logger.warning("Google Fact Check API key not configured")
            return []
        
        try:
            params = {
                "query": headline,
                "pageSize": max_results,
                "key": api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(GOOGLE_FACT_CHECK_API, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        fact_checks = []
                        
                        for claim in data.get("claims", []):
                            for review in claim.get("claimReview", []):
                                fact_check = FactCheck(
                                    title=review.get("publisher", {}).get("name", "Unknown"),
                                    url=review.get("url", ""),
                                    claim_reviewed=claim.get("text", ""),
                                    rating=review.get("textualRating", "Unknown")
                                )
                                fact_checks.append(fact_check)
                        
                        return fact_checks
                    else:
                        logger.error(f"Fact Check API returned status {response.status}")
                        return []
                        
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching fact checks: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in fact check service: {e}")
            return []
    
    @staticmethod
    def normalize_rating(rating: str) -> float:
        """
        Normalize textual rating to a score between -1 and 1.
        -1: Fake, 0: Uncertain/Mixed, 1: Real
        """
        rating_lower = rating.lower()
        
        # Fake indicators
        if any(word in rating_lower for word in ['false', 'fake', 'incorrect', 'pants on fire', 'misleading', 'hoax']):
            return -1.0
        
        # Partially true/uncertain indicators
        if any(word in rating_lower for word in ['mostly false', 'partially', 'mixture', 'disputed', 'uncertain']):
            return -0.5
        
        # Mostly true indicators
        if any(word in rating_lower for word in ['mostly true', 'correct', 'accurate']):
            return 0.5
            
        # Real indicators
        if any(word in rating_lower for word in ['true', 'real', 'verified']):
            return 1.0
            
        return 0.0

    @staticmethod
    def get_weighted_evidence(fact_checks: List[FactCheck]) -> Tuple[float, float]:
        """
        Calculate a consensus score and confidence from fact-checks.
        Returns: (consensus_score, weight)
        """
        if not fact_checks:
            return 0.0, 0.0
            
        scores = [FactCheckService.normalize_rating(fc.rating) for fc in fact_checks]
        
        # Simple weighted average (can be improved)
        consensus = sum(scores) / len(scores)
        # Weight based on number of fact-checks (logarithmic scaling)
        import math
        weight = min(1.0, math.log(len(fact_checks) + 1, 4)) 
        
        return consensus, weight

    @staticmethod
    async def get_fact_check_summary(fact_checks: List[FactCheck]) -> str:
        """
        Generate summary from fact checks
        """
        if not fact_checks:
            return "No fact-check references found."
        
        summary = f"Found {len(fact_checks)} fact-check reference(s):\n"
        for i, fc in enumerate(fact_checks, 1):
            summary += f"\n{i}. {fc.title} - Rating: {fc.rating}\n"
            summary += f"   Claim: {fc.claim_reviewed}\n"
        
        return summary
