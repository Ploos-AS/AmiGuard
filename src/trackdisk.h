#ifndef AMIGUARD_TRACKDISK_H
#define AMIGUARD_TRACKDISK_H

#include <exec/types.h>

#define AMIGUARD_MAX_FLOPPY_UNIT 3
#define AMIGUARD_BOOTBLOCK_BYTES 1024UL
#define AMIGUARD_DD_FLOPPY_BYTES 901120UL
#define AMIGUARD_TRACKDISK_SECTOR_BYTES 512UL

LONG amiguard_read_bootblock(
    UBYTE unit,
    unsigned char *buffer,
    ULONG buffer_size
);

/* Read one bounded region without ever issuing a write command. */
LONG amiguard_read_raw_region(
    UBYTE unit,
    ULONG offset,
    unsigned char *buffer,
    ULONG length,
    ULONG media_limit
);

#endif
