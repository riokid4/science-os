"""
INDRA to MLIR Ingestion Bridge
Converts INDRA JSON statements into Science dialect MLIR operations.
"""

import json
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Grounded biological entity with database references."""
    name: str
    entity_type: str
    db_refs: Dict[str, str]
    organism: Optional[str] = None
    
    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        if self.entity_type == "protein" and "UP" in self.db_refs:
            return self.db_refs.get("UP") == other.db_refs.get("UP")
        return self.name == other.name
    
    def __hash__(self):
        if self.entity_type == "protein" and "UP" in self.db_refs:
            return hash(self.db_refs["UP"])
        return hash(self.name)
    
    def to_mlir_type(self) -> str:
        if self.entity_type == "protein":
            uniprot = self.db_refs.get("UP", "UNKNOWN")
            return f"!science.protein<{uniprot}>"
        elif self.entity_type == "gene":
            symbol = self.name
            db_id = self.db_refs.get("HGNC", self.db_refs.get("EGID", "UNKNOWN"))
            return f"!science.gene<{symbol}, {db_id}>"
        elif self.entity_type == "chemical":
            name = self.name
            db_id = self.db_refs.get("PUBCHEM", self.db_refs.get("CHEBI", "UNKNOWN"))
            return f"!science.chemical<{name}, {db_id}>"
        return f"!science.unknown<{self.name}>"
    
    def to_mlir_ssa(self) -> str:
        if self.entity_type == "protein" and "UP" in self.db_refs:
            base = self.db_refs["UP"].lower().replace("-", "_")
        else:
            base = self.name.lower().replace("-", "_").replace(" ", "_")
        return f"%{base}"


@dataclass
class MLIRModule:
    operations: List[str] = field(default_factory=list)
    entities: Dict[str, Entity] = field(default_factory=dict)
    
    def add_entity(self, entity: Entity) -> str:
        ssa_name = entity.to_mlir_ssa()
        if ssa_name not in self.entities:
            self.entities[ssa_name] = entity
        return ssa_name
    
    def add_operation(self, op: str):
        self.operations.append(op)
    
    def emit(self) -> str:
        lines = [
            '// Science OS - Auto-generated from INDRA',
            'module {',
            '',
            '  // Entity Definitions'
        ]
        
        for ssa_name, entity in self.entities.items():
            lines.append(f'  {ssa_name} = constant {entity.to_mlir_type()}')
        
        lines.append('')
        lines.append('  // Mechanistic Operations')
        for op in self.operations:
            lines.append(f'  {op}')
        
        lines.append('}')
        return '\n'.join(lines)


class INDRAConverter:
    def __init__(self):
        self.module = MLIRModule()
        self.statement_count = 0
        self.error_count = 0
    
    def parse_entity(self, entity_data: Dict[str, Any]) -> Optional[Entity]:
        if not entity_data:
            return None
        
        name = entity_data.get("name", "UNKNOWN")
        db_refs = entity_data.get("db_refs", {})
        
        if "UP" in db_refs:
            entity_type = "protein"
        elif "HGNC" in db_refs or "EGID" in db_refs:
            entity_type = "gene"
        elif "PUBCHEM" in db_refs or "CHEBI" in db_refs:
            entity_type = "chemical"
        else:
            entity_type = "unknown"
        
        return Entity(name=name, entity_type=entity_type, db_refs=db_refs)
    
    def parse_context(self, evidence_list: List[Dict]) -> str:
        parts = []
        for ev in evidence_list:
            annotations = ev.get("annotations", {})
            if "cell_line" in annotations:
                cell = annotations["cell_line"].get("name")
                if cell:
                    parts.append(f'cell_type="{cell}"')
            if "species" in annotations:
                org = annotations["species"].get("name")
                if org:
                    parts.append(f'organism="{org}"')
        
        if not parts:
            return "#science.context<>"
        return f"#science.context<{', '.join(parts)}>"
    
    def parse_evidence(self, evidence_list: List[Dict]) -> str:
        if not evidence_list:
            return '#science.evidence<"unknown", "unknown", 0.5>'
        
        best_ev = evidence_list[0]
        pmid = best_ev.get("pmid", "unknown")
        epistemics = best_ev.get("epistemics", {})
        confidence = epistemics.get("direct", 0.8)
        evidence_type = best_ev.get("source_api", "literature")
        
        return f'#science.evidence<"{pmid}", "unknown", {confidence}, "{evidence_type}">'
    
    def convert_phosphorylation(self, stmt: Dict) -> Optional[str]:
        try:
            enz = self.parse_entity(stmt.get("enz"))
            sub = self.parse_entity(stmt.get("sub"))
            
            if not enz or not sub:
                return None
            
            enz_ssa = self.module.add_entity(enz)
            sub_ssa = self.module.add_entity(sub)
            
            residue = stmt.get("residue", "")
            position = stmt.get("position", "")
            site = f"{residue}{position}" if residue and position else "unknown"
            
            evidence_list = stmt.get("evidence", [])
            context = self.parse_context(evidence_list)
            evidence = self.parse_evidence(evidence_list)
            
            stmt_id = f"{id(stmt) % 100000}"
            result_ssa = f"%phospho_{sub.name.lower()}_{stmt_id}"
            
            op = f'{result_ssa} = science.phosphorylate {enz_ssa}, {sub_ssa} at "{site}" ' \
                 f'{{context = {context}}} {{evidence = {evidence}}} ' \
                 f': ({enz.to_mlir_type()}, {sub.to_mlir_type()}) -> {sub.to_mlir_type()}'
            
            return op
        except Exception as e:
            logger.error(f"Error converting phosphorylation: {e}")
            self.error_count += 1
            return None
    
    def convert_activation(self, stmt: Dict) -> Optional[str]:
        try:
            subj = self.parse_entity(stmt.get("subj"))
            obj = self.parse_entity(stmt.get("obj"))
            
            if not subj or not obj:
                return None
            
            subj_ssa = self.module.add_entity(subj)
            obj_ssa = self.module.add_entity(obj)
            
            evidence_list = stmt.get("evidence", [])
            context = self.parse_context(evidence_list)
            evidence = self.parse_evidence(evidence_list)
            
            stmt_id = f"{id(stmt) % 100000}"
            result_ssa = f"%activated_{obj.name.lower()}_{stmt_id}"
            
            op = f'{result_ssa} = science.activate {subj_ssa}, {obj_ssa} ' \
                 f'{{context = {context}}} {{evidence = {evidence}}} ' \
                 f': ({subj.to_mlir_type()}, {obj.to_mlir_type()}) -> {obj.to_mlir_type()}'
            
            return op
        except Exception as e:
            logger.error(f"Error converting activation: {e}")
            self.error_count += 1
            return None
    
    def convert_inhibition(self, stmt: Dict) -> Optional[str]:
        try:
            subj = self.parse_entity(stmt.get("subj"))
            obj = self.parse_entity(stmt.get("obj"))
            
            if not subj or not obj:
                return None
            
            subj_ssa = self.module.add_entity(subj)
            obj_ssa = self.module.add_entity(obj)
            
            evidence_list = stmt.get("evidence", [])
            context = self.parse_context(evidence_list)
            evidence = self.parse_evidence(evidence_list)
            
            stmt_id = f"{id(stmt) % 100000}"
            result_ssa = f"%inhibited_state_{stmt_id}"
            
            op = f'{result_ssa} = science.inhibit {subj_ssa}, {obj_ssa} ' \
                 f'{{context = {context}}} {{evidence = {evidence}}} ' \
                 f': ({subj.to_mlir_type()}, {obj.to_mlir_type()}) -> !science.cellstate<"inhibited">'
            
            return op
        except Exception as e:
            logger.error(f"Error converting inhibition: {e}")
            self.error_count += 1
            return None
    
    def convert_complex(self, stmt: Dict) -> Optional[str]:
        try:
            members = stmt.get("members", [])
            if len(members) < 2:
                return None
            
            ent1 = self.parse_entity(members[0])
            ent2 = self.parse_entity(members[1])
            
            if not ent1 or not ent2:
                return None
            
            ent1_ssa = self.module.add_entity(ent1)
            ent2_ssa = self.module.add_entity(ent2)
            
            evidence_list = stmt.get("evidence", [])
            context = self.parse_context(evidence_list)
            evidence = self.parse_evidence(evidence_list)
            
            stmt_id = f"{id(stmt) % 100000}"
            result_ssa = f"%complex_{stmt_id}"
            
            op = f'{result_ssa} = science.bind {ent1_ssa}, {ent2_ssa} ' \
                 f'{{context = {context}}} {{evidence = {evidence}}} ' \
                 f': ({ent1.to_mlir_type()}, {ent2.to_mlir_type()}) -> !science.protein<complex>'
            
            return op
        except Exception as e:
            logger.error(f"Error converting complex: {e}")
            self.error_count += 1
            return None
    
    def convert_statement(self, stmt: Dict) -> Optional[str]:
        stmt_type = stmt.get("type")
        
        converters = {
            "Phosphorylation": self.convert_phosphorylation,
            "Inhibition": self.convert_inhibition,
            "Activation": self.convert_activation,
            "Complex": self.convert_complex,
        }
        
        converter = converters.get(stmt_type)
        if not converter:
            logger.warning(f"Unsupported statement type: {stmt_type}")
            return None
        
        return converter(stmt)
    
    def process_indra_json(self, json_path: Path) -> str:
        logger.info(f"Processing INDRA JSON: {json_path}")
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        statements = data if isinstance(data, list) else data.get("statements", [])
        logger.info(f"Found {len(statements)} statements")
        
        for stmt in statements:
            self.statement_count += 1
            op = self.convert_statement(stmt)
            if op:
                self.module.add_operation(op)
        
        logger.info(f"Converted {self.statement_count} statements")
        logger.info(f"Generated {len(self.module.operations)} MLIR operations")
        
        return self.module.emit()


def main():
    if len(sys.argv) < 3:
        print("Usage: python indra_to_mlir.py <input.json> <output.mlir>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    converter = INDRAConverter()
    mlir_code = converter.process_indra_json(input_path)
    
    with open(output_path, 'w') as f:
        f.write(mlir_code)
    
    print(f"\n✓ Successfully generated MLIR: {output_path}")
    print(f"  Statements: {converter.statement_count}")
    print(f"  Operations: {len(converter.module.operations)}")


if __name__ == "__main__":
    main()
