import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from autodev_worker.config import get_settings
from autodev_worker.workflows import ConnectivityWorkflow


async def run_worker() -> None:
    settings = get_settings()
    client = await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
    )
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[ConnectivityWorkflow],
    )
    logging.getLogger(__name__).info(
        "worker_started",
        extra={"task_queue": settings.temporal_task_queue},
    )
    await worker.run()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
