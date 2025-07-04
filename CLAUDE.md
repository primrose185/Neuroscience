# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Vue 3 Frontend
- **Install dependencies**: `yarn install`
- **Start development server**: `yarn dev` (runs on localhost:5173)
- **Build for production**: `yarn build`
- **Preview production build**: `yarn preview`
- **Type checking**: `vue-tsc --noEmit` (TypeScript checking without emitting files)

### Deployment
- **Vercel deployment**: `vercel` or `vercel --prod`
- **Vercel dev**: `vercel dev` (local development with Vercel environment)

## Architecture Overview

### Project Structure
This is a frontend-only Vue 3 application focused on neuroscience education with interactive 3D visualizations.

### Technology Stack
- **Framework**: Vue 3 with Composition API and `<script setup>` syntax
- **Language**: TypeScript with strict type checking
- **Build System**: Vite for fast development and optimized production builds
- **Styling**: Tailwind CSS with CSS custom properties and shadcn-vue components
- **UI Components**: shadcn-vue component library with Reka UI primitives
- **3D Graphics**: Three.js with STL/GLTF model loading capabilities
- **Routing**: Vue Router with history mode for SEO-friendly URLs
- **Package Management**: Yarn 1.22.22 (specified in packageManager field)

### Application Architecture
- **Layout System**: Fixed sidebar navigation with resizable content panels
- **Route Structure**: Topic-based routing (`/topic1/page1`, `/topic1/page2`, `/topic2/page1`, etc.)
- **State Management**: Vue 3 reactivity system with composables pattern
- **Component Pattern**: Single File Components (SFCs) with TypeScript and scoped styling
- **3D Integration**: Custom Three.js integration with STL file loading and interactive controls

### Key Components
- **App.vue**: Root component managing sidebar state and router navigation
- **Sidebar.vue**: Collapsible navigation with expandable menu items and mobile responsiveness
- **Page Components**: Topic-specific pages with split-panel layouts for content and 3D visualizations
- **BlenderModelViewer.js**: Comprehensive Three.js wrapper for GLTF/GLB model loading with animations

### 3D Visualization Features
- **Model Loading**: Support for STL and GLTF/GLB formats
- **Interactive Controls**: Orbit controls, auto-rotation, and camera fitting
- **Animation Support**: GLTF animation playback with mixer controls
- **Lighting System**: Ambient and directional lighting with shadow mapping
- **Resizable Panels**: Dynamic content/visualization layout with draggable resize handles

### Development Workflow
1. Install dependencies with `yarn install`
2. Start development server with `yarn dev`
3. Build for production with `yarn build`
4. Deploy to Vercel using `vercel` command or git integration

### File Structure
- `src/App.vue` - Root application component with sidebar management
- `src/components/` - Reusable Vue components including UI components
- `src/pages/` - Topic-specific page components with split layouts
- `src/router/` - Vue Router configuration with topic-based routes
- `src/utilities/` - Utility classes like BlenderModelViewer for 3D functionality
- `src/assets/` - Static assets and styling
- `public/` - Public static files including 3D models
- `dist/` - Production build output (generated)

### TypeScript Configuration
- **Strict Mode**: Enabled with `noUnusedLocals` and `noUnusedParameters`
- **Path Aliases**: `@/*` maps to `src/*` for cleaner imports
- **Vue Support**: Full TypeScript support for Vue SFCs with vue-tsc

### Styling Architecture
- **Tailwind CSS**: Utility-first CSS framework with custom configuration
- **CSS Variables**: Used for theme colors and consistent design tokens
- **Responsive Design**: Mobile-first approach with breakpoint-based layouts
- **Component Scoping**: Scoped styles in Vue components with global utilities

## Custom Commands

### /commit - Smart Commit
Automatically checks the current diff, adds all changed files, creates a proper commit message, and commits to the current branch with correct co-author attribution.

**Usage**: `/commit` or just type "commit my changes"

**What it does**:
1. Runs `git status` to check for modified files
2. Runs `git diff` to analyze changes
3. Gets current git config for co-author information
4. Adds all modified files with `git add`
5. Creates a descriptive commit message based on the changes
6. Commits with proper Claude Code attribution and co-author

**Safe for**: Non-main branches only (as specified by user preference)S

### /pr - Smart Pull Request
Automatically creates a pull request against the dev branch following the project's PR title conventions and includes proper commit analysis.

**Usage**: `/pr` or just type "create pull request"

**What it does**:
1. Runs `git status` and `git diff` to check current changes
2. Analyzes commit history from dev branch divergence using `git diff dev...HEAD`
3. Pushes current branch to remote with upstream tracking
4. Creates PR with properly formatted title using required prefixes:
   - `Fix:` for bug fixes
   - `Feat:` for new features
   - `Docs:`, `Test:`, `Chore:`, `CI:`, `Perf:`, `Refactor:`, `Revert:`, `Style:`
   - Or scoped versions like `Fix(scope):`, `Feat(scope):`
5. Generates comprehensive PR body with summary, changes, and test plan
6. Sets base branch to `dev` (default target branch)

**PR Title Format**: Must match patterns in `.github/pr-title-checker-config.json`
**Safe for**: Any feature branch that needs to merge into dev