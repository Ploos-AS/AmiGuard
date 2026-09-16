#include <stdio.h>
#include <string.h>

#include "memory_exec_provider.h"

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
    static const unsigned char task_bytes[] = { 1U, 2U, 3U, 4U };
    static const unsigned char library_bytes[] = { 5U, 6U, 7U };
    static const unsigned char resident_bytes[] = { 8U, 9U };
    struct amiguard_exec_snapshot snapshots[3];
    struct amiguard_exec_provider provider;
    struct amiguard_memory_object object;
    unsigned char buffer[4];
    long count;

    memset(snapshots, 0, sizeof(snapshots));
    snapshots[0].kind = AMIGUARD_MEMORY_OBJECT_TASK;
    snapshots[0].address = task_bytes;
    snapshots[0].size = sizeof(task_bytes);
    strcpy(snapshots[0].name, "safe-task");
    snapshots[1].kind = AMIGUARD_MEMORY_OBJECT_LIBRARY;
    snapshots[1].address = library_bytes;
    snapshots[1].size = sizeof(library_bytes);
    strcpy(snapshots[1].name, "safe.library");
    snapshots[2].kind = AMIGUARD_MEMORY_OBJECT_RESIDENT;
    snapshots[2].address = resident_bytes;
    snapshots[2].size = sizeof(resident_bytes);
    strcpy(snapshots[2].name, "safe-resident");

    amiguard_exec_provider_init(&provider, snapshots, 3UL);
    if (!expect(amiguard_exec_provider_next(&provider, &object) == 1,
                "first object enumerated"))
        return 1;
    if (!expect(object.kind == AMIGUARD_MEMORY_OBJECT_TASK,
                "task class retained"))
        return 1;
    if (!expect(strcmp(object.name, "safe-task") == 0,
                "task name retained"))
        return 1;
    if (!expect(amiguard_exec_provider_read(&provider, &object, 1UL,
                                            buffer, 2UL) == 2L,
                "bounded object read"))
        return 1;
    if (!expect(buffer[0] == 2U && buffer[1] == 3U,
                "read bytes correct"))
        return 1;
    if (!expect(amiguard_exec_provider_read(&provider, &object, 99UL,
                                            buffer, 1UL) < 0L,
                "out-of-range read rejected"))
        return 1;

    if (!expect(amiguard_exec_provider_next(&provider, &object) == 1,
                "second object enumerated"))
        return 1;
    if (!expect(object.kind == AMIGUARD_MEMORY_OBJECT_LIBRARY,
                "library class retained"))
        return 1;

    if (!expect(amiguard_exec_provider_next(&provider, &object) == 1,
                "resident object enumerated"))
        return 1;
    if (!expect(object.kind == AMIGUARD_MEMORY_OBJECT_RESIDENT,
                "resident class retained"))
        return 1;
    if (!expect(strcmp(object.name, "safe-resident") == 0,
                "resident name retained"))
        return 1;

    if (!expect(amiguard_exec_provider_next(&provider, &object) == 0,
                "provider end reported"))
        return 1;

    count = amiguard_exec_snapshot_system(snapshots, 3UL);
#ifndef __AMIGA__
    if (!expect(count == 0L, "host snapshot is inert"))
        return 1;
#else
    if (!expect(count >= 0L, "native snapshot completed"))
        return 1;
#endif

    printf("PASS: Exec memory provider task/library/resident coverage and bounded reads\n");
    return 0;
}
