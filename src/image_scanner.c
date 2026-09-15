#include <string.h>

#include "image_scanner.h"

struct amiguard_disk_result amiguard_scan_adf_readonly(
    const struct amiguard_disk_limits *limits,
    const struct amiguard_image_ops *ops,
    unsigned long image_size
)
{
    struct amiguard_disk_result result;
    unsigned char buffer[AMIGUARD_DISK_IO_BUFFER_BYTES];
    unsigned long offset;
    unsigned long length;

    memset(&result, 0, sizeof(result));
    result.verdict = AMIGUARD_DISK_CLEAN;
    result.message = "ADF image read complete";

    if (!amiguard_disk_limits_valid(limits) || ops == 0 || ops->read_at == 0 ||
        image_size == 0UL || image_size > limits->max_raw_bytes ||
        (image_size % AMIGUARD_ADF_SECTOR_BYTES) != 0UL) {
        result.verdict = AMIGUARD_DISK_ERROR;
        result.stats.errors = 1UL;
        result.message = "invalid ADF scan configuration";
        return result;
    }

    offset = 0UL;
    while (offset < image_size) {
        if (result.stats.objects_seen >= limits->max_objects) {
            result.verdict = AMIGUARD_DISK_ERROR;
            result.stats.errors++;
            result.message = "ADF object limit reached";
            return result;
        }
        length = image_size - offset;
        if (length > (unsigned long)sizeof(buffer))
            length = (unsigned long)sizeof(buffer);
        if (ops->read_at(ops->context, offset, buffer, length) != 0) {
            result.verdict = AMIGUARD_DISK_ERROR;
            result.stats.errors++;
            result.message = "ADF image read failed";
            return result;
        }
        result.stats.objects_seen++;
        result.stats.raw_regions_seen++;
        result.stats.bytes_read += length;
        offset += length;
    }

    return result;
}
