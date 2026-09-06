#ifndef AMIGUARD_SIGNATURES_H
#define AMIGUARD_SIGNATURES_H

struct amiguard_signature {
    const char *name;
    unsigned short offset;
    unsigned char length;
    const unsigned char *pattern;
    const unsigned char *mask;
};

const struct amiguard_signature *amiguard_signatures(unsigned long *count);

#endif
