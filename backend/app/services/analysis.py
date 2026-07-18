"""
Analysis Service
Handles database operations for analyses
"""

import logging
from datetime import datetime, timedelta
import asyncio
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
            
            # 1. Pipeline for counts by prediction (Group by prediction)
            counts_pipeline = [
                {"$group": {"_id": "$prediction", "count": {"$sum": 1}}}
            ]
            
            # 2. Pipeline for average confidence
            avg_conf_pipeline = [
                {"$group": {"_id": None, "avg_confidence": {"$avg": "$confidence"}}}
            ]
            
            # 3. Pipeline for predictions by date (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            date_pipeline = [
                {"$match": {"created_at": {"$gte": seven_days_ago}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            # 4. Query for top headlines (last 5)
            top_headlines_query = (
                analyses_collection.find({}, {"headline": 1})
                .sort("created_at", -1)
                .limit(5)
            )

            # Execute aggregations and queries concurrently
            counts_task = analyses_collection.aggregate(counts_pipeline).to_list(length=10)
            avg_conf_task = analyses_collection.aggregate(avg_conf_pipeline).to_list(length=1)
            date_task = analyses_collection.aggregate(date_pipeline).to_list(length=10)
            top_headlines_task = top_headlines_query.to_list(length=5)
            
            counts_res, avg_conf_res, date_res, top_res = await asyncio.gather(
                counts_task,
                avg_conf_task,
                date_task,
                top_headlines_task
            )
            
            # Process counts
            fake_count = 0
            real_count = 0
            misleading_count = 0
            total = 0
            
            for item in counts_res:
                pred = item["_id"]
                count = item["count"]
                total += count
                if pred == "Fake":
                    fake_count = count
                elif pred == "Real":
                    real_count = count
                elif pred == "Misleading":
                    misleading_count = count
            
            # Process average confidence
            avg_confidence = avg_conf_res[0]["avg_confidence"] if avg_conf_res else 0
            
            # Process predictions by date
            predictions_by_date = {doc["_id"]: doc["count"] for doc in date_res if doc.get("_id")}
            
            # Process top headlines
            top_headlines = [doc["headline"] for doc in top_res if "headline" in doc]
            
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
