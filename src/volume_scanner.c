#include <stdlib.h>
#include <string.h>

#include "file_intake.h"
#include "volume_scanner.h"

static void init_result(struct amiguard_disk_result *result)
{
    memset(result, 0, sizeof(*result));
    result->verdict = AMIGUARD_DISK_CLEAN;
    result->message = "volume scan complete";
}

static void merge_file_result(
    struct amiguard_disk_result *result,
    const struct amiguard_file_result *file_result
)
{
    result->stats.files_seen++;
    result->stats.objects_seen++;
    result->stats.bytes_read += file_result->size;

    if (file_result->status == AMIGUARD_FILE_ERROR) {
        result->stats.errors++;
        if (result->verdict == AMIGUARD_DISK_CLEAN)
            result->verdict = AMIGUARD_DISK_ERROR;
    } else if (file_result->status == AMIGUARD_FILE_INFECTED) {
        result->verdict = AMIGUARD_DISK_INFECTED;
        result->message = file_result->message;
    } else if (file_result->status == AMIGUARD_FILE_TEST_SIGNATURE &&
               result->verdict != AMIGUARD_DISK_INFECTED) {
        result->verdict = AMIGUARD_DISK_TEST_SIGNATURE;
        result->message = file_result->message;
    } else if (file_result->status == AMIGUARD_FILE_XVS_DETECTED &&
               result->verdict != AMIGUARD_DISK_INFECTED &&
               result->verdict != AMIGUARD_DISK_TEST_SIGNATURE) {
        result->verdict = AMIGUARD_DISK_XVS_DETECTED;
        result->message = file_result->message;
    }
}

static int join_path(char *out, const char *base, const char *name)
{
    unsigned long a = (unsigned long)strlen(base);
    unsigned long b = (unsigned long)strlen(name);
    int separator = (a != 0UL && base[a - 1UL] != '/' && base[a - 1UL] != ':');

    if (a + (separator ? 1UL : 0UL) + b + 1UL > AMIGUARD_DISK_PATH_MAX)
        return 0;
    strcpy(out, base);
    if (separator)
        strcat(out, "/");
    strcat(out, name);
    return 1;
}

static int scan_directory(
    const char *path,
    unsigned long depth,
    const struct amiguard_disk_limits *limits,
    const struct amiguard_volume_ops *ops,
    struct amiguard_disk_result *result
)
{
    void *handle = 0;
    struct amiguard_volume_entry entry;
    char child[AMIGUARD_DISK_PATH_MAX];
    int next;

    if (depth > limits->max_depth) {
        result->stats.errors++;
        return 0;
    }
    if (ops->open_directory(ops->context, path, &handle) != 0) {
        result->stats.errors++;
        return 0;
    }

    while ((next = ops->next_entry(ops->context, handle, &entry)) > 0) {
        struct amiguard_file_result file_result;

        if (result->stats.objects_seen >= limits->max_objects) {
            result->stats.errors++;
            ops->close_directory(ops->context, handle);
            return 0;
        }
        if (entry.name == 0 || entry.name[0] == '\0' ||
            strcmp(entry.name, ".") == 0 || strcmp(entry.name, "..") == 0)
            continue;
        if (!join_path(child, path, entry.name)) {
            result->stats.errors++;
            continue;
        }

        if (entry.is_directory) {
            result->stats.objects_seen++;
            if (!scan_directory(child, depth + 1UL, limits, ops, result)) {
                ops->close_directory(ops->context, handle);
                return 0;
            }
        } else {
            file_result = ops->scan_file(ops->context, child);
            merge_file_result(result, &file_result);
        }
    }

    ops->close_directory(ops->context, handle);
    if (next < 0) {
        result->stats.errors++;
        return 0;
    }
    return 1;
}

struct amiguard_disk_result amiguard_scan_volume_readonly(
    const char *root,
    const struct amiguard_disk_limits *limits,
    const struct amiguard_volume_ops *ops
)
{
    struct amiguard_disk_result result;
    init_result(&result);

    if (root == 0 || root[0] == '\0' || !amiguard_disk_limits_valid(limits) ||
        ops == 0 || ops->open_directory == 0 || ops->next_entry == 0 ||
        ops->close_directory == 0 || ops->scan_file == 0) {
        result.verdict = AMIGUARD_DISK_ERROR;
        result.stats.errors = 1UL;
        result.message = "invalid volume scan configuration";
        return result;
    }

    if (!scan_directory(root, 0UL, limits, ops, &result) &&
        result.verdict == AMIGUARD_DISK_CLEAN) {
        result.verdict = AMIGUARD_DISK_ERROR;
        result.message = "volume scan incomplete";
    }
    return result;
}
