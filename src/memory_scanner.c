#include "memory_scanner.h"

int amiguard_memory_limits_valid(const struct amiguard_memory_limits *limits)
{
    if (limits == 0)
        return 0;
    if (limits->max_objects == 0UL)
        return 0;
    if (limits->max_bytes == 0UL)
        return 0;
    if (limits->max_region_bytes == 0UL)
        return 0;
    if (limits->max_region_bytes > limits->max_bytes)
        return 0;
    return 1;
}

int amiguard_memory_object_valid(const struct amiguard_memory_object *object,
                                 const struct amiguard_memory_limits *limits)
{
    if (object == 0 || !amiguard_memory_limits_valid(limits))
        return 0;

    if (object->kind < AMIGUARD_MEMORY_OBJECT_RESIDENT ||
        object->kind > AMIGUARD_MEMORY_OBJECT_REGION)
        return 0;

    if (object->address == 0 || object->size == 0UL)
        return 0;

    if (object->size > limits->max_region_bytes)
        return 0;

    return 1;
}
