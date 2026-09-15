#ifndef AMIGUARD_MEMORY_SCANNER_H
#define AMIGUARD_MEMORY_SCANNER_H

/*
 * M4 memory scanner contract.
 *
 * The core is deliberately read-only: providers can enumerate memory objects
 * and copy bounded bytes into caller-owned buffers, but there is no write,
 * patch, quarantine or repair callback.
 */

#define AMIGUARD_MEMORY_IO_BUFFER_BYTES 1024UL
#define AMIGUARD_MEMORY_NAME_MAX 64U

#define AMIGUARD_MEMORY_OBJECT_RESIDENT 1
#define AMIGUARD_MEMORY_OBJECT_TASK     2
#define AMIGUARD_MEMORY_OBJECT_LIBRARY  3
#define AMIGUARD_MEMORY_OBJECT_DEVICE   4
#define AMIGUARD_MEMORY_OBJECT_VECTOR   5
#define AMIGUARD_MEMORY_OBJECT_REGION   6

#define AMIGUARD_MEMORY_CLEAN           0
#define AMIGUARD_MEMORY_TEST_SIGNATURE  1
#define AMIGUARD_MEMORY_INFECTED        2
#define AMIGUARD_MEMORY_SUSPICIOUS      3
#define AMIGUARD_MEMORY_ERROR          -1

struct amiguard_memory_limits {
    unsigned long max_objects;
    unsigned long max_bytes;
    unsigned long max_region_bytes;
};

struct amiguard_memory_object {
    int kind;
    const char *name;
    const void *address;
    unsigned long size;
};

struct amiguard_memory_stats {
    unsigned long objects_seen;
    unsigned long residents_seen;
    unsigned long tasks_seen;
    unsigned long libraries_seen;
    unsigned long devices_seen;
    unsigned long vectors_seen;
    unsigned long regions_seen;
    unsigned long bytes_read;
    unsigned long errors;
};

struct amiguard_memory_result {
    int verdict;
    struct amiguard_memory_stats stats;
    const char *message;
};

struct amiguard_memory_provider {
    void *context;

    /* Return 1 for an object, 0 at end, negative on provider error. */
    int (*next_object)(void *context, struct amiguard_memory_object *object);

    /* Copy at most length bytes from object+offset into buffer. */
    long (*read_object)(void *context,
                        const struct amiguard_memory_object *object,
                        unsigned long offset,
                        unsigned char *buffer,
                        unsigned long length);

    /* Optional provider cleanup. Must not mutate the inspected system. */
    void (*close_object)(void *context,
                         const struct amiguard_memory_object *object);
};

int amiguard_memory_limits_valid(const struct amiguard_memory_limits *limits);
int amiguard_memory_object_valid(const struct amiguard_memory_object *object,
                                 const struct amiguard_memory_limits *limits);

#endif
