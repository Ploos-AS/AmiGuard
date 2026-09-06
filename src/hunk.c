#include "hunk.h"

#define HUNK_HEADER 1011UL
#define HUNK_CODE 1001UL
#define HUNK_DATA 1002UL
#define HUNK_BSS 1003UL
#define HUNK_RELOC32 1004UL
#define HUNK_SYMBOL 1008UL
#define HUNK_DEBUG 1009UL
#define HUNK_END 1010UL

static int read_u32(const unsigned char *data, unsigned long size,
                    unsigned long *offset, unsigned long *value)
{
    unsigned long pos = *offset;
    if (pos > size || size - pos < 4UL)
        return 0;
    *value = ((unsigned long)data[pos] << 24)
           | ((unsigned long)data[pos + 1] << 16)
           | ((unsigned long)data[pos + 2] << 8)
           | (unsigned long)data[pos + 3];
    *offset = pos + 4UL;
    return 1;
}

static int skip_longs(unsigned long count, unsigned long size,
                      unsigned long *offset)
{
    unsigned long bytes;
    if (count > (~0UL / 4UL))
        return 0;
    bytes = count * 4UL;
    if (*offset > size || size - *offset < bytes)
        return 0;
    *offset += bytes;
    return 1;
}

static int skip_name_table(const unsigned char *data, unsigned long size,
                           unsigned long *offset)
{
    unsigned long words;
    for (;;) {
        if (!read_u32(data, size, offset, &words))
            return 0;
        if (words == 0UL)
            return 1;
        if (!skip_longs(words, size, offset))
            return 0;
    }
}

static int skip_reloc32(const unsigned char *data, unsigned long size,
                        unsigned long *offset)
{
    unsigned long count;
    unsigned long target;
    for (;;) {
        if (!read_u32(data, size, offset, &count))
            return 0;
        if (count == 0UL)
            return 1;
        if (!read_u32(data, size, offset, &target))
            return 0;
        (void)target;
        if (!skip_longs(count, size, offset))
            return 0;
    }
}

static int skip_symbol_table(const unsigned char *data, unsigned long size,
                             unsigned long *offset)
{
    unsigned long words;
    unsigned long value;
    for (;;) {
        if (!read_u32(data, size, offset, &words))
            return 0;
        if (words == 0UL)
            return 1;
        if (!skip_longs(words, size, offset))
            return 0;
        if (!read_u32(data, size, offset, &value))
            return 0;
        (void)value;
    }
}

enum amiguard_hunk_result amiguard_parse_hunk(const unsigned char *data,
                                                unsigned long size)
{
    unsigned long offset = 0UL;
    unsigned long value;
    unsigned long table_size;
    unsigned long first_hunk;
    unsigned long last_hunk;
    unsigned long i;
    int saw_hunk = 0;

    if (data == 0 || size < 4UL)
        return AMIGUARD_HUNK_NOT_HUNK;
    if (!read_u32(data, size, &offset, &value))
        return AMIGUARD_HUNK_NOT_HUNK;
    if (value != HUNK_HEADER)
        return AMIGUARD_HUNK_NOT_HUNK;

    if (!skip_name_table(data, size, &offset))
        return AMIGUARD_HUNK_MALFORMED;
    if (!read_u32(data, size, &offset, &table_size)
        || !read_u32(data, size, &offset, &first_hunk)
        || !read_u32(data, size, &offset, &last_hunk))
        return AMIGUARD_HUNK_MALFORMED;
    if (table_size == 0UL || last_hunk < first_hunk)
        return AMIGUARD_HUNK_MALFORMED;
    if (last_hunk - first_hunk + 1UL != table_size)
        return AMIGUARD_HUNK_MALFORMED;
    if (!skip_longs(table_size, size, &offset))
        return AMIGUARD_HUNK_MALFORMED;

    for (i = 0UL; i < table_size; ++i) {
        int ended = 0;
        while (!ended) {
            unsigned long hunk_type;
            unsigned long count;
            if (!read_u32(data, size, &offset, &hunk_type))
                return AMIGUARD_HUNK_MALFORMED;
            hunk_type &= 0x3fffffffUL;
            switch (hunk_type) {
            case HUNK_CODE:
            case HUNK_DATA:
                if (!read_u32(data, size, &offset, &count)
                    || !skip_longs(count, size, &offset))
                    return AMIGUARD_HUNK_MALFORMED;
                saw_hunk = 1;
                break;
            case HUNK_BSS:
                if (!read_u32(data, size, &offset, &count))
                    return AMIGUARD_HUNK_MALFORMED;
                saw_hunk = 1;
                break;
            case HUNK_RELOC32:
                if (!skip_reloc32(data, size, &offset))
                    return AMIGUARD_HUNK_MALFORMED;
                break;
            case HUNK_SYMBOL:
                if (!skip_symbol_table(data, size, &offset))
                    return AMIGUARD_HUNK_MALFORMED;
                break;
            case HUNK_DEBUG:
                if (!read_u32(data, size, &offset, &count)
                    || !skip_longs(count, size, &offset))
                    return AMIGUARD_HUNK_MALFORMED;
                break;
            case HUNK_END:
                ended = 1;
                break;
            default:
                return AMIGUARD_HUNK_MALFORMED;
            }
        }
    }

    if (!saw_hunk)
        return AMIGUARD_HUNK_MALFORMED;
    if (offset != size)
        return AMIGUARD_HUNK_MALFORMED;
    return AMIGUARD_HUNK_VALID;
}
