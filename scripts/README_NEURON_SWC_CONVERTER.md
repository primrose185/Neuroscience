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
- `cheetah_pyramidal_neuron.json` - **NEW:** Three.js-compatible voltage animation data
- `simulation_results.png` - Visualization plots (if `--plot` used)

### File Structure

#### Pickle File (BlenderSpike)
The pickle file contains properly connected sections with:
- **Morphology data**: X, Y, Z coordinates and diameters
- **Voltage data**: Time-series voltage for each section
- **Metadata**: Section types and IDs
- **Animation frames**: 400 frames of voltage evolution

#### JSON File (Three.js)
The JSON file contains voltage animation data for web visualization:
- **Metadata**: Frame count, duration, time step, global voltage range
- **Timepoints**: Array of simulation time values
- **Sections**: Per-section voltage data with:
  - Section ID, name, and type (soma/axon/dendrite/apical)
  - Voltage frames array (400 values per section)
  - Individual voltage range for each section

## Visualization Platforms

### Blender (Traditional Workflow)
1. **Load in Blender**: Load the pickle file and verify connectivity
2. **Customize visualization**: Adjust colors, thickness, and animation timing
3. **Create renders**: Export high-quality animations and images

### Web Browser (New Three.js Integration)
1. **Automatic loading**: JSON file automatically loaded alongside GLB model
2. **Real-time animation**: Voltage propagation displayed in real-time
3. **Interactive viewing**: Full 3D navigation and camera controls
4. **Educational demos**: Perfect for web-based neuroscience education

## Next Steps

1. **Test both platforms**: Verify output in both Blender and web browser
2. **Create educational content**: Document different viewing angles and scenarios
3. **Extend to other morphologies**: Test with additional SWC files
4. **Customize activity patterns**: Modify stimulation protocols for different demonstrations

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
- **Web-based interactive demonstrations** (via Three.js JSON export)

The proper connectivity ensures that voltage propagation follows realistic pathways, making it ideal for educational demonstrations and research presentations. The dual-format export (pickle + JSON) enables both traditional Blender workflows and modern web-based visualizations.

## Technical Details

### JSON Format Structure
```json
{
  "metadata": {
    "format_version": "1.0",
    "frames": 400,
    "duration_ms": 50.0,
    "time_step_ms": 0.025,
    "global_voltage_range": {"min": -70.0, "max": 40.0}
  },
  "timepoints": [0.0, 0.025, 0.05, ...],
  "sections": [
    {
      "id": 0,
      "name": "soma[0]", 
      "type": "soma",
      "voltage_frames": [-70.0, -69.8, -69.5, ...],
      "voltage_range": {"min": -70.0, "max": 40.0}
    }
  ]
}
```

### Customizing Activity Patterns
To create different types of neural activity, modify the stimulation in `neuron_swc_to_blenderspike.py`:

```python
# Example: Multiple stimulation sites
stim1 = h.IClamp(soma(0.5))
stim1.delay, stim1.dur, stim1.amp = 5, 2, 0.5

stim2 = h.IClamp(dendrite[10](0.5)) 
stim2.delay, stim2.dur, stim2.amp = 15, 1, 0.3

# Example: Synaptic input
syn = h.ExpSyn(dendrite[5](0.7))
syn.tau = 2.0
netcon = h.NetCon(None, syn)
netcon.weight[0] = 0.01
```