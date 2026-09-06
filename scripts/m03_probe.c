/* Qualification-only observer: Exec/DOS 1.x APIs, never opens a disk device. */
#include <exec/execbase.h>
#include <exec/memory.h>
#include <dos/dosextens.h>
#include <proto/exec.h>
#include <proto/dos.h>
#include <stdio.h>

int main(void)
{
    struct Library *version;
    struct Process *process;
    struct CommandLineInterface *cli;
    ULONG chip, fast;
    LONG previous = -1;

    process = (struct Process *)FindTask(0);
    if (process->pr_CLI != 0) {
        cli = (struct CommandLineInterface *)BADDR(process->pr_CLI);
        previous = cli->cli_ReturnCode;
    }
    chip = AvailMem(MEMF_CHIP);
    fast = AvailMem(MEMF_FAST);
    printf("Exec=%u.%u DOS=%u.%u free-chip=%lu free-fast=%lu previous-rc=%ld\n",
        (unsigned)SysBase->LibNode.lib_Version,
        (unsigned)SysBase->LibNode.lib_Revision,
        (unsigned)DOSBase->dl_lib.lib_Version,
        (unsigned)DOSBase->dl_lib.lib_Revision,
        (unsigned long)chip, (unsigned long)fast, (long)previous);
    version = OpenLibrary((STRPTR)"version.library", 0UL);
    if (version != 0) {
        printf("Workbench=%u.%u\n", (unsigned)version->lib_Version,
            (unsigned)version->lib_Revision);
        CloseLibrary(version);
    }
    return 0;
}
