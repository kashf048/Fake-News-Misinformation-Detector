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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Analyze headline and image for misinformation
    """
    try:
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
                if ImageAnalyzer.validate_image_url(request.image_url):
                    logger.info(f"[yellow]Running image-text similarity analysis...[/yellow]")
                    img_start = time.time()
                    similarity = await AIModels.analyze_image_text_similarity(
                        request.image_url,
                        request.headline
                    )
                    img_time = time.time() - img_start
                    logger.info(f"[green]Image analysis completed in {img_time:.2f}s[/green]")
                else:
                    logger.warning(f"Invalid image URL: {request.image_url}")
            except Exception as e:
                logger.error(f"Error analyzing image: {e}")
        
        # Generate explanation
        explanation = AIModels.generate_explanation(request.headline, prediction, confidence)
        
        # Search for fact checks
        fact_checks = await FactCheckService.search_fact_checks(request.headline)
        
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
