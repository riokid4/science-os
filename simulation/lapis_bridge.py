"""
Science OS - LAPIS Simulation Bridge  
Compiles MLIR operations to executable simulations
"""

import re
import sys
from typing import List, Dict
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Species:
    name: str
    ssa_value: str
    initial_concentration: float = 1.0


@dataclass  
class Reaction:
    reaction_type: str
    inputs: List[str]
    enzyme: str = None
    rate: float = 0.1


class MLIRToSimulation:
    def __init__(self, mlir_text: str):
        self.mlir_text = mlir_text
        self.species: Dict[str, Species] = {}
        self.reactions: List[Reaction] = []
        self._parse()
    
    def _parse(self):
        lines = self.mlir_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Parse entities
            if '= constant' in line:
                match = re.match(r'(%\w+)\s*=\s*constant', line)
                if match:
                    ssa = match.group(1)
                    name = ssa[1:]
                    self.species[ssa] = Species(name=name, ssa_value=ssa)
            
            # Parse operations
            elif 'science.phosphorylate' in line:
                parts = line.split('=')
                if len(parts) >= 2:
                    rhs = parts[1]
                    ssa_vals = re.findall(r'%\w+', rhs)
                    if len(ssa_vals) >= 2:
                        self.reactions.append(Reaction(
                            reaction_type="phosphorylate",
                            inputs=ssa_vals,
                            enzyme=ssa_vals[0],
                            rate=0.1
                        ))
            
            elif 'science.activate' in line:
                parts = line.split('=')
                if len(parts) >= 2:
                    rhs = parts[1]
                    ssa_vals = re.findall(r'%\w+', rhs)
                    if len(ssa_vals) >= 2:
                        self.reactions.append(Reaction(
                            reaction_type="activate",
                            inputs=ssa_vals,
                            rate=0.1
                        ))
            
            elif 'science.inhibit' in line:
                parts = line.split('=')
                if len(parts) >= 2:
                    rhs = parts[1]
                    ssa_vals = re.findall(r'%\w+', rhs)
                    if len(ssa_vals) >= 2:
                        self.reactions.append(Reaction(
                            reaction_type="inhibit",
                            inputs=ssa_vals,
                            rate=0.05
                        ))
    
    def generate_simulation_code(self) -> str:
        code = [
            '"""Auto-generated Science OS Simulation"""',
            'import numpy as np',
            'from scipy.integrate import odeint',
            'import matplotlib.pyplot as plt',
            '',
            f'# Species: {len(self.species)}',
            f'# Reactions: {len(self.reactions)}',
            '',
        ]
        
        # Species mapping
        ssa_to_idx = {s.ssa_value: i for i, s in enumerate(self.species.values())}
        
        code.append('def get_initial_conditions():')
        code.append(f'    return np.ones({len(self.species)})')
        code.append('')
        
        # ODE system
        code.append('def ode_system(y, t):')
        code.append(f'    dydt = np.zeros({len(self.species)})')
        
        for rxn in self.reactions:
            if rxn.reaction_type == "phosphorylate" and len(rxn.inputs) >= 2:
                e = ssa_to_idx.get(rxn.inputs[0], 0)
                s = ssa_to_idx.get(rxn.inputs[1], 0)
                code.append(f'    dydt[{s}] -= {rxn.rate} * y[{e}] * y[{s}]  # phosphorylation')
            
            elif rxn.reaction_type == "activate" and len(rxn.inputs) >= 2:
                a = ssa_to_idx.get(rxn.inputs[0], 0)
                t = ssa_to_idx.get(rxn.inputs[1], 0)
                code.append(f'    dydt[{t}] += {rxn.rate} * y[{a}]  # activation')
            
            elif rxn.reaction_type == "inhibit" and len(rxn.inputs) >= 2:
                i = ssa_to_idx.get(rxn.inputs[0], 0)
                t = ssa_to_idx.get(rxn.inputs[1], 0)
                code.append(f'    dydt[{t}] -= {rxn.rate} * y[{i}]  # inhibition')
        
        code.append('    return dydt')
        code.append('')
        
        # Run simulation
        code.extend([
            'def run_simulation():',
            '    print("Running p53 pathway simulation...")',
            '    y0 = get_initial_conditions()',
            '    t = np.linspace(0, 100, 1000)',
            '    sol = odeint(ode_system, y0, t)',
            '    ',
            '    plt.figure(figsize=(10, 6))',
        ])
        
        for i, sp in enumerate(self.species.values()):
            code.append(f'    plt.plot(t, sol[:, {i}], label="{sp.name}")')
        
        code.extend([
            '    plt.xlabel("Time")',
            '    plt.ylabel("Concentration")',
            '    plt.title("Science OS - p53 Signaling")',
            '    plt.legend()',
            '    plt.grid(True)',
            '    plt.tight_layout()',
            '    plt.savefig("p53_simulation.png", dpi=150)',
            '    print("✓ Done! Saved to p53_simulation.png")',
            '',
            'if __name__ == "__main__":',
            '    run_simulation()',
        ])
        
        return '\n'.join(code)


def main():
    if len(sys.argv) < 3:
        print("Usage: python lapis_bridge.py <input.mlir> <output.py>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    with open(input_path, 'r') as f:
        mlir_text = f.read()
    
    converter = MLIRToSimulation(mlir_text)
    code = converter.generate_simulation_code()
    
    with open(output_path, 'w') as f:
        f.write(code)
    
    print(f"✓ Generated: {output_path}")
    print(f"  Species: {len(converter.species)}")
    print(f"  Reactions: {len(converter.reactions)}")


if __name__ == "__main__":
    main()
