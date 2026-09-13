#include <exec/libraries.h>
#include <exec/types.h>
#include <proto/exec.h>
#include <inline/macros.h>
#include <stdio.h>

static struct Library *xvsBase;

#define xvsSelfTest() \
    LP0(0x1e, BOOL, xvsSelfTest, \
    , xvsBase)

int main(void)
{
    int ok;

    xvsBase = OpenLibrary((STRPTR)"xvs.library", 33UL);
    if (xvsBase == 0) {
        printf("xvs-open=UNAVAILABLE\n");
        return 20;
    }

    printf("xvs-open=%u.%u\n",
        (unsigned)xvsBase->lib_Version,
        (unsigned)xvsBase->lib_Revision);
    ok = xvsSelfTest() != 0;
    printf("xvs-self-test=%s\n", ok ? "PASS" : "FAIL");
    CloseLibrary(xvsBase);
    xvsBase = 0;
    return ok ? 0 : 20;
}
