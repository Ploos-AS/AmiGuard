#ifndef AMIGUARD_DISK_SCANNER_H
#define AMIGUARD_DISK_SCANNER_H

/*
 * M3 disk scanning is deliberately split into orchestration and providers.
 * The core never writes media. Providers expose bounded read-only objects;
 * existing file and bootblock detectors remain the verdict authorities.
 */

#define AMIGUARD_DISK_PATH_MAX 256U
#define AMIGUARD_DISK_IO_BUFFER_BYTES 4096UL

enum amiguard_disk_source_kind {
    AMIGUARD_DISK_SOURCE_VOLUME = 1,
    AMIGUARD_DISK_SOURCE_TRACKDISK = 2,
    AMIGUARD_DISK_SOURCE_IMAGE = 3
};

enum amiguard_disk_object_kind {
    AMIGUARD_DISK_OBJECT_FILE = 1,
    AMIGUARD_DISK_OBJECT_BOOTBLOCK = 2,
    AMIGUARD_DISK_OBJECT_RAW_REGION = 3
};

enum amiguard_disk_verdict {
    AMIGUARD_DISK_ERROR = -1,
    AMIGUARD_DISK_CLEAN = 0,
    AMIGUARD_DISK_TEST_SIGNATURE = 1,
    AMIGUARD_DISK_INFECTED = 2,
    AMIGUARD_DISK_XVS_DETECTED = 3
};

struct amiguard_disk_limits {
    unsigned long max_objects;
    unsigned long max_depth;
    unsigned long max_raw_bytes;
};

struct amiguard_disk_stats {
    unsigned long objects_seen;
    unsigned long files_seen;
    unsigned long bootblocks_seen;
    unsigned long raw_regions_seen;
    unsigned long bytes_read;
    unsigned long errors;
};

struct amiguard_disk_result {
    enum amiguard_disk_verdict verdict;
    struct amiguard_disk_stats stats;
    const char *message;
};

/*
 * Provider contract for later M3 milestones. read_object() returns bytes from
 * one logical object into caller-owned bounded storage. No write callback is
 * part of the interface by design.
 */
struct amiguard_disk_provider {
    enum amiguard_disk_source_kind source_kind;
    void *context;
    int (*next_object)(void *context, enum amiguard_disk_object_kind *kind);
    long (*read_object)(void *context, unsigned char *buffer, unsigned long size);
    int (*close_object)(void *context);
};

int amiguard_disk_limits_valid(const struct amiguard_disk_limits *limits);

#endif
