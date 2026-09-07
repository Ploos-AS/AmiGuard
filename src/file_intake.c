#include <stdio.h>
#include <stdlib.h>

#include "file_intake.h"
#include "file_signatures.h"

#define AMIGUARD_FILE_READ_CHUNK 4096UL

static struct amiguard_file_result make_result(
    enum amiguard_file_status status,
    const char *message,
    unsigned long size
)
{
    struct amiguard_file_result result;
    result.status = status;
    result.message = message;
    result.size = size;
    return result;
}

enum amiguard_file_status amiguard_classify_file_buffer(
    const unsigned char *data,
    unsigned long size
)
{
    enum amiguard_hunk_result hunk_result;

    if (size > AMIGUARD_FILE_MAX_SIZE)
        return AMIGUARD_FILE_ERROR;

    hunk_result = amiguard_parse_hunk(data, size);
    if (hunk_result == AMIGUARD_HUNK_VALID)
        return AMIGUARD_FILE_VALID_HUNK;
    if (hunk_result == AMIGUARD_HUNK_NOT_HUNK)
        return AMIGUARD_FILE_NOT_HUNK;
    return AMIGUARD_FILE_MALFORMED_HUNK;
}

struct amiguard_file_result amiguard_scan_file_readonly(const char *path)
{
    FILE *fp;
    unsigned char *buffer;
    unsigned long size = 0UL;
    unsigned long capacity = AMIGUARD_FILE_READ_CHUNK;
    enum amiguard_file_status status;
    struct amiguard_file_signature_match signature_match;

    if (path == 0 || path[0] == '\0')
        return make_result(AMIGUARD_FILE_ERROR, "invalid file path", 0UL);

    fp = fopen(path, "rb");
    if (fp == 0)
        return make_result(AMIGUARD_FILE_ERROR, "cannot open file read-only", 0UL);

    buffer = (unsigned char *)malloc(capacity);
    if (buffer == 0) {
        fclose(fp);
        return make_result(AMIGUARD_FILE_ERROR, "out of memory", 0UL);
    }

    for (;;) {
        size_t available = (size_t)(capacity - size);
        size_t got = fread(buffer + size, 1U, available, fp);
        size += (unsigned long)got;

        if (got < available) {
            if (ferror(fp)) {
                free(buffer);
                fclose(fp);
                return make_result(AMIGUARD_FILE_ERROR, "file read failed", size);
            }
            break;
        }

        if (capacity == AMIGUARD_FILE_MAX_SIZE) {
            int extra = fgetc(fp);
            if (extra != EOF) {
                free(buffer);
                fclose(fp);
                return make_result(
                    AMIGUARD_FILE_ERROR,
                    "file exceeds 128 KiB M2.1 limit",
                    size + 1UL
                );
            }
            if (ferror(fp)) {
                free(buffer);
                fclose(fp);
                return make_result(AMIGUARD_FILE_ERROR, "file read failed", size);
            }
            break;
        }

        {
            unsigned long new_capacity = capacity * 2UL;
            unsigned char *grown;
            if (new_capacity > AMIGUARD_FILE_MAX_SIZE)
                new_capacity = AMIGUARD_FILE_MAX_SIZE;
            grown = (unsigned char *)realloc(buffer, new_capacity);
            if (grown == 0) {
                free(buffer);
                fclose(fp);
                return make_result(AMIGUARD_FILE_ERROR, "out of memory", size);
            }
            buffer = grown;
            capacity = new_capacity;
        }
    }

    fclose(fp);

    signature_match = amiguard_match_file_signature(buffer, size);
    if (signature_match.matched) {
        enum amiguard_file_status match_status = signature_match.test_only
            ? AMIGUARD_FILE_TEST_SIGNATURE
            : AMIGUARD_FILE_INFECTED;
        const char *match_name = signature_match.name;
        free(buffer);
        return make_result(match_status, match_name, size);
    }

    status = amiguard_classify_file_buffer(buffer, size);
    free(buffer);

    if (status == AMIGUARD_FILE_VALID_HUNK)
        return make_result(status, "supported Amiga HUNK structure", size);
    if (status == AMIGUARD_FILE_NOT_HUNK)
        return make_result(status, "not an Amiga HUNK file", size);
    if (status == AMIGUARD_FILE_MALFORMED_HUNK)
        return make_result(status, "HUNK structure is malformed or unsupported", size);
    return make_result(AMIGUARD_FILE_ERROR, "file exceeds M2.1 policy", size);
}
