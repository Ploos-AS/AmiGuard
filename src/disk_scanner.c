#include "disk_scanner.h"

int amiguard_disk_limits_valid(const struct amiguard_disk_limits *limits)
{
    if (limits == 0) {
        return 0;
    }
    if (limits->max_objects == 0UL) {
        return 0;
    }
    if (limits->max_depth == 0UL) {
        return 0;
    }
    if (limits->max_raw_bytes == 0UL) {
        return 0;
    }
    return 1;
}
