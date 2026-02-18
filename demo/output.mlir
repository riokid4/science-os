// Science OS - Auto-generated from INDRA
module {

  // Entity Definitions
  %q13315 = constant !science.protein<Q13315>
  %p04637 = constant !science.protein<P04637>
  %p38936 = constant !science.protein<P38936>
  %q00987 = constant !science.protein<Q00987>

  // Mechanistic Operations
  %phospho_tp53_82304 = science.phosphorylate %q13315, %p04637 at "S15" {context = #science.context<cell_type="HCT116", organism="human">} {evidence = #science.evidence<"9724731", "unknown", 0.95, "reach">} : (!science.protein<Q13315>, !science.protein<P04637>) -> !science.protein<P04637>
  %activated_cdkn1a_81856 = science.activate %p04637, %p38936 {context = #science.context<organism="human">} {evidence = #science.evidence<"8242752", "unknown", 0.92, "reach">} : (!science.protein<P04637>, !science.protein<P38936>) -> !science.protein<P38936>
  %inhibited_state_75712 = science.inhibit %q00987, %p04637 {context = #science.context<organism="human">} {evidence = #science.evidence<"8293284", "unknown", 0.9, "reach">} : (!science.protein<Q00987>, !science.protein<P04637>) -> !science.cellstate<"inhibited">
}