#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

RUN = Path("/tmp/amiguard-v010-native-95ea949")
REPO = Path("/home/pgo/Projects/Ploos-AS/AmiGuard")
EICAR = Path("/home/pgo/Downloads/eicar.com.txt")
XVS = Path("/home/pgo/Documents/FS-UAE/Hard Drives/Work/Install/xvs/libs/xvs.library")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


subprocess.run([
    "/opt/amiga/bin/m68k-amigaos-gcc",
    "-O2", "-Wall", "-Wextra", "-Werror", "-m68000", "-mcrt=nix13",
    str(RUN / "xvs_probe.c"), "-o", str(RUN / "work/XVSCheck")
], check=True)

fixtures = RUN / "fixtures"
fixtures.mkdir()
eicar = EICAR.read_bytes()
assert len(eicar) == 68
(fixtures / "eicar.com.txt").write_bytes(eicar)
(fixtures / "plain.txt").write_bytes(b"Harmless AmiGuard v0.1.0 qualification fixture.\n")
(fixtures / "xvs-eicar-wrapped.bin").write_bytes(b"\0\0\0\0" + eicar)
for path in fixtures.iterdir():
    path.chmod(0o444)


def stage(work, name, command):
    (work / name).write_text(
        "FailAt 21\n" + command + f"\nProbe >AGTest:{name}-probe.log\n"
        f"Type AGTest:{name}.log\nEcho >AGTest:{name}.done \"RETURNED\"\n"
        f"Echo \"{name.upper()} RETURNED\"\n"
    )


template = RUN / "work"
setup = template / "setup"
setup.write_text(setup.read_text().replace(
    "Assign T: RAM:\n",
    "Assign T: RAM:\nAssign LIBS: AGTest:libs\n"
).replace(
    "Type AGTest:start.log\n",
    "Type AGTest:start.log\nType AGTest:start-probe.log\n"
))
stage(template, "banner", "AmiGuard >AGTest:banner.log")
stage(template, "bootblock", "AmiGuard >AGTest:bootblock.log DF0:")
stage(template, "fileplain", "AmiGuard >AGTest:fileplain.log FILE AGFiles:plain.txt")
stage(template, "eicar", "AmiGuard >AGTest:eicar.log FILE AGFiles:eicar.com.txt")
stage(template, "xvswrapped", "AmiGuard >AGTest:xvswrapped.log FILE AGFiles:xvs-eicar-wrapped.bin")
stage(template, "xvsopen", "XVSCheck >AGTest:xvsopen.log")
stage(template, "post", "Dir >AGTest:post.log DF0:")

base_config = (RUN / "runtime.fs-uae").read_text()
for mode in ("absent", "present"):
    work = RUN / f"work-{mode}"
    shutil.copytree(template, work)
    if mode == "present":
        shutil.copyfile(XVS, work / "libs/xvs.library")
        (work / "libs/xvs.library").chmod(0o644)
    assert (work / "libs/xvs.library").exists() == (mode == "present")
    config = base_config.replace(
        f"base_dir = {RUN}/fsuae", f"base_dir = {RUN}/fsuae-{mode}"
    ).replace(
        f"hard_drive_0 = {template}", f"hard_drive_0 = {work}"
    ).replace(
        f"screenshots_output_dir = {RUN}/screenshots",
        f"screenshots_output_dir = {RUN}/screenshots-{mode}"
    )
    config += (
        f"\nhard_drive_1 = {fixtures}\n"
        "hard_drive_1_label = AGFiles\n"
        "hard_drive_1_read_only = 1\n"
    )
    (RUN / f"screenshots-{mode}").mkdir()
    (RUN / f"runtime-{mode}.fs-uae").write_text(config)
    (RUN / f"evidence/{mode}").mkdir()
    shutil.copyfile(
        RUN / f"runtime-{mode}.fs-uae",
        RUN / f"evidence/{mode}/runtime.fs-uae"
    )

manifest_path = RUN / "evidence/manifest.json"
manifest = json.loads(manifest_path.read_text())
manifest.update({
    "qualification": "AmiGuard v0.1.0 native release candidate",
    "build_command": "make CC=/opt/amiga/bin/m68k-amigaos-gcc",
    "native_flags": "-DAMIGUARD_NATIVE_XVS=1 -m68000 -mcrt=nix13",
    "fs_uae_version": subprocess.check_output(["fs-uae", "--version"], text=True).strip(),
    "file_before": {path.name: digest(path) for path in sorted(fixtures.iterdir())},
    "xvs_local_source": str(XVS),
    "xvs_sha256": digest(XVS),
    "xvs_bytes": XVS.stat().st_size,
    "xvs_staged_sha256": digest(RUN / "work-present/libs/xvs.library"),
    "xvs_absent_verified": not (RUN / "work-absent/libs/xvs.library").exists(),
})
manifest["original_sha256"][str(EICAR)] = digest(EICAR)
manifest["original_sha256"][str(XVS)] = digest(XVS)
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
