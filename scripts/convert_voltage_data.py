"""
convert_voltage_data.py

Convert voltage data from sim_ommatidia.py format (Format 1) to
BlenderModelViewer expected format (Format 2) for 3D visualization.

Input: voltages.json (array of {time, v1, v2, norm_v1, norm_v2})
Output: voltages_formatted.json (sections array with metadata)
"""

import json
import numpy as np

# Input and output files
input_file = "voltages.json"
output_file = "voltages_formatted.json"

print(f"Reading {input_file}...")
with open(input_file, 'r') as f:
    data = json.load(f)

# Extract data
times = [d['time'] for d in data]
v1_values = [d['v1'] for d in data]
v2_values = [d['v2'] for d in data]

# Calculate metadata
n_frames = len(data)
duration_ms = times[-1]
time_step_ms = times[1] - times[0]

# Calculate voltage ranges
v1_min, v1_max = min(v1_values), max(v1_values)
v2_min, v2_max = min(v2_values), max(v2_values)
global_min = min(v1_min, v2_min)
global_max = max(v1_max, v2_max)

print(f"Frames: {n_frames}")
print(f"Duration: {duration_ms:.2f} ms")
print(f"Time step: {time_step_ms:.3f} ms")
print(f"V1 range: {v1_min:.2f} to {v1_max:.2f} mV")
print(f"V2 range: {v2_min:.2f} to {v2_max:.2f} mV")
print(f"Global range: {global_min:.2f} to {global_max:.2f} mV")

# Create formatted output structure
formatted_data = {
    "metadata": {
        "frames": n_frames,
        "duration_ms": duration_ms,
        "time_step_ms": time_step_ms,
        "global_voltage_range": {
            "min": round(global_min, 2),
            "max": round(global_max, 2)
        }
    },
    "material_config": {
        "emission_strength": 3.0,  # Higher for better visibility
        "colormap_steps": 20,      # Smooth gradient
        "cmap_start": 0.0,
        "cmap_end": 1.0,
        "colormap_name": "plasma",
        "voltage_range": {
            "min": round(global_min, 2),
            "max": round(global_max, 2)
        }
    },
    "timepoints": times,
    "sections": [
        {
            "id": 0,
            "name": "ommatidium_1",
            "type": "eccentric_cell",
            "voltage_frames": v1_values
        },
        {
            "id": 1,
            "name": "ommatidium_2",
            "type": "eccentric_cell",
            "voltage_frames": v2_values
        }
    ]
}

# Write output
print(f"\nWriting {output_file}...")
with open(output_file, 'w') as f:
    json.dump(formatted_data, f, indent=2)

print(f"✓ Conversion complete! Created {output_file}")
print(f"  - 2 sections (ommatidium_1, ommatidium_2)")
print(f"  - {n_frames} frames")
print(f"  - {duration_ms:.2f} ms duration")
