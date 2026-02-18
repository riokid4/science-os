#include "science/Dialect/ScienceDialect.h"
#include "mlir/IR/Builders.h"
#include "llvm/ADT/TypeSwitch.h"

#include "science/Dialect/ScienceDialect.cpp.inc"

#define GET_TYPEDEF_CLASSES
#include "science/Dialect/ScienceOpsTypes.cpp.inc"

void mlir::science::ScienceDialect::initialize() {
  addOperations<
#define GET_OP_LIST
#include "science/Dialect/ScienceOps.cpp.inc"
      >();
  addTypes<
#define GET_TYPEDEF_LIST
#include "science/Dialect/ScienceOpsTypes.cpp.inc"
      >();
}
