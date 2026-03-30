"""
MongoDB Connection Module
Handles database initialization and connection management
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)

# Global database instance
db = None
client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """
    Initialize MongoDB connection
    """
    global client, db
    
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "misinformation_db")
    
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable not set")
    
    try:
        # Create async client
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]
        
        # Verify connection
        await client.admin.command("ping")
        logger.info(f"Connected to MongoDB database: {db_name}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """
    Close MongoDB connection
    """
    global client
    
    if client:
        client.close()
        logger.info("Closed MongoDB connection")


async def create_indexes():
    """
    Create database indexes for better query performance
    """
    try:
        analyses_collection = db["analyses"]
        
        # Create index on created_at for sorting
        await analyses_collection.create_index("created_at")
        
        # Create index on prediction for filtering
        await analyses_collection.create_index("prediction")
        
        # Create compound index for common queries
        await analyses_collection.create_index([("created_at", -1), ("prediction", 1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")


def get_database():
    """
    Get the database instance
    """
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return db


def sync_connect_to_mongo():
    """
    Synchronous MongoDB connection for testing
    """
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "misinformation_db")
    
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable not set")
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        logger.info(f"Connected to MongoDB database (sync): {db_name}")
        return client[db_name]
    except ServerSelectionTimeoutError as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
