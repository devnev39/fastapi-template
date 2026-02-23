import asyncio
import logging

import typer

from scripts.exporter.importer import import_logs
from src.db.db import get_db_context
from src.models.log import Log as LogModel
from src.schemas.log import Log

logger = logging.getLogger(__name__)


async def export(logs: list[Log]):
    async with get_db_context() as db:
        db.add_all([LogModel(**lg.model_dump()) for lg in logs])
        await db.commit()
        logger.info("Logs pushed to db...")


typer = typer.Typer()


@typer.command()
def push_logs(file_name: str, view_sample: bool = False):
    logs = import_logs(file_name=file_name)
    if view_sample:
        logger.info(f"sample - {logs[0] if len(logs) else None}")
    asyncio.run(export(logs))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    typer()
