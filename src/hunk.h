#ifndef AMIGUARD_HUNK_H
#define AMIGUARD_HUNK_H

enum amiguard_hunk_result {
    AMIGUARD_HUNK_MALFORMED = -1,
    AMIGUARD_HUNK_NOT_HUNK = 0,
    AMIGUARD_HUNK_VALID = 1
};

enum amiguard_hunk_result amiguard_parse_hunk(const unsigned char *data, unsigned long size);

#endif
