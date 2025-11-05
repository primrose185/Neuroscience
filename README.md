# nREM - Neuroscience Research Explained Modestly

An interactive educational web platform that brings neuroscience research to life through engaging 3D visualizations and storytelling. Built with Vue 3 and Three.js, nREM makes complex neuroscience concepts accessible through modern web technologies and immersive 3D models.

## Overview

nREM presents neuroscience research through a unique combination of narrative-driven content and interactive 3D visualizations. The first example is the Haldan Keffer Hartline's Nobel Prize-winning work (1967) on visual processes, lateral inhibition, and retinal interactions in the horseshoe crab (*Limulus polyphemus*).

### Key Features

- **Interactive 3D Model Viewer** - Real-time WebGL-based 3D models with orbit controls and custom camera positioning
- **Voltage Animation System** - Visualize membrane potential changes with real-time voltage animations using NEURON simulation data
- **Scroll-Based Storytelling** - 3D models synchronized with educational content that changes as you scroll
- **Split-Pane Layouts** - Resizable panels for content and visualizations with mobile-responsive design
- **Fuzzy Search** - Powerful search across all pages, topics, and glossary terms
- **Model-Specific Camera Positions** - Each visualization has optimized viewing angles with smooth transitions

## Main Idea and Implementation

### Architecture

The platform uses a **component-based architecture** with Vue 3's Composition API and TypeScript for type safety. The core innovation is the seamless integration of educational content with interactive 3D models:

```
┌─────────────────────────────────────────────────┐
│  Narrative Content (Markdown/HTML)              │
│  ├─ Story blocks with scroll triggers           │
│  └─ Educational text and explanations           │
└─────────────────────────────────────────────────┘
                      ↓ synchronized
┌─────────────────────────────────────────────────┐
│  3D Visualization Layer (Three.js)              │
│  ├─ GLTF/GLB model loading                      │
│  ├─ Real-time voltage animations                │
│  ├─ Custom camera positioning                   │
│  └─ Interactive controls (orbit, zoom)          │
└─────────────────────────────────────────────────┘
```

### Core Technologies

- **Blender** - 3D modeling and simulation
- **Vue 3** - Reactive UI framework with Composition API
- **TypeScript** - Type-safe development
- **Three.js** - WebGL 3D graphics rendering
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **shadcn-vue** - High-quality UI component library

### 3D Visualization System

Two custom model viewer implementations power the platform:

1. **BlenderModelViewer.js** - Advanced viewer with voltage animation capabilities

   - Real-time membrane potential visualization
   - Matplotlib plasma colormap implementation in WebGL
   - Frame-by-frame voltage data interpolation
   - Support for NEURON simulation data
2. **Generic3DModelViewer.js** - General-purpose viewer for anatomical models

   - Optimized camera positioning per model
   - Auto-rotation and orbit controls
   - Shadow mapping and PBR materials
   - GLTF animation playback

### Scroll-Driven Storytelling

The `StickyStoryBlocks` component creates an immersive learning experience:

```typescript
// As users scroll through story blocks...
<StickyStoryBlocks :stories="storyData" />

// ...models automatically switch based on scroll position
{
  model: '/models/horseshoe_crab.glb',
  content: 'Introduction to our model organism...'
}
```

The Intersection Observer API tracks scroll position and triggers model changes, creating a seamless narrative flow.

## Getting Started

### Prerequisites

- **Node.js** 16+
- **Yarn** 1.22+ (specified in packageManager)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Neuroscience
   ```
2. **Install dependencies**

   ```bash
   yarn install
   ```
3. **Start the development server**

   ```bash
   yarn dev
   ```

   The application will be available at `http://localhost:5173`

### Available Scripts

```bash
# Development server with hot-reload
yarn dev

# Build for production
yarn build

# Preview production build locally
yarn preview

# Type checking (no output)
vue-tsc --noEmit
```

### Deployment

The project is configured for deployment to Vercel:

```bash
# Deploy to preview environment
vercel

# Deploy to production
vercel --prod
```

## Project Structure

```
Neuroscience/
├── src/
│   ├── App.vue                    # Root component with sidebar navigation
│   ├── main.ts                    # Application entry point
│   ├── components/
│   │   ├── Sidebar.vue           # Collapsible navigation menu
│   │   ├── SearchBar.vue         # Fuzzy search interface
│   │   ├── StickyStoryBlocks.vue # Scroll-based storytelling
│   │   ├── TwoPaneVisualizationSection.vue # Split-pane layout
│   │   └── Shared3DModelViewer.vue # 3D model viewer wrapper
│   ├── pages/
│   │   ├── HomePage.vue          # Landing page with hero model
│   │   ├── Topic1Page1.vue       # Visual receptors introduction
│   │   ├── Topic1Page2.vue       # Single ommatidia experiments
│   │   └── ...                   # Additional topic pages
│   ├── router/
│   │   └── index.ts              # Vue Router configuration
│   ├── utilities/
│   │   ├── BlenderModelViewer.js  # Voltage animation viewer
│   │   └── Generic3DModelViewer.js # General 3D model viewer
│   └── types/
│       └── index.ts              # TypeScript type definitions
├── public/
│   ├── models/                   # 3D models (GLTF/GLB)
│   └── data/                     # Voltage simulation data
├── dist/                         # Production build output
└── package.json
```

## Educational Content

### Current Topics

**Topic 1: Visual Receptors and Retinal Interaction (Hartline, 1967)**

- Introducing *Limulus polyphemus* as a model organism
- Experimental setup with recording chambers
- Action potential visualization with voltage animations
- Lateral inhibition and sensory adaptation
- Mathematical models of retinal interaction

**Topic 2: Neuroscience Fundamentals**

- Neural anatomy and brain structure
- Neural circuits and connectivity
- Brain imaging and analysis

**Topic 3: Advanced Neural Networks** *(Coming Soon)*

### Platform Features

- **Interactive Glossary** - Searchable neuroscience terminology
- **Platform Guide** - Tutorials on using 3D visualizations
- **Search Functionality** - Find content across all topics

## Technology Highlights

### Voltage Animation System

The platform features a sophisticated voltage animation system that visualizes membrane potential changes in real-time:

```javascript
// Load voltage data from NEURON simulations
await viewer.loadVoltageAnimation('/data/voltage_frames.json');

// Play animation synchronized with educational content
viewer.playVoltageAnimation();
```

Features:

- Accurate matplotlib plasma colormap in WebGL
- Frame-by-frame interpolation for smooth transitions
- Material configuration for different neuron components
- Real-time color mapping based on voltage values (-80mV to +40mV)

### Model-Specific Camera System

Each 3D model has optimized camera settings that automatically apply when the model loads:

```javascript
const cameraSettings = {
  'horseshoe_crab_basic.glb': {
    position: { x: 0, y: 2, z: 5 },
    target: { x: 0, y: 0, z: 0 }
  },
  'eccentric_bipolarblend.glb': {
    position: { x: 0.5, y: 1, z: 3 },
    target: { x: 0, y: 0.5, z: 0 }
  }
};
```

This prevents jarring transitions and ensures each visualization is presented from the best angle.

## Visualizations

> [Placeholder: Screenshots and GIFs of key visualizations will be added here]

### Home Page - Horseshoe Crab Model

![Placeholder for home page hero visualization](#)

### Recording Chamber Visualization

![Placeholder for experimental setup 3D model](#)

### Voltage Animation - Action Potential

![Placeholder for animated neuron with voltage colormap](#)

### Scroll-Based Storytelling

![Placeholder for sticky story blocks demonstration](#)

### Split-Pane Layout

![Placeholder for resizable content/visualization panels](#)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

WebGL support is required for 3D visualizations.

## Contributing

This is an educational project focused on making neuroscience research accessible. Contributions are welcome!

### Development Guidelines

- Use TypeScript for all new code
- Follow Vue 3 Composition API patterns
- Use Tailwind CSS utility classes for styling
- Maintain mobile responsiveness
- Add TypeScript types for new components

## License

[Add license information]

## Acknowledgments

- Nobel Prize winner Haldan Keffer Hartline for pioneering visual neuroscience research
- The horseshoe crab (*Limulus polyphemus*) as an invaluable model organism
- Three.js community for excellent 3D graphics tools
- Vue.js team for the fantastic framework

---

Built with Vue 3, Three.js, and a passion for making neuroscience accessible to everyone.
