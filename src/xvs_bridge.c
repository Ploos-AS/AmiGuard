#include <exec/libraries.h>
#include <exec/types.h>
#include <proto/exec.h>
#include <inline/macros.h>
#include <string.h>

#include "xvs_bridge.h"

#define AMIGUARD_XVS_MIN_VERSION 33
#define AMIGUARD_XVSOBJ_BOOTINFO 1UL
#define AMIGUARD_XVSOBJ_FILEINFO 3UL
#define AMIGUARD_XVSBT_VIRUS 4UL
#define AMIGUARD_XVSFT_DATAVIRUS 4UL
#define AMIGUARD_XVSFT_FILEVIRUS 5UL
#define AMIGUARD_XVSFT_LINKVIRUS 6UL
#define AMIGUARD_BOOTBLOCK_BYTES 1024UL

struct xvsBootInfo {
    APTR xvsbi_Bootblock;
    STRPTR xvsbi_Name;
    UBYTE xvsbi_BootType;
    UBYTE xvsbi_DosType;
    UBYTE xvsbi_ChkSumFlag;
    UBYTE xvsbi_Reserved0;
};

struct xvsFileInfo {
    APTR xvsfi_File;
    ULONG xvsfi_FileLen;
    STRPTR xvsfi_Name;
    UBYTE xvsfi_FileType;
    UBYTE xvsfi_ModifiedFlag;
    UBYTE xvsfi_ErrorCode;
    UBYTE xvsfi_InternalType;
    APTR xvsfi_Fixed;
    ULONG xvsfi_FixedLen;
};

static struct Library *xvsBase;
static char xvs_name[AMIGUARD_XVS_NAME_MAX];

#define xvsSelfTest() \
    LP0(0x1e, BOOL, xvsSelfTest, \
    , xvsBase)

#define xvsAllocObject(objecttype) \
    LP1(0x30, APTR, xvsAllocObject, ULONG, objecttype, d0, \
    , xvsBase)

#define xvsFreeObject(object) \
    LP1NR(0x36, xvsFreeObject, APTR, object, a1, \
    , xvsBase)

#define xvsCheckBootblock(bootinfo) \
    LP1(0x42, ULONG, xvsCheckBootblock, struct xvsBootInfo *, bootinfo, a0, \
    , xvsBase)

#define xvsCheckFile(fileinfo) \
    LP1(0x60, ULONG, xvsCheckFile, struct xvsFileInfo *, fileinfo, a0, \
    , xvsBase)

static struct amiguard_xvs_result make_result(
    enum amiguard_xvs_status status,
    const char *name
)
{
    struct amiguard_xvs_result result;
    result.status = status;
    result.name = name;
    return result;
}

static const char *copy_name(const char *name)
{
    unsigned long n;

    if (name == 0 || name[0] == '\0')
        name = "xvs.library detection";

    n = (unsigned long)strlen(name);
    if (n >= AMIGUARD_XVS_NAME_MAX)
        n = AMIGUARD_XVS_NAME_MAX - 1UL;
    memcpy(xvs_name, name, (size_t)n);
    xvs_name[n] = '\0';
    return xvs_name;
}

static int open_xvs(void)
{
    xvsBase = OpenLibrary((STRPTR)"xvs.library", AMIGUARD_XVS_MIN_VERSION);
    if (xvsBase == 0)
        return 0;
    if (!xvsSelfTest()) {
        CloseLibrary(xvsBase);
        xvsBase = 0;
        return -1;
    }
    return 1;
}

static void close_xvs(void)
{
    if (xvsBase != 0) {
        CloseLibrary(xvsBase);
        xvsBase = 0;
    }
}

struct amiguard_xvs_result amiguard_xvs_scan_file_buffer(
    const unsigned char *data,
    unsigned long size
)
{
    struct xvsFileInfo *info;
    ULONG type;
    int opened;
    const char *name;

    if (data == 0 || size == 0UL)
        return make_result(AMIGUARD_XVS_ERROR, 0);

    opened = open_xvs();
    if (opened == 0)
        return make_result(AMIGUARD_XVS_UNAVAILABLE, 0);
    if (opened < 0)
        return make_result(AMIGUARD_XVS_ERROR, 0);

    info = (struct xvsFileInfo *)xvsAllocObject(AMIGUARD_XVSOBJ_FILEINFO);
    if (info == 0) {
        close_xvs();
        return make_result(AMIGUARD_XVS_ERROR, 0);
    }

    info->xvsfi_File = (APTR)data;
    info->xvsfi_FileLen = (ULONG)size;
    type = xvsCheckFile(info);

    if (type == AMIGUARD_XVSFT_DATAVIRUS ||
        type == AMIGUARD_XVSFT_FILEVIRUS ||
        type == AMIGUARD_XVSFT_LINKVIRUS) {
        name = copy_name((const char *)info->xvsfi_Name);
        xvsFreeObject(info);
        close_xvs();
        return make_result(AMIGUARD_XVS_DETECTED, name);
    }

    xvsFreeObject(info);
    close_xvs();
    return make_result(AMIGUARD_XVS_CLEAN, 0);
}

struct amiguard_xvs_result amiguard_xvs_scan_bootblock(
    const unsigned char *data,
    unsigned long size
)
{
    struct xvsBootInfo *info;
    ULONG type;
    int opened;
    const char *name;

    if (data == 0 || size != AMIGUARD_BOOTBLOCK_BYTES)
        return make_result(AMIGUARD_XVS_ERROR, 0);

    opened = open_xvs();
    if (opened == 0)
        return make_result(AMIGUARD_XVS_UNAVAILABLE, 0);
    if (opened < 0)
        return make_result(AMIGUARD_XVS_ERROR, 0);

    info = (struct xvsBootInfo *)xvsAllocObject(AMIGUARD_XVSOBJ_BOOTINFO);
    if (info == 0) {
        close_xvs();
        return make_result(AMIGUARD_XVS_ERROR, 0);
    }

    info->xvsbi_Bootblock = (APTR)data;
    type = xvsCheckBootblock(info);

    if (type == AMIGUARD_XVSBT_VIRUS ||
        info->xvsbi_BootType == (UBYTE)AMIGUARD_XVSBT_VIRUS) {
        name = copy_name((const char *)info->xvsbi_Name);
        xvsFreeObject(info);
        close_xvs();
        return make_result(AMIGUARD_XVS_DETECTED, name);
    }

    xvsFreeObject(info);
    close_xvs();
    return make_result(AMIGUARD_XVS_CLEAN, 0);
}
