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

int main(void)
{
    unsigned char buf[64];
    struct amiguard_file_signature_match match;
    int failed = 0;

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

    if (failed)
        return 1;
    printf("file signature matcher tests: PASS\n");
    return 0;
}
