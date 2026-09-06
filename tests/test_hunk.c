#include <stdio.h>
#include <string.h>

#include "hunk.h"

static int failures = 0;

static void expect_result(const char *name, enum amiguard_hunk_result got,
                          enum amiguard_hunk_result expected)
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
    expect_result("short", amiguard_parse_hunk(buf, 3UL), AMIGUARD_HUNK_NOT_HUNK);

    memset(buf, 0, sizeof(buf));
    size = make_valid_code(buf);
    expect_result("valid-code", amiguard_parse_hunk(buf, size), AMIGUARD_HUNK_VALID);

    buf[size - 1] = 0;
    expect_result("truncated-end", amiguard_parse_hunk(buf, size - 1UL), AMIGUARD_HUNK_MALFORMED);

    memset(buf, 0, sizeof(buf));
    size = make_valid_code(buf);
    buf[0] = 0;
    expect_result("not-hunk", amiguard_parse_hunk(buf, size), AMIGUARD_HUNK_NOT_HUNK);

    memset(buf, 0, sizeof(buf));
    size = make_valid_code(buf);
    put_u32(buf, &size, 0UL);
    expect_result("trailing-data", amiguard_parse_hunk(buf, size), AMIGUARD_HUNK_MALFORMED);

    if (failures != 0)
        return 1;
    puts("hunk parser tests: PASS");
    return 0;
}
