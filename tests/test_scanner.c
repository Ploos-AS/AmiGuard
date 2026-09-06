#include <stdio.h>
#include <string.h>
#include "scanner.h"

static int failures;
static void expect(int ok, const char *name)
{
    if (ok) printf("PASS: %s\n", name);
    else { fprintf(stderr, "FAIL: %s\n", name); ++failures; }
}

int main(void)
{
    unsigned char block[AMIGUARD_BOOTBLOCK_SIZE];
    struct amiguard_detection d;

    memset(block, 0, sizeof(block));
    block[0]='D'; block[1]='O'; block[2]='S';
    d=amiguard_scan_bootblock(block,sizeof(block));
    expect(d.result==AMIGUARD_RESULT_STANDARD,"DOS bootblock");

    memset(block,0,sizeof(block));
    memcpy(block+64,"AMIGUARD",8);
    d=amiguard_scan_bootblock(block,sizeof(block));
    expect(d.result==AMIGUARD_RESULT_INFECTED,"synthetic signature");

    memset(block,0x5a,sizeof(block));
    d=amiguard_scan_bootblock(block,sizeof(block));
    expect(d.result==AMIGUARD_RESULT_UNKNOWN,"unknown bootblock");
    d=amiguard_scan_bootblock(block,100);
    expect(d.result==AMIGUARD_RESULT_ERROR,"short block rejected");

    if (failures) return 1;
    puts("All scanner tests passed.");
    return 0;
}
