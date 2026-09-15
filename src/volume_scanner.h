#ifndef AMIGUARD_VOLUME_SCANNER_H
#define AMIGUARD_VOLUME_SCANNER_H

#include "disk_scanner.h"

struct amiguard_volume_entry {
    const char *name;
    int is_directory;
};

/* Host/native filesystem adapter. All callbacks are read-only. */
struct amiguard_volume_ops {
    void *context;
    int (*open_directory)(void *context, const char *path, void **handle);
    int (*next_entry)(void *context, void *handle, struct amiguard_volume_entry *entry);
    void (*close_directory)(void *context, void *handle);
    struct amiguard_file_result (*scan_file)(void *context, const char *path);
};

struct amiguard_disk_result amiguard_scan_volume_readonly(
    const char *root,
    const struct amiguard_disk_limits *limits,
    const struct amiguard_volume_ops *ops
);

#endif
