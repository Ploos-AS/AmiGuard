#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "file_signatures.h"

#include "file_signatures_generated.inc"

#define AMIGUARD_RUNTIME_MAX_SIGNATURES 64U
#define AMIGUARD_RUNTIME_MAX_PATTERN 64U
#define AMIGUARD_RUNTIME_MAX_NAME 80U
#define AMIGUARD_RUNTIME_LINE_MAX 512U
#define AMIGUARD_RUNTIME_SOURCE_MAX 256U

struct runtime_signature_slot {
    char name[AMIGUARD_RUNTIME_MAX_NAME];
    unsigned char pattern[AMIGUARD_RUNTIME_MAX_PATTERN];
    unsigned char mask[AMIGUARD_RUNTIME_MAX_PATTERN];
    unsigned long offset;
    unsigned int length;
    int test_only;
};

static struct runtime_signature_slot runtime_storage[AMIGUARD_RUNTIME_MAX_SIGNATURES];
static struct runtime_signature_slot staging_storage[AMIGUARD_RUNTIME_MAX_SIGNATURES];
static struct amiguard_file_signature runtime_table[AMIGUARD_RUNTIME_MAX_SIGNATURES];
static unsigned long runtime_count = 0UL;
static int runtime_active = 0;
static char runtime_source[AMIGUARD_RUNTIME_SOURCE_MAX] = "builtin";

static void set_detail(char *detail, unsigned long detail_size, const char *text)
{
    if (detail == 0 || detail_size == 0UL)
        return;
    if (text == 0)
        text = "";
    strncpy(detail, text, (size_t)(detail_size - 1UL));
    detail[detail_size - 1UL] = '\0';
}

static int hex_value(int ch)
{
    if (ch >= '0' && ch <= '9')
        return ch - '0';
    ch = tolower((unsigned char)ch);
    if (ch >= 'a' && ch <= 'f')
        return ch - 'a' + 10;
    return -1;
}

static int decode_hex(
    const char *text,
    unsigned char *out,
    unsigned int out_size,
    unsigned int *decoded_length
)
{
    unsigned long text_length;
    unsigned long i;
    unsigned int count;

    if (text == 0 || out == 0 || decoded_length == 0)
        return 0;

    text_length = (unsigned long)strlen(text);
    if (text_length == 0UL || (text_length & 1UL) != 0UL)
        return 0;
    if ((text_length / 2UL) > (unsigned long)out_size)
        return 0;

    count = (unsigned int)(text_length / 2UL);
    for (i = 0UL; i < text_length; i += 2UL) {
        int hi = hex_value((unsigned char)text[i]);
        int lo = hex_value((unsigned char)text[i + 1UL]);
        if (hi < 0 || lo < 0)
            return 0;
        out[i / 2UL] = (unsigned char)((hi << 4) | lo);
    }

    *decoded_length = count;
    return 1;
}

static void bind_runtime_entry(unsigned long index)
{
    runtime_table[index].name = runtime_storage[index].name;
    runtime_table[index].offset = runtime_storage[index].offset;
    runtime_table[index].length = runtime_storage[index].length;
    runtime_table[index].pattern = runtime_storage[index].pattern;
    runtime_table[index].mask = runtime_storage[index].mask;
    runtime_table[index].test_only = runtime_storage[index].test_only;
}

static int parse_record(
    char *line,
    struct runtime_signature_slot *slot,
    char *detail,
    unsigned long detail_size
)
{
    char *kind;
    char *name;
    char *offset_text;
    char *test_only_text;
    char *pattern_text;
    char *mask_text;
    char *extra;
    char *end;
    unsigned long offset;
    unsigned long test_only;
    unsigned int pattern_length;
    unsigned int mask_length;

    kind = strtok(line, "|");
    name = strtok(0, "|");
    offset_text = strtok(0, "|");
    test_only_text = strtok(0, "|");
    pattern_text = strtok(0, "|");
    mask_text = strtok(0, "|\r\n");
    extra = strtok(0, "|");

    if (kind == 0 || name == 0 || offset_text == 0 || test_only_text == 0 ||
        pattern_text == 0 || mask_text == 0 || extra != 0) {
        set_detail(detail, detail_size, "invalid signature record");
        return 0;
    }
    if (strcmp(kind, "FILE") != 0) {
        set_detail(detail, detail_size, "unsupported signature kind");
        return 0;
    }
    if (name[0] == '\0' || strlen(name) >= AMIGUARD_RUNTIME_MAX_NAME) {
        set_detail(detail, detail_size, "invalid signature name");
        return 0;
    }

    offset = strtoul(offset_text, &end, 10);
    if (end == offset_text || *end != '\0') {
        set_detail(detail, detail_size, "invalid signature offset");
        return 0;
    }

    test_only = strtoul(test_only_text, &end, 10);
    if (end == test_only_text || *end != '\0' || test_only > 1UL) {
        set_detail(detail, detail_size, "invalid test-only flag");
        return 0;
    }

    if (!decode_hex(pattern_text, slot->pattern, AMIGUARD_RUNTIME_MAX_PATTERN, &pattern_length)) {
        set_detail(detail, detail_size, "invalid signature pattern");
        return 0;
    }
    if (!decode_hex(mask_text, slot->mask, AMIGUARD_RUNTIME_MAX_PATTERN, &mask_length)) {
        set_detail(detail, detail_size, "invalid signature mask");
        return 0;
    }
    if (pattern_length != mask_length) {
        set_detail(detail, detail_size, "pattern/mask length mismatch");
        return 0;
    }

    strcpy(slot->name, name);
    slot->offset = offset;
    slot->length = pattern_length;
    slot->test_only = (int)test_only;
    return 1;
}

static int masked_match(
    const unsigned char *data,
    const struct amiguard_file_signature *sig
)
{
    unsigned int i;
    for (i = 0U; i < sig->length; ++i) {
        unsigned char mask = sig->mask[i];
        if ((data[sig->offset + i] & mask) != (sig->pattern[i] & mask))
            return 0;
    }
    return 1;
}

const struct amiguard_file_signature *amiguard_file_signatures(unsigned long *count)
{
    if (runtime_active) {
        if (count != 0)
            *count = runtime_count;
        if (runtime_count == 0UL)
            return 0;
        return runtime_table;
    }

    if (count != 0)
        *count = (unsigned long)(sizeof(file_signatures) / sizeof(file_signatures[0]));
    return file_signatures;
}

unsigned long amiguard_file_signature_count(void)
{
    unsigned long count = 0UL;
    (void)amiguard_file_signatures(&count);
    return count;
}

int amiguard_file_signature_load_database(
    const char *path,
    char *detail,
    unsigned long detail_size
)
{
    FILE *fp;
    char line[AMIGUARD_RUNTIME_LINE_MAX];
    unsigned long count = 0UL;
    unsigned long i;
    int saw_header = 0;

    set_detail(detail, detail_size, "");
    if (path == 0 || path[0] == '\0') {
        set_detail(detail, detail_size, "database path required");
        return 0;
    }

    fp = fopen(path, "rb");
    if (fp == 0) {
        set_detail(detail, detail_size, "cannot open signature database");
        return 0;
    }

    while (fgets(line, sizeof(line), fp) != 0) {
        size_t length = strlen(line);
        char *start = line;

        if (length == sizeof(line) - 1U && line[length - 1U] != '\n') {
            fclose(fp);
            set_detail(detail, detail_size, "signature database line too long");
            return 0;
        }

        while (*start != '\0' && isspace((unsigned char)*start))
            ++start;
        if (*start == '\0' || *start == '#')
            continue;

        if (!saw_header) {
            char *endline = strpbrk(start, "\r\n");
            if (endline != 0)
                *endline = '\0';
            if (strcmp(start, "AMIGUARD-FILE-SIGDB 1") != 0) {
                fclose(fp);
                set_detail(detail, detail_size, "invalid signature database header");
                return 0;
            }
            saw_header = 1;
            continue;
        }

        if (count >= AMIGUARD_RUNTIME_MAX_SIGNATURES) {
            fclose(fp);
            set_detail(detail, detail_size, "too many signatures in database");
            return 0;
        }

        memset(&staging_storage[count], 0, sizeof(staging_storage[count]));
        if (!parse_record(start, &staging_storage[count], detail, detail_size)) {
            fclose(fp);
            return 0;
        }
        ++count;
    }

    if (ferror(fp)) {
        fclose(fp);
        set_detail(detail, detail_size, "error reading signature database");
        return 0;
    }
    fclose(fp);

    if (!saw_header) {
        set_detail(detail, detail_size, "signature database header missing");
        return 0;
    }
    if (count == 0UL) {
        set_detail(detail, detail_size, "signature database is empty");
        return 0;
    }

    for (i = 0UL; i < count; ++i) {
        runtime_storage[i] = staging_storage[i];
        bind_runtime_entry(i);
    }
    runtime_count = count;
    runtime_active = 1;
    strncpy(runtime_source, path, sizeof(runtime_source) - 1U);
    runtime_source[sizeof(runtime_source) - 1U] = '\0';
    set_detail(detail, detail_size, "runtime signature database loaded");
    return 1;
}

void amiguard_file_signature_use_builtin(void)
{
    runtime_active = 0;
    runtime_count = 0UL;
    strcpy(runtime_source, "builtin");
}

int amiguard_file_signature_database_active(void)
{
    return runtime_active;
}

const char *amiguard_file_signature_database_source(void)
{
    return runtime_source;
}

struct amiguard_file_signature_match amiguard_match_file_signature(
    const unsigned char *data,
    unsigned long size
)
{
    struct amiguard_file_signature_match result;
    unsigned long i;
    unsigned long count = 0UL;
    const struct amiguard_file_signature *signatures = amiguard_file_signatures(&count);

    result.matched = 0;
    result.test_only = 0;
    result.name = 0;

    if (data == 0 || signatures == 0)
        return result;

    for (i = 0UL; i < count; ++i) {
        const struct amiguard_file_signature *sig = &signatures[i];
        if (sig->offset > size)
            continue;
        if ((unsigned long)sig->length > size - sig->offset)
            continue;
        if (masked_match(data, sig)) {
            result.matched = 1;
            result.test_only = sig->test_only;
            result.name = sig->name;
            return result;
        }
    }

    return result;
}
