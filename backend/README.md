# Backend for Neuroscience Website

## Setup

1. Install [Poetry](https://python-poetry.org/docs/#installation)
2. Install dependencies:
   ```bash
   cd backend
   poetry install
   ```
3. Run the server:
   ```bash
   poetry run uvicorn backend.main:app --reload
   ```
4. Run tests:
   ```bash
   poetry run pytest
   ```

## Features
- FastAPI
- Click CLI
- pytest for testing
- Example API endpoint
