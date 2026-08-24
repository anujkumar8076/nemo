from datetime import timedelta

from temporalio import workflow


def connectivity_response(message: str) -> str:
    """Return the deterministic foundation handshake."""
    if not message.strip():
        raise ValueError("message must not be empty")
    return f"worker-ready:{message}"


@workflow.defn
class ConnectivityWorkflow:
    """Deterministic foundation workflow used to verify worker connectivity."""

    @workflow.run
    async def run(self, message: str) -> str:
        await workflow.sleep(timedelta(milliseconds=1))
        return connectivity_response(message)
