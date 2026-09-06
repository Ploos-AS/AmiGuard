#include "scanner.h"
#include "signatures.h"

static int bytes_match_masked(const unsigned char *data,
                              const unsigned char *pattern,
                              const unsigned char *mask,
                              unsigned long n)
{
    unsigned long i;
    for (i = 0; i < n; ++i) {
        if ((data[i] & mask[i]) != (pattern[i] & mask[i])) return 0;
    }
    return 1;
}

static unsigned long read_be32(const unsigned char *p)
{
    return ((unsigned long)p[0] << 24)
         | ((unsigned long)p[1] << 16)
         | ((unsigned long)p[2] << 8)
         | (unsigned long)p[3];
}

int amiguard_bootblock_checksum_valid(const unsigned char *data, unsigned long size)
{
    unsigned long i;
    unsigned long sum = 0;

    if (data == 0 || size != AMIGUARD_BOOTBLOCK_SIZE) return 0;

    for (i = 0; i < size; i += 4) {
        unsigned long word = read_be32(data + i);
        unsigned long previous = sum;
        sum += word;
        if (sum < previous) ++sum;
    }

    return sum == 0xffffffffUL;
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
        if (end <= size && bytes_match_masked(data + items[i].offset,
                                              items[i].pattern,
                                              items[i].mask,
                                              items[i].length)) {
            out.result = AMIGUARD_RESULT_INFECTED;
            out.name = items[i].name;
            return out;
        }
    }

    if (data[0] == 'D' && data[1] == 'O' && data[2] == 'S' && data[3] <= 7U) {
        if (amiguard_bootblock_checksum_valid(data, size)) {
            out.result = AMIGUARD_RESULT_STANDARD;
            out.name = "Amiga DOS bootblock (valid checksum)";
        } else {
            out.result = AMIGUARD_RESULT_UNKNOWN;
            out.name = "Amiga DOS bootblock (invalid checksum)";
        }
    } else {
        out.result = AMIGUARD_RESULT_UNKNOWN;
        out.name = "unknown bootblock";
    }
    return out;
}
