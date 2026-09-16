#include <stdio.h>
#include <string.h>

#include "memory_vectors.h"

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
    static const unsigned char target_a = 1U;
    static const unsigned char target_b = 2U;
    struct amiguard_vector_snapshot item;
    struct amiguard_vector_snapshot native_items[4];
    struct amiguard_vector_baseline baseline[1];
    long count;

    memset(&item, 0, sizeof(item));
    item.kind = AMIGUARD_VECTOR_KIND_INTERRUPT;
    item.slot = 3L;
    item.target = &target_a;
    strcpy(item.name, "safe-vector");

    baseline[0].kind = AMIGUARD_VECTOR_KIND_INTERRUPT;
    baseline[0].slot = 3L;
    baseline[0].target = &target_a;
    baseline[0].name = "baseline";

    if (!expect(amiguard_vector_snapshot_valid(&item), "valid vector accepted"))
        return 1;
    if (!expect(amiguard_vector_compare(&item, baseline, 1UL) ==
                AMIGUARD_VECTOR_STATE_BASELINE, "baseline target accepted"))
        return 1;

    item.target = &target_b;
    if (!expect(amiguard_vector_compare(&item, baseline, 1UL) ==
                AMIGUARD_VECTOR_STATE_CHANGED, "changed target reported"))
        return 1;

    item.slot = 9L;
    if (!expect(amiguard_vector_compare(&item, baseline, 1UL) ==
                AMIGUARD_VECTOR_STATE_UNKNOWN, "unknown vector stays neutral"))
        return 1;

    item.target = 0;
    if (!expect(amiguard_vector_compare(&item, baseline, 1UL) ==
                AMIGUARD_VECTOR_STATE_ERROR, "invalid vector rejected"))
        return 1;

    count = amiguard_exec_snapshot_vectors(native_items, 4UL);
#ifndef __AMIGA__
    if (!expect(count == 0L, "host native snapshot inert"))
        return 1;
#else
    if (!expect(count >= 0L, "native vector snapshot completed"))
        return 1;
#endif

    printf("PASS: vector baseline/changed/unknown separation\n");
    return 0;
}
