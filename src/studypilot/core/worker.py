import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any, Awaitable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("studypilot.worker")

class JobAction(Enum):
    PROCESS = "process"
    DELETE = "delete"

@dataclass
class DocumentJob:
    document_id: str
    action: JobAction

class BackgroundWorker:
    def __init__(self):
        self.queue: asyncio.Queue[DocumentJob] = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None
        self._processor: Callable[[DocumentJob], Awaitable[None]] | None = None

    def set_processor(self, processor: Callable[[DocumentJob], Awaitable[None]]):
        self._processor = processor

    async def enqueue(self, job: DocumentJob):
        await self.queue.put(job)
        logger.info(f"Enqueued job {job.action} for document {job.document_id}")

    async def _work(self):
        while True:
            job = await self.queue.get()
            try:
                if self._processor:
                    await self._processor(job)
                else:
                    logger.error("No processor set for BackgroundWorker")
            except Exception as e:
                logger.exception(f"Error processing job {job}: {e}")
            finally:
                self.queue.task_done()

    async def start(self):
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._work())
            logger.info("Background worker started")

    async def stop(self):
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None
            logger.info("Background worker stopped")

# Singleton instance
worker = BackgroundWorker()
