# Python Environment

This project uses Python for the agent pipeline, API, scraping, extraction, RAG, and recommendation services.

## Recommendation

Use Python 3.11, 3.12, or 3.13 for the project environment when possible. The current machine also has a Python 3.14 virtual environment at the repository root, but some AI and scraping libraries may lag behind the newest Python release.

## Existing Environment

A virtual environment already exists at:

```powershell
.\venv
```

Activate it from the repository root:

```powershell
.\venv\Scripts\Activate.ps1
```

Check Python and pip:

```powershell
python --version
python -m pip --version
```

## Install Dependencies

From `ai-agent-system`:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m playwright install
```

Use `requirements.txt` for runtime dependencies and `requirements-dev.txt` for local development and tests.

## Environment Variables

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Fill only local secrets in `.env`. Do not commit `.env`.

## Notes

- Keep `venv/` and `.venv/` out of Git.
- Prefer adding dependencies to `requirements.txt` before installing them manually.
- Keep NVIDIA recommendation logic evidence-driven, as required by the project document.
