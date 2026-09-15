#include <stdio.h>
#include <string.h>

#include "file_intake.h"
#include "volume_scanner.h"

struct fixture { int root_index; int sub_index; };

static int open_dir(void *context, const char *path, void **handle)
{
    struct fixture *f = (struct fixture *)context;
    if (strcmp(path, "DH0:") == 0) { f->root_index = 0; *handle = (void *)1; return 0; }
    if (strcmp(path, "DH0:sub") == 0) { f->sub_index = 0; *handle = (void *)2; return 0; }
    return -1;
}

static int next_entry(void *context, void *handle, struct amiguard_volume_entry *entry)
{
    struct fixture *f = (struct fixture *)context;
    if (handle == (void *)1) {
        if (f->root_index++ == 0) { entry->name = "clean"; entry->is_directory = 0; return 1; }
        if (f->root_index == 2) { entry->name = "sub"; entry->is_directory = 1; return 1; }
        return 0;
    }
    if (f->sub_index++ == 0) { entry->name = "infected"; entry->is_directory = 0; return 1; }
    return 0;
}

static void close_dir(void *context, void *handle) { (void)context; (void)handle; }

static struct amiguard_file_result scan_file(void *context, const char *path)
{
    struct amiguard_file_result r;
    (void)context;
    r.size = 10UL;
    r.message = "fixture";
    r.status = strstr(path, "infected") ? AMIGUARD_FILE_INFECTED : AMIGUARD_FILE_NOT_HUNK;
    return r;
}

int main(void)
{
    struct fixture fixture;
    struct amiguard_volume_ops ops;
    struct amiguard_disk_limits limits;
    struct amiguard_disk_result result;

    memset(&fixture, 0, sizeof(fixture));
    ops.context = &fixture; ops.open_directory = open_dir; ops.next_entry = next_entry;
    ops.close_directory = close_dir; ops.scan_file = scan_file;
    limits.max_objects = 10UL; limits.max_depth = 4UL; limits.max_raw_bytes = 1UL;

    result = amiguard_scan_volume_readonly("DH0:", &limits, &ops);
    if (result.verdict != AMIGUARD_DISK_INFECTED) return 1;
    if (result.stats.files_seen != 2UL) return 1;
    if (result.stats.objects_seen != 3UL) return 1;
    if (result.stats.bytes_read != 20UL) return 1;
    puts("PASS: recursive volume scan and verdict propagation");
    return 0;
}
