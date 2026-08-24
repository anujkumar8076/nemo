import pytest

from autodev_worker.workflows import connectivity_response


def test_connectivity_response() -> None:
    assert connectivity_response("ping") == "worker-ready:ping"


def test_connectivity_response_rejects_empty_message() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        connectivity_response(" ")
