#ifndef AMIGUARD_IMAGE_SCANNER_H
#define AMIGUARD_IMAGE_SCANNER_H

#include "disk_scanner.h"

#define AMIGUARD_ADF_DD_BYTES 901120UL
#define AMIGUARD_ADF_SECTOR_BYTES 512UL

struct amiguard_image_ops {
    void *context;
    int (*read_at)(void *context, unsigned long offset, unsigned char *buffer, unsigned long length);
    /*
     * Optional filesystem-visible file provider. It must be read-only and
     * bounded by the supplied disk limits. The returned result is merged into
     * the image verdict; omitting it leaves filesystem traversal unavailable.
     */
    struct amiguard_disk_result (*scan_filesystem)(
        void *context,
        const struct amiguard_disk_limits *limits
    );
};

struct amiguard_disk_result amiguard_scan_adf_readonly(
    const struct amiguard_disk_limits *limits,
    const struct amiguard_image_ops *ops,
    unsigned long image_size
);

#endif
