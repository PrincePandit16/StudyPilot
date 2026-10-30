from typing import Optional, List
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

from src.studypilot.core.config import settings

class GraphCheckpointer:
    """
    Manages PostgreSQL checkpointer for LangGraph.
    """
    def __init__(self):
        self.pool = ConnectionPool(
            conninfo=settings.DATABASE_URL,
            max_size=20,
            kwargs={"autocommit": True}
        )
        self.saver = PostgresSaver(self.pool)
        # The saver must be setup (create tables) before use
        self.saver.setup()

    def get_saver(self):
        return self.saver

    def close(self):
        self.pool.close()

# Singleton instance
checkpointer = GraphCheckpointer()
