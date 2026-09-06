#include <exec/types.h>
#include <dos/dos.h>
#include <stdio.h>

#include "scanner.h"
#include "trackdisk.h"

static int parse_unit(const char *arg, UBYTE *unit)
{
    if (arg == 0 || unit == 0) {
        return 0;
    }

    if (arg[0] != 'D' && arg[0] != 'd') return 0;
    if (arg[1] != 'F' && arg[1] != 'f') return 0;
    if (arg[2] < '0' || arg[2] > '3') return 0;
    if (arg[3] != ':' || arg[4] != '\0') return 0;

    *unit = (UBYTE)(arg[2] - '0');
    return 1;
}

static void print_result(const struct amiguard_detection *d)
{
    if (d->result == AMIGUARD_RESULT_INFECTED) {
        printf("INFECTED: %s\n", d->name);
    } else if (d->result == AMIGUARD_RESULT_STANDARD) {
        printf("STANDARD: %s\n", d->name);
    } else if (d->result == AMIGUARD_RESULT_UNKNOWN) {
        printf("UNKNOWN: %s\n", d->name);
    } else {
        printf("ERROR: %s\n", d->name);
    }
}

int main(int argc, char **argv)
{
    unsigned char block[AMIGUARD_BOOTBLOCK_SIZE];
    struct amiguard_detection detection;
    UBYTE unit;
    LONG io_error;

    printf("AmiGuard 0.0.2 M0.2\n");
    printf("Target: Kickstart 1.2+ / Motorola 68000\n");

    if (argc != 2 || !parse_unit(argv[1], &unit)) {
        printf("Usage: AmiGuard DF0:|DF1:|DF2:|DF3:\n");
        return RETURN_ERROR;
    }

    printf("Reading %s bootblock (read-only)...\n", argv[1]);
    io_error = amiguard_read_bootblock(
        unit,
        block,
        AMIGUARD_BOOTBLOCK_SIZE
    );
    if (io_error != 0) {
        printf("trackdisk.device read failed, error %ld\n", (long)io_error);
        return RETURN_FAIL;
    }

    printf("trackdisk.device: read 1024 bytes at offset 0\n");
    detection = amiguard_scan_bootblock(block, AMIGUARD_BOOTBLOCK_SIZE);
    print_result(&detection);

    return detection.result == AMIGUARD_RESULT_ERROR ? RETURN_FAIL : RETURN_OK;
}
