#include "signatures.h"

/*
 * Native tables are generated from provenance-bearing host metadata under
 * signatures/bootblocks/. The generated include contains only compact data
 * needed by the Kickstart 1.2 scanner.
 */
#include "signatures_generated.inc"

const struct amiguard_signature *amiguard_signatures(unsigned long *count)
{
    if (count != 0) {
        *count = (unsigned long)(sizeof(signatures) / sizeof(signatures[0]));
    }
    return signatures;
}
