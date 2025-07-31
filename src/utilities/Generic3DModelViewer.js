import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

class Generic3DModelViewer {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.mixer = null;
    this.clock = new THREE.Clock();
    this.animations = [];
    this.currentModel = null;
    
    // Default options
    this.options = {
      enableControls: true,
      static: false,
      autoRotate: false,
      background: 0x000000,
      fog: false,
      lights: {
        ambient: { color: 0x404040, intensity: 0.4 },
        directional: { color: 0xffffff, intensity: 0.8 }
      },
      camera: {
        position: { x: 0, y: 5, z: 10 },
        fov: 75,
        near: 0.1,
        far: 1000
      },
      materials: {
        color: 0xffffff,
        metalness: 0.1,
        roughness: 0.7,
        transparent: false,
        opacity: 1.0
      },
      ...options
    };
    
    this.init();
  }
  
  init() {
    // Scene setup
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(this.options.background);
    
    // Add fog if enabled
    if (this.options.fog) {
      this.scene.fog = new THREE.Fog(this.options.background, 1, 100);
    }
    
    // Camera setup
    const aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(
      this.options.camera.fov,
      aspect,
      this.options.camera.near,
      this.options.camera.far
    );
    
    this.camera.position.set(
      this.options.camera.position.x,
      this.options.camera.position.y,
      this.options.camera.position.z
    );
    
    // Renderer setup
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1;
    
    this.container.appendChild(this.renderer.domElement);
    
    // Controls setup
    if (this.options.enableControls && !this.options.static) {
      this.controls = new OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.autoRotate = this.options.autoRotate;
      this.controls.autoRotateSpeed = 2.0;
    }
    
    // Lighting setup
    this.setupLights();
    
    // Handle window resize
    window.addEventListener('resize', () => this.onWindowResize());
    
    // Start render loop
    this.animate();
  }
  
  setupLights() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(
      this.options.lights.ambient.color,
      this.options.lights.ambient.intensity
    );
    this.scene.add(ambientLight);
    
    // Directional light
    const directionalLight = new THREE.DirectionalLight(
      this.options.lights.directional.color,
      this.options.lights.directional.intensity
    );
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 500;
    this.scene.add(directionalLight);
    
    // Helper light for better model visibility
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-10, 0, -10);
    this.scene.add(fillLight);
  }
  
  async loadModel(modelPath, options = {}) {
    const loader = new GLTFLoader();
    
    // Setup DRACO decoder for compressed models
    const dracoLoader = new DRACOLoader();
    dracoLoader.setDecoderPath('/draco/');
    loader.setDRACOLoader(dracoLoader);
    
    try {
      const gltf = await new Promise((resolve, reject) => {
        loader.load(
          modelPath,
          resolve,
          (progress) => {
            console.log('Loading progress:', (progress.loaded / progress.total * 100) + '%');
          },
          reject
        );
      });
      
      // Remove previous model if exists
      if (this.currentModel) {
        this.scene.remove(this.currentModel);
      }
      
      // Stop previous animations
      if (this.mixer) {
        this.mixer.stopAllAction();
      }
      
      const model = gltf.scene;
      this.currentModel = model;
      
      // Apply transform options
      if (options.scale) {
        model.scale.setScalar(options.scale);
      }
      
      if (options.position) {
        model.position.set(options.position.x, options.position.y, options.position.z);
      }
      
      if (options.rotation) {
        model.rotation.set(options.rotation.x, options.rotation.y, options.rotation.z);
      }
      
      // Configure model materials and shadows with texture preservation
      this.configureModelMaterials(model, options);
      
      // Setup animations
      if (gltf.animations && gltf.animations.length > 0) {
        this.mixer = new THREE.AnimationMixer(model);
        this.animations = gltf.animations;
        
        // Auto-play first animation if specified
        if (options.autoPlay !== false) {
          this.playAnimation(0);
        }
      }
      
      // Add to scene
      this.scene.add(model);
      
      // Auto-fit camera if specified
      if (options.fitCamera !== false) {
        this.fitCameraToModel(model);
      }
      
      console.log('Model loaded successfully:', modelPath);
      console.log('Available animations:', this.getAnimationNames());
      
      return { model, animations: this.animations };
      
    } catch (error) {
      console.error('Error loading model:', error);
      throw error;
    }
  }
  
  configureModelMaterials(model, options) {
    model.traverse((child) => {
      if (child.isMesh && child.material) {
        child.castShadow = true;
        child.receiveShadow = true;
        
        // Check if material has textures (UV mapped textures, normal maps, etc.)
        const hasTextures = child.material.map || 
                           child.material.normalMap || 
                           child.material.roughnessMap || 
                           child.material.metalnessMap ||
                           child.material.aoMap ||
                           child.material.emissiveMap;
        
        if (hasTextures) {
          console.log('Preserving textured material for:', child.name || 'unnamed mesh');
          
          // Preserve textured material but allow selective property updates
          if (options.material) {
            // Only update properties that don't conflict with textures
            if (options.material.metalness !== undefined) {
              child.material.metalness = options.material.metalness;
            }
            if (options.material.roughness !== undefined) {
              child.material.roughness = options.material.roughness;
            }
            if (options.material.transparent !== undefined) {
              child.material.transparent = options.material.transparent;
            }
            if (options.material.opacity !== undefined) {
              child.material.opacity = options.material.opacity;
            }
            
            // Only override color if there's no color map AND force override is enabled
            if (options.material.color !== undefined && 
                (!child.material.map || options.forceMaterialOverride)) {
              child.material.color.setHex(options.material.color);
            }
          }
          
          // Ensure proper texture settings for Three.js
          if (child.material.map) {
            child.material.map.flipY = false;
            child.material.map.colorSpace = THREE.SRGBColorSpace;
          }
          
        } else if (options.material || this.options.materials || options.forceMaterialOverride) {
          // No textures detected, safe to replace with custom material
          console.log('Applying custom material to:', child.name || 'unnamed mesh');
          
          const materialConfig = { ...this.options.materials, ...options.material };
          child.material = new THREE.MeshStandardMaterial({
            color: materialConfig.color,
            metalness: materialConfig.metalness,
            roughness: materialConfig.roughness,
            transparent: materialConfig.transparent,
            opacity: materialConfig.opacity
          });
        }
        
        child.material.needsUpdate = true;
      }
    });
  }
  
  fitCameraToModel(model) {
    const box = new THREE.Box3().setFromObject(model);
    const size = box.getSize(new THREE.Vector3()).length();
    const center = box.getCenter(new THREE.Vector3());
    
    // Adjust camera position
    const distance = size * 1.5;
    this.camera.position.copy(center);
    this.camera.position.x += distance;
    this.camera.position.y += distance * 0.5;
    this.camera.position.z += distance;
    
    // Update controls target
    if (this.controls) {
      this.controls.target.copy(center);
      this.controls.update();
    }
  }
  
  playAnimation(index, options = {}) {
    if (!this.mixer || !this.animations[index]) {
      console.warn('Animation not found:', index);
      return;
    }
    
    const action = this.mixer.clipAction(this.animations[index]);
    
    // Apply options
    if (options.loop !== undefined) {
      action.loop = options.loop;
    }
    
    if (options.clampWhenFinished) {
      action.clampWhenFinished = true;
    }
    
    if (options.weight !== undefined) {
      action.weight = options.weight;
    }
    
    action.play();
    
    return action;
  }
  
  stopAnimation(index) {
    if (!this.mixer || !this.animations[index]) {
      return;
    }
    
    const action = this.mixer.clipAction(this.animations[index]);
    action.stop();
  }
  
  stopAllAnimations() {
    if (this.mixer) {
      this.mixer.stopAllAction();
    }
  }
  
  getAnimationNames() {
    return this.animations.map(animation => animation.name);
  }
  
  setBackground(color) {
    this.scene.background = new THREE.Color(color);
  }
  
  addEnvironmentMap(texturePath) {
    const loader = new THREE.CubeTextureLoader();
    const texture = loader.load([
      texturePath, texturePath, texturePath,
      texturePath, texturePath, texturePath
    ]);
    
    this.scene.environment = texture;
    this.scene.background = texture;
  }
  
  updateMaterials(materialConfig) {
    if (!this.currentModel) return;
    
    this.currentModel.traverse((child) => {
      if (child.isMesh && child.material) {
        // Check if material has textures before updating
        const hasTextures = child.material.map || 
                           child.material.normalMap || 
                           child.material.roughnessMap || 
                           child.material.metalnessMap;
        
        if (hasTextures) {
          // For textured materials, only update non-conflicting properties
          if (materialConfig.metalness !== undefined) {
            child.material.metalness = materialConfig.metalness;
          }
          if (materialConfig.roughness !== undefined) {
            child.material.roughness = materialConfig.roughness;
          }
          if (materialConfig.opacity !== undefined) {
            child.material.opacity = materialConfig.opacity;
          }
          if (materialConfig.transparent !== undefined) {
            child.material.transparent = materialConfig.transparent;
          }
          
          // Only update color if no color map exists or force override
          if (materialConfig.color !== undefined && 
              (!child.material.map || materialConfig.forceColorOverride)) {
            child.material.color.setHex(materialConfig.color);
          }
        } else {
          // No textures, safe to update all properties
          if (materialConfig.color !== undefined) {
            child.material.color.setHex(materialConfig.color);
          }
          if (materialConfig.metalness !== undefined) {
            child.material.metalness = materialConfig.metalness;
          }
          if (materialConfig.roughness !== undefined) {
            child.material.roughness = materialConfig.roughness;
          }
          if (materialConfig.opacity !== undefined) {
            child.material.opacity = materialConfig.opacity;
          }
          if (materialConfig.transparent !== undefined) {
            child.material.transparent = materialConfig.transparent;
          }
        }
        
        child.material.needsUpdate = true;
      }
    });
  }
  
  // New method to force material override (useful for debugging)
  forceReplaceMaterials(materialConfig) {
    if (!this.currentModel) return;
    
    this.currentModel.traverse((child) => {
      if (child.isMesh) {
        child.material = new THREE.MeshStandardMaterial({
          color: materialConfig.color || 0xffffff,
          metalness: materialConfig.metalness || 0.1,
          roughness: materialConfig.roughness || 0.7,
          transparent: materialConfig.transparent || false,
          opacity: materialConfig.opacity || 1.0
        });
        child.material.needsUpdate = true;
      }
    });
  }
  
  // Debug method to inspect materials
  inspectMaterials() {
    if (!this.currentModel) {
      console.log('No model loaded');
      return;
    }
    
    console.log('=== Material Inspection ===');
    this.currentModel.traverse((child, index) => {
      if (child.isMesh && child.material) {
        console.log(`Mesh ${index}: ${child.name || 'unnamed'}`);
        console.log('- Material type:', child.material.type);
        console.log('- Has color map:', !!child.material.map);
        console.log('- Has normal map:', !!child.material.normalMap);
        console.log('- Has roughness map:', !!child.material.roughnessMap);
        console.log('- Has metalness map:', !!child.material.metalnessMap);
        console.log('- Base color:', child.material.color);
        console.log('- Metalness:', child.material.metalness);
        console.log('- Roughness:', child.material.roughness);
        console.log('---');
      }
    });
  }
  
  onWindowResize() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }
  
  animate() {
    requestAnimationFrame(() => this.animate());
    
    const delta = this.clock.getDelta();
    
    // Update animations
    if (this.mixer) {
      this.mixer.update(delta);
    }
    
    // Update controls
    if (this.controls) {
      this.controls.update();
    }
    
    // Render
    this.renderer.render(this.scene, this.camera);
  }
  
  dispose() {
    // Clean up resources
    if (this.mixer) {
      this.mixer.stopAllAction();
    }
    
    if (this.controls) {
      this.controls.dispose();
    }
    
    if (this.renderer) {
      this.renderer.dispose();
    }
    
    window.removeEventListener('resize', this.onWindowResize);
  }
}

// Export for use in Vue components
export default Generic3DModelViewer;

// Updated usage example:
/*
// In your Vue component:
import Generic3DModelViewer from './Generic3DModelViewer.js';

export default {
  mounted() {
    this.viewer = new Generic3DModelViewer('model-container', {
      enableControls: true,
      autoRotate: true,
      background: 0x222222,
      fog: true,
      // Only set default materials if you want to override non-textured materials
      materials: {
        color: 0x4488ff,
        metalness: 0.2,
        roughness: 0.8
      }
    });
    
    this.loadModel();
  },
  
  methods: {
    async loadModel() {
      try {
        // Load model preserving UV textures
        const result = await this.viewer.loadModel('/models/my-model.glb', {
          scale: 1,
          position: { x: 0, y: 0, z: 0 },
          autoPlay: true,
          fitCamera: true
          // Don't specify material options to preserve UV textures
        });
        
        // Inspect materials after loading
        this.viewer.inspectMaterials();
        
        console.log('Available animations:', this.viewer.getAnimationNames());
      } catch (error) {
        console.error('Failed to load model:', error);
      }
    },
    
    // Load model with selective material overrides
    async loadModelWithCustomMaterial() {
      try {
        const result = await this.viewer.loadModel('/models/my-model.glb', {
          scale: 1,
          fitCamera: true,
          material: {
            // Only override metalness and roughness, preserve textures
            metalness: 0.3,
            roughness: 0.6
            // Don't set color to preserve UV painted textures
          }
        });
      } catch (error) {
        console.error('Failed to load model:', error);
      }
    },
    
    // Force material override (for debugging)
    forceCustomMaterial() {
      this.viewer.forceReplaceMaterials({
        color: 0xff4444,
        metalness: 0.3,
        roughness: 0.6
      });
    },
    
    playAnimation(name) {
      const index = this.viewer.getAnimationNames().indexOf(name);
      if (index !== -1) {
        this.viewer.playAnimation(index, {
          loop: THREE.LoopRepeat,
          clampWhenFinished: false
        });
      }
    },
    
    // Update only metalness/roughness without affecting textures
    updateMaterialProperties(metalness, roughness) {
      this.viewer.updateMaterials({ 
        metalness: metalness, 
        roughness: roughness 
      });
    }
  },
  
  beforeUnmount() {
    if (this.viewer) {
      this.viewer.dispose();
    }
  }
}
*/