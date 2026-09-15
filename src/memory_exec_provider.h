#ifndef AMIGUARD_MEMORY_EXEC_PROVIDER_H
#define AMIGUARD_MEMORY_EXEC_PROVIDER_H

#include "memory_scanner.h"

#define AMIGUARD_EXEC_NAME_BYTES 64U

struct amiguard_exec_snapshot {
    int kind;
    const void *address;
    unsigned long size;
    char name[AMIGUARD_EXEC_NAME_BYTES];
};

struct amiguard_exec_provider {
    struct amiguard_exec_snapshot *objects;
    unsigned long count;
    unsigned long index;
};

void amiguard_exec_provider_init(struct amiguard_exec_provider *provider,
                                 struct amiguard_exec_snapshot *objects,
                                 unsigned long count);
int amiguard_exec_provider_next(void *context,
                                struct amiguard_memory_object *object);
long amiguard_exec_provider_read(void *context,
                                 const struct amiguard_memory_object *object,
                                 unsigned long offset,
                                 unsigned char *buffer,
                                 unsigned long length);
void amiguard_exec_provider_close(void *context,
                                  const struct amiguard_memory_object *object);

/*
 * Fill caller-owned snapshot storage from classic Exec lists.  The native
 * implementation is compiled only for Amiga; host builds return zero.
 */
long amiguard_exec_snapshot_system(struct amiguard_exec_snapshot *objects,
                                   unsigned long capacity);

#endif
