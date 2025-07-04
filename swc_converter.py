from neuron import h
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from collections import defaultdict
import argparse

# Load standard run library
h.load_file("stdrun.hoc")

# Try to import BlenderSpike
try:
    from blenderspike_py import CellRecorder
    BLENDERSPIKE_AVAILABLE = True
    print("BlenderSpike module found - 3D export will be available!")
except ImportError:
    BLENDERSPIKE_AVAILABLE = False
    print("BlenderSpike module not found - running simulation only")

class SWCParser:
    """Parse SWC files and extract morphological data"""
    
    # SWC type constants
    SWC_TYPES = {
        1: 'soma',
        2: 'axon', 
        3: 'basal_dendrite',
        4: 'apical_dendrite',
        5: 'custom',
        6: 'unspecified',
        7: 'glia'
    }
    
    def __init__(self, swc_file):
        self.swc_file = swc_file
        self.nodes = {}
        self.children = defaultdict(list)
        self.sections_data = defaultdict(list)
        
    def parse(self):
        """Parse the SWC file and organize data"""
        print(f"Parsing SWC file: {self.swc_file}")
        
        # Read SWC file
        with open(self.swc_file, 'r') as f:
            lines = f.readlines()
        
        # Parse each line
        for line in lines:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
                
            parts = line.split()
            if len(parts) != 7:
                continue
                
            node_id = int(parts[0])
            node_type = int(parts[1])
            x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
            radius = float(parts[5])
            parent_id = int(parts[6]) if int(parts[6]) != -1 else None
            
            self.nodes[node_id] = {
                'type': node_type,
                'x': x, 'y': y, 'z': z,
                'radius': radius,
                'parent': parent_id
            }
            
            if parent_id is not None:
                self.children[parent_id].append(node_id)
        
        print(f"Parsed {len(self.nodes)} nodes")
        self._organize_sections()
        
    def _organize_sections(self):
        """Organize nodes into sections based on branching"""
        visited = set()
        section_counter = defaultdict(int)
        
        def trace_section(start_id, section_type):
            """Trace a section from start_id until branching or end"""
            current_id = start_id
            section_nodes = []
            
            while current_id and current_id not in visited:
                visited.add(current_id)
                section_nodes.append(current_id)
                
                # Check if this node has children
                node_children = self.children.get(current_id, [])
                
                if len(node_children) == 0:
                    # End of section
                    break
                elif len(node_children) == 1:
                    # Continue along section
                    current_id = node_children[0]
                else:
                    # Branching point - end this section and start new ones
                    for child_id in node_children:
                        if child_id not in visited:
                            child_type = self.nodes[child_id]['type']
                            trace_section(child_id, child_type)
                    break
            
            if section_nodes:
                section_counter[section_type] += 1
                section_name = f"{self.SWC_TYPES.get(section_type, 'unknown')}_{section_counter[section_type]}"
                self.sections_data[section_name] = section_nodes
        
        # Find root nodes (nodes with no parent or parent = -1)
        root_nodes = [node_id for node_id, data in self.nodes.items() 
                     if data['parent'] is None]
        
        # Start tracing from root nodes
        for root_id in root_nodes:
            root_type = self.nodes[root_id]['type']
            trace_section(root_id, root_type)
        
        print(f"Organized into {len(self.sections_data)} sections")
        for section_name, nodes in self.sections_data.items():
            print(f"  {section_name}: {len(nodes)} nodes")

class SWCNeuron:
    """Create a NEURON model from SWC data"""
    
    def __init__(self, swc_parser):
        self.swc_parser = swc_parser
        self.sections = {}
        self.all_sections = []
        self.recordings = {}
        
        self.create_sections()
        self.build_topology()
        self.define_geometry()
        self.define_biophysics()
        self.setup_recording()
        
    def create_sections(self):
        """Create NEURON sections from SWC data"""
        print("Creating NEURON sections...")
        
        for section_name, node_ids in self.swc_parser.sections_data.items():
            if not node_ids:
                continue
                
            # Create section
            section = h.Section(name=section_name)
            self.sections[section_name] = section
            self.all_sections.append(section)
            
            # Set number of segments based on section length
            section.nseg = max(1, len(node_ids) // 5)  # Reasonable segmentation
            
        print(f"Created {len(self.sections)} sections")
    
    def build_topology(self):
        """Build the topology connections between sections"""
        print("Building topology...")
        
        # Find connections between sections
        for section_name, node_ids in self.swc_parser.sections_data.items():
            if not node_ids:
                continue
                
            section = self.sections[section_name]
            first_node_id = node_ids[0]
            first_node = self.swc_parser.nodes[first_node_id]
            parent_id = first_node['parent']
            
            if parent_id is not None:
                # Find which section contains the parent
                parent_section = self._find_section_containing_node(parent_id)
                if parent_section:
                    # Connect this section to parent section
                    section.connect(parent_section(1))  # Connect to end of parent
    
    def _find_section_containing_node(self, node_id):
        """Find which section contains a given node"""
        for section_name, node_ids in self.swc_parser.sections_data.items():
            if node_id in node_ids:
                return self.sections[section_name]
        return None
    
    def define_geometry(self):
        """Define 3D geometry from SWC coordinates"""
        print("Defining geometry...")
        
        for section_name, node_ids in self.swc_parser.sections_data.items():
            if not node_ids:
                continue
                
            section = self.sections[section_name]
            
            # Calculate section length and diameter
            total_length = 0
            diameters = []
            
            for i, node_id in enumerate(node_ids):
                node = self.swc_parser.nodes[node_id]
                diameters.append(node['radius'] * 2)  # SWC radius -> diameter
                
                if i > 0:
                    prev_node = self.swc_parser.nodes[node_ids[i-1]]
                    dx = node['x'] - prev_node['x']
                    dy = node['y'] - prev_node['y']
                    dz = node['z'] - prev_node['z']
                    total_length += np.sqrt(dx**2 + dy**2 + dz**2)
            
            # Set section properties
            section.L = max(total_length, 1)  # Minimum length of 1 µm
            section.diam = np.mean(diameters) if diameters else 1
            
            # Set 3D coordinates
            h.pt3dclear(sec=section)
            for node_id in node_ids:
                node = self.swc_parser.nodes[node_id]
                h.pt3dadd(node['x'], node['y'], node['z'], 
                         node['radius'] * 2, sec=section)
    
    def define_biophysics(self):
        """Define biophysical properties"""
        print("Defining biophysics...")
        
        for section_name, section in self.sections.items():
            section.Ra = 100  # Axial resistance
            section.cm = 1    # Membrane capacitance
            
            # Assign membrane mechanisms based on section type
            if 'soma' in section_name.lower():
                # Active soma
                section.insert('hh')
                
            elif 'axon' in section_name.lower():
                # Active axon
                section.insert('hh')
                # Higher sodium conductance for better propagation
                for seg in section:
                    seg.hh.gnabar = 0.15
                    
            else:
                # Passive dendrites
                section.insert('pas')
                section.g_pas = 0.0002
                section.e_pas = -70
    
    def setup_recording(self):
        """Setup voltage recording from key locations"""
        print("Setting up recordings...")
        
        # Record from soma if available
        soma_sections = [name for name in self.sections.keys() 
                        if 'soma' in name.lower()]
        if soma_sections:
            soma_sec = self.sections[soma_sections[0]]
            self.recordings['soma'] = h.Vector().record(soma_sec(0.5)._ref_v)
        
        # Record from a few other sections
        record_count = 0
        for section_name, section in self.sections.items():
            if record_count < 5:  # Limit number of recordings
                self.recordings[section_name] = h.Vector().record(section(0.5)._ref_v)
                record_count += 1
        
        self.t = h.Vector().record(h._ref_t)
        
        print(f"Recording from {len(self.recordings)} locations")

def create_stimulation(neuron, amp=0.5, delay=5, duration=2):
    """Create current clamp stimulation"""
    # Find soma for stimulation
    soma_sections = [name for name in neuron.sections.keys() 
                    if 'soma' in name.lower()]
    
    if not soma_sections:
        print("No soma found, using first section for stimulation")
        stim_section = list(neuron.sections.values())[0]
    else:
        stim_section = neuron.sections[soma_sections[0]]
    
    stim = h.IClamp(stim_section(0.5))
    stim.delay = delay
    stim.dur = duration
    stim.amp = amp
    
    return stim

def run_simulation(neuron, tstop=50):
    """Run the NEURON simulation"""
    print(f"Running simulation for {tstop} ms...")
    
    h.dt = 0.025
    h.celsius = 37
    h.finitialize(-70)
    h.tstop = tstop
    h.run()
    
    print("Simulation complete!")

def save_blenderspike_data(neuron, output_path):
    """Save data for BlenderSpike"""
    if not BLENDERSPIKE_AVAILABLE:
        print("BlenderSpike not available - skipping export")
        return
        
    print("Saving data for BlenderSpike...")
    
    try:
        # Filter out sections with problematic geometry
        valid_sections = []
        for section in neuron.all_sections:
            try:
                # Check if section has valid 3D points
                n_points = int(h.n3d(sec=section))
                if n_points >= 2:  # Need at least 2 points for a valid section
                    # Check if all coordinates are valid numbers
                    valid = True
                    for i in range(n_points):
                        x, y, z = h.x3d(i, sec=section), h.y3d(i, sec=section), h.z3d(i, sec=section)
                        if not (np.isfinite(x) and np.isfinite(y) and np.isfinite(z)):
                            valid = False
                            break
                    if valid and section.L > 0 and section.diam > 0:
                        valid_sections.append(section)
                    else:
                        print(f"Skipping section {section.name()} - invalid coordinates or dimensions")
                else:
                    print(f"Skipping section {section.name()} - insufficient 3D points ({n_points})")
            except Exception as e:
                print(f"Skipping section {section.name()} - geometry error: {e}")
        
        print(f"Using {len(valid_sections)} out of {len(neuron.all_sections)} sections for BlenderSpike")
        
        if len(valid_sections) == 0:
            print("No valid sections found for BlenderSpike export")
            return False
        
        # Debug info
        print(f"Total simulation time: {h.tstop} ms")
        print(f"Time step: {h.dt} ms")
        print(f"Expected frames: {int(h.tstop/h.dt)}")
        
        # Create new voltage recordings for all valid sections
        print("Setting up voltage recordings for BlenderSpike...")
        voltage_recordings = {}
        
        for section in valid_sections:
            # Record voltage from center of each section
            voltage_recordings[section.name()] = h.Vector().record(section(0.5)._ref_v)
        
        print(f"Recording from {len(voltage_recordings)} sections")
        
        # Re-run a very short simulation to populate voltage data
        print("Running brief simulation to populate voltage data...")
        h.finitialize(-70)
        h.dt = 0.1  # Larger time step for efficiency
        h.tstop = 5   # Very short simulation
        h.run()
        
        # Create CellRecorder AFTER simulation
        cell_recorder = CellRecorder(valid_sections)
        
        # Try different save methods
        try:
            cell_recorder.save_pickle(output_path)
            print(f"Saved: {output_path}")
            return True
        except Exception as e:
            print(f"Standard save failed: {e}")
            
            # Try alternative approach - create minimal dataset
            print("Trying alternative BlenderSpike export...")
            try:
                # Save with minimal frames
                cell_recorder.save_pickle(output_path, n_frames=50)
                print(f"Saved with reduced frames: {output_path}")
                return True
            except Exception as e2:
                print(f"Reduced frames failed: {e2}")
                
                # Last resort - try with very few sections
                print("Trying with reduced section count...")
                try:
                    # Use only first 10 sections
                    minimal_sections = valid_sections[:10]
                    minimal_recorder = CellRecorder(minimal_sections)
                    minimal_recorder.save_pickle(output_path)
                    print(f"Saved with {len(minimal_sections)} sections: {output_path}")
                    return True
                except Exception as e3:
                    print(f"Minimal sections failed: {e3}")
                    return False
        
    except Exception as e:
        print(f"Error saving BlenderSpike data: {e}")
        print("This might be due to complex morphology or geometry issues")
        print("Try using a simpler SWC file or check the SWC format")
        
        # Print some debug info
        print(f"Debug info:")
        print(f"  Total sections: {len(neuron.all_sections)}")
        print(f"  BlenderSpike available: {BLENDERSPIKE_AVAILABLE}")
        
        return False

def plot_results(neuron, swc_file):
    """Create analysis plots"""
    print("Creating analysis plots...")
    
    plt.figure(figsize=(15, 10))
    
    # Voltage traces
    plt.subplot(2, 2, 1)
    for name, v_vec in neuron.recordings.items():
        plt.plot(neuron.t, v_vec, label=name[:20], linewidth=2)  # Truncate long names
    plt.xlabel('Time (ms)')
    plt.ylabel('Voltage (mV)')
    plt.title('Multi-Location Voltage Recording')
    plt.legend()
    plt.grid(True)
    
    # Morphology plot (3D projection)
    plt.subplot(2, 2, 2)
    colors = plt.cm.tab10(np.linspace(0, 1, len(neuron.sections)))
    
    for i, (section_name, section) in enumerate(neuron.sections.items()):
        # Extract 3D coordinates
        x_coords, y_coords, z_coords = [], [], []
        
        for j in range(int(h.n3d(sec=section))):
            x_coords.append(h.x3d(j, sec=section))
            y_coords.append(h.y3d(j, sec=section))
            z_coords.append(h.z3d(j, sec=section))
        
        if x_coords:
            plt.plot(x_coords, y_coords, color=colors[i], linewidth=2, 
                    label=section_name[:15] if i < 10 else "")
    
    plt.xlabel('X (µm)')
    plt.ylabel('Y (µm)')
    plt.title('Neuron Morphology (XY Projection)')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    
    # Section information
    plt.subplot(2, 2, 3)
    section_info = []
    total_length = 0
    
    for section_name, section in neuron.sections.items():
        length = section.L
        total_length += length
        section_info.append(f"{section_name[:20]}: {length:.1f}µm")
    
    # Display info
    info_text = [
        f"SWC File: {os.path.basename(swc_file)}",
        f"Total sections: {len(neuron.sections)}",
        f"Total length: {total_length:.1f}µm",
        f"Total segments: {sum(sec.nseg for sec in neuron.all_sections)}",
        "",
        "Sections:"
    ] + section_info[:15]  # Show first 15 sections
    
    if len(section_info) > 15:
        info_text.append(f"... and {len(section_info) - 15} more")
    
    for i, line in enumerate(info_text):
        plt.text(0.05, 0.95 - i*0.05, line, transform=plt.gca().transAxes,
                fontsize=9, fontfamily='monospace')
    
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    plt.title('Model Summary')
    
    # 3D morphology (XZ projection)
    plt.subplot(2, 2, 4)
    for i, (section_name, section) in enumerate(neuron.sections.items()):
        x_coords, z_coords = [], []
        
        for j in range(int(h.n3d(sec=section))):
            x_coords.append(h.x3d(j, sec=section))
            z_coords.append(h.z3d(j, sec=section))
        
        if x_coords:
            plt.plot(x_coords, z_coords, color=colors[i], linewidth=2)
    
    plt.xlabel('X (µm)')
    plt.ylabel('Z (µm)')
    plt.title('Neuron Morphology (XZ Projection)')
    plt.grid(True)
    plt.axis('equal')
    
    plt.tight_layout()
    plt.show()

def create_simple_blenderspike_export(neuron, output_path):
    """Create a simplified BlenderSpike export that's more likely to work"""
    if not BLENDERSPIKE_AVAILABLE:
        print("BlenderSpike not available - skipping export")
        return False
        
    print("Creating simplified BlenderSpike export...")
    
    try:
        # Get only the most important sections
        important_sections = []
        
        # Add soma sections
        for section in neuron.all_sections:
            if 'soma' in section.name().lower():
                important_sections.append(section)
        
        # Add some dendrite sections (limit to 20 total)
        dendrite_count = 0
        for section in neuron.all_sections:
            if 'dend' in section.name().lower() and dendrite_count < 15:
                try:
                    n_points = int(h.n3d(sec=section))
                    if n_points >= 2 and section.L > 5:  # Only larger sections
                        important_sections.append(section)
                        dendrite_count += 1
                except:
                    continue
        
        # Add axon sections
        axon_count = 0
        for section in neuron.all_sections:
            if 'axon' in section.name().lower() and axon_count < 5:
                try:
                    n_points = int(h.n3d(sec=section))
                    if n_points >= 2:
                        important_sections.append(section)
                        axon_count += 1
                except:
                    continue
        
        print(f"Selected {len(important_sections)} important sections for BlenderSpike")
        
        if len(important_sections) == 0:
            print("No suitable sections found for BlenderSpike")
            return False
        
        # Create a simple, short simulation
        print("Running simplified simulation...")
        
        # Clear any existing recordings
        for section in important_sections:
            h.Vector().record(section(0.5)._ref_v)
        
        # Simple parameters
        h.dt = 0.1
        h.tstop = 10  # Very short
        h.finitialize(-70)
        h.run()
        
        # Create CellRecorder
        cell_recorder = CellRecorder(important_sections)
        
        # Save with minimal parameters
        cell_recorder.save_pickle(output_path, n_frames=100)
        
        print(f"Simplified BlenderSpike file saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"Simplified export also failed: {e}")
        return False

def main():
    """Main function to run the SWC to NEURON conversion"""
    parser = argparse.ArgumentParser(description='Convert SWC file to NEURON model and export for BlenderSpike')
    parser.add_argument('swc_file', help='Path to the SWC file')
    parser.add_argument('--output', '-o', default=None, help='Output path for BlenderSpike pickle file')
    parser.add_argument('--amp', '-a', type=float, default=0.5, help='Stimulation amplitude (nA)')
    parser.add_argument('--duration', '-d', type=float, default=50, help='Simulation duration (ms)')
    parser.add_argument('--no-plot', action='store_true', help='Skip plotting')
    
    args = parser.parse_args()
    
    # Check if SWC file exists
    if not os.path.exists(args.swc_file):
        print(f"Error: SWC file not found: {args.swc_file}")
        return
    
    # Set default output path
    if args.output is None:
        base_name = os.path.splitext(os.path.basename(args.swc_file))[0]
        args.output = f"{base_name}_blenderspike.pickle"
    
    try:
        # Parse SWC file
        parser_obj = SWCParser(args.swc_file)
        parser_obj.parse()
        
        # Create NEURON model
        neuron = SWCNeuron(parser_obj)
        
        # Create stimulation
        stim = create_stimulation(neuron, amp=args.amp)
        
        # Run simulation
        run_simulation(neuron, tstop=args.duration)
        
        # Save for BlenderSpike
        success = save_blenderspike_data(neuron, args.output)
        
        # If that fails, try simplified version
        if not success:
            print("\nTrying simplified BlenderSpike export...")
            success = create_simple_blenderspike_export(neuron, args.output)
        
        # Plot results
        if not args.no_plot:
            plot_results(neuron, args.swc_file)
        
        # Print summary
        print("\n" + "="*60)
        print("CONVERSION COMPLETE!")
        print("="*60)
        print(f"Input SWC: {args.swc_file}")
        print(f"Sections created: {len(neuron.sections)}")
        print(f"Total segments: {sum(sec.nseg for sec in neuron.all_sections)}")
        
        if success:
            print(f"BlenderSpike file: {args.output}")
            print("\nNext steps:")
            print("1. Install BlenderSpike addon in Blender")
            print("2. Load the pickle file in BlenderSpike")
            print("3. Adjust visualization settings as needed")
        else:
            print("BlenderSpike export failed - check error messages above")
            
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # If run directly, you can also call it programmatically
    import sys
    if len(sys.argv) > 1:
        main()
    else:
        print("Usage: python swc_converter.py <swc_file> [options]")
        print("Example: python swc_converter.py neuron.swc --amp 0.8 --duration 100")