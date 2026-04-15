from __future__ import annotations

import pytest

from app.services.file_reader import FileValidationError, UploadedFile, read_uploaded_file


def _read_csv_bytes(filename: str, content: str):
    uploaded_file = UploadedFile(
        filename=filename,
        content=content.encode("utf-8"),
        file_type="csv",
    )
    return read_uploaded_file(uploaded_file)


def test_csv_auto_detects_semicolon_delimiter():
    dataframe, read_time_ms, warnings = _read_csv_bytes(
        "semicolon.csv",
        "name;score\nalice;10\nbob;20\n",
    )

    assert dataframe.columns == ["name", "score"]
    assert dataframe.to_dicts() == [{"name": "alice", "score": 10}, {"name": "bob", "score": 20}]
    assert read_time_ms >= 0
    assert warnings == []


def test_csv_auto_detects_tab_delimiter():
    dataframe, read_time_ms, warnings = _read_csv_bytes(
        "tab.csv",
        "name\tscore\nalice\t10\nbob\t20\n",
    )

    assert dataframe.columns == ["name", "score"]
    assert dataframe.to_dicts() == [{"name": "alice", "score": 10}, {"name": "bob", "score": 20}]
    assert read_time_ms >= 0
    assert warnings == []


def test_csv_rejects_unsupported_delimiter_instead_of_misprofiling():
    with pytest.raises(FileValidationError, match="supported CSV delimiter"):
        _read_csv_bytes(
            "pipe.csv",
            "name|score\nalice|10\nbob|20\n",
        )
