#ifndef AMIGUARD_TRACKDISK_H
#define AMIGUARD_TRACKDISK_H

#include <exec/types.h>

#define AMIGUARD_MAX_FLOPPY_UNIT 3
#define AMIGUARD_BOOTBLOCK_BYTES 1024UL

LONG amiguard_read_bootblock(
    UBYTE unit,
    unsigned char *buffer,
    ULONG buffer_size
);

#endif
