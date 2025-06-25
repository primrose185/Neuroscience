# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Vue 3 Frontend
- **Install dependencies**: `yarn install`
- **Start development server**: `yarn dev` (runs on localhost:5173)
- **Build for production**: `yarn build`
- **Preview production build**: `yarn preview`
- **Type checking**: `yarn type-check` (if vue-tsc available)

### Deployment
- **Vercel deployment**: `vercel` or `vercel --prod`
- **Vercel dev**: `vercel dev` (local development with Vercel environment)

## Architecture Overview

### Project Structure
This is a frontend-only Vue 3 application:

- **Framework**: Vue 3 with Composition API and TypeScript
- **Build System**: Vite for fast development and optimized production builds
- **Styling**: Tailwind CSS with shadcn-vue components
- **Package Management**: Yarn (specified in packageManager field)

### Frontend Architecture
- **Framework**: Vue 3 with Composition API and TypeScript
- **UI Components**: shadcn-vue components with Tailwind CSS styling
- **3D Graphics**: Three.js integration for 3D visualizations
- **Routing**: Vue Router with topic-based page structure (`/topic1/page1`, `/topic2/page1`, etc.)
- **State Management**: Vue 3 reactivity and composables pattern
- **Layout**: Sidebar navigation with collapsible menu structure

### Key Features
- **TypeScript**: Full type safety throughout the application
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Component Architecture**: Reusable Vue components following shadcn-vue patterns
- **Router**: Client-side routing with history mode for SEO-friendly URLs
- **3D Visualization**: Three.js integration for interactive 3D content

### Development Workflow
1. Install dependencies with `yarn install`
2. Start development server with `yarn dev`
3. Build for production with `yarn build`
4. Deploy to Vercel using `vercel` command or git integration

### File Structure
- `src/App.vue` - Root application component
- `src/components/` - Reusable Vue components
- `src/pages/` - Page components for different routes  
- `src/router/` - Vue Router configuration
- `src/assets/` - Static assets
- `public/` - Public static files
- `dist/` - Production build output (generated)