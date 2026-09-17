#include <string.h>

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
            baseline[i].exec_revision == provenance->exec_revision &&
            baseline[i].source != 0 &&
            strcmp(baseline[i].source, provenance->source) == 0) {
            if (baseline[i].target == item->target)
                return AMIGUARD_VECTOR_STATE_BASELINE;
            return AMIGUARD_VECTOR_STATE_CHANGED;
        }
    }

    /* Different version/source or an unrecorded slot is not evidence of tampering. */
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
#include <exec/nodes.h>
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

    /* Observation only: capture vector targets without installing or changing them. */
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

long amiguard_exec_snapshot_interrupt_servers(struct amiguard_vector_snapshot *items,
                                              unsigned long capacity,
                                              unsigned long max_per_vector)
{
    unsigned long used;
    unsigned int i;

    if (items == 0 || capacity == 0UL || max_per_vector == 0UL || SysBase == 0)
        return -1;

    used = 0UL;

    /*
     * iv_Node may point at the first Interrupt server for a chained vector.
     * Copy only scalar metadata while interrupts are disabled and retain no
     * server-node pointer for later dereference. Stop on the Exec list tail,
     * a self-link, or the explicit per-vector/aggregate bounds. These guards
     * make damaged lists fail bounded rather than hanging the scanner.
     */
    Disable();
    for (i = 0U; i < 16U && used < capacity; ++i) {
        struct Node *node;
        unsigned long ordinal;

        node = SysBase->IntVects[i].iv_Node;
        ordinal = 0UL;
        while (node != 0 && node->ln_Succ != 0 &&
               ordinal < max_per_vector && used < capacity) {
            struct Interrupt *server;
            struct Node *next;

            server = (struct Interrupt *)node;
            next = node->ln_Succ;
            if (server->is_Code != 0) {
                items[used].kind = AMIGUARD_VECTOR_KIND_SERVER;
                items[used].slot = ((long)i << 16) | (long)(ordinal & 0xffffUL);
                items[used].target = (const void *)server->is_Code;
                copy_name(items[used].name, AMIGUARD_VECTOR_NAME_BYTES,
                          server->is_Node.ln_Name != 0 ? server->is_Node.ln_Name :
                          "exec.interrupt-server");
                ++used;
            }
            ++ordinal;
            if (next == node)
                break;
            node = next;
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

long amiguard_exec_snapshot_interrupt_servers(struct amiguard_vector_snapshot *items,
                                              unsigned long capacity,
                                              unsigned long max_per_vector)
{
    (void)items;
    (void)capacity;
    (void)max_per_vector;
    return 0;
}

int amiguard_exec_vector_provenance(struct amiguard_vector_provenance *provenance)
{
    (void)provenance;
    return 0;
}
#endif
