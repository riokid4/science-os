# python/science_os/multimodal_ingestor.py

def ingest_literature(text):
    print(f"Ingesting Literature Claim: {text[:50]}...")
    return f"science.claim<text='{text[:20]}'>"

def ingest_sequence(data, kind="DNA"):
    print(f"Ingesting {kind} Sequence: {len(data)} bases")
    return f"!science.seq<alphabet='{kind}', length={len(data)}>"

def ingest_molecule(smiles):
    print(f"Ingesting Chemical Structure: {smiles}")
    return f"!science.molecule<smiles='{smiles}'>"

def ingest_omics(data_id, modality="transcriptomics"):
    print(f"Ingesting Omics Tensor: {data_id} ({modality})")
    return f"!science.omic<modality='{modality}', shape=[variable]>"

def process_workload(workload):
    print("--- SCIENCE OS MULTI-MODAL INGESTION START ---")
    ir_outputs = []
    for item in workload:
        t = item['type']
        if t == 'text': ir_outputs.append(ingest_literature(item['data']))
        elif t == 'dna': ir_outputs.append(ingest_sequence(item['data'], "DNA"))
        elif t == 'chemical': ir_outputs.append(ingest_molecule(item['data']))
        elif t == 'omics': ir_outputs.append(ingest_omics(item['data'], "transcriptomics"))
    print("\n--- GENERATED UNIFIED SCIENCE IR ---")
    for op in ir_outputs: print(f"  {op}")

if __name__ == "__main__":
    my_data = [
        {"type": "text", "data": "Aspirin inhibits COX-2 expression in human cells."},
        {"type": "dna", "data": "ATGCGTACGTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG"},
        {"type": "chemical", "data": "CC(=O)OC1=CC=CC=C1C(=O)O"},
        {"type": "omics", "data": "EXP_BATCH_001_LIVER"}
    ]
    process_workload(my_data)
