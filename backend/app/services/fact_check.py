"""
Fact Check Service
Integrates with Google Fact Check API
"""

import os
import logging
import aiohttp
from typing import List, Dict
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
