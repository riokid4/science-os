"""
Science OS - Verification Layer
Checks MLIR operations against physical laws
"""

import re
import sys
from typing import List, Dict, Tuple
from pathlib import Path

class Violation:
    def __init__(self, severity, location, message):
        self.severity = severity
        self.location = location
        self.message = message
    
    def __str__(self):
        emoji = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[self.severity]
        return f"{emoji} [{self.severity}] {self.location}: {self.message}"


class ScienceVerifier:
    def __init__(self, mlir_text: str):
        self.mlir_text = mlir_text
        self.violations: List[Violation] = []
        self.operations = []
        self.entities = {}
        self._parse()
    
    def _parse(self):
        lines = self.mlir_text.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if '= constant' in line:
                match = re.match(r'(%\w+)\s*=\s*constant\s+(!science\.\w+<[^>]+>)', line)
                if match:
                    self.entities[match.group(1)] = match.group(2)
            elif '= science.' in line:
                self.operations.append((i, line))
    
    def verify_all(self) -> List[Violation]:
        self._verify_evidence()
        self._verify_types()
        self._verify_contradictions()
        return self.violations
    
    def _verify_evidence(self):
        for line_num, op in self.operations:
            if 'evidence' not in op:
                self.violations.append(Violation(
                    "warning", f"Line {line_num}", "Missing evidence"
                ))
            else:
                conf_match = re.search(r',\s*([\d.]+)(?:,|\>)', op)
                if conf_match:
                    conf = float(conf_match.group(1))
                    if conf < 0.5:
                        self.violations.append(Violation(
                            "info", f"Line {line_num}", f"Low confidence: {conf}"
                        ))
    
    def _verify_types(self):
        for line_num, op in self.operations:
            if 'phosphorylate' in op:
                inputs = re.findall(r'%[\w_]+', op.split('at')[0])
                if len(inputs) >= 3:
                    kinase = inputs[1]
                    if kinase in self.entities:
                        if 'protein' not in self.entities[kinase]:
                            self.violations.append(Violation(
                                "error", f"Line {line_num}", "Kinase must be protein"
                            ))
    
    def _verify_contradictions(self):
        interactions = {}
        for line_num, op in self.operations:
            inputs = re.findall(r'%[\w_]+', op.split('at')[0].split('{')[0])
            if len(inputs) >= 3:
                pair = (inputs[1], inputs[2])
                op_type = re.search(r'science\.(\w+)', op)
                if op_type:
                    op_name = op_type.group(1)
                    if pair not in interactions:
                        interactions[pair] = []
                    interactions[pair].append(op_name)
        
        for pair, ops in interactions.items():
            if 'inhibit' in ops and 'activate' in ops:
                self.violations.append(Violation(
                    "warning", "Multiple ops", 
                    f"{pair[0]} both inhibits AND activates {pair[1]}"
                ))
    
    def generate_report(self) -> str:
        lines = [
            "=" * 80,
            "SCIENCE OS - VERIFICATION REPORT",
            "=" * 80,
            "",
            f"Operations Verified: {len(self.operations)}",
            f"Violations Found: {len(self.violations)}",
            "",
            "VIOLATIONS:",
            "-" * 80
        ]
        
        for v in self.violations:
            lines.append(str(v))
        
        if not self.violations:
            lines.append("✓ No violations found!")
        
        lines.append("=" * 80)
        return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify.py <input.mlir>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    with open(input_path, 'r') as f:
        mlir_text = f.read()
    
    verifier = ScienceVerifier(mlir_text)
    violations = verifier.verify_all()
    
    print(verifier.generate_report())
    
    errors = [v for v in violations if v.severity == "error"]
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
