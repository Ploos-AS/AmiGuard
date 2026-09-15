#include <stdio.h>

#include "disk_scanner.h"

static int failures = 0;

static void expect(int condition, const char *name)
{
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", name);
        failures++;
    } else {
        printf("PASS: %s\n", name);
    }
}

int main(void)
{
    struct amiguard_disk_limits limits;

    limits.max_objects = 4096UL;
    limits.max_depth = 32UL;
    limits.max_raw_bytes = 901120UL;
    expect(amiguard_disk_limits_valid(&limits), "bounded limits accepted");
    expect(!amiguard_disk_limits_valid(0), "null limits rejected");

    limits.max_objects = 0UL;
    expect(!amiguard_disk_limits_valid(&limits), "unbounded object count rejected");
    limits.max_objects = 4096UL;
    limits.max_depth = 0UL;
    expect(!amiguard_disk_limits_valid(&limits), "unbounded traversal depth rejected");
    limits.max_depth = 32UL;
    limits.max_raw_bytes = 0UL;
    expect(!amiguard_disk_limits_valid(&limits), "unbounded raw read rejected");

    return failures ? 1 : 0;
}
