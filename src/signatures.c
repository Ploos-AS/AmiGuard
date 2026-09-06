#include "signatures.h"

/* M0 contains no copied third-party or real malware signatures. */
static const unsigned char test_marker[] = {
    0x41, 0x4d, 0x49, 0x47, 0x55, 0x41, 0x52, 0x44
};

static const struct amiguard_signature signatures[] = {
    { "AmiGuard.Test.Marker", 64U, 8U, test_marker }
};

const struct amiguard_signature *amiguard_signatures(unsigned long *count)
{
    if (count != 0) {
        *count = (unsigned long)(sizeof(signatures) / sizeof(signatures[0]));
    }
    return signatures;
}
