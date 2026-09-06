#ifndef AMIGUARD_SCANNER_H
#define AMIGUARD_SCANNER_H

#define AMIGUARD_BOOTBLOCK_SIZE 1024U

enum amiguard_result {
    AMIGUARD_RESULT_ERROR = -1,
    AMIGUARD_RESULT_UNKNOWN = 0,
    AMIGUARD_RESULT_STANDARD = 1,
    AMIGUARD_RESULT_INFECTED = 2
};

struct amiguard_detection {
    enum amiguard_result result;
    const char *name;
};

struct amiguard_detection amiguard_scan_bootblock(const unsigned char *data, unsigned long size);

#endif
