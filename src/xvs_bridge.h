#ifndef AMIGUARD_XVS_BRIDGE_H
#define AMIGUARD_XVS_BRIDGE_H

#define AMIGUARD_XVS_NAME_MAX 96

enum amiguard_xvs_status {
    AMIGUARD_XVS_UNAVAILABLE = 0,
    AMIGUARD_XVS_CLEAN = 1,
    AMIGUARD_XVS_DETECTED = 2,
    AMIGUARD_XVS_ERROR = 3
};

struct amiguard_xvs_result {
    enum amiguard_xvs_status status;
    const char *name;
};

struct amiguard_xvs_result amiguard_xvs_scan_file_buffer(
    const unsigned char *data,
    unsigned long size
);

struct amiguard_xvs_result amiguard_xvs_scan_bootblock(
    const unsigned char *data,
    unsigned long size
);

#endif
