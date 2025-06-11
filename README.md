# Neuroscience Website

This is a full-stack monorepo template for a modern web application inspired by [charts.upgrad.com](https://charts.upgrad.com).

## Project Structure

### Backend (`/backend`)
- **Technology Stack**: FastAPI, Poetry, Click CLI, pytest
- **Key Components**:
  - `backend/main.py` - FastAPI application entry point
  - `backend/api.py` - API route definitions
  - `backend/cli.py` - Command-line interface tools
  - `backend/config.py` - Configuration settings
  - `tests/` - Test suite using pytest
- **Dependencies**: Managed via Poetry (`pyproject.toml` and `poetry.lock`)

### Frontend (`/frontend`)
- **Technology Stack**: Vue 3, Vite, TypeScript, Tailwind CSS, shadcn-vue, Vitest
- **Key Components**:
  - `src/App.vue` - Root Vue component
  - `src/components/` - Reusable Vue components
  - `src/lib/` - Utility functions and shared code
  - `src/assets/` - Static assets (images, fonts, etc.)
  - `src/style.css` & `index.css` - Global styles and Tailwind configuration
- **Dependencies**: Managed via Yarn (`package.json` and `yarn.lock`)

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
- The frontend expects the backend API at `http://localhost:8000/api`
- CORS is configured for development at `http://localhost:8000`
- The project follows a modular architecture with clear separation between frontend and backend
- TypeScript is used throughout the frontend for type safety
- FastAPI provides automatic OpenAPI/Swagger documentation at `/docs`

## Testing
- Backend: `poetry run pytest`
- Frontend: `yarn test`
  - Unit tests with Vitest
  - Component testing capabilities included

## CI/CD
- Template CI configuration provided in `ci.template.yml`
- Supports automated testing, building, and deployment
- Customize the CI/CD pipeline based on your deployment needs

## Project Features
- Modern full-stack development setup
- Type-safe frontend with TypeScript
- Fast API development with automatic OpenAPI docs
- Component-driven UI development
- Built-in testing infrastructure
- Development hot-reloading for both frontend and backend

---

For detailed setup and component documentation, see the `README.md` in each subfolder.
