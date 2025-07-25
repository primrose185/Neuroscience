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
    this.materialConfig = null;
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
      
      // Load material configuration if available
      if (this.voltageData.material_config) {
        this.materialConfig = this.voltageData.material_config;
        console.log('Material configuration loaded:');
        console.log(`  - Colormap: ${this.materialConfig.colormap_name}`);
        console.log(`  - Emission strength: ${this.materialConfig.emission_strength}`);
        console.log(`  - Colormap steps: ${this.materialConfig.colormap_steps}`);
        console.log(`  - Colormap range: ${this.materialConfig.cmap_start} to ${this.materialConfig.cmap_end}`);
        console.log(`  - Material voltage range: ${this.materialConfig.voltage_range.min} to ${this.materialConfig.voltage_range.max} mV`);
      } else {
        // Fallback to default material configuration for backward compatibility
        this.materialConfig = {
          emission_strength: 2.0,
          colormap_steps: 10,
          cmap_start: 0.0,
          cmap_end: 1.0,
          colormap_name: 'plasma',
          voltage_range: {
            min: this.voltageData.metadata.global_voltage_range?.min || -70,
            max: this.voltageData.metadata.global_voltage_range?.max || 20
          }
        };
        console.log('Using default material configuration (no material_config found in data)');
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
    
    // Collect all meshes in scene traversal order
    const meshes = [];
    this.currentModel.traverse((child) => {
      if (child.isMesh) {
        meshes.push(child);
      }
    });
    
    // Sort meshes by name to ensure consistent ordering
    meshes.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`Found ${meshes.length} meshes, ${this.voltageData.sections.length} voltage sections`);
    
    // Map by index since GLB export preserves order but not names
    meshes.forEach((mesh, index) => {
      if (index < this.voltageData.sections.length) {
        const sectionData = this.voltageData.sections[index];
        this.voltageAnimation.meshMap.set(mesh, sectionData);
        console.log(`  - Mapped mesh[${index}] "${mesh.name}" to section "${sectionData.name}" (type: ${sectionData.type})`);
      } else {
        console.warn(`  - Mesh[${index}] "${mesh.name}" has no corresponding voltage data`);
      }
    });
    
    // Verify mapping success
    const mappedCount = this.voltageAnimation.meshMap.size;
    const expectedCount = Math.min(meshes.length, this.voltageData.sections.length);
    
    if (mappedCount === expectedCount) {
      console.log(`✓ Successfully mapped ${mappedCount}/${expectedCount} meshes to voltage data`);
    } else {
      console.error(`✗ Mapping incomplete: ${mappedCount}/${expectedCount} meshes mapped`);
    }
  }
  
  voltageToColor(voltage, minVoltage = -70, maxVoltage = 20) {
    // Normalize voltage to 0-1 range
    const normalized = (voltage - minVoltage) / (maxVoltage - minVoltage);
    const clamped = Math.max(0, Math.min(1, normalized));
    
    // Apply colormap range if material configuration is available
    let colormapPosition = clamped;
    if (this.materialConfig) {
      // Map the 0-1 normalized voltage to the colormap range (cmap_start to cmap_end)
      colormapPosition = this.materialConfig.cmap_start + 
        (this.materialConfig.cmap_end - this.materialConfig.cmap_start) * clamped;
      colormapPosition = Math.max(0, Math.min(1, colormapPosition));
    }
    
    // Accurate matplotlib plasma colormap implementation
    // These are the exact RGB values from matplotlib's plasma colormap
    const plasmaColors = [
      [0.050383, 0.029803, 0.527975],  // 0.0 - Dark purple
      [0.063536, 0.028426, 0.533124],  // 0.1
      [0.075353, 0.027206, 0.538007],  // 0.2
      [0.086222, 0.026125, 0.542658],  // 0.3
      [0.096379, 0.025165, 0.547103],  // 0.4
      [0.105980, 0.024309, 0.551368],  // 0.5
      [0.115124, 0.023556, 0.555468],  // 0.6
      [0.123903, 0.022878, 0.559423],  // 0.7
      [0.132381, 0.022258, 0.563250],  // 0.8
      [0.140603, 0.021687, 0.566959],  // 0.9
      [0.148607, 0.021154, 0.570562],  // 1.0
      [0.156421, 0.020651, 0.574065],  // 1.1
      [0.164070, 0.020171, 0.577478],  // 1.2
      [0.171574, 0.019706, 0.580806],  // 1.3
      [0.178950, 0.019252, 0.584054],  // 1.4
      [0.186213, 0.018803, 0.587228],  // 1.5
      [0.193374, 0.018354, 0.590330],  // 1.6
      [0.200445, 0.017902, 0.593364],  // 1.7
      [0.207435, 0.017442, 0.596333],  // 1.8
      [0.214350, 0.016973, 0.599239],  // 1.9
      [0.221197, 0.016497, 0.602083],  // 2.0
      [0.227983, 0.016007, 0.604867],  // 2.1
      [0.234715, 0.015502, 0.607592],  // 2.2
      [0.241396, 0.014979, 0.610259],  // 2.3
      [0.248032, 0.014439, 0.612868],  // 2.4
      [0.254627, 0.013882, 0.615419],  // 2.5
      [0.261183, 0.013308, 0.617911],  // 2.6
      [0.267703, 0.012716, 0.620346],  // 2.7
      [0.274191, 0.012109, 0.622722],  // 2.8
      [0.280648, 0.011488, 0.625038],  // 2.9
      [0.287076, 0.010855, 0.627295],  // 3.0
      [0.293478, 0.010213, 0.629490],  // 3.1
      [0.299855, 0.009561, 0.631624],  // 3.2
      [0.306210, 0.008902, 0.633694],  // 3.3
      [0.312543, 0.008239, 0.635700],  // 3.4
      [0.318856, 0.007576, 0.637640],  // 3.5
      [0.325150, 0.006915, 0.639512],  // 3.6
      [0.331426, 0.006261, 0.641316],  // 3.7
      [0.337683, 0.005618, 0.643049],  // 3.8
      [0.343925, 0.004991, 0.644710],  // 3.9
      [0.350150, 0.004382, 0.646298],  // 4.0
      [0.356359, 0.003798, 0.647810],  // 4.1
      [0.362553, 0.003242, 0.649245],  // 4.2
      [0.368733, 0.002722, 0.650601],  // 4.3
      [0.374897, 0.002245, 0.651876],  // 4.4
      [0.381047, 0.001814, 0.653068],  // 4.5
      [0.387183, 0.001434, 0.654177],  // 4.6
      [0.393304, 0.001114, 0.655199],  // 4.7
      [0.399411, 0.000859, 0.656133],  // 4.8
      [0.405503, 0.000678, 0.656977],  // 4.9
      [0.411580, 0.000577, 0.657730],  // 5.0
      [0.417642, 0.000564, 0.658390],  // 5.1
      [0.423689, 0.000646, 0.658956],  // 5.2
      [0.429719, 0.000831, 0.659425],  // 5.3
      [0.435734, 0.001127, 0.659797],  // 5.4
      [0.441732, 0.001540, 0.660069],  // 5.5
      [0.447714, 0.002080, 0.660240],  // 5.6
      [0.453677, 0.002755, 0.660310],  // 5.7
      [0.459623, 0.003574, 0.660277],  // 5.8
      [0.465550, 0.004545, 0.660139],  // 5.9
      [0.471457, 0.005678, 0.659897],  // 6.0
      [0.477344, 0.006980, 0.659549],  // 6.1
      [0.483210, 0.008460, 0.659095],  // 6.2
      [0.489055, 0.010127, 0.658534],  // 6.3
      [0.494877, 0.011990, 0.657865],  // 6.4
      [0.500678, 0.014055, 0.657088],  // 6.5
      [0.506454, 0.016333, 0.656202],  // 6.6
      [0.512206, 0.018833, 0.655209],  // 6.7
      [0.517933, 0.021563, 0.654109],  // 6.8
      [0.523633, 0.024532, 0.652901],  // 6.9
      [0.529306, 0.027747, 0.651586],  // 7.0
      [0.534952, 0.031217, 0.650165],  // 7.1
      [0.540570, 0.034950, 0.648640],  // 7.2
      [0.546157, 0.038954, 0.647010],  // 7.3
      [0.551715, 0.043136, 0.645277],  // 7.4
      [0.557243, 0.047331, 0.643443],  // 7.5
      [0.562738, 0.051545, 0.641509],  // 7.6
      [0.568201, 0.055778, 0.639477],  // 7.7
      [0.573632, 0.060028, 0.637349],  // 7.8
      [0.579029, 0.064296, 0.635126],  // 7.9
      [0.584391, 0.068579, 0.632812],  // 8.0
      [0.589719, 0.072878, 0.630408],  // 8.1
      [0.595011, 0.077190, 0.627917],  // 8.2
      [0.600266, 0.081516, 0.625342],  // 8.3
      [0.605485, 0.085854, 0.622686],  // 8.4
      [0.610667, 0.090204, 0.619951],  // 8.5
      [0.615812, 0.094564, 0.617140],  // 8.6
      [0.620919, 0.098934, 0.614257],  // 8.7
      [0.625987, 0.103312, 0.611305],  // 8.8
      [0.631017, 0.107699, 0.608287],  // 8.9
      [0.636008, 0.112092, 0.605205],  // 9.0
      [0.640959, 0.116492, 0.602065],  // 9.1
      [0.645872, 0.120898, 0.598867],  // 9.2
      [0.650746, 0.125309, 0.595617],  // 9.3
      [0.655580, 0.129725, 0.592317],  // 9.4
      [0.660374, 0.134144, 0.588971],  // 9.5
      [0.665129, 0.138566, 0.585582],  // 9.6
      [0.669845, 0.142992, 0.582154],  // 9.7
      [0.674522, 0.147419, 0.578688],  // 9.8
      [0.679160, 0.151848, 0.575189],  // 9.9
      [0.683758, 0.156278, 0.571660],  // 10.0 - Bright yellow
    ];
    
    // Interpolate between colors based on position
    const scaledPos = colormapPosition * (plasmaColors.length - 1);
    const index = Math.floor(scaledPos);
    const t = scaledPos - index;
    
    const color1 = plasmaColors[Math.min(index, plasmaColors.length - 1)];
    const color2 = plasmaColors[Math.min(index + 1, plasmaColors.length - 1)];
    
    // Linear interpolation between colors
    const r = color1[0] + t * (color2[0] - color1[0]);
    const g = color1[1] + t * (color2[1] - color1[1]);
    const b = color1[2] + t * (color2[2] - color1[2]);
    
    return new THREE.Color(r, g, b);
  }
  
  updateVoltageFrame(frameIndex) {
    if (!this.voltageData || !this.currentModel || !this.materialConfig) return;
    
    const clampedFrame = Math.max(0, Math.min(frameIndex, this.voltageAnimation.totalFrames - 1));
    this.voltageAnimation.currentFrame = clampedFrame;
    
    // Use material configuration voltage range if available, otherwise fall back to global range
    const voltageRange = this.materialConfig.voltage_range || this.voltageData.metadata.global_voltage_range;
    const { min: minVoltage, max: maxVoltage } = voltageRange;
    
    // Update materials for each mapped mesh
    this.voltageAnimation.meshMap.forEach((sectionData, mesh) => {
      if (clampedFrame < sectionData.voltage_frames.length) {
        const voltage = sectionData.voltage_frames[clampedFrame];
        this.applyVoltageToMesh(mesh, voltage, minVoltage, maxVoltage);
      }
    });
  }
  
  updateVoltageFrameInterpolated(frameFloat) {
    if (!this.voltageData || !this.currentModel || !this.materialConfig) return;
    
    const clampedFrame = Math.max(0, Math.min(frameFloat, this.voltageAnimation.totalFrames - 1));
    
    // Get integer frame indices for interpolation
    const frameIndex = Math.floor(clampedFrame);
    const nextFrameIndex = Math.min(frameIndex + 1, this.voltageAnimation.totalFrames - 1);
    const frameFraction = clampedFrame - frameIndex;
    
    // Use material configuration voltage range
    const voltageRange = this.materialConfig.voltage_range || this.voltageData.metadata.global_voltage_range;
    const { min: minVoltage, max: maxVoltage } = voltageRange;
    
    // Update materials with interpolated voltage values
    this.voltageAnimation.meshMap.forEach((sectionData, mesh) => {
      if (frameIndex < sectionData.voltage_frames.length) {
        const currentVoltage = sectionData.voltage_frames[frameIndex] || 0;
        const nextVoltage = sectionData.voltage_frames[nextFrameIndex] || currentVoltage;
        
        // Linear interpolation between frames
        const interpolatedVoltage = currentVoltage + (nextVoltage - currentVoltage) * frameFraction;
        
        this.applyVoltageToMesh(mesh, interpolatedVoltage, minVoltage, maxVoltage);
      }
    });
  }
  
  applyVoltageToMesh(mesh, voltage, minVoltage, maxVoltage) {
    const color = this.voltageToColor(voltage, minVoltage, maxVoltage);
    
    // Create or update material with proper PBR properties
    if (!mesh.material.isVoltageCustom) {
      // Create new voltage-optimized material
      mesh.material = new THREE.MeshStandardMaterial({
        color: color,
        emissive: new THREE.Color(0, 0, 0),
        emissiveIntensity: 1.0,
        metalness: 0.1,
        roughness: 0.6,
        transparent: true,
        opacity: 0.95,
        side: THREE.FrontSide,
        flatShading: false
      });
      mesh.material.isVoltageCustom = true;
      
      // Mark mesh to receive shadows
      mesh.receiveShadow = true;
      mesh.castShadow = true;
    }
    
    // Update material properties efficiently
    mesh.material.color.copy(color);
    
    // Calculate normalized voltage for emission scaling
    const normalizedVoltage = Math.max(0, Math.min(1, (voltage - minVoltage) / (maxVoltage - minVoltage)));
    
    // Apply emission with material configuration
    const baseEmission = this.materialConfig.emission_strength || 2.0;
    const emissionIntensity = normalizedVoltage * baseEmission;
    
    // Create realistic membrane glow effect
    const emissionColor = color.clone();
    emissionColor.multiplyScalar(0.4); // Base emission color
    mesh.material.emissive.copy(emissionColor);
    mesh.material.emissiveIntensity = emissionIntensity;
    
    // Adjust transparency based on voltage activity
    mesh.material.opacity = 0.85 + normalizedVoltage * 0.15;
    
    // Adjust roughness for more realistic appearance during action potentials
    mesh.material.roughness = 0.8 - normalizedVoltage * 0.3;
    
    mesh.material.needsUpdate = true;
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
    
    // Update voltage animation with smooth interpolation
    if (this.voltageAnimation.isPlaying && this.voltageData) {
      // Calculate frame rate based on metadata
      const framesPerSecond = this.voltageAnimation.totalFrames / (this.voltageData.metadata.duration_ms / 1000);
      const frameIncrement = delta * framesPerSecond * this.voltageAnimation.speed;
      
      this.voltageAnimation.currentFrame += frameIncrement;
      
      // Loop animation
      if (this.voltageAnimation.currentFrame >= this.voltageAnimation.totalFrames) {
        this.voltageAnimation.currentFrame = 0;
      }
      
      // Update voltage colors with interpolation
      this.updateVoltageFrameInterpolated(this.voltageAnimation.currentFrame);
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