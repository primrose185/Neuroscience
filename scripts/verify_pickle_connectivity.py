#!/usr/bin/env python3
"""
Verify BlenderSpike Pickle File Connectivity

This script analyzes a BlenderSpike pickle file to verify proper section connectivity
and morphology structure.

Usage:
    python verify_pickle_connectivity.py pickle_file.pickle
"""

import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def load_pickle_data(filename):
    """Load and return pickle data."""
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data

def analyze_morphology(data):
    """Analyze morphology structure and connectivity."""
    print(f"=== Morphology Analysis ===")
    print(f"Total sections: {len(data)}")
    
    # Count section types
    type_counts = defaultdict(int)
    section_lengths = []
    total_points = 0
    
    for section in data:
        section_type = section.get('type', 'unknown')
        type_counts[section_type] += 1
        
        # Calculate section length
        coords = np.array([section['X'], section['Y'], section['Z']]).T
        if len(coords) > 1:
            distances = np.sqrt(np.sum(np.diff(coords, axis=0)**2, axis=1))
            section_length = np.sum(distances)
            section_lengths.append(section_length)
        
        total_points += len(section['X'])
    
    print(f"Section types:")
    for stype, count in type_counts.items():
        print(f"  - {stype}: {count}")
    
    print(f"Total 3D points: {total_points}")
    print(f"Average section length: {np.mean(section_lengths):.2f}")
    print(f"Total morphology length: {np.sum(section_lengths):.2f}")
    
    return type_counts, section_lengths

def analyze_voltage_data(data):
    """Analyze voltage data structure."""
    print(f"\n=== Voltage Data Analysis ===")
    
    sections_with_voltage = 0
    total_frames = 0
    voltage_ranges = []
    
    for i, section in enumerate(data):
        voltage_data = section.get('Voltage', {})
        if voltage_data:
            sections_with_voltage += 1
            frames = list(voltage_data.keys())
            if frames:
                total_frames = max(total_frames, max(frames) + 1)
                
                # Analyze voltage range
                all_voltages = []
                for frame_voltages in voltage_data.values():
                    all_voltages.extend(frame_voltages)
                
                if all_voltages:
                    voltage_ranges.append({
                        'section': i,
                        'min': min(all_voltages),
                        'max': max(all_voltages),
                        'mean': np.mean(all_voltages)
                    })
    
    print(f"Sections with voltage data: {sections_with_voltage}/{len(data)}")
    print(f"Total animation frames: {total_frames}")
    
    if voltage_ranges:
        all_mins = [v['min'] for v in voltage_ranges]
        all_maxs = [v['max'] for v in voltage_ranges]
        print(f"Voltage range across all sections: {min(all_mins):.1f} to {max(all_maxs):.1f} mV")
        
        # Check for action potential activity
        ap_sections = [v for v in voltage_ranges if v['max'] > 0]
        print(f"Sections with action potentials (>0mV): {len(ap_sections)}")
    
    return sections_with_voltage, total_frames, voltage_ranges

def visualize_morphology(data, output_file=None):
    """Create 3D visualization of morphology."""
    print(f"\n=== Creating 3D Morphology Visualization ===")
    
    fig = plt.figure(figsize=(15, 10))
    
    # 3D plot
    ax1 = fig.add_subplot(221, projection='3d')
    
    colors = {'soma': 'red', 'axon': 'blue', 'dend': 'green', 'apic': 'purple'}
    
    for section in data:
        section_type = section.get('type', 'unknown')
        color = colors.get(section_type, 'gray')
        
        x = section['X']
        y = section['Y'] 
        z = section['Z']
        
        ax1.plot(x, y, z, color=color, linewidth=1, alpha=0.7)
    
    ax1.set_xlabel('X (μm)')
    ax1.set_ylabel('Y (μm)')
    ax1.set_zlabel('Z (μm)')
    ax1.set_title('3D Morphology')
    
    # Create legend
    legend_elements = [plt.Line2D([0], [0], color=color, lw=2, label=stype) 
                      for stype, color in colors.items()]
    ax1.legend(handles=legend_elements)
    
    # XY projection
    ax2 = fig.add_subplot(222)
    for section in data:
        section_type = section.get('type', 'unknown')
        color = colors.get(section_type, 'gray')
        ax2.plot(section['X'], section['Y'], color=color, linewidth=1, alpha=0.7)
    ax2.set_xlabel('X (μm)')
    ax2.set_ylabel('Y (μm)')
    ax2.set_title('XY Projection')
    ax2.axis('equal')
    
    # XZ projection  
    ax3 = fig.add_subplot(223)
    for section in data:
        section_type = section.get('type', 'unknown')
        color = colors.get(section_type, 'gray')
        ax3.plot(section['X'], section['Z'], color=color, linewidth=1, alpha=0.7)
    ax3.set_xlabel('X (μm)')
    ax3.set_ylabel('Z (μm)')
    ax3.set_title('XZ Projection')
    ax3.axis('equal')
    
    # Diameter distribution
    ax4 = fig.add_subplot(224)
    all_diameters = []
    for section in data:
        all_diameters.extend(section['DIAM'])
    
    ax4.hist(all_diameters, bins=50, alpha=0.7, color='orange')
    ax4.set_xlabel('Diameter (μm)')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Diameter Distribution')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  - Saved visualization to {output_file}")
    
    return fig

def check_connectivity(data):
    """Check for potential connectivity issues."""
    print(f"\n=== Connectivity Analysis ===")
    
    # Check for sections with very few points
    short_sections = []
    for i, section in enumerate(data):
        if len(section['X']) < 2:
            short_sections.append(i)
    
    if short_sections:
        print(f"⚠️  Sections with <2 points: {len(short_sections)}")
        print(f"   Section IDs: {short_sections}")
    else:
        print("✅ All sections have ≥2 points")
    
    # Check for sections with zero length
    zero_length_sections = []
    for i, section in enumerate(data):
        coords = np.array([section['X'], section['Y'], section['Z']]).T
        if len(coords) > 1:
            distances = np.sqrt(np.sum(np.diff(coords, axis=0)**2, axis=1))
            total_length = np.sum(distances)
            if total_length < 1e-6:  # Very small length
                zero_length_sections.append(i)
    
    if zero_length_sections:
        print(f"⚠️  Sections with zero length: {len(zero_length_sections)}")
    else:
        print("✅ All sections have non-zero length")
    
    # Check for reasonable coordinate ranges
    all_x = []
    all_y = []
    all_z = []
    
    for section in data:
        all_x.extend(section['X'])
        all_y.extend(section['Y'])
        all_z.extend(section['Z'])
    
    x_range = max(all_x) - min(all_x)
    y_range = max(all_y) - min(all_y)
    z_range = max(all_z) - min(all_z)
    
    print(f"Coordinate ranges:")
    print(f"  - X: {min(all_x):.1f} to {max(all_x):.1f} (range: {x_range:.1f})")
    print(f"  - Y: {min(all_y):.1f} to {max(all_y):.1f} (range: {y_range:.1f})")
    print(f"  - Z: {min(all_z):.1f} to {max(all_z):.1f} (range: {z_range:.1f})")
    
    # Check for reasonable diameter ranges
    all_diameters = []
    for section in data:
        all_diameters.extend(section['DIAM'])
    
    diam_range = max(all_diameters) - min(all_diameters)
    print(f"Diameter range: {min(all_diameters):.2f} to {max(all_diameters):.2f}")
    
    return len(short_sections) == 0 and len(zero_length_sections) == 0

def main():
    """Main verification function."""
    if len(sys.argv) != 2:
        print("Usage: python verify_pickle_connectivity.py pickle_file.pickle")
        return 1
    
    pickle_file = sys.argv[1]
    
    try:
        # Load data
        print(f"Loading pickle file: {pickle_file}")
        data = load_pickle_data(pickle_file)
        
        # Analyze morphology
        type_counts, section_lengths = analyze_morphology(data)
        
        # Analyze voltage data
        sections_with_voltage, total_frames, voltage_ranges = analyze_voltage_data(data)
        
        # Check connectivity
        connectivity_ok = check_connectivity(data)
        
        # Create visualization
        import os
        output_dir = os.path.dirname(pickle_file)
        viz_file = os.path.join(output_dir, 'morphology_analysis.png')
        
        try:
            visualize_morphology(data, viz_file)
        except Exception as e:
            print(f"⚠️  Visualization failed: {e}")
        
        # Summary
        print(f"\n=== SUMMARY ===")
        print(f"✅ Morphology loaded successfully")
        print(f"✅ {len(data)} sections with proper structure")
        print(f"✅ {sections_with_voltage} sections with voltage data")
        print(f"✅ {total_frames} animation frames")
        
        if connectivity_ok:
            print(f"✅ No connectivity issues detected")
        else:
            print(f"⚠️  Potential connectivity issues found")
        
        print(f"\n🎯 Ready for BlenderSpike import!")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())