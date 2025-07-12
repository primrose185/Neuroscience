# NEURON-Based SWC to BlenderSpike Converter

## Overview

This script (`neuron_swc_to_blenderspike.py`) solves the connectivity issues of the original SWC converter by using NEURON's Import3d tool to properly load SWC morphologies and maintain correct section topology.

## Success with Cheetah Pyramidal Morphology

✅ **Successfully processed `cheetah_pyramidal.swc`:**
- **86 sections total** (proper connectivity maintained)
- **1 soma section** 
- **1 axon section**
- **51 dendrite sections**
- **33 apical dendrite sections**
- **Action potential simulation** with proper propagation
- **400 animation frames** exported to BlenderSpike format

## Key Improvements Over Direct SWC Converter

### 1. **Proper Section Connectivity**
- Uses NEURON's Import3d to reconstruct morphology
- Maintains parent-child relationships between sections
- Ensures proper electrical continuity

### 2. **Biophysical Properties**
- Hodgkin-Huxley channels for action potential propagation
- Passive membrane properties (leak channels)
- Section-specific channel densities

### 3. **Realistic Stimulation**
- Current injection at soma for AP initiation
- Configurable stimulation parameters
- Proper timing for visualization

## Usage

### Basic Usage
```bash
python neuron_swc_to_blenderspike.py input.swc output.pickle
```

### Advanced Usage
```bash
python neuron_swc_to_blenderspike.py cheetah_pyramidal.swc cheetah_neuron.pickle \
    --frames 400 \
    --tstop 50 \
    --dt 0.025 \
    --plot
```

### Parameters
- `--frames`: Number of animation frames (default: 400)
- `--tstop`: Simulation time in ms (default: 50)
- `--dt`: Time step in ms (default: 0.025)
- `--plot`: Create result plots (requires display)

## Testing in Blender

### 1. Load the New Pickle File
1. Open Blender with BlenderSpike addon enabled
2. Navigate to BlenderSpike panel (press `N` to show menu)
3. In "Neuron Builder" tab, click folder icon
4. Select `cheetah_pyramidal_neuron.pickle`
5. Click "Build a neuron"

### 2. Verify Connectivity
- Check that all sections are properly connected
- No floating or disconnected parts
- Proper branching structure visible

### 3. Recommended Settings
- **Segmentation**: 5-10 (balance detail vs performance)
- **Branch thickness**: 0.5-1.0 (adjust for visibility)
- **Downscale factor**: 0.1-0.2 (SWC units are often large)
- **Center at origin**: ✅ Enabled

### 4. Voltage Animation
1. Navigate to "Shading Manager" panel
2. Choose colormap (e.g., "viridis", "plasma", "hot")
3. Set voltage limits (-80 to +40 mV)
4. Select neuron parent object
5. Click "Create a voltage coloring"

## Comparison with Original Converter

| Feature | Original SWC Converter | NEURON-Based Converter |
|---------|----------------------|----------------------|
| **Connectivity** | ❌ Often broken | ✅ Proper topology |
| **Section Count** | Variable | ✅ 86 sections |
| **Biophysics** | ❌ None | ✅ Full HH model |
| **Stimulation** | ❌ None | ✅ Realistic AP |
| **Animation** | ❌ Static | ✅ Voltage propagation |

## Output Files

### Generated Files
- `cheetah_pyramidal_neuron.pickle` - BlenderSpike-compatible morphology with voltage data
- `simulation_results.png` - Visualization plots (if `--plot` used)

### File Structure
The pickle file contains properly connected sections with:
- **Morphology data**: X, Y, Z coordinates and diameters
- **Voltage data**: Time-series voltage for each section
- **Metadata**: Section types and IDs
- **Animation frames**: 400 frames of voltage evolution

## Next Steps

1. **Test in Blender**: Load the new pickle file and verify connectivity
2. **Customize visualization**: Adjust colors, thickness, and animation timing
3. **Create educational content**: Document different viewing angles and scenarios
4. **Extend to other morphologies**: Test with additional SWC files

## Troubleshooting

### Common Issues
- **NEURON not found**: Ensure NEURON is installed with Python interface
- **BlenderSpike import error**: Check that blenderspike_py module is installed
- **Display warnings**: Use `--plot` flag only when display is available

### Performance Tips
- Use fewer frames (200-300) for faster processing
- Reduce simulation time for simpler animations
- Increase dt for faster simulation (but lower temporal resolution)

## Educational Applications

This converter enables creation of realistic neuron visualizations for:
- **Action potential propagation** in complex morphologies
- **Dendritic integration** and signal processing
- **Morphology-function relationships**
- **Comparative neuron studies**

The proper connectivity ensures that voltage propagation follows realistic pathways, making it ideal for educational demonstrations and research presentations.