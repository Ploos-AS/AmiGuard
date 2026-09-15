#include <stdio.h>
#include <string.h>

#include "image_scanner.h"

struct fixture {
    unsigned long expected_offset;
    unsigned long calls;
    int fail_call;
};

static int read_at(void *context, unsigned long offset, unsigned char *buffer, unsigned long length)
{
    struct fixture *f = (struct fixture *)context;
    if (offset != f->expected_offset || length == 0UL) return -1;
    f->calls++;
    if (f->fail_call > 0 && f->calls == (unsigned long)f->fail_call) return -1;
    memset(buffer, 0, (size_t)length);
    f->expected_offset += length;
    return 0;
}

int main(void)
{
    struct fixture fixture;
    struct amiguard_image_ops ops;
    struct amiguard_disk_limits limits;
    struct amiguard_disk_result result;

    memset(&fixture, 0, sizeof(fixture));
    ops.context = &fixture;
    ops.read_at = read_at;
    limits.max_objects = 300UL;
    limits.max_depth = 1UL;
    limits.max_raw_bytes = AMIGUARD_ADF_DD_BYTES;

    result = amiguard_scan_adf_readonly(&limits, &ops, AMIGUARD_ADF_DD_BYTES);
    if (result.verdict != AMIGUARD_DISK_CLEAN) return 1;
    if (result.stats.bytes_read != AMIGUARD_ADF_DD_BYTES) return 1;
    if (result.stats.raw_regions_seen != 220UL) return 1;

    memset(&fixture, 0, sizeof(fixture));
    fixture.fail_call = 2;
    result = amiguard_scan_adf_readonly(&limits, &ops, AMIGUARD_ADF_DD_BYTES);
    if (result.verdict != AMIGUARD_DISK_ERROR || result.stats.errors != 1UL) return 1;

    result = amiguard_scan_adf_readonly(&limits, &ops, AMIGUARD_ADF_DD_BYTES - 1UL);
    if (result.verdict != AMIGUARD_DISK_ERROR) return 1;

    limits.max_raw_bytes = AMIGUARD_ADF_DD_BYTES - AMIGUARD_ADF_SECTOR_BYTES;
    result = amiguard_scan_adf_readonly(&limits, &ops, AMIGUARD_ADF_DD_BYTES);
    if (result.verdict != AMIGUARD_DISK_ERROR) return 1;

    puts("PASS: bounded full ADF image traversal and error handling");
    return 0;
}
