from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import polars as pl
from robyn.testing import TestClient as RobynClient

from app.main import create_app
from app.services.file_reader import UploadedFile, read_uploaded_file
from app.services.profiler import build_profile_view_model

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_read_uploaded_csv_and_detect_signals():
    uploaded_file = UploadedFile(
        filename="sample_profile.csv",
        content=(FIXTURE_DIR / "sample_profile.csv").read_bytes(),
        file_type="csv",
    )

    dataframe, read_time_ms, warnings = read_uploaded_file(uploaded_file)
    profile = build_profile_view_model(
        uploaded_file=uploaded_file,
        dataframe=dataframe,
        read_time_ms=read_time_ms,
        warnings=warnings,
        upload_token="token",
        sample_seed=42,
    )

    signal_kinds = {(signal["column"], signal["kind"]) for signal in profile["signals"]}
    assert ("customer_id", "Possible ID") in signal_kinds
    assert ("status", "Low variance") in signal_kinds
    assert ("churn_flag", "Binary / target") in signal_kinds
    assert ("mostly_missing", "Mostly missing") in signal_kinds
    assert ("mixed_value", "Suspicious mixed types") in signal_kinds
    assert ("mostly_missing", "Binary / target") not in signal_kinds
    assert ("mostly_missing", "Possible ID") not in signal_kinds
    assert ("status", "Binary / target") not in signal_kinds
    assert ("notes", "Possible ID") not in signal_kinds
    assert ("mixed_value", "Possible ID") not in signal_kinds
    assert ("score", "Possible ID") not in signal_kinds
    assert ("customer_id", "Likely categorical") not in signal_kinds
    assert ("opt_in_text", "Boolean disguised as string") in signal_kinds
    assert ("opt_in_text", "Binary / target") not in signal_kinds
    assert ("opt_in_text", "Likely categorical") not in signal_kinds
    assert ("churn_flag", "Likely categorical") not in signal_kinds
    assert profile["file_summary"]["rows"] == 12
    assert len(profile["sample_rows"]) == 10


def test_read_uploaded_parquet(tmp_path):
    dataframe = pl.read_csv(FIXTURE_DIR / "sample_profile.csv")
    parquet_path = tmp_path / "sample_profile.parquet"
    dataframe.write_parquet(parquet_path)

    uploaded_file = UploadedFile(
        filename="sample_profile.parquet",
        content=parquet_path.read_bytes(),
        file_type="parquet",
    )

    profiled_frame, read_time_ms, warnings = read_uploaded_file(uploaded_file)
    assert profiled_frame.shape == dataframe.shape
    assert read_time_ms >= 0
    assert warnings == []


def test_extracts_filename_from_multipart_request_when_files_are_raw_bytes():
    csv_bytes = (FIXTURE_DIR / "sample_profile.csv").read_bytes()
    boundary = "----DataPeekBoundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="dataset"; filename="sample_profile.csv"\r\n'
        "Content-Type: text/csv\r\n\r\n"
    ).encode("utf-8") + csv_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    request = SimpleNamespace(
        body=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    uploaded_file = UploadedFile.from_request_files({"dataset": csv_bytes}, request=request)

    assert uploaded_file.filename == "sample_profile.csv"
    assert uploaded_file.file_type == "csv"
    assert uploaded_file.content == csv_bytes


def test_extracts_filename_from_string_multipart_body():
    csv_bytes = (FIXTURE_DIR / "sample_profile.csv").read_bytes()
    boundary = "----DataPeekBoundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="dataset"; filename="original_name.csv"\r\n'
        "Content-Type: text/csv\r\n\r\n"
    ).encode("utf-8") + csv_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    request = SimpleNamespace(
        body=body.decode("utf-8", errors="ignore"),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    uploaded_file = UploadedFile.from_request_files({"dataset": csv_bytes}, request=request)

    assert uploaded_file.filename == "original_name.csv"
    assert uploaded_file.file_type == "csv"


def test_infers_csv_type_when_filename_metadata_is_missing():
    csv_bytes = (FIXTURE_DIR / "sample_profile.csv").read_bytes()

    uploaded_file = UploadedFile.from_request_files({"dataset": csv_bytes})

    assert uploaded_file.filename == "upload.csv"
    assert uploaded_file.file_type == "csv"
    assert uploaded_file.content == csv_bytes


def test_prefers_filename_from_form_data_when_metadata_is_missing():
    csv_bytes = (FIXTURE_DIR / "sample_profile.csv").read_bytes()

    uploaded_file = UploadedFile.from_request_files(
        {"dataset": csv_bytes},
        preferred_filename="customers.csv",
    )

    assert uploaded_file.filename == "customers.csv"
    assert uploaded_file.file_type == "csv"


def test_routes_render_profile_and_resample():
    client = RobynClient(create_app())
    csv_bytes = (FIXTURE_DIR / "sample_profile.csv").read_bytes()

    analyze_response = client.post(
        "/analyze",
        files={"dataset": {"filename": "sample_profile.csv", "content": csv_bytes}},
    )

    assert analyze_response.status_code == 200
    assert "Sample rows (random)" in analyze_response.text
    assert "Column Overview" in analyze_response.text
    assert "Signals / Warnings" in analyze_response.text
    assert "Boolean disguised as string" in analyze_response.text

    token = _extract_hidden_value(analyze_response.text, "upload_token")
    next_seed = _extract_hidden_value(analyze_response.text, "resample_seed")

    resample_response = client.post(
        "/resample",
        form_data={"upload_token": token, "resample_seed": next_seed},
    )

    assert resample_response.status_code == 200
    assert "Sample rows (random)" in resample_response.text


def _extract_hidden_value(html: str, field_name: str) -> str:
    marker = f'name="{field_name}" value="'
    start = html.index(marker) + len(marker)
    end = html.index('"', start)
    return html[start:end]
