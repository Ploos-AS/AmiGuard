#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

RUN = Path("/tmp/amiguard-v010-native-95ea949")
REPO = Path("/home/pgo/Projects/Ploos-AS/AmiGuard")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def execute(mode):
    work = RUN / f"work-{mode}"
    evidence = RUN / f"evidence/{mode}"
    screenshots = RUN / f"screenshots-{mode}"
    config = RUN / f"runtime-{mode}.fs-uae"
    console = (evidence / "console.log").open("w")
    emulator = subprocess.Popen(["fs-uae", str(config)], stdout=console, stderr=subprocess.STDOUT)

    def gui(*args):
        last = None
        for attempt in range(5):
            try:
                command([
                    sys.executable, REPO / "scripts/m03_gui.py",
                    "--screenshots-dir", screenshots, *args
                ], cwd=REPO)
                return
            except subprocess.CalledProcessError as error:
                last = error
                if attempt == 4:
                    raise
                time.sleep(1)
        raise last

    def wait_stage(name, timeout=180):
        deadline = time.monotonic() + timeout
        marker = work / f"{name}.done"
        while time.monotonic() < deadline:
            if emulator.poll() is not None:
                raise RuntimeError(f"FS-UAE exited during {name}: {emulator.returncode}")
            if marker.exists() and marker.read_text().strip() == "RETURNED":
                time.sleep(1)
                return
            time.sleep(0.5)
        raise RuntimeError(f"Timeout during {name}; visible emulator remains open")

    def stage(name):
        gui("type", f"Execute AGTest:{name}\n")
        wait_stage(name)
        gui("shot", str(evidence / f"{name}.png"))

    def output(name):
        return (work / f"{name}.log").read_text(errors="replace")

    def probe(name):
        return (work / f"{name}-probe.log").read_text(errors="replace")

    def require(name, expected, code):
        text = output(name)
        previous = probe(name)
        if expected not in text or f"previous-rc={code}\n" not in previous:
            raise RuntimeError(f"Unexpected {name}: output={text!r}, probe={previous!r}")
        return text

    completed = False
    checks = {}
    try:
        wait_stage("setup")
        gui("shot", str(evidence / "startup.png"))
        start = output("start")
        identity = probe("start")
        if "AmiGuard 0.0.2 M2.3" not in start or "Usage: AmiGuard" not in start:
            raise RuntimeError(f"Startup/banner failure: {start!r}")
        if "previous-rc=10\n" not in identity:
            raise RuntimeError(f"Startup return code failure: {identity!r}")
        if "Exec=33." not in identity or "Workbench=33." not in identity:
            raise RuntimeError(f"Not a Kickstart/Workbench 1.2 runtime: {identity!r}")
        if "free-fast=0" not in identity:
            raise RuntimeError(f"Unexpected Fast RAM: {identity!r}")
        checks["startup_banner_cli"] = "PASS"
        checks["kickstart_workbench_1_2"] = "PASS"
        checks["zero_fast_ram"] = "PASS"

        stage("banner")
        require("banner", "Usage: AmiGuard", 10)
        checks["banner_cli_repeat"] = "PASS"

        stage("bootblock")
        boot = require("bootblock", "STANDARD: Amiga DOS bootblock (valid checksum)", 0)
        if "Reading DF0: bootblock (read-only)" not in boot or "read 1024 bytes at offset 0" not in boot:
            raise RuntimeError(f"Missing read-only bootblock evidence: {boot!r}")
        if "INFECTED" in boot:
            raise RuntimeError(f"False INFECTED bootblock verdict: {boot!r}")
        checks["df0_read_only_standard_not_infected"] = "PASS"

        stage("fileplain")
        plain = require("fileplain", "NOT-HUNK: not an Amiga HUNK file", 0)
        if "Reading file read-only: AGFiles:plain.txt" not in plain or "INFECTED" in plain:
            raise RuntimeError(f"Plain file gate failure: {plain!r}")
        checks["file_path_read_only"] = "PASS"

        stage("eicar")
        eicar = require("eicar", "TEST-SIGNATURE: EICAR Standard Anti-Virus Test File (68 bytes)", 0)
        if "INFECTED" in eicar or "XVS-DETECTED" in eicar:
            raise RuntimeError(f"Safe-test verdict contamination: {eicar!r}")
        checks["harmless_test_signature_never_infected"] = "PASS"

        stage("xvsopen")
        xvs = output("xvsopen")
        if mode == "absent":
            require("xvsopen", "xvs-open=UNAVAILABLE", 20)
            checks["xvs_absent_startup_independent"] = "PASS"
        else:
            require("xvsopen", "xvs-open=33.49", 0)
            if "xvs-self-test=PASS" not in xvs:
                raise RuntimeError(f"xvs self-test failed: {xvs!r}")
            checks["xvs_optional_open_and_self_test"] = "PASS"

        stage("xvswrapped")
        wrapped = output("xvswrapped")
        if mode == "absent":
            require("xvswrapped", "NOT-HUNK: not an Amiga HUNK file", 0)
            if "XVS-DETECTED" in wrapped or "INFECTED" in wrapped:
                raise RuntimeError(f"Absent xvs changed normal scan: {wrapped!r}")
            checks["xvs_absent_normal_scan"] = "PASS"
        else:
            if "previous-rc=0\n" not in probe("xvswrapped"):
                raise RuntimeError(f"Wrapped safe-test scan failed: {probe('xvswrapped')!r}")
            if "INFECTED" in wrapped:
                raise RuntimeError(f"xvs result mislabeled INFECTED: {wrapped!r}")
            if "XVS-DETECTED" in wrapped and "not an AmiGuard INFECTED verdict" not in wrapped:
                raise RuntimeError(f"Missing xvs verdict separation: {wrapped!r}")
            observed = "XVS-DETECTED" in wrapped
            for name in ("xvszip", "xvszip2"):
                stage(name)
                text = output(name)
                if "previous-rc=0\n" not in probe(name) or "INFECTED" in text:
                    raise RuntimeError(f"Safe xvs archive probe failed: {name}: {text!r}")
                if "XVS-DETECTED" in text:
                    if "not an AmiGuard INFECTED verdict" not in text:
                        raise RuntimeError(f"Missing xvs verdict separation: {text!r}")
                    observed = True
            checks["xvs_safe_probe_never_amiguard_infected"] = "PASS"
            checks["xvs_detected_runtime_observed"] = observed

        stage("post")
        post = require("post", "System (dir)", 0)
        checks["session_responsive_after_scans"] = "PASS"
        checks["no_repair_delete"] = "PASS (no such operation invoked)"
        completed = True
    finally:
        for path in work.glob("*.log"):
            shutil.copyfile(path, evidence / path.name)
        if completed:
            gui("chord", "F12", "q")
            emulator.wait(timeout=30)
        console.close()
        log_dir = RUN / f"fsuae-{mode}/Cache/Logs"
        for name in ("fs-uae.log.txt", "debug.uae"):
            if (log_dir / name).exists():
                shutil.copyfile(log_dir / name, evidence / name)
        manifest = json.loads((RUN / "evidence/manifest.json").read_text())
        observations = {
            "mode": mode,
            "completed_log_checks": completed,
            "checks": checks,
            "binary_after": digest(work / "AmiGuard"),
            "file_after": {
                path.name: digest(path) for path in sorted((RUN / "fixtures").iterdir())
            },
            "media_after": {
                name: digest(RUN / name) for name in manifest["media_before"]
            },
            "original_after": {
                path: digest(Path(path)) for path in manifest["original_sha256"]
            },
            "screenshots_require_human_review": True,
        }
        (evidence / "observations.json").write_text(json.dumps(observations, indent=2) + "\n")
        if observations["binary_after"] != manifest["binary_sha256"]:
            raise RuntimeError("Staged AmiGuard binary changed")
        if observations["file_after"] != manifest["file_before"]:
            raise RuntimeError("Fixture changed")
        if observations["media_after"] != manifest["media_before"]:
            raise RuntimeError("Disposable media changed")
        if observations["original_after"] != manifest["original_sha256"]:
            raise RuntimeError("Original input changed")
    print(json.dumps({"mode": mode, "completed": completed, "checks": checks}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("absent", "present"))
    execute(parser.parse_args().mode)
