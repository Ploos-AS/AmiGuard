#include <string.h>

#include "memory_exec_provider.h"

void amiguard_exec_provider_init(struct amiguard_exec_provider *provider,
                                 struct amiguard_exec_snapshot *objects,
                                 unsigned long count)
{
    if (provider == 0)
        return;
    provider->objects = objects;
    provider->count = count;
    provider->index = 0UL;
}

int amiguard_exec_provider_next(void *context,
                                struct amiguard_memory_object *object)
{
    struct amiguard_exec_provider *provider;
    struct amiguard_exec_snapshot *snapshot;

    if (context == 0 || object == 0)
        return -1;

    provider = (struct amiguard_exec_provider *)context;
    if (provider->index >= provider->count)
        return 0;

    snapshot = &provider->objects[provider->index++];
    object->kind = snapshot->kind;
    object->name = snapshot->name;
    object->address = snapshot->address;
    object->size = snapshot->size;
    return 1;
}

long amiguard_exec_provider_read(void *context,
                                 const struct amiguard_memory_object *object,
                                 unsigned long offset,
                                 unsigned char *buffer,
                                 unsigned long length)
{
    const unsigned char *source;
    unsigned long remaining;

    (void)context;
    if (object == 0 || buffer == 0 || object->address == 0)
        return -1;
    if (offset > object->size)
        return -1;

    remaining = object->size - offset;
    if (length > remaining)
        length = remaining;
    if (length == 0UL)
        return 0;

    source = (const unsigned char *)object->address;
    memcpy(buffer, source + offset, (size_t)length);
    return (long)length;
}

void amiguard_exec_provider_close(void *context,
                                  const struct amiguard_memory_object *object)
{
    (void)context;
    (void)object;
}

#ifdef __AMIGA__
#include <exec/execbase.h>
#include <exec/lists.h>
#include <exec/nodes.h>
#include <exec/resident.h>
#include <proto/exec.h>

extern struct ExecBase *SysBase;

static void copy_name(char *destination, const char *source)
{
    unsigned int i;

    if (destination == 0)
        return;
    if (source == 0) {
        destination[0] = '\0';
        return;
    }
    for (i = 0U; i + 1U < AMIGUARD_EXEC_NAME_BYTES && source[i] != '\0'; ++i)
        destination[i] = source[i];
    destination[i] = '\0';
}

static unsigned long snapshot_list(struct List *list,
                                   int kind,
                                   struct amiguard_exec_snapshot *objects,
                                   unsigned long capacity,
                                   unsigned long used)
{
    struct Node *node;

    if (list == 0 || objects == 0)
        return used;

    for (node = list->lh_Head;
         node != 0 && node->ln_Succ != 0 && used < capacity;
         node = node->ln_Succ) {
        objects[used].kind = kind;
        objects[used].address = (const void *)node;
        objects[used].size = (unsigned long)sizeof(struct Node);
        copy_name(objects[used].name, node->ln_Name);
        ++used;
    }
    return used;
}

long amiguard_exec_snapshot_system(struct amiguard_exec_snapshot *objects,
                                   unsigned long capacity)
{
    unsigned long used;

    if (objects == 0 || capacity == 0UL || SysBase == 0)
        return -1;

    used = 0UL;

    /*
     * Forbid() gives us a short, bounded snapshot window.  Only node metadata
     * is retained; scanning occurs after Permit(), never while multitasking is
     * suppressed.  No list or object is modified.
     */
    Forbid();
    used = snapshot_list(&SysBase->TaskReady, AMIGUARD_MEMORY_OBJECT_TASK,
                         objects, capacity, used);
    used = snapshot_list(&SysBase->LibList, AMIGUARD_MEMORY_OBJECT_LIBRARY,
                         objects, capacity, used);
    used = snapshot_list(&SysBase->DeviceList, AMIGUARD_MEMORY_OBJECT_DEVICE,
                         objects, capacity, used);
    Permit();

    return (long)used;
}
#else
long amiguard_exec_snapshot_system(struct amiguard_exec_snapshot *objects,
                                   unsigned long capacity)
{
    (void)objects;
    (void)capacity;
    return 0;
}
#endif
