# Contributing to VehicleGPT

## Project Maintainers & Authors
- **Susmitha Jillella** ([@Susmitha967](https://github.com/Susmitha967)) - Ingestion, Real-Data Importers, Physics Analytics, Battery SOH, CAN Protocols, Test Automation.
- **Reshma Kodavali** ([@Reshma-1717](https://github.com/Reshma-1717)) - Core Architecture, Database WAL Persistence, React Dashboard UI, Edge Deployment.

## Branch Strategy & Ownership
The repository uses feature branches to organize development:
- `feature/real-data-ingestion`: Real-world CSV, BLF, and CAN log drive cycle ingestion.
- `feature/ingestion-and-simulation`: Live protocol adapters (SOME/IP, VHAL, CAN) and normalizer.
- `feature/analytics-and-slm`: Range reduction physics, SOH degradation, and edge SLM reasoning.
- `feature/api-service`: FastAPI REST microservice endpoints and route controllers.
- `feature/frontend-ui`: React 19 dashboard layout, widgets, and live telemetry graphs.
- `feature/testing-and-deployment`: Pytest test suites, Docker edge containerization, and benchmarks.

## Commit Guidelines
- Every action and code modification must be backed by a discrete, atomic commit.
- Use Conventional Commits formatting:
  - `feat(...)`: New physical signal extractor or endpoint.
  - `test(...)`: Automated pytest test suite additions.
  - `docs(...)`: Architectural, dataset, or benchmark documentation.
  - `chore(...)`: Configuration or build script maintenance.
- Ensure all 41+ automated tests pass prior to pushing to `origin/main`.
