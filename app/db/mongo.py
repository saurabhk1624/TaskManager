from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.core.config import Settings


class MongoClientManager:
    """
    Simple wrapper around Motor client to keep database concerns
    out of the API layer.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncIOMotorClient | None = None

    def connect(self) -> None:
        if self._client is None:
            self._client = AsyncIOMotorClient(self._settings.mongo_uri)

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._client is None:
            raise RuntimeError("Mongo client is not initialized")
        return self._client[self._settings.mongo_db_name]

    @property
    def tasks_collection(self) -> AsyncIOMotorCollection:
        return self.db["tasks"]

