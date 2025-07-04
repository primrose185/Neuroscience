import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

class BlenderModelViewer {
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
    this.renderer.outputEncoding = THREE.sRGBEncoding;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1;
    
    this.container.appendChild(this.renderer.domElement);
    
    // Controls setup
    if (this.options.enableControls) {
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
      
      // Apply options
      if (options.scale) {
        model.scale.setScalar(options.scale);
      }
      
      if (options.position) {
        model.position.set(options.position.x, options.position.y, options.position.z);
      }
      
      if (options.rotation) {
        model.rotation.set(options.rotation.x, options.rotation.y, options.rotation.z);
      }
      
      // Enable shadows
      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });
      
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
      return { model, animations: this.animations };
      
    } catch (error) {
      console.error('Error loading model:', error);
      throw error;
    }
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
export default BlenderModelViewer;

// Usage example:
/*
// In your Vue component:
import BlenderModelViewer from './BlenderModelViewer.js';

export default {
  mounted() {
    this.viewer = new BlenderModelViewer('model-container', {
      enableControls: true,
      autoRotate: true,
      background: 0x222222,
      fog: true
    });
    
    this.loadModel();
  },
  
  methods: {
    async loadModel() {
      try {
        const result = await this.viewer.loadModel('/models/my-model.glb', {
          scale: 1,
          position: { x: 0, y: 0, z: 0 },
          autoPlay: true,
          fitCamera: true
        });
        
        console.log('Available animations:', this.viewer.getAnimationNames());
      } catch (error) {
        console.error('Failed to load model:', error);
      }
    },
    
    playAnimation(name) {
      const index = this.viewer.getAnimationNames().indexOf(name);
      if (index !== -1) {
        this.viewer.playAnimation(index, {
          loop: THREE.LoopRepeat,
          clampWhenFinished: false
        });
      }
    }
  },
  
  beforeUnmount() {
    if (this.viewer) {
      this.viewer.dispose();
    }
  }
}
*/