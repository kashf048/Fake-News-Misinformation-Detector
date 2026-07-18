"""
Analysis Routes
API endpoints for analysis operations
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import os
import tempfile
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisHistoryResponse,
    DeleteResponse,
    AnalyticsResponse
)
from fastapi.concurrency import run_in_threadpool
import time
from app.services.ai_models import AIModels, TextAnalyzer, ImageAnalyzer
from app.services.fact_check import FactCheckService
from app.services.analysis import AnalysisService
from app.services.report import ReportService
from app.utils.validators import InputValidator, XSSProtection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Analyze headline and image for misinformation
    """
    try:
        # Sanitize and validate headline input
        try:
            sanitized_headline = XSSProtection.remove_html_tags(request.headline)
            sanitized_headline = InputValidator.validate_headline(sanitized_headline)
            # Escape HTML to prevent XSS
            sanitized_headline = XSSProtection.escape_html(sanitized_headline)
            request.headline = sanitized_headline
        except ValueError as val_err:
            raise HTTPException(status_code=400, detail=str(val_err))

        # Validate image URL format if provided
        if request.image_url:
            if not InputValidator.validate_image_url(request.image_url):
                raise HTTPException(status_code=400, detail="Invalid image URL format or unsupported extension")

        logger.info(f"Analyzing headline: {request.headline[:50]}...")
        
        # Analyze text
        start_time = time.time()
        logger.info(f"[yellow]Running text analysis...[/yellow]")
        prediction, confidence = await run_in_threadpool(AIModels.analyze_text, request.headline)
        text_time = time.time() - start_time
        logger.info(f"[green]Text analysis completed in {text_time:.2f}s[/green]")
        
        # Analyze image if provided
        similarity = None
        if request.image_url:
            try:
                is_valid_image = await run_in_threadpool(ImageAnalyzer.validate_image_url, request.image_url)
                if is_valid_image:
                    logger.info(f"[yellow]Running image-text similarity analysis...[/yellow]")
                    img_start = time.time()
                    similarity = await run_in_threadpool(
                        AIModels.analyze_image_text_similarity,
                        request.image_url,
                        request.headline
                    )
                    img_time = time.time() - img_start
                    logger.info(f"[green]Image analysis completed in {img_time:.2f}s[/green]")
                else:
                    logger.warning(f"Invalid or inaccessible image URL: {request.image_url}")
            except Exception as e:
                logger.error(f"Error analyzing image: {e}")
        
        # Generate explanation
        explanation = AIModels.generate_explanation(request.headline, prediction, confidence)
        
        # Search for fact checks
        fact_checks = await FactCheckService.search_fact_checks(request.headline)
        
        # Combined Decision Engines
        if fact_checks:
            logger.info(f"[yellow]Applying hybrid decision logic with fact-check evidence...[/yellow]")
            consensus, fc_weight = FactCheckService.get_weighted_evidence(fact_checks)
            
            # Map prediction: Fake -> -1.0, Real -> 1.0, Misleading -> 0.0
            ai_score = -1.0 if prediction == "Fake" else 1.0 if prediction == "Real" else 0.0
            
            # Weighted average - Fact checks are stronger (60%) if they exist and are high quality
            final_score = (ai_score * (1.0 - fc_weight * 0.7)) + (consensus * (fc_weight * 0.7))
            
            # Recalculate prediction and confidence
            if final_score < -0.2:
                prediction = "Fake"
                confidence = min(0.99, abs(final_score) + 0.1)
            elif final_score > 0.2:
                prediction = "Real"
                confidence = min(0.99, abs(final_score) + 0.1)
            else:
                prediction = "Misleading"
                confidence = max(0.5, 1.0 - abs(final_score))
            
            # Cap confidence to avoid 100% or extreme values
            confidence = min(0.98, max(0.55, confidence))
            
            # Update explanation based on combined results
            if consensus < -0.4 and ai_score > 0.4:
                explanation = f"While AI analysis initially categorized this as potentially real, multiple external fact-checks from authoritative sources have flagged it as inaccurate. Based on verified evidence, this content is categorized as misinformation."
            elif consensus > 0.4 and ai_score < -0.4:
                explanation = f"Although initial detection patterns suggested irregularities, external fact-checking verification indicates the claim is largely factual or supported by reputable sources."

        # Save to database
        analysis_id = await AnalysisService.save_analysis(
            headline=request.headline,
            image_url=request.image_url,
            prediction=prediction,
            confidence=confidence,
            similarity=similarity,
            explanation=explanation,
            fact_checks=fact_checks
        )
        
        # Fetch saved analysis
        analysis = await AnalysisService.get_analysis(analysis_id)
        
        return AnalysisResponse(
            _id=analysis_id,
            headline=analysis["headline"],
            image_url=analysis["image_url"],
            prediction=analysis["prediction"],
            confidence=analysis["confidence"],
            similarity=analysis["similarity"],
            explanation=analysis["explanation"],
            fact_checks=analysis["fact_checks"],
            created_at=analysis["created_at"]
        )
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=AnalysisHistoryResponse)
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    prediction: str = Query(None, regex="^(Fake|Real|Misleading)$")
):
    """
    Get analysis history with pagination
    """
    try:
        # Validate pagination and filter params
        page, limit = InputValidator.validate_pagination(page, limit)
        if prediction:
            try:
                prediction = InputValidator.validate_filter(prediction)
            except ValueError as val_err:
                raise HTTPException(status_code=400, detail=str(val_err))

        logger.info(f"Fetching history: page={page}, limit={limit}, prediction={prediction}")
        
        result = await AnalysisService.get_history(
            page=page,
            limit=limit,
            prediction_filter=prediction
        )
        
        items = [
            AnalysisResponse(
                _id=item["_id"],
                headline=item["headline"],
                image_url=item.get("image_url"),
                prediction=item["prediction"],
                confidence=item["confidence"],
                similarity=item.get("similarity"),
                explanation=item["explanation"],
                fact_checks=item.get("fact_checks", []),
                created_at=item["created_at"]
            )
            for item in result["items"]
        ]
        
        return AnalysisHistoryResponse(
            total=result["total"],
            page=result["page"],
            limit=result["limit"],
            items=items
        )
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{analysis_id}", response_model=DeleteResponse)
async def delete_analysis(analysis_id: str):
    """
    Delete analysis by ID
    """
    try:
        logger.info(f"Deleting analysis: {analysis_id}")
        
        success = await AnalysisService.delete_analysis(analysis_id)
        
        if success:
            return DeleteResponse(success=True, message="Analysis deleted successfully")
        else:
            raise HTTPException(status_code=404, detail="Analysis not found")
            
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Error deleting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """
    Get analytics dashboard data
    """
    try:
        logger.info("Fetching analytics data")
        
        analytics = await AnalysisService.get_analytics()
        
        return AnalyticsResponse(
            total_analyses=analytics["total_analyses"],
            fake_count=analytics["fake_count"],
            real_count=analytics["real_count"],
            misleading_count=analytics["misleading_count"],
            average_confidence=analytics["average_confidence"],
            predictions_by_date=analytics["predictions_by_date"],
            top_headlines=analytics["top_headlines"]
        )
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{analysis_id}/pdf")
async def download_report(analysis_id: str):
    """
    Generate and download PDF report for an analysis
    """
    try:
        logger.info(f"Generating PDF report for analysis: {analysis_id}")
        
        # Fetch analysis
        analysis = await AnalysisService.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
            
        # Create temp file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"analysis_report_{analysis_id}.pdf")
        
        # Generate PDF
        success = ReportService.generate_analysis_pdf(analysis, file_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to generate PDF report")
            
        return FileResponse(
            path=file_path,
            filename=f"fake_news_report_{analysis_id[:8]}.pdf",
            media_type="application/pdf"
        )
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Error serving PDF report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Fake News Detector API",
        "version": "1.0.0"
    }
