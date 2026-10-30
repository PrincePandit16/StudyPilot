import asyncio
import logging
from typing import Callable, Awaitable
from src.studypilot.core.worker import worker, DocumentJob, JobAction
from src.studypilot.services.document_service import DocumentService
from src.studypilot.core.database import SessionLocal
import uuid

logger = logging.getLogger("studypilot.worker")

async def process_document_task(job: DocumentJob):
    if job.action == JobAction.PROCESS:
        # Need a fresh DB session for the background worker
        with SessionLocal() as db:
            service = DocumentService(db)
            try:
                await service.process_document(uuid.UUID(job.document_id))
                logger.info(f"Successfully processed document {job.document_id}")
            except Exception as e:
                logger.exception(f"Failed to process document {job.document_id}: {e}")
    elif job.action == JobAction.DELETE:
        # Handle deletion if needed (already synchronous in this version)
        pass

async def start_worker():
    worker.set_processor(process_document_task)
    await worker.start()

async def stop_worker():
    await worker.stop()
