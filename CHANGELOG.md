# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project uses semantic versioning tags.

## [0.1.1] - 2026-04-20

### Added
- Render deployment configuration via `render.yaml` for a single starter-tier web service.
- Lightweight `/health` endpoint for platform health checks.

### Changed
- Runtime startup now prefers `PORT` and `HOST` environment variables, with CLI flags still available as overrides.
- README now documents the Render deployment model, health check path, and the single-instance in-memory upload assumptions.
- Tests now cover the health endpoint and launcher runtime configuration behavior.

## [0.1.0] - 2026-04-15

### Added
- Initial DataPeek MVP built with Robyn, Polars, and Jinja2.
- CSV and Parquet upload with single-page profiling output.
- File summary, column overview, numeric summary, random sample, head, and tail views.
- Column-level signals for possible IDs, missingness, low variance, binary targets, boolean disguised as string, mixed types, and categorical/high-cardinality cues.
- Upload/resample flow, logo/favicons, Makefile, README, and GitHub Actions CI.
