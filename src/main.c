#include <exec/types.h>
#include <dos/dos.h>
#include <stdio.h>
#include <string.h>

#include "file_intake.h"
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

static int is_file_mode(const char *arg)
{
    return arg != 0 && strcmp(arg, "FILE") == 0;
}

static void print_result(const struct amiguard_detection *d)
{
    if (d->result == AMIGUARD_RESULT_INFECTED) {
        printf("INFECTED: %s\n", d->name);
    } else if (d->result == AMIGUARD_RESULT_STANDARD) {
        printf("STANDARD: %s\n", d->name);
    } else if (d->result == AMIGUARD_RESULT_CUSTOM) {
        printf("CUSTOM: %s\n", d->name);
    } else if (d->result == AMIGUARD_RESULT_UNKNOWN) {
        printf("UNKNOWN: %s\n", d->name);
    } else {
        printf("ERROR: %s\n", d->name);
    }
}

static int scan_file_mode(const char *path)
{
    struct amiguard_file_result result;

    printf("Reading file read-only: %s\n", path);
    result = amiguard_scan_file_readonly(path);

    if (result.status == AMIGUARD_FILE_VALID_HUNK) {
        printf("VALID-HUNK: %s (%lu bytes)\n", result.message, result.size);
        return RETURN_OK;
    }
    if (result.status == AMIGUARD_FILE_NOT_HUNK) {
        printf("NOT-HUNK: %s (%lu bytes)\n", result.message, result.size);
        return RETURN_OK;
    }
    if (result.status == AMIGUARD_FILE_MALFORMED_HUNK) {
        printf("MALFORMED-HUNK: %s (%lu bytes)\n", result.message, result.size);
        return RETURN_OK;
    }

    printf("ERROR: %s", result.message);
    if (result.size != 0UL)
        printf(" (%lu bytes)", result.size);
    printf("\n");
    return RETURN_FAIL;
}

int main(int argc, char **argv)
{
    unsigned char block[AMIGUARD_BOOTBLOCK_SIZE];
    struct amiguard_detection detection;
    UBYTE unit;
    LONG io_error;

    printf("AmiGuard 0.0.2 M0.2\n");
    printf("Target: Kickstart 1.2+ / Motorola 68000\n");

    if (argc == 3 && is_file_mode(argv[1]))
        return scan_file_mode(argv[2]);

    if (argc != 2 || !parse_unit(argv[1], &unit)) {
        printf("Usage: AmiGuard DF0:|DF1:|DF2:|DF3:\n");
        printf("       AmiGuard FILE <path>\n");
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
