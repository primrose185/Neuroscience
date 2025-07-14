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
    this.voltageData = null;
    this.voltageAnimation = {
      isPlaying: false,
      currentFrame: 0,
      totalFrames: 0,
      speed: 1.0,
      meshMap: new Map() // Maps mesh names to section data
    };
    
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
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
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
      
      // Enable shadows and debug model data
      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
          
          // Debug vertex attributes
          console.log('Mesh:', child.name);
          console.log('Geometry attributes:', Object.keys(child.geometry.attributes));
          
          // Check for Voltage attribute specifically
          if (child.geometry.attributes.Voltage) {
            console.log('✓ Voltage attribute found:', child.geometry.attributes.Voltage);
          } else {
            console.log('✗ No Voltage attribute found');
          }
          
          // Debug materials
          console.log('Material:', child.material);
          if (child.material.userData) {
            console.log('Material userData:', child.material.userData);
          }
          
          // Apply fallback emission material if Voltage attribute missing
          if (!child.geometry.attributes.Voltage) {
            const emissionMaterial = new THREE.MeshStandardMaterial({
              color: 0x4444ff,
              emissive: 0x002288,
              emissiveIntensity: 0.3,
              metalness: 0.1,
              roughness: 0.7
            });
            child.material = emissionMaterial;
            console.log('Applied fallback emission material');
          }
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
      
      // Create mesh mapping for voltage data if available
      if (this.voltageData) {
        this.mapVoltageDataToMeshes();
      }
      
      // Auto-fit camera if specified
      if (options.fitCamera !== false) {
        this.fitCameraToModel(model);
      }
      
      // Debug animation data
      console.log('Available animations:', gltf.animations);
      gltf.animations.forEach((anim, index) => {
        console.log(`Animation ${index}:`, anim.name);
        console.log('Tracks:', anim.tracks.map(track => ({
          name: track.name,
          type: track.ValueTypeName,
          times: track.times.length
        })));
      });

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
  
  async loadVoltageData(jsonPath) {
    try {
      console.log('Loading voltage animation data:', jsonPath);
      
      const response = await fetch(jsonPath);
      if (!response.ok) {
        throw new Error(`Failed to load voltage data: ${response.status}`);
      }
      
      this.voltageData = await response.json();
      
      // Validate data structure
      if (!this.voltageData.sections || !this.voltageData.metadata) {
        throw new Error('Invalid voltage data format');
      }
      
      // Set up animation parameters
      this.voltageAnimation.totalFrames = this.voltageData.metadata.frames;
      this.voltageAnimation.currentFrame = 0;
      
      // Create mesh mapping
      if (this.currentModel) {
        this.mapVoltageDataToMeshes();
      }
      
      console.log('Voltage data loaded successfully:');
      console.log(`  - ${this.voltageData.sections.length} sections`);
      console.log(`  - ${this.voltageAnimation.totalFrames} frames`);
      console.log(`  - Duration: ${this.voltageData.metadata.duration_ms}ms`);
      console.log(`  - Voltage range: ${this.voltageData.metadata.global_voltage_range.min} to ${this.voltageData.metadata.global_voltage_range.max} mV`);
      
      return this.voltageData;
      
    } catch (error) {
      console.error('Error loading voltage data:', error);
      throw error;
    }
  }
  
  mapVoltageDataToMeshes() {
    if (!this.voltageData || !this.currentModel) return;
    
    console.log('Mapping voltage data to model meshes...');
    this.voltageAnimation.meshMap.clear();
    
    // Traverse model to find meshes and match them to voltage sections
    this.currentModel.traverse((child) => {
      if (child.isMesh) {
        // Try to match mesh name to section name
        const meshName = child.name;
        
        // Find corresponding section data
        const sectionData = this.voltageData.sections.find(section => {
          // Try exact match first
          if (section.name === meshName) return true;
          
          // Try partial matches (mesh names might be modified during export)
          if (meshName.includes(section.name) || section.name.includes(meshName)) return true;
          
          // Try matching by index if names don't work
          const meshIndex = parseInt(meshName.match(/\d+$/)?.[0]);
          if (!isNaN(meshIndex) && meshIndex === section.id) return true;
          
          return false;
        });
        
        if (sectionData) {
          this.voltageAnimation.meshMap.set(child, sectionData);
          console.log(`  - Mapped mesh "${meshName}" to section "${sectionData.name}"`);
        } else {
          console.warn(`  - No voltage data found for mesh "${meshName}"`);
        }
      }
    });
    
    console.log(`Mapped ${this.voltageAnimation.meshMap.size} meshes to voltage data`);
  }
  
  voltageToColor(voltage, minVoltage = -70, maxVoltage = 20) {
    // Normalize voltage to 0-1 range
    const normalized = (voltage - minVoltage) / (maxVoltage - minVoltage);
    const clamped = Math.max(0, Math.min(1, normalized));
    
    // Create color based on voltage (mimicking BlenderSpike's plasma colormap)
    // Low voltage (rest): dark blue/purple
    // High voltage (action potential): bright yellow/white
    
    if (clamped < 0.25) {
      // Dark blue to blue
      return new THREE.Color(0.05 + clamped * 0.6, 0.05 + clamped * 0.2, 0.3 + clamped * 2.8);
    } else if (clamped < 0.5) {
      // Blue to purple/magenta
      const t = (clamped - 0.25) * 4;
      return new THREE.Color(0.2 + t * 0.6, 0.1, 0.8 + t * 0.2);
    } else if (clamped < 0.75) {
      // Purple to red/orange
      const t = (clamped - 0.5) * 4;
      return new THREE.Color(0.8 + t * 0.2, 0.1 + t * 0.7, 0.8 - t * 0.8);
    } else {
      // Red/orange to yellow/white
      const t = (clamped - 0.75) * 4;
      return new THREE.Color(1.0, 0.8 + t * 0.2, t * 0.8);
    }
  }
  
  updateVoltageFrame(frameIndex) {
    if (!this.voltageData || !this.currentModel) return;
    
    const clampedFrame = Math.max(0, Math.min(frameIndex, this.voltageAnimation.totalFrames - 1));
    this.voltageAnimation.currentFrame = clampedFrame;
    
    const { min: minVoltage, max: maxVoltage } = this.voltageData.metadata.global_voltage_range;
    
    // Update materials for each mapped mesh
    this.voltageAnimation.meshMap.forEach((sectionData, mesh) => {
      if (clampedFrame < sectionData.voltage_frames.length) {
        const voltage = sectionData.voltage_frames[clampedFrame];
        const color = this.voltageToColor(voltage, minVoltage, maxVoltage);
        
        // Update material color and emission
        if (mesh.material) {
          mesh.material.color.copy(color);
          mesh.material.emissive.copy(color.clone().multiplyScalar(0.3));
          mesh.material.emissiveIntensity = 0.2 + (voltage - minVoltage) / (maxVoltage - minVoltage) * 0.8;
          mesh.material.needsUpdate = true;
        }
      }
    });
  }
  
  playVoltageAnimation(speed = 1.0) {
    this.voltageAnimation.isPlaying = true;
    this.voltageAnimation.speed = speed;
    console.log('Started voltage animation');
  }
  
  pauseVoltageAnimation() {
    this.voltageAnimation.isPlaying = false;
    console.log('Paused voltage animation');
  }
  
  stopVoltageAnimation() {
    this.voltageAnimation.isPlaying = false;
    this.voltageAnimation.currentFrame = 0;
    this.updateVoltageFrame(0);
    console.log('Stopped voltage animation');
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
    
    // Update voltage animation
    if (this.voltageAnimation.isPlaying && this.voltageData) {
      // Calculate frame rate based on metadata
      const framesPerSecond = this.voltageAnimation.totalFrames / (this.voltageData.metadata.duration_ms / 1000);
      const frameIncrement = delta * framesPerSecond * this.voltageAnimation.speed;
      
      this.voltageAnimation.currentFrame += frameIncrement;
      
      // Loop animation
      if (this.voltageAnimation.currentFrame >= this.voltageAnimation.totalFrames) {
        this.voltageAnimation.currentFrame = 0;
      }
      
      // Update voltage colors
      this.updateVoltageFrame(Math.floor(this.voltageAnimation.currentFrame));
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