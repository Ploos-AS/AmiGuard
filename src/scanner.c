#include "scanner.h"
#include "signatures.h"

static int bytes_equal(const unsigned char *a, const unsigned char *b, unsigned long n)
{
    unsigned long i;
    for (i = 0; i < n; ++i) if (a[i] != b[i]) return 0;
    return 1;
}

struct amiguard_detection amiguard_scan_bootblock(const unsigned char *data, unsigned long size)
{
    const struct amiguard_signature *items;
    unsigned long count, i;
    struct amiguard_detection out;

    out.result = AMIGUARD_RESULT_ERROR;
    out.name = "invalid bootblock";
    if (data == 0 || size != AMIGUARD_BOOTBLOCK_SIZE) return out;

    items = amiguard_signatures(&count);
    for (i = 0; i < count; ++i) {
        unsigned long end = (unsigned long)items[i].offset + (unsigned long)items[i].length;
        if (end <= size && bytes_equal(data + items[i].offset, items[i].pattern, items[i].length)) {
            out.result = AMIGUARD_RESULT_INFECTED;
            out.name = items[i].name;
            return out;
        }
    }

    if (data[0] == 'D' && data[1] == 'O' && data[2] == 'S' && data[3] <= 7U) {
        out.result = AMIGUARD_RESULT_STANDARD;
        out.name = "Amiga DOS bootblock";
    } else {
        out.result = AMIGUARD_RESULT_UNKNOWN;
        out.name = "unknown bootblock";
    }
    return out;
}
