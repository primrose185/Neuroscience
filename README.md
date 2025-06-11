# Neuroscience Website

This is a full-stack monorepo template for a modern web application inspired by [charts.upgrad.com](https://charts.upgrad.com).

## Structure

- `backend/` — FastAPI, Poetry, Click CLI, pytest
- `frontend/` — Vue 3, Vite, TypeScript, Tailwind CSS, shadcn-vue, Vitest

## Quick Start

### Backend
```bash
cd backend
poetry install
poetry run uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
yarn install
yarn dev
```

## Development
- The frontend expects the backend API at `http://localhost:8000/api` (CORS is not yet configured for production).
- Example integration: Click the button on the homepage to call the backend `/api/hello` endpoint.

## Testing
- Backend: `poetry run pytest`
- Frontend: `yarn test`

## CI/CD
- Add your preferred CI/CD configuration in each folder (see `ci.template.yml` for a starting point).

---

For detailed setup, see the `README.md` in each subfolder.
