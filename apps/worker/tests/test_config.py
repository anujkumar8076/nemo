from autodev_worker.config import WorkerSettings


def test_worker_settings_reject_empty_temporal_address() -> None:
    try:
        WorkerSettings(temporal_address="")
    except ValueError:
        return
    raise AssertionError("empty Temporal address must be rejected")
