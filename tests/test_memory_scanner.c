#include <stdio.h>

#include "memory_scanner.h"

static int expect(int condition, const char *message)
{
    if (!condition) {
        printf("FAIL: %s\n", message);
        return 0;
    }
    return 1;
}

int main(void)
{
    struct amiguard_memory_limits limits;
    struct amiguard_memory_object object;
    unsigned char byte;

    limits.max_objects = 256UL;
    limits.max_bytes = 524288UL;
    limits.max_region_bytes = 65536UL;

    if (!expect(amiguard_memory_limits_valid(&limits), "valid limits"))
        return 1;
    if (!expect(!amiguard_memory_limits_valid(0), "null limits rejected"))
        return 1;

    object.kind = AMIGUARD_MEMORY_OBJECT_REGION;
    object.name = "safe-test-region";
    object.address = &byte;
    object.size = 1024UL;

    if (!expect(amiguard_memory_object_valid(&object, &limits),
                "bounded region accepted"))
        return 1;

    object.size = limits.max_region_bytes + 1UL;
    if (!expect(!amiguard_memory_object_valid(&object, &limits),
                "oversized region rejected"))
        return 1;

    object.size = 1024UL;
    object.address = 0;
    if (!expect(!amiguard_memory_object_valid(&object, &limits),
                "null address rejected"))
        return 1;

    object.address = &byte;
    object.kind = 99;
    if (!expect(!amiguard_memory_object_valid(&object, &limits),
                "unknown object kind rejected"))
        return 1;

    printf("PASS: memory scanner bounds and object validation\n");
    return 0;
}
