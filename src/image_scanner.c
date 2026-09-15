#include <string.h>

#include "image_scanner.h"
#include "scanner.h"

static void merge_result(struct amiguard_disk_result *out,
                         const struct amiguard_disk_result *part)
{
    out->stats.objects_seen += part->stats.objects_seen;
    out->stats.files_seen += part->stats.files_seen;
    out->stats.bootblocks_seen += part->stats.bootblocks_seen;
    out->stats.raw_regions_seen += part->stats.raw_regions_seen;
    out->stats.bytes_read += part->stats.bytes_read;
    out->stats.errors += part->stats.errors;

    if (part->verdict == AMIGUARD_DISK_INFECTED)
        out->verdict = AMIGUARD_DISK_INFECTED;
    else if (part->verdict == AMIGUARD_DISK_TEST_SIGNATURE &&
             out->verdict != AMIGUARD_DISK_INFECTED)
        out->verdict = AMIGUARD_DISK_TEST_SIGNATURE;
    else if (part->verdict == AMIGUARD_DISK_XVS_DETECTED &&
             out->verdict == AMIGUARD_DISK_CLEAN)
        out->verdict = AMIGUARD_DISK_XVS_DETECTED;
    else if (part->verdict == AMIGUARD_DISK_ERROR &&
             out->verdict == AMIGUARD_DISK_CLEAN)
        out->verdict = AMIGUARD_DISK_ERROR;
}

struct amiguard_disk_result amiguard_scan_adf_readonly(
    const struct amiguard_disk_limits *limits,
    const struct amiguard_image_ops *ops,
    unsigned long image_size
)
{
    struct amiguard_disk_result result;
    struct amiguard_disk_result filesystem_result;
    struct amiguard_detection boot;
    unsigned char buffer[AMIGUARD_DISK_IO_BUFFER_BYTES];
    unsigned long offset;
    unsigned long length;

    memset(&result, 0, sizeof(result));
    result.verdict = AMIGUARD_DISK_CLEAN;
    result.message = "ADF image scan complete";

    if (!amiguard_disk_limits_valid(limits) || ops == 0 || ops->read_at == 0 ||
        image_size == 0UL || image_size > limits->max_raw_bytes ||
        image_size < AMIGUARD_BOOTBLOCK_SIZE ||
        (image_size % AMIGUARD_ADF_SECTOR_BYTES) != 0UL) {
        result.verdict = AMIGUARD_DISK_ERROR;
        result.stats.errors = 1UL;
        result.message = "invalid ADF scan configuration";
        return result;
    }

    /* Read and classify the bootblock through the established bootblock engine. */
    if (ops->read_at(ops->context, 0UL, buffer, AMIGUARD_BOOTBLOCK_SIZE) != 0) {
        result.verdict = AMIGUARD_DISK_ERROR;
        result.stats.errors = 1UL;
        result.message = "ADF bootblock read failed";
        return result;
    }
    result.stats.objects_seen++;
    result.stats.bootblocks_seen++;
    result.stats.bytes_read += AMIGUARD_BOOTBLOCK_SIZE;
    boot = amiguard_scan_bootblock(buffer, AMIGUARD_BOOTBLOCK_SIZE);
    if (boot.result == AMIGUARD_RESULT_INFECTED)
        result.verdict = AMIGUARD_DISK_INFECTED;
    else if (boot.result == AMIGUARD_RESULT_ERROR) {
        result.verdict = AMIGUARD_DISK_ERROR;
        result.stats.errors++;
    }

    /* Traverse every remaining raw region exactly once with bounded storage. */
    offset = AMIGUARD_BOOTBLOCK_SIZE;
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

    /*
     * Filesystem parsing is provider-specific. When available, reuse its file
     * scanner results rather than inventing a second file detector here.
     */
    if (ops->scan_filesystem != 0) {
        filesystem_result = ops->scan_filesystem(ops->context, limits);
        merge_result(&result, &filesystem_result);
    }

    return result;
}
