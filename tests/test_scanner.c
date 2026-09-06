#include <stdio.h>
#include <string.h>
#include "scanner.h"

static int failures;
static void expect(int ok, const char *name)
{
    if (ok) printf("PASS: %s\n", name);
    else { fprintf(stderr, "FAIL: %s\n", name); ++failures; }
}

static void make_valid_dos_bootblock(unsigned char *block)
{
    memset(block, 0, AMIGUARD_BOOTBLOCK_SIZE);
    block[0] = 'D'; block[1] = 'O'; block[2] = 'S'; block[3] = 0;

    /* 0x444f5300 + 0xbbb0acff == 0xffffffff. */
    block[4] = 0xbb;
    block[5] = 0xb0;
    block[6] = 0xac;
    block[7] = 0xff;
}

int main(void)
{
    unsigned char block[AMIGUARD_BOOTBLOCK_SIZE];
    struct amiguard_detection d;

    make_valid_dos_bootblock(block);
    expect(amiguard_bootblock_checksum_valid(block, sizeof(block)),
           "valid DOS checksum");
    d = amiguard_scan_bootblock(block, sizeof(block));
    expect(d.result == AMIGUARD_RESULT_STANDARD,
           "valid DOS bootblock classified known");

    block[100] = 1;
    expect(!amiguard_bootblock_checksum_valid(block, sizeof(block)),
           "corrupt DOS checksum rejected");
    d = amiguard_scan_bootblock(block, sizeof(block));
    expect(d.result == AMIGUARD_RESULT_UNKNOWN,
           "invalid-checksum DOS bootblock classified unknown");

    memset(block, 0, sizeof(block));
    memcpy(block + 64, "AMIGUARD", 8);
    d = amiguard_scan_bootblock(block, sizeof(block));
    expect(d.result == AMIGUARD_RESULT_INFECTED, "synthetic signature");

    memset(block, 0x5a, sizeof(block));
    d = amiguard_scan_bootblock(block, sizeof(block));
    expect(d.result == AMIGUARD_RESULT_UNKNOWN, "unknown bootblock");

    expect(!amiguard_bootblock_checksum_valid(block, 100),
           "checksum rejects short block");
    d = amiguard_scan_bootblock(block, 100);
    expect(d.result == AMIGUARD_RESULT_ERROR, "short block rejected");

    if (failures) return 1;
    puts("All scanner tests passed.");
    return 0;
}
