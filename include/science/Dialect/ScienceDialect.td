ifndef SCIENCE_DIALECT
#define SCIENCE_DIALECT

include "mlir/IR/OpBase.td"

def Science_Dialect : Dialect {
  let name = "science";
  let summary = "A formal intermediate representation for scientific mechanisms.";
  let cppNamespace = "::mlir::science";
}

#endif // SCIENCE_DIALECT
