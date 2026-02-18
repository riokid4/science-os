#ifndef SCIENCE_OPS
#define SCIENCE_OPS

include "ScienceDialect.td"
include "mlir/IR/AttrTypeBase.td"
include "mlir/Interfaces/SideEffectInterfaces.td"

def Science_AgentType : TypeDef<Science_Dialect, "Agent"> {
  let mnemonic = "agent";
  let parameters = (ins "StringAttr":$db_name, "StringAttr":$db_id);
}

def Science_EvidenceAttr : AttrDef<Science_Dialect, "Evidence"> {
  let mnemonic = "evidence";
  let parameters = (ins "StringAttr":$doi, "F64Attr":$belief_score, "BoolAttr":$is_retracted);
}

def Science_InhibitOp : Op<Science_Dialect, "inhibit", [Pure]> {
  let summary = "Represents a causal inhibition mechanism.";
  let arguments = (ins Science_AgentType:$agent, Science_AgentType:$target, Science_EvidenceAttr:$metadata);
}

#endif // SCIENCE_OPS
