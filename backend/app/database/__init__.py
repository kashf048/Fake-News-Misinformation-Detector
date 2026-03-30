"""Database module"""
from .connection import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
    sync_connect_to_mongo
)

__all__ = [
    "connect_to_mongo",
    "close_mongo_connection",
    "get_database",
    "sync_connect_to_mongo"
]
