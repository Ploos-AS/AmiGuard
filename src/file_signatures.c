#include <stddef.h>

#include "file_signatures.h"

#include "file_signatures_generated.inc"

static int masked_match(
    const unsigned char *data,
    const struct amiguard_file_signature *sig
)
{
    unsigned int i;
    for (i = 0U; i < sig->length; ++i) {
        unsigned char mask = sig->mask[i];
        if ((data[sig->offset + i] & mask) != (sig->pattern[i] & mask))
            return 0;
    }
    return 1;
}

struct amiguard_file_signature_match amiguard_match_file_signature(
    const unsigned char *data,
    unsigned long size
)
{
    struct amiguard_file_signature_match result;
    unsigned long i;
    unsigned long count = (unsigned long)(sizeof(file_signatures) / sizeof(file_signatures[0]));

    result.matched = 0;
    result.test_only = 0;
    result.name = 0;

    if (data == 0)
        return result;

    for (i = 0UL; i < count; ++i) {
        const struct amiguard_file_signature *sig = &file_signatures[i];
        if (sig->offset > size)
            continue;
        if ((unsigned long)sig->length > size - sig->offset)
            continue;
        if (masked_match(data, sig)) {
            result.matched = 1;
            result.test_only = sig->test_only;
            result.name = sig->name;
            return result;
        }
    }

    return result;
}
