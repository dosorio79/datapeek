from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services.session_store import InMemoryUploadStore


def test_upload_store_evicts_oldest_entry():
    store = InMemoryUploadStore(max_entries=2)

    first = store.save(_upload("first.csv"))
    second = store.save(_upload("second.csv"))
    third = store.save(_upload("third.csv"))

    assert store.get(first) is None
    assert store.get(second) is not None
    assert store.get(third) is not None


def test_upload_store_get_marks_entry_recent():
    store = InMemoryUploadStore(max_entries=2)

    first = store.save(_upload("first.csv"))
    second = store.save(_upload("second.csv"))

    assert store.get(first) is not None

    third = store.save(_upload("third.csv"))

    assert store.get(first) is not None
    assert store.get(second) is None
    assert store.get(third) is not None


def test_upload_store_rejects_invalid_capacity():
    with pytest.raises(ValueError, match="max_entries must be at least 1"):
        InMemoryUploadStore(max_entries=0)


def _upload(filename: str) -> SimpleNamespace:
    return SimpleNamespace(
        filename=filename,
        content=b"abc",
        file_type="csv",
    )
