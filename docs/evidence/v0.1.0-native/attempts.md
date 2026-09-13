# Disposable harness attempt record

No AmiGuard runtime or detection gate was hidden or waived. The following
pre-final-run harness/setup issues were diagnosed in disposable state:

1. The first absent-XVS run used scenario name `xvsprobe` and helper binary
   name `XVSProbe`. Amiga's case-insensitive lookup made the scenario recurse.
   The helper was renamed `XVSCheck`, old completion markers were archived,
   and the entire absent-XVS session was rerun successfully.
2. The first present-XVS run incorrectly required a four-byte-prefixed EICAR
   file to be recognized by xvs. xvs correctly returned no detection. The
   non-authoritative experimental expectation was removed; the required
   open/self-test gate and normal AmiGuard behavior remained mandatory.
3. One retry stopped when desktop focus changed between a command and its
   screenshot. The existing safety check sent no input to another window.
   Limited focus retry was added and the whole present-XVS session was rerun.
4. The next run showed `xvs-open=UNAVAILABLE` because `LIBS:` still pointed to
   the Workbench floppy rather than disposable `AGTest:libs`. The present-XVS
   setup was corrected to assign `LIBS: AGTest:libs`.
5. FS-UAE then logged `my_open ... xvs.library, 2`: the disposable library was
   mode 0444 on a writable directory mount. Its disposable copy was changed to
   normal mode 0644; the original library was never changed.
6. A partially started stale-marker run during that correction was explicitly
   interrupted and not used as evidence.

The final present-XVS run began with no old `.done` or output logs, executed
all gates from startup through the post-scan directory listing, and quit
normally. Only the final successful absent/present logs and screenshots are in
the qualification evidence directories.
