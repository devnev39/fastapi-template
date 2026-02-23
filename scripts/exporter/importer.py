import json
import logging
from pathlib import Path

import typer

from src.schemas.log import Log

logger = logging.getLogger(__name__)


def import_logs(
    file_name: str,
) -> list[Log]:
    """
    read file and parse it to log model and return the list of logs
    """
    logs = []
    with Path.open(Path(file_name)) as file:
        for line in file:
            log = json.loads(line)
            logs.append(Log(**log))
    return logs


app = typer.Typer()


@app.command()
def main(file_name: str, print_first: int | None = None):
    logs = import_logs(file_name)
    if print_first:
        print(logs[:print_first])
    else:
        print(logs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()
