"""
convert_voltage_single.py

Convert single ommatidium voltage data from sim_single_ommatidium.py format
to BlenderModelViewer format.

Model structure:
- Single ommatidium: 6 mesh segments (all receive same voltage data)
- Total: 6 sections in output

Input: voltages_single.json (array of {time, v, norm_v})
Output: voltages_formatted_single.json (6 sections array with metadata)
"""

import json
import numpy as np

# Configuration
SINGLE_OMMATIDIUM_SEGMENTS = 6  # Number of mesh segments in single ommatidium

# Input and output files
input_file = "voltages_single.json"
output_file = "voltages_formatted_single.json"

print(f"Reading {input_file}...")
with open(input_file, 'r') as f:
    data = json.load(f)

# Extract data
times = [d['time'] for d in data]
v_values = [d['v'] for d in data]

# Calculate metadata
n_frames = len(data)
duration_ms = times[-1]
time_step_ms = times[1] - times[0]

# Calculate voltage range
v_min, v_max = min(v_values), max(v_values)

print(f"\nData Summary:")
print(f"  Frames: {n_frames}")
print(f"  Duration: {duration_ms:.2f} ms")
print(f"  Time step: {time_step_ms:.3f} ms")
print(f"  Voltage range: {v_min:.2f} to {v_max:.2f} mV")

print(f"\nCreating sections:")
print(f"  Single ommatidium: {SINGLE_OMMATIDIUM_SEGMENTS} segments (using v data)")
print(f"  Total sections: {SINGLE_OMMATIDIUM_SEGMENTS}")

# Create sections array (all segments use same voltage data)
sections = []
for i in range(SINGLE_OMMATIDIUM_SEGMENTS):
    sections.append({
        "id": i,
        "name": f"ommatidium_segment_{i}",
        "type": "eccentric_cell",
        "voltage_frames": v_values
    })
    print(f"  Section {i}: ommatidium_segment_{i} → v data")

# Create formatted output structure
formatted_data = {
    "metadata": {
        "frames": n_frames,
        "duration_ms": duration_ms,
        "time_step_ms": time_step_ms,
        "global_voltage_range": {
            "min": round(v_min, 2),
            "max": round(v_max, 2)
        }
    },
    "material_config": {
        "emission_strength": 3.0,  # Higher for better visibility
        "colormap_steps": 20,      # Smooth gradient
        "cmap_start": 0.0,
        "cmap_end": 1.0,
        "colormap_name": "plasma",
        "voltage_range": {
            "min": round(v_min, 2),
            "max": round(v_max, 2)
        }
    },
    "timepoints": times,
    "sections": sections
}

# Write output
print(f"\nWriting {output_file}...")
with open(output_file, 'w') as f:
    json.dump(formatted_data, f, indent=2)

print(f"✓ Conversion complete! Created {output_file}")
print(f"\nOutput summary:")
print(f"  - {len(sections)} sections total")
print(f"  - {SINGLE_OMMATIDIUM_SEGMENTS} sections with v data (single ommatidium)")
print(f"  - {n_frames} frames per section")
print(f"  - {duration_ms:.2f} ms duration")
