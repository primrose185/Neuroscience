#!/usr/bin/env python3
"""
NEURON-based SWC to BlenderSpike Converter

This script uses NEURON's Import3d tool to properly load SWC morphology files
and maintain correct section connectivity, then exports to BlenderSpike format.

Usage:
    python neuron_swc_to_blenderspike.py input.swc output.pickle

Requirements:
    - NEURON with Python interface
    - BlenderSpike Python module (blenderspike_py)
    - numpy, matplotlib

Author: Generated with Claude Code
"""

import sys
import os
import argparse
import json
import numpy as np
from neuron import h
from neuron.units import um, mV, ms
import matplotlib.pyplot as plt

# Add BlenderSpike to path if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'BlenderSpike'))
import blenderspike_py

# Load NEURON's Import3d tools
h.load_file("import3d.hoc")

class SWCNeuronCell:
    """A NEURON cell class that loads morphology from SWC files using Import3d."""
    
    def __init__(self, swc_file, name="SWC_Cell"):
        """Initialize the cell by loading SWC morphology."""
        self.name = name
        self.swc_file = swc_file
        self.all_sections = []
        
        # Load the morphology
        self._load_morphology()
        
        # Set up basic biophysics
        self._setup_biophysics()
        
        # Set up stimulation
        self._setup_stimulation()
        
        print(f"Created {self.name} with {len(self.all_sections)} sections")
        
    def _load_morphology(self):
        """Load SWC morphology using NEURON's Import3d."""
        print(f"Loading morphology from {self.swc_file}")
        
        # Create Import3d reader for SWC files
        swc_reader = h.Import3d_SWC_read()
        swc_reader.input(self.swc_file)
        
        # Create Import3d GUI (this instantiates the morphology)
        import3d_gui = h.Import3d_GUI(swc_reader, 0)
        import3d_gui.instantiate(self)
        
        # Get all sections that were created
        self.all_sections = list(h.allsec())
        
        # Categorize sections by type
        self.soma_sections = []
        self.axon_sections = []
        self.dendrite_sections = []
        self.apical_sections = []
        
        for sec in self.all_sections:
            sec_name = sec.name().lower()
            if 'soma' in sec_name:
                self.soma_sections.append(sec)
            elif 'axon' in sec_name:
                self.axon_sections.append(sec)
            elif 'apic' in sec_name:
                self.apical_sections.append(sec)
            else:
                self.dendrite_sections.append(sec)
        
        print(f"  - Soma sections: {len(self.soma_sections)}")
        print(f"  - Axon sections: {len(self.axon_sections)}")
        print(f"  - Dendrite sections: {len(self.dendrite_sections)}")
        print(f"  - Apical sections: {len(self.apical_sections)}")
        
    def _setup_biophysics(self):
        """Set up basic biophysical properties."""
        print("Setting up biophysics...")
        
        # Basic biophysical parameters
        Ra = 100  # Ohm-cm
        cm = 1.0  # uF/cm2
        
        for sec in self.all_sections:
            sec.Ra = Ra
            sec.cm = cm
            
            # Insert passive properties
            sec.insert('pas')
            sec.g_pas = 3e-5  # S/cm2
            sec.e_pas = -70   # mV
            
            # Insert HH channels for action potential propagation
            sec.insert('hh')
            
            # Adjust channel densities based on section type
            sec_name = sec.name().lower()
            if 'soma' in sec_name:
                sec.gnabar_hh = 0.12  # S/cm2
                sec.gkbar_hh = 0.036  # S/cm2
            elif 'axon' in sec_name:
                sec.gnabar_hh = 0.12  # S/cm2
                sec.gkbar_hh = 0.036  # S/cm2
            else:  # dendrites
                sec.gnabar_hh = 0.12  # S/cm2
                sec.gkbar_hh = 0.036  # S/cm2
        
        print("  - Applied passive properties")
        print("  - Applied HH channels")
        
    def _setup_stimulation(self):
        """Set up current injection for action potential initiation."""
        print("Setting up stimulation...")
        
        # Find soma for stimulation
        if self.soma_sections:
            stim_location = self.soma_sections[0](0.5)
            print(f"  - Stimulating at {self.soma_sections[0].name()}")
        else:
            # If no soma, use first section
            stim_location = self.all_sections[0](0.5)
            print(f"  - Stimulating at {self.all_sections[0].name()}")
        
        # Create current clamp
        self.stim = h.IClamp(stim_location)
        self.stim.delay = 5 * ms    # Start stimulation at 5ms
        self.stim.dur = 2 * ms      # Duration of 2ms
        self.stim.amp = 0.5         # Current amplitude in nA
        
        print(f"  - IClamp: delay={self.stim.delay}ms, dur={self.stim.dur}ms, amp={self.stim.amp}nA")

def run_simulation(cell, tstop=50, dt=0.025):
    """Run NEURON simulation and record voltage."""
    print(f"\\nRunning simulation for {tstop}ms with dt={dt}ms...")
    
    # Load standard run procedures
    h.load_file("stdrun.hoc")
    
    # Set up simulation parameters
    h.dt = dt
    h.tstop = tstop
    h.v_init = -70
    
    # Initialize CellRecorder to capture voltage from all sections
    recorder = blenderspike_py.CellRecorder(cell.all_sections, dt=dt)
    
    # Record time
    t_vec = h.Vector()
    t_vec.record(h._ref_t)
    
    # Run simulation
    h.finitialize(-70 * mV)
    h.continuerun(tstop * ms)
    
    print(f"  - Simulation completed")
    print(f"  - Recorded {len(recorder.monitors)} section monitors")
    
    return recorder, t_vec

def plot_results(recorder, t_vec, output_dir=None):
    """Create plots of the simulation results."""
    print("\\nCreating result plots...")
    
    # Convert time vector to numpy array
    time = np.array(t_vec)
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Action Potential Propagation in SWC Morphology', fontsize=16)
    
    # Plot 1: Soma voltage (if available)
    ax1 = axes[0, 0]
    if len(recorder.monitors) > 0:
        soma_voltage = np.array(recorder.monitors[0].Vectors[0])
        ax1.plot(time, soma_voltage, 'b-', linewidth=2)
        ax1.set_title('Soma Voltage')
        ax1.set_xlabel('Time (ms)')
        ax1.set_ylabel('Voltage (mV)')
        ax1.grid(True)
    
    # Plot 2: Multiple section voltages
    ax2 = axes[0, 1]
    n_sections_to_plot = min(5, len(recorder.monitors))
    colors = plt.cm.viridis(np.linspace(0, 1, n_sections_to_plot))
    
    for i in range(n_sections_to_plot):
        voltage = np.array(recorder.monitors[i].Vectors[0])
        ax2.plot(time, voltage, color=colors[i], linewidth=1.5, 
                label=f'Section {i}')
    
    ax2.set_title('Multiple Section Voltages')
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Voltage (mV)')
    ax2.legend()
    ax2.grid(True)
    
    # Plot 3: Voltage distribution at peak
    ax3 = axes[1, 0]
    if len(recorder.monitors) > 0:
        # Find time of peak voltage
        soma_voltage = np.array(recorder.monitors[0].Vectors[0])
        peak_idx = np.argmax(soma_voltage)
        peak_time = time[peak_idx]
        
        # Get voltage at peak time from all sections
        peak_voltages = []
        for monitor in recorder.monitors:
            if len(monitor.Vectors) > 0:
                voltage = np.array(monitor.Vectors[0])
                peak_voltages.append(voltage[peak_idx])
        
        ax3.bar(range(len(peak_voltages)), peak_voltages, color='orange', alpha=0.7)
        ax3.set_title(f'Voltage Distribution at Peak Time ({peak_time:.1f}ms)')
        ax3.set_xlabel('Section Index')
        ax3.set_ylabel('Voltage (mV)')
        ax3.grid(True)
    
    # Plot 4: Section count summary
    ax4 = axes[1, 1]
    section_counts = {
        'Total': len(recorder.monitors),
        'With Recordings': len([m for m in recorder.monitors if len(m.Vectors) > 0])
    }
    
    ax4.bar(section_counts.keys(), section_counts.values(), color=['blue', 'green'])
    ax4.set_title('Recording Summary')
    ax4.set_ylabel('Number of Sections')
    ax4.grid(True)
    
    plt.tight_layout()
    
    if output_dir:
        plot_file = os.path.join(output_dir, 'simulation_results.png')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"  - Saved plot to {plot_file}")
    
    plt.show()
    
    return fig

def export_voltage_data_json(recorder, t_vec, cell, output_file, frames=400, material_config=None):
    """Export voltage data to JSON format for Three.js animation with material configuration."""
    print(f"\nExporting voltage data to JSON...")
    
    # Convert time vector to numpy array
    time = np.array(t_vec)
    
    # Default material configuration if not provided
    if material_config is None:
        material_config = {
            'emission_strength': 2.0,
            'colormap_steps': 10,
            'cmap_start': 0.0,
            'cmap_end': 1.0,
            'colormap_name': 'plasma',
            'min_voltage': -70,
            'max_voltage': 20
        }
    
    # Prepare data structure
    animation_data = {
        "metadata": {
            "format_version": "1.1",
            "description": "NEURON voltage animation data for Three.js with material configuration",
            "frames": frames,
            "duration_ms": float(time[-1]) if len(time) > 0 else 50.0,
            "time_step_ms": float(time[1] - time[0]) if len(time) > 1 else 0.025
        },
        "material_config": {
            "emission_strength": material_config['emission_strength'],
            "colormap_steps": material_config['colormap_steps'],
            "cmap_start": material_config['cmap_start'],
            "cmap_end": material_config['cmap_end'],
            "colormap_name": material_config['colormap_name'],
            "voltage_range": {
                "min": material_config['min_voltage'],
                "max": material_config['max_voltage']
            }
        },
        "timepoints": time.tolist(),
        "sections": []
    }
    
    # Process each section's voltage data
    for i, monitor in enumerate(recorder.monitors):
        if len(monitor.Vectors) > 0:
            # Get voltage data
            voltage = np.array(monitor.Vectors[0])
            
            # Get section information
            section = cell.all_sections[i] if i < len(cell.all_sections) else None
            section_name = section.name() if section else f"section_{i}"
            
            # Determine section type
            section_type = "dendrite"  # default
            if section:
                name_lower = section_name.lower()
                if 'soma' in name_lower:
                    section_type = "soma"
                elif 'axon' in name_lower:
                    section_type = "axon"
                elif 'apic' in name_lower:
                    section_type = "apical"
            
            # Resample voltage data to match requested frame count
            if len(voltage) > frames:
                # Downsample
                indices = np.linspace(0, len(voltage)-1, frames, dtype=int)
                voltage_frames = voltage[indices]
            elif len(voltage) < frames:
                # Upsample using interpolation
                original_indices = np.arange(len(voltage))
                new_indices = np.linspace(0, len(voltage)-1, frames)
                voltage_frames = np.interp(new_indices, original_indices, voltage)
            else:
                voltage_frames = voltage
            
            # Create section data
            section_data = {
                "id": i,
                "name": section_name,
                "type": section_type,
                "voltage_frames": voltage_frames.tolist(),
                "voltage_range": {
                    "min": float(np.min(voltage)),
                    "max": float(np.max(voltage))
                }
            }
            
            animation_data["sections"].append(section_data)
    
    # Calculate global voltage range for consistent coloring
    all_voltages = []
    for section in animation_data["sections"]:
        all_voltages.extend(section["voltage_frames"])
    
    if all_voltages:
        animation_data["metadata"]["global_voltage_range"] = {
            "min": float(np.min(all_voltages)),
            "max": float(np.max(all_voltages))
        }
    
    # Save to JSON file
    json_file = output_file.replace('.pickle', '.json')
    with open(json_file, 'w') as f:
        json.dump(animation_data, f, indent=2)
    
    print(f"  - Saved voltage data to {json_file}")
    print(f"  - {len(animation_data['sections'])} sections with voltage data")
    print(f"  - {frames} frames per section")
    print(f"  - Global voltage range: {animation_data['metadata']['global_voltage_range']['min']:.1f} to {animation_data['metadata']['global_voltage_range']['max']:.1f} mV")
    print(f"  - Material config: {material_config['colormap_name']} colormap, emission_strength={material_config['emission_strength']}")
    print(f"  - Colormap range: {material_config['cmap_start']:.1f} to {material_config['cmap_end']:.1f}, steps={material_config['colormap_steps']}")
    
    return json_file

def main():
    """Main function to run the SWC to BlenderSpike conversion."""
    parser = argparse.ArgumentParser(description='Convert SWC morphology to BlenderSpike format using NEURON')
    parser.add_argument('swc_file', help='Input SWC file')
    parser.add_argument('output_file', help='Output pickle file')
    parser.add_argument('--frames', type=int, default=400, help='Number of animation frames')
    parser.add_argument('--tstop', type=float, default=50, help='Simulation time (ms)')
    parser.add_argument('--dt', type=float, default=0.025, help='Time step (ms)')
    parser.add_argument('--plot', action='store_true', help='Create result plots')
    
    # Material configuration arguments
    parser.add_argument('--emission-strength', type=float, default=2.0, help='Material emission strength (default: 2.0)')
    parser.add_argument('--colormap-steps', type=int, default=10, help='Number of colormap steps (default: 10)')
    parser.add_argument('--cmap-start', type=float, default=0.0, help='Colormap start position 0-1 (default: 0.0)')
    parser.add_argument('--cmap-end', type=float, default=1.0, help='Colormap end position 0-1 (default: 1.0)')
    parser.add_argument('--colormap-name', type=str, default='plasma', help='Colormap name (default: plasma)')
    parser.add_argument('--min-voltage', type=float, default=-70, help='Minimum voltage for material range (default: -70)')
    parser.add_argument('--max-voltage', type=float, default=20, help='Maximum voltage for material range (default: 20)')
    
    args = parser.parse_args()
    
    # Check if SWC file exists
    if not os.path.exists(args.swc_file):
        print(f"Error: SWC file '{args.swc_file}' not found")
        return 1
    
    try:
        # Create cell from SWC file
        cell = SWCNeuronCell(args.swc_file)
        
        # Run simulation
        recorder, t_vec = run_simulation(cell, tstop=args.tstop, dt=args.dt)
        
        # Create plots if requested
        if args.plot:
            plot_results(recorder, t_vec, output_dir=os.path.dirname(args.output_file))
        
        # Export to BlenderSpike format
        print(f"\\nExporting to BlenderSpike format...")
        recorder.save_pickle(args.output_file, FRAME_NUM=args.frames)
        print(f"  - Saved to {args.output_file}")
        print(f"  - {args.frames} animation frames")
        
        # Export voltage data to JSON for Three.js with material configuration
        material_config = {
            'emission_strength': args.emission_strength,
            'colormap_steps': args.colormap_steps,
            'cmap_start': args.cmap_start,
            'cmap_end': args.cmap_end,
            'colormap_name': args.colormap_name,
            'min_voltage': args.min_voltage,
            'max_voltage': args.max_voltage
        }
        json_file = export_voltage_data_json(recorder, t_vec, cell, args.output_file, frames=args.frames, material_config=material_config)
        print(f"  - Also saved JSON animation data for Three.js with material configuration")
        
        print("\\nConversion completed successfully!")
        print("\\nNext steps:")
        print("1. Open Blender with BlenderSpike addon")
        print("2. Load the pickle file using BlenderSpike")
        print("3. Adjust morphology settings (scaling, thickness)")
        print("4. Create voltage coloring and animation")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())