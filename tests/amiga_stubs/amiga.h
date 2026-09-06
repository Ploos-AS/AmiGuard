#ifndef AMIGUARD_TEST_AMIGA_H
#define AMIGUARD_TEST_AMIGA_H
/* Only the fields used by trackdisk.c; this tests control flow, not the ABI. */
typedef unsigned char UBYTE;
typedef unsigned long ULONG;
typedef long LONG;
typedef void *APTR;
typedef char *STRPTR;
struct MsgPort { int unused; };
struct IORequest { int unused; };
struct IOStdReq {
    unsigned short io_Command;
    APTR io_Data;
    ULONG io_Length, io_Offset, io_Actual;
};
struct IOExtTD { struct IOStdReq iotd_Req; };
#define TD_NAME "trackdisk.device"
#define CMD_READ 2
struct MsgPort *CreatePort(STRPTR name, LONG priority);
APTR CreateExtIO(struct MsgPort *port, ULONG size);
void DeletePort(struct MsgPort *port);
void DeleteExtIO(struct IORequest *request);
LONG OpenDevice(STRPTR name, ULONG unit, struct IORequest *request, ULONG flags);
LONG DoIO(struct IORequest *request);
void CloseDevice(struct IORequest *request);
#endif
