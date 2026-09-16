#include "memory_vectors.h"

int amiguard_vector_snapshot_valid(const struct amiguard_vector_snapshot *item)
{
    if (item == 0)
        return 0;
    if (item->kind < AMIGUARD_VECTOR_KIND_EXEC_LVO ||
        item->kind > AMIGUARD_VECTOR_KIND_HOOK)
        return 0;
    if (item->target == 0)
        return 0;
    return 1;
}

int amiguard_vector_provenance_valid(const struct amiguard_vector_provenance *provenance)
{
    if (provenance == 0)
        return 0;
    if (provenance->exec_version == 0U)
        return 0;
    if (provenance->source[0] == '\0')
        return 0;
    return 1;
}

int amiguard_vector_compare_versioned(const struct amiguard_vector_snapshot *item,
                                      const struct amiguard_vector_baseline *baseline,
                                      unsigned long baseline_count,
                                      const struct amiguard_vector_provenance *provenance)
{
    unsigned long i;

    if (!amiguard_vector_snapshot_valid(item) || baseline == 0 ||
        !amiguard_vector_provenance_valid(provenance))
        return AMIGUARD_VECTOR_STATE_ERROR;

    for (i = 0UL; i < baseline_count; ++i) {
        if (baseline[i].kind == item->kind && baseline[i].slot == item->slot &&
            baseline[i].exec_version == provenance->exec_version &&
            baseline[i].exec_revision == provenance->exec_revision) {
            if (baseline[i].target == item->target)
                return AMIGUARD_VECTOR_STATE_BASELINE;
            return AMIGUARD_VECTOR_STATE_CHANGED;
        }
    }

    /* A different or unrecorded Exec version is not evidence of tampering. */
    return AMIGUARD_VECTOR_STATE_UNKNOWN;
}

int amiguard_vector_compare(const struct amiguard_vector_snapshot *item,
                            const struct amiguard_vector_baseline *baseline,
                            unsigned long baseline_count)
{
    unsigned long i;

    if (!amiguard_vector_snapshot_valid(item) || baseline == 0)
        return AMIGUARD_VECTOR_STATE_ERROR;

    for (i = 0UL; i < baseline_count; ++i) {
        if (baseline[i].kind == item->kind && baseline[i].slot == item->slot) {
            if (baseline[i].target == item->target)
                return AMIGUARD_VECTOR_STATE_BASELINE;
            return AMIGUARD_VECTOR_STATE_CHANGED;
        }
    }
    return AMIGUARD_VECTOR_STATE_UNKNOWN;
}

#ifdef __AMIGA__
#include <exec/execbase.h>
#include <exec/interrupts.h>
#include <proto/exec.h>

extern struct ExecBase *SysBase;

static void copy_name(char *destination, unsigned int capacity, const char *source)
{
    unsigned int i;

    if (destination == 0 || capacity == 0U)
        return;
    if (source == 0) {
        destination[0] = '\0';
        return;
    }
    for (i = 0U; i + 1U < capacity && source[i] != '\0'; ++i)
        destination[i] = source[i];
    destination[i] = '\0';
}

long amiguard_exec_snapshot_vectors(struct amiguard_vector_snapshot *items,
                                   unsigned long capacity)
{
    unsigned long used;
    unsigned int i;

    if (items == 0 || capacity == 0UL || SysBase == 0)
        return -1;

    used = 0UL;

    /*
     * Capture interrupt vector targets only. This is deliberately an
     * observation API: it never calls SetFunction(), SetIntVector() or writes
     * to ExecBase. Baseline classification is performed after the snapshot.
     */
    Disable();
    for (i = 0U; i < 16U && used < capacity; ++i) {
        struct IntVector *vector;
        vector = &SysBase->IntVects[i];
        if (vector->iv_Code != 0) {
            items[used].kind = AMIGUARD_VECTOR_KIND_INTERRUPT;
            items[used].slot = (long)i;
            items[used].target = (const void *)vector->iv_Code;
            copy_name(items[used].name, AMIGUARD_VECTOR_NAME_BYTES,
                      "exec.interrupt");
            ++used;
        }
    }
    Enable();

    return (long)used;
}

int amiguard_exec_vector_provenance(struct amiguard_vector_provenance *provenance)
{
    if (provenance == 0 || SysBase == 0)
        return 0;

    provenance->exec_version = SysBase->LibNode.lib_Version;
    provenance->exec_revision = SysBase->LibNode.lib_Revision;
    copy_name(provenance->source, AMIGUARD_VECTOR_SOURCE_BYTES, "exec.library");
    return amiguard_vector_provenance_valid(provenance);
}
#else
long amiguard_exec_snapshot_vectors(struct amiguard_vector_snapshot *items,
                                   unsigned long capacity)
{
    (void)items;
    (void)capacity;
    return 0;
}

int amiguard_exec_vector_provenance(struct amiguard_vector_provenance *provenance)
{
    (void)provenance;
    return 0;
}
#endif
