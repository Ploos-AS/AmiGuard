#include <stdio.h>
#include <string.h>

#include "file_signatures.h"

static int expect(int condition, const char *name)
{
    if (!condition) {
        printf("FAIL: %s\n", name);
        return 1;
    }
    return 0;
}

static int write_text_file(const char *path, const char *text)
{
    FILE *fp = fopen(path, "wb");
    if (fp == 0)
        return 0;
    if (fputs(text, fp) == EOF) {
        fclose(fp);
        return 0;
    }
    return fclose(fp) == 0;
}

int main(void)
{
    unsigned char buf[64];
    struct amiguard_file_signature_match match;
    char detail[128];
    const char *runtime_path = "build/runtime-signatures.db";
    const char *invalid_path = "build/runtime-signatures-invalid.db";
    unsigned long builtin_count;
    int failed = 0;

    amiguard_file_signature_use_builtin();
    builtin_count = amiguard_file_signature_count();
    failed |= expect(builtin_count > 0UL, "builtin signature table is available");
    failed |= expect(amiguard_file_signature_database_active() == 0, "builtin table is default");
    failed |= expect(strcmp(amiguard_file_signature_database_source(), "builtin") == 0, "builtin source is reported");

    memset(buf, 0, sizeof(buf));
    memcpy(buf + 4, "AMIGUARD-FILE-TEST", 18);
    match = amiguard_match_file_signature(buf, sizeof(buf));
    failed |= expect(match.matched == 1, "synthetic marker matches");
    failed |= expect(match.test_only == 1, "synthetic marker is test-only");
    failed |= expect(match.name != 0, "match has name");

    buf[10] ^= 1U;
    match = amiguard_match_file_signature(buf, sizeof(buf));
    failed |= expect(match.matched == 0, "changed marker does not match");

    match = amiguard_match_file_signature(buf, 8UL);
    failed |= expect(match.matched == 0, "short buffer is safe");

    match = amiguard_match_file_signature(0, 0UL);
    failed |= expect(match.matched == 0, "null buffer is safe");

    failed |= expect(
        write_text_file(
            runtime_path,
            "AMIGUARD-FILE-SIGDB 1\n"
            "FILE|Runtime.Test.Marker|3|1|52554e54494d45|ffffffffffffff\n"
        ),
        "runtime fixture is written"
    );
    failed |= expect(
        amiguard_file_signature_load_database(runtime_path, detail, sizeof(detail)) == 1,
        "runtime database loads"
    );
    failed |= expect(amiguard_file_signature_database_active() == 1, "runtime database becomes active");
    failed |= expect(amiguard_file_signature_count() == 1UL, "runtime database replaces active table");
    failed |= expect(strcmp(amiguard_file_signature_database_source(), runtime_path) == 0, "runtime source is reported");

    memset(buf, 0, sizeof(buf));
    memcpy(buf + 3, "RUNTIME", 7);
    match = amiguard_match_file_signature(buf, sizeof(buf));
    failed |= expect(match.matched == 1, "runtime signature matches");
    failed |= expect(match.test_only == 1, "runtime test-only flag is preserved");
    failed |= expect(match.name != 0 && strcmp(match.name, "Runtime.Test.Marker") == 0, "runtime name is preserved");

    failed |= expect(
        write_text_file(
            invalid_path,
            "AMIGUARD-FILE-SIGDB 1\n"
            "FILE|Broken|0|0|aa|ffff\n"
        ),
        "invalid runtime fixture is written"
    );
    failed |= expect(
        amiguard_file_signature_load_database(invalid_path, detail, sizeof(detail)) == 0,
        "invalid database is rejected"
    );
    failed |= expect(amiguard_file_signature_database_active() == 1, "failed load preserves prior runtime table");
    failed |= expect(amiguard_file_signature_count() == 1UL, "failed load preserves prior runtime count");

    memset(buf, 0, sizeof(buf));
    memcpy(buf + 3, "RUNTIME", 7);
    match = amiguard_match_file_signature(buf, sizeof(buf));
    failed |= expect(match.matched == 1, "failed load preserves prior matcher state");

    amiguard_file_signature_use_builtin();
    failed |= expect(amiguard_file_signature_database_active() == 0, "builtin fallback can be restored");
    failed |= expect(amiguard_file_signature_count() == builtin_count, "builtin count is restored");

    remove(runtime_path);
    remove(invalid_path);

    if (failed)
        return 1;
    printf("file signature matcher/runtime database tests: PASS\n");
    return 0;
}
