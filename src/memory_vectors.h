#ifndef AMIGUARD_MEMORY_VECTORS_H
#define AMIGUARD_MEMORY_VECTORS_H

#define AMIGUARD_VECTOR_NAME_BYTES 48U
#define AMIGUARD_VECTOR_SOURCE_BYTES 32U

#define AMIGUARD_VECTOR_KIND_EXEC_LVO 1
#define AMIGUARD_VECTOR_KIND_INTERRUPT 2
#define AMIGUARD_VECTOR_KIND_SERVER 3
#define AMIGUARD_VECTOR_KIND_HOOK 4

#define AMIGUARD_VECTOR_STATE_BASELINE 0
#define AMIGUARD_VECTOR_STATE_CHANGED 1
#define AMIGUARD_VECTOR_STATE_UNKNOWN 2
#define AMIGUARD_VECTOR_STATE_ERROR (-1)

struct amiguard_vector_snapshot {
    int kind;
    long slot;
    const void *target;
    char name[AMIGUARD_VECTOR_NAME_BYTES];
};

struct amiguard_vector_provenance {
    unsigned short exec_version;
    unsigned short exec_revision;
    char source[AMIGUARD_VECTOR_SOURCE_BYTES];
};

struct amiguard_vector_baseline {
    int kind;
    long slot;
    const void *target;
    const char *name;
    unsigned short exec_version;
    unsigned short exec_revision;
    const char *source;
};

int amiguard_vector_snapshot_valid(const struct amiguard_vector_snapshot *item);
int amiguard_vector_provenance_valid(const struct amiguard_vector_provenance *provenance);
int amiguard_vector_compare_versioned(const struct amiguard_vector_snapshot *item,
                                      const struct amiguard_vector_baseline *baseline,
                                      unsigned long baseline_count,
                                      const struct amiguard_vector_provenance *provenance);
int amiguard_vector_compare(const struct amiguard_vector_snapshot *item,
                            const struct amiguard_vector_baseline *baseline,
                            unsigned long baseline_count);

/* Native Exec snapshot. Host builds return zero. Read-only only. */
long amiguard_exec_snapshot_vectors(struct amiguard_vector_snapshot *items,
                                   unsigned long capacity);
int amiguard_exec_vector_provenance(struct amiguard_vector_provenance *provenance);

#endif
