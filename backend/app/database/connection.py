"""
MongoDB Connection Module
Handles database initialization and connection management
"""

import os
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)

# Global database instance
db = None
client = None


class MockCursor:
    """Mock MongoDB Async Cursor"""
    def __init__(self, data):
        self.data = data
        self._index = 0

    def sort(self, key, direction=1):
        if isinstance(key, list):
            sort_key, sort_dir = key[0]
        else:
            sort_key = key
            sort_dir = direction

        def get_sort_key(d):
            val = d.get(sort_key)
            if val is None:
                return datetime.min
            return val

        self.data.sort(key=get_sort_key, reverse=(sort_dir == -1))
        return self

    def skip(self, n):
        self.data = self.data[n:]
        return self

    def limit(self, n):
        self.data = self.data[:n]
        return self

    async def to_list(self, length=None):
        if length is not None:
            return self.data[:length]
        return self.data

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index < len(self.data):
            val = self.data[self._index]
            self._index += 1
            return val
        else:
            raise StopAsyncIteration


class MockCollection:
    """Mock MongoDB Collection"""
    def __init__(self, name):
        self.name = name
        self.docs = []

    async def create_index(self, *args, **kwargs):
        pass

    async def insert_one(self, doc):
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        doc_copy = dict(doc)
        self.docs.append(doc_copy)

        class InsertOneResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertOneResult(doc_copy["_id"])

    async def find_one(self, query):
        for doc in self.docs:
            if self._matches(doc, query):
                return dict(doc)
        return None

    def find(self, query=None):
        query = query or {}
        matched = [dict(doc) for doc in self.docs if self._matches(doc, query)]
        return MockCursor(matched)

    async def count_documents(self, query):
        count = 0
        for doc in self.docs:
            if self._matches(doc, query):
                count += 1
        return count

    async def delete_one(self, query):
        deleted_count = 0
        for idx, doc in enumerate(self.docs):
            if self._matches(doc, query):
                self.docs.pop(idx)
                deleted_count = 1
                break

        class DeleteResult:
            def __init__(self, deleted_count):
                self.deleted_count = deleted_count
        return DeleteResult(deleted_count)

    async def delete_many(self, query):
        new_docs = []
        deleted_count = 0
        for doc in self.docs:
            if self._matches(doc, query):
                deleted_count += 1
            else:
                new_docs.append(doc)
        self.docs = new_docs

        class DeleteResult:
            def __init__(self, deleted_count):
                self.deleted_count = deleted_count
        return DeleteResult(deleted_count)

    async def update_one(self, query, update):
        set_dict = update.get("$set", {})
        matched_count = 0
        modified_count = 0
        for doc in self.docs:
            if self._matches(doc, query):
                matched_count = 1
                for k, v in set_dict.items():
                    doc[k] = v
                modified_count = 1
                break

        class UpdateResult:
            def __init__(self, matched_count, modified_count):
                self.matched_count = matched_count
                self.modified_count = modified_count
        return UpdateResult(matched_count, modified_count)

    async def find_one_and_update(self, query, update, return_document=False):
        set_dict = update.get("$set", {})
        for doc in self.docs:
            if self._matches(doc, query):
                for k, v in set_dict.items():
                    doc[k] = v
                return dict(doc)
        return None

    def _matches(self, doc, query):
        for k, v in query.items():
            if k == "_id":
                if ObjectId(doc.get("_id")) != ObjectId(v):
                    return False
            elif isinstance(v, dict):
                val = doc.get(k)
                for op, op_val in v.items():
                    if op == "$lt":
                        if not (val is not None and val < op_val):
                            return False
                    elif op == "$gt":
                        if not (val is not None and val > op_val):
                            return False
                    elif op == "$lte":
                        if not (val is not None and val <= op_val):
                            return False
                    elif op == "$gte":
                        if not (val is not None and val >= op_val):
                            return False
                    else:
                        return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    def aggregate(self, pipeline):
        docs = [dict(d) for d in self.docs]

        for stage in pipeline:
            if "$sort" in stage:
                sort_stage = stage["$sort"]
                for key, direction in sort_stage.items():
                    def get_sort_key(d):
                        val = d.get(key)
                        if val is None:
                            return datetime.min
                        return val
                    docs.sort(key=get_sort_key, reverse=(direction == -1))
            elif "$limit" in stage:
                limit = stage["$limit"]
                docs = docs[:limit]
            elif "$project" in stage:
                project = stage["$project"]
                new_docs = []
                for d in docs:
                    new_d = {}
                    for k, v in project.items():
                        if v == 1:
                            new_d[k] = d.get(k)
                    if "_id" in d and "_id" not in new_d:
                        new_d["_id"] = d["_id"]
                    new_docs.append(new_d)
                docs = new_docs
            elif "$group" in stage:
                group = stage["$group"]
                group_id_expr = group.get("_id")

                if group_id_expr is None:
                    result_doc = {"_id": None}
                    for out_key, out_val in group.items():
                        if out_key == "_id":
                            continue
                        if isinstance(out_val, dict) and "$avg" in out_val:
                            avg_field = out_val["$avg"]
                            if avg_field.startswith("$"):
                                avg_field = avg_field[1:]
                            vals = [d.get(avg_field) for d in docs if d.get(avg_field) is not None]
                            result_doc[out_key] = sum(vals) / len(vals) if vals else 0
                    docs = [result_doc]
                else:
                    groups = {}
                    for d in docs:
                        group_key = None
                        if isinstance(group_id_expr, dict) and "$dateToString" in group_id_expr:
                            date_expr = group_id_expr["$dateToString"]
                            date_field = date_expr.get("date")
                            if date_field.startswith("$"):
                                date_field = date_field[1:]
                            date_val = d.get(date_field)
                            if isinstance(date_val, datetime):
                                group_key = date_val.strftime("%Y-%m-%d")
                            else:
                                group_key = str(date_val)
                        elif isinstance(group_id_expr, str) and group_id_expr.startswith("$"):
                            group_key = d.get(group_id_expr[1:])
                        else:
                            group_key = str(group_id_expr)

                        if group_key not in groups:
                            groups[group_key] = []
                        groups[group_key].append(d)

                    grouped_docs = []
                    for g_key, g_docs in groups.items():
                        result_doc = {"_id": g_key}
                        for out_key, out_val in group.items():
                            if out_key == "_id":
                                continue
                            if isinstance(out_val, dict) and "$sum" in out_val:
                                sum_val = out_val["$sum"]
                                if isinstance(sum_val, int):
                                    result_doc[out_key] = len(g_docs) * sum_val
                                else:
                                    if sum_val.startswith("$"):
                                        sum_val = sum_val[1:]
                                    result_doc[out_key] = sum(doc.get(sum_val, 0) for doc in g_docs)
                        grouped_docs.append(result_doc)
                    docs = grouped_docs

        return MockCursor(docs)


class MockDatabase:
    """Mock MongoDB Database"""
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]

    def __getattr__(self, name):
        return self[name]

    async def command(self, cmd_name, *args, **kwargs):
        if cmd_name == "ping":
            return {"ok": 1}
        raise NotImplementedError(f"Mock command {cmd_name} not implemented")


class MockClient:
    """Mock MongoDB Client"""
    def __init__(self):
        self.db = MockDatabase()

    def __getitem__(self, name):
        return self.db

    def close(self):
        pass

    @property
    def admin(self):
        return self.db


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
        logger.warning("FALLING BACK TO IN-MEMORY MOCK DATABASE CLIENT")
        client = MockClient()
        db = client[db_name]
        await create_indexes()


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
    global db
    if db is None:
        logger.warning("Database not initialized, returning mock database instance")
        db = MockClient()["misinformation_db"]
    return db


async def get_db():
    """
    Get the database instance asynchronously
    """
    return get_database()


def sync_connect_to_mongo():
    """
    Synchronous MongoDB connection for testing
    """
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "misinformation_db")
    
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable not set")
    
    try:
        sync_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        sync_client.admin.command("ping")
        logger.info(f"Connected to MongoDB database (sync): {db_name}")
        return sync_client[db_name]
    except ServerSelectionTimeoutError as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("FALLING BACK TO IN-MEMORY MOCK DATABASE CLIENT (sync)")
        return MockClient()["misinformation_db"]
