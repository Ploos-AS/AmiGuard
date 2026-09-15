#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "amiga.h"
#include "trackdisk.h"

static struct MsgPort port;
static struct IOExtTD request;
static unsigned char block[4096];
static int fail_port, fail_request, opened, reads, closed, ports, requests;
static LONG open_error, read_error;
static ULONG actual;
static ULONG expected_length, expected_offset;

struct MsgPort *CreatePort(STRPTR name, LONG priority)
{
    assert(name == 0 && priority == 0);
    if (fail_port) return 0;
    ++ports;
    return &port;
}
APTR CreateExtIO(struct MsgPort *p, ULONG size)
{
    assert(p == &port && size == sizeof(request));
    if (fail_request) return 0;
    memset(&request, 0, sizeof(request));
    ++requests;
    return &request;
}
void DeletePort(struct MsgPort *p) { assert(p == &port); --ports; }
void DeleteExtIO(struct IORequest *r) { assert(r == (void *)&request); --requests; }
LONG OpenDevice(STRPTR name, ULONG unit, struct IORequest *r, ULONG flags)
{
    assert(strcmp(name, "trackdisk.device") == 0);
    assert(unit == 0 && r == (void *)&request && flags == 0);
    ++opened;
    return open_error;
}
LONG DoIO(struct IORequest *r)
{
    assert(r == (void *)&request);
    assert(request.iotd_Req.io_Command == CMD_READ);
    assert(request.iotd_Req.io_Length == expected_length);
    assert(request.iotd_Req.io_Offset == expected_offset);
    assert(request.iotd_Req.io_Data == block);
    request.iotd_Req.io_Actual = actual;
    ++reads;
    return read_error;
}
void CloseDevice(struct IORequest *r) { assert(r == (void *)&request); ++closed; }

static void reset(ULONG length, ULONG offset)
{
    assert(ports == 0 && requests == 0);
    fail_port = fail_request = opened = reads = closed = 0;
    open_error = read_error = 0;
    actual = length;
    expected_length = length;
    expected_offset = offset;
}

int main(void)
{
    int i;
    reset(1024, 0);
    assert(amiguard_read_bootblock(4, block, 1024) != 0);
    assert(amiguard_read_bootblock(0, 0, 1024) != 0);
    assert(amiguard_read_bootblock(0, block, 1023) != 0);
    assert(opened == 0 && reads == 0);

    reset(4096, 4096);
    assert(amiguard_read_raw_region(0, 4096, block, 4096, AMIGUARD_DD_FLOPPY_BYTES) == 0);
    assert(opened == 1 && reads == 1 && closed == 1);

    reset(512, 0);
    assert(amiguard_read_raw_region(0, 1, block, 512, AMIGUARD_DD_FLOPPY_BYTES) != 0);
    assert(amiguard_read_raw_region(0, 0, block, 513, AMIGUARD_DD_FLOPPY_BYTES) != 0);
    assert(amiguard_read_raw_region(0, AMIGUARD_DD_FLOPPY_BYTES, block, 512, AMIGUARD_DD_FLOPPY_BYTES) != 0);
    assert(opened == 0 && reads == 0);

    reset(1024, 0); fail_port = 1;
    assert(amiguard_read_bootblock(0, block, 1024) != 0);
    reset(1024, 0); fail_request = 1;
    assert(amiguard_read_bootblock(0, block, 1024) != 0);
    reset(1024, 0); open_error = 5;
    assert(amiguard_read_bootblock(0, block, 1024) == 5);
    assert(reads == 0 && closed == 0);
    reset(1024, 0); read_error = 29;
    assert(amiguard_read_bootblock(0, block, 1024) == 29);
    assert(reads == 1 && closed == 1);
    reset(1024, 0); actual = 512;
    assert(amiguard_read_bootblock(0, block, 1024) != 0);
    for (i = 0; i < 10; ++i) {
        reset(1024, 0);
        assert(amiguard_read_bootblock(0, block, 1024) == 0);
        assert(opened == 1 && reads == 1 && closed == 1);
    }
    reset(1024, 0);
    puts("PASS: trackdisk bounded raw reads, validation and cleanup paths");
    return 0;
}
