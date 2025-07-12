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

def main():
    """Main function to run the SWC to BlenderSpike conversion."""
    parser = argparse.ArgumentParser(description='Convert SWC morphology to BlenderSpike format using NEURON')
    parser.add_argument('swc_file', help='Input SWC file')
    parser.add_argument('output_file', help='Output pickle file')
    parser.add_argument('--frames', type=int, default=400, help='Number of animation frames')
    parser.add_argument('--tstop', type=float, default=50, help='Simulation time (ms)')
    parser.add_argument('--dt', type=float, default=0.025, help='Time step (ms)')
    parser.add_argument('--plot', action='store_true', help='Create result plots')
    
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