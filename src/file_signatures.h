#ifndef AMIGUARD_FILE_SIGNATURES_H
#define AMIGUARD_FILE_SIGNATURES_H

struct amiguard_file_signature {
    const char *name;
    unsigned long offset;
    unsigned int length;
    const unsigned char *pattern;
    const unsigned char *mask;
    int test_only;
};

struct amiguard_file_signature_match {
    int matched;
    int test_only;
    const char *name;
};

struct amiguard_file_signature_match amiguard_match_file_signature(
    const unsigned char *data,
    unsigned long size
);

#endif
