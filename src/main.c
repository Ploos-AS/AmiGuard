#include <exec/types.h>
#include <dos/dos.h>
#include <proto/dos.h>
#include "scanner.h"

int main(void)
{
    unsigned char block[AMIGUARD_BOOTBLOCK_SIZE];
    struct amiguard_detection d;
    unsigned long i;

    for (i = 0; i < AMIGUARD_BOOTBLOCK_SIZE; ++i) block[i] = 0U;
    block[0] = 'D'; block[1] = 'O'; block[2] = 'S'; block[3] = 0U;

    Printf("AmiGuard 0.0.1 M0\n");
    Printf("Target: Kickstart 1.2+ / Motorola 68000\n");
    d = amiguard_scan_bootblock(block, AMIGUARD_BOOTBLOCK_SIZE);
    Printf("Scanner: %s\n", (LONG)d.name);
    Printf("Read-only trackdisk scanning follows in M0.2.\n");
    return RETURN_OK;
}
