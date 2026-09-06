#include <exec/io.h>
#include <exec/memory.h>
#include <exec/ports.h>
#include <devices/trackdisk.h>
#include <proto/exec.h>
#include <clib/alib_protos.h>

#include "trackdisk.h"

LONG amiguard_read_bootblock(
    UBYTE unit,
    unsigned char *buffer,
    ULONG buffer_size
)
{
    struct MsgPort *port;
    struct IOExtTD *request;
    LONG error;

    if (buffer == 0 || buffer_size < AMIGUARD_BOOTBLOCK_BYTES) {
        return -1;
    }

    if (unit > AMIGUARD_MAX_FLOPPY_UNIT) {
        return -1;
    }

    port = CreatePort(0, 0);
    if (port == 0) {
        return -1;
    }

    request = (struct IOExtTD *)CreateExtIO(port, sizeof(struct IOExtTD));
    if (request == 0) {
        DeletePort(port);
        return -1;
    }

    error = OpenDevice(
        (STRPTR)TD_NAME,
        (ULONG)unit,
        (struct IORequest *)request,
        0UL
    );
    if (error != 0) {
        DeleteExtIO((struct IORequest *)request);
        DeletePort(port);
        return error;
    }

    request->iotd_Req.io_Command = CMD_READ;
    request->iotd_Req.io_Data = (APTR)buffer;
    request->iotd_Req.io_Length = AMIGUARD_BOOTBLOCK_BYTES;
    request->iotd_Req.io_Offset = 0UL;

    error = DoIO((struct IORequest *)request);
    if (error == 0 && request->iotd_Req.io_Actual != AMIGUARD_BOOTBLOCK_BYTES) {
        error = -1;
    }

    CloseDevice((struct IORequest *)request);
    DeleteExtIO((struct IORequest *)request);
    DeletePort(port);

    return error;
}
