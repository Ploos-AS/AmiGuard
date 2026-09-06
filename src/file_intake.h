#ifndef AMIGUARD_FILE_INTAKE_H
#define AMIGUARD_FILE_INTAKE_H

#include "hunk.h"

#define AMIGUARD_FILE_MAX_SIZE (128UL * 1024UL)

enum amiguard_file_status {
    AMIGUARD_FILE_ERROR = -1,
    AMIGUARD_FILE_NOT_HUNK = 0,
    AMIGUARD_FILE_VALID_HUNK = 1,
    AMIGUARD_FILE_MALFORMED_HUNK = 2
};

struct amiguard_file_result {
    enum amiguard_file_status status;
    const char *message;
    unsigned long size;
};

enum amiguard_file_status amiguard_classify_file_buffer(
    const unsigned char *data,
    unsigned long size
);

struct amiguard_file_result amiguard_scan_file_readonly(const char *path);

#endif
