"""
Analysis Service
Handles database operations for analyses
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict
from bson import ObjectId
from app.database import get_database
from app.schemas.analysis import AnalysisResponse, FactCheck

logger = logging.getLogger(__name__)


class AnalysisService:
    """Handles analysis database operations"""
    
    @staticmethod
    async def save_analysis(
        headline: str,
        image_url: Optional[str],
        prediction: str,
        confidence: float,
        similarity: Optional[float],
        explanation: str,
        fact_checks: List[FactCheck]
    ) -> str:
        """
        Save analysis result to database
        Returns: analysis ID
        """
        try:
            db = get_database()
            analyses_collection = db["analyses"]
            
            analysis_doc = {
                "headline": headline,
                "image_url": image_url,
                "prediction": prediction,
                "confidence": confidence,
                "similarity": similarity,
                "explanation": explanation,
                "fact_checks": [fc.dict() for fc in fact_checks],
                "created_at": datetime.utcnow()
            }
            
            result = await analyses_collection.insert_one(analysis_doc)
            logger.info(f"Analysis saved with ID: {result.inserted_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise
    
    @staticmethod
    async def get_analysis(analysis_id: str) -> Optional[Dict]:
        """
        Get analysis by ID
        """
        try:
            db = get_database()
            analyses_collection = db["analyses"]
            
            analysis = await analyses_collection.find_one({"_id": ObjectId(analysis_id)})
            return analysis
            
        except Exception as e:
            logger.error(f"Error fetching analysis: {e}")
            return None
    
    @staticmethod
    async def get_history(
        page: int = 1,
        limit: int = 10,
        prediction_filter: Optional[str] = None
    ) -> Dict:
        """
        Get analysis history with pagination
        """
        try:
            db = get_database()
            analyses_collection = db["analyses"]
            
            # Build filter
            filter_query = {}
            if prediction_filter:
                filter_query["prediction"] = prediction_filter
            
            # Get total count
            total = await analyses_collection.count_documents(filter_query)
            
            # Calculate skip
            skip = (page - 1) * limit
            
            # Get paginated results
            cursor = analyses_collection.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
            analyses = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for analysis in analyses:
                analysis["_id"] = str(analysis["_id"])
            
            return {
                "total": total,
                "page": page,
                "limit": limit,
                "items": analyses
            }
            
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            raise
    
    @staticmethod
    async def delete_analysis(analysis_id: str) -> bool:
        """
        Delete analysis by ID
        """
        try:
            db = get_database()
            analyses_collection = db["analyses"]
            
            result = await analyses_collection.delete_one({"_id": ObjectId(analysis_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Analysis deleted: {analysis_id}")
                return True
            else:
                logger.warning(f"Analysis not found: {analysis_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting analysis: {e}")
            raise
    
    @staticmethod
    async def get_analytics() -> Dict:
        """
        Get analytics data
        """
        try:
            db = get_database()
            analyses_collection = db["analyses"]
            
            total = await analyses_collection.count_documents({})
            
            # Count by prediction
            fake_count = await analyses_collection.count_documents({"prediction": "Fake"})
            real_count = await analyses_collection.count_documents({"prediction": "Real"})
            misleading_count = await analyses_collection.count_documents({"prediction": "Misleading"})
            
            # Calculate average confidence
            pipeline = [
                {"$group": {"_id": None, "avg_confidence": {"$avg": "$confidence"}}}
            ]
            result = await analyses_collection.aggregate(pipeline).to_list(length=1)
            avg_confidence = result[0]["avg_confidence"] if result else 0
            
            # Get predictions by date (last 7 days)
            pipeline = [
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            predictions_by_date = {}
            async for doc in analyses_collection.aggregate(pipeline):
                predictions_by_date[doc["_id"]] = doc["count"]
            
            # Get top headlines
            pipeline = [
                {"$sort": {"created_at": -1}},
                {"$limit": 5},
                {"$project": {"headline": 1}}
            ]
            top_headlines = []
            async for doc in analyses_collection.aggregate(pipeline):
                top_headlines.append(doc["headline"])
            
            return {
                "total_analyses": total,
                "fake_count": fake_count,
                "real_count": real_count,
                "misleading_count": misleading_count,
                "average_confidence": round(avg_confidence, 2),
                "predictions_by_date": predictions_by_date,
                "top_headlines": top_headlines
            }
            
        except Exception as e:
            logger.error(f"Error fetching analytics: {e}")
            raise
    
    @staticmethod
    async def clear_old_analyses(days: int = 30) -> int:
        """
        Delete analyses older than specified days
        """
        try:
            from datetime import timedelta
            
            db = get_database()
            analyses_collection = db["analyses"]
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = await analyses_collection.delete_many({"created_at": {"$lt": cutoff_date}})
            
            logger.info(f"Deleted {result.deleted_count} old analyses")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing old analyses: {e}")
            raise
