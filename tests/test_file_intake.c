#include <stdio.h>
#include <string.h>

#include "file_intake.h"

static int failures = 0;

static void expect_status(const char *name, enum amiguard_file_status got,
                          enum amiguard_file_status expected)
{
    if (got != expected) {
        fprintf(stderr, "%s: got %d expected %d\n", name, (int)got, (int)expected);
        failures++;
    }
}

static void put_u32(unsigned char *buf, unsigned long *offset, unsigned long value)
{
    buf[*offset] = (unsigned char)((value >> 24) & 0xffUL);
    buf[*offset + 1] = (unsigned char)((value >> 16) & 0xffUL);
    buf[*offset + 2] = (unsigned char)((value >> 8) & 0xffUL);
    buf[*offset + 3] = (unsigned char)(value & 0xffUL);
    *offset += 4UL;
}

static unsigned long make_valid_code(unsigned char *buf)
{
    unsigned long o = 0UL;
    put_u32(buf, &o, 1011UL);
    put_u32(buf, &o, 0UL);
    put_u32(buf, &o, 1UL);
    put_u32(buf, &o, 0UL);
    put_u32(buf, &o, 0UL);
    put_u32(buf, &o, 1UL);
    put_u32(buf, &o, 1001UL);
    put_u32(buf, &o, 1UL);
    put_u32(buf, &o, 0x4e754e75UL);
    put_u32(buf, &o, 1010UL);
    return o;
}

int main(void)
{
    unsigned char buf[128];
    unsigned long size;

    memset(buf, 0, sizeof(buf));
    expect_status("empty", amiguard_classify_file_buffer(buf, 0UL),
                  AMIGUARD_FILE_NOT_HUNK);
    expect_status("short", amiguard_classify_file_buffer(buf, 3UL),
                  AMIGUARD_FILE_NOT_HUNK);

    size = make_valid_code(buf);
    expect_status("valid", amiguard_classify_file_buffer(buf, size),
                  AMIGUARD_FILE_VALID_HUNK);

    expect_status("truncated", amiguard_classify_file_buffer(buf, size - 1UL),
                  AMIGUARD_FILE_MALFORMED_HUNK);

    memset(buf, 0, sizeof(buf));
    buf[0] = 0x7f;
    expect_status("not-hunk", amiguard_classify_file_buffer(buf, 4UL),
                  AMIGUARD_FILE_NOT_HUNK);

    expect_status("oversize-policy",
                  amiguard_classify_file_buffer(buf, AMIGUARD_FILE_MAX_SIZE + 1UL),
                  AMIGUARD_FILE_ERROR);

    if (failures != 0)
        return 1;
    puts("file intake tests: PASS");
    return 0;
}
