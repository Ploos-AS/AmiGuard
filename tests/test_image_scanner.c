#include <stdio.h>
#include <string.h>

#include "image_scanner.h"

struct fixture {
    unsigned long expected_offset;
    unsigned long calls;
    int fail_call;
    enum amiguard_disk_verdict filesystem_verdict;
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

static struct amiguard_disk_result scan_filesystem(
    void *context,
    const struct amiguard_disk_limits *limits
)
{
    struct fixture *f = (struct fixture *)context;
    struct amiguard_disk_result result;
    (void)limits;
    memset(&result, 0, sizeof(result));
    result.verdict = f->filesystem_verdict;
    result.stats.objects_seen = 2UL;
    result.stats.files_seen = 2UL;
    result.stats.bytes_read = 32UL;
    result.message = "synthetic filesystem corpus";
    return result;
}

static void reset_fixture(struct fixture *fixture)
{
    memset(fixture, 0, sizeof(*fixture));
    fixture->filesystem_verdict = AMIGUARD_DISK_CLEAN;
}

int main(void)
{
    struct fixture fixture;
    struct amiguard_image_ops ops;
    struct amiguard_disk_limits limits;
    struct amiguard_disk_result result;

    reset_fixture(&fixture);
    memset(&ops, 0, sizeof(ops));
    ops.context = &fixture;
    ops.read_at = read_at;
    ops.scan_filesystem = scan_filesystem;
    limits.max_objects = 300UL;
    limits.max_depth = 1UL;
    limits.max_raw_bytes = AMIGUARD_ADF_DD_BYTES;

    /* Clean synthetic full-image corpus: bootblock + raw image + visible files. */
    result = amiguard_scan_adf_readonly(&limits, &ops, AMIGUARD_ADF_DD_BYTES);
    if (result.verdict != AMIGUARD_DISK_CLEAN) return 1;
    if (result.stats.bytes_read != AMIGUARD_ADF_DD_BYTES + 32UL) return 1;
    if (result.stats.bootblocks_seen != 1UL) return 1;
    if (result.stats.raw_regions_seen != 220UL) return 1;
    if (result.stats.files_seen != 2UL) return 1;

    /* Safe-test filesystem corpus must stay distinct from production INFECTED. */
    reset_fixture(&fixture);
    fixture.filesystem_verdict = AMIGUARD_DISK_TEST_SIGNATURE;
    result = amiguard_scan_adf_readonly(&limits, &ops, AMIGUARD_ADF_DD_BYTES);
    if (result.verdict != AMIGUARD_DISK_TEST_SIGNATURE) return 1;

    reset_fixture(&fixture);
    fixture.fail_call = 2;
    result = amiguard_scan_adf_readonly(&limits, &ops, AMIGUARD_ADF_DD_BYTES);
    if (result.verdict != AMIGUARD_DISK_ERROR || result.stats.errors != 1UL) return 1;

    reset_fixture(&fixture);
    result = amiguard_scan_adf_readonly(&limits, &ops, AMIGUARD_ADF_DD_BYTES - 1UL);
    if (result.verdict != AMIGUARD_DISK_ERROR) return 1;

    limits.max_raw_bytes = AMIGUARD_ADF_DD_BYTES - AMIGUARD_ADF_SECTOR_BYTES;
    result = amiguard_scan_adf_readonly(&limits, &ops, AMIGUARD_ADF_DD_BYTES);
    if (result.verdict != AMIGUARD_DISK_ERROR) return 1;

    puts("PASS: ADF bootblock, raw-region and filesystem qualification corpora");
    return 0;
}
