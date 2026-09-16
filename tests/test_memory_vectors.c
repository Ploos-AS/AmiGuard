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
    struct amiguard_vector_provenance provenance;
    long count;
    long server_count;

    memset(&item, 0, sizeof(item));
    item.kind = AMIGUARD_VECTOR_KIND_INTERRUPT;
    item.slot = 3L;
    item.target = &target_a;
    strcpy(item.name, "safe-vector");

    baseline[0].kind = AMIGUARD_VECTOR_KIND_INTERRUPT;
    baseline[0].slot = 3L;
    baseline[0].target = &target_a;
    baseline[0].name = "baseline";
    baseline[0].exec_version = 37U;
    baseline[0].exec_revision = 175U;
    baseline[0].source = "safe-test";

    memset(&provenance, 0, sizeof(provenance));
    provenance.exec_version = 37U;
    provenance.exec_revision = 175U;
    strcpy(provenance.source, "safe-test");

    if (!expect(amiguard_vector_snapshot_valid(&item), "valid vector accepted"))
        return 1;
    if (!expect(amiguard_vector_provenance_valid(&provenance),
                "valid provenance accepted"))
        return 1;
    if (!expect(amiguard_vector_compare_versioned(&item, baseline, 1UL, &provenance) ==
                AMIGUARD_VECTOR_STATE_BASELINE, "matching version/source baseline accepted"))
        return 1;

    item.target = &target_b;
    if (!expect(amiguard_vector_compare_versioned(&item, baseline, 1UL, &provenance) ==
                AMIGUARD_VECTOR_STATE_CHANGED, "same provenance changed target reported"))
        return 1;

    item.target = &target_a;
    strcpy(provenance.source, "other-source");
    if (!expect(amiguard_vector_compare_versioned(&item, baseline, 1UL, &provenance) ==
                AMIGUARD_VECTOR_STATE_UNKNOWN,
                "different provenance source stays neutral"))
        return 1;

    strcpy(provenance.source, "safe-test");
    provenance.exec_version = 36U;
    if (!expect(amiguard_vector_compare_versioned(&item, baseline, 1UL, &provenance) ==
                AMIGUARD_VECTOR_STATE_UNKNOWN,
                "different Exec version stays neutral"))
        return 1;

    provenance.exec_version = 37U;
    item.slot = 9L;
    if (!expect(amiguard_vector_compare_versioned(&item, baseline, 1UL, &provenance) ==
                AMIGUARD_VECTOR_STATE_UNKNOWN, "unknown vector stays neutral"))
        return 1;

    item.target = 0;
    if (!expect(amiguard_vector_compare_versioned(&item, baseline, 1UL, &provenance) ==
                AMIGUARD_VECTOR_STATE_ERROR, "invalid vector rejected"))
        return 1;

    count = amiguard_exec_snapshot_vectors(native_items, 4UL);
    server_count = amiguard_exec_snapshot_interrupt_servers(native_items, 4UL, 8UL);
#ifndef __AMIGA__
    if (!expect(count == 0L, "host native snapshot inert"))
        return 1;
    if (!expect(server_count == 0L, "host server snapshot inert"))
        return 1;
    if (!expect(amiguard_exec_vector_provenance(&provenance) == 0,
                "host native provenance inert"))
        return 1;
#else
    if (!expect(count >= 0L, "native vector snapshot completed"))
        return 1;
    if (!expect(server_count >= 0L && server_count <= 4L,
                "native bounded server snapshot completed"))
        return 1;
    if (!expect(amiguard_exec_vector_provenance(&provenance),
                "native Exec provenance captured"))
        return 1;
#endif

    printf("PASS: version/source-aware vector and bounded server snapshots\n");
    return 0;
}
