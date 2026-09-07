#!/usr/bin/env python3
"""Prepare and run the visible M0.3 qualification in a NEW disposable directory.

Requires FS-UAE 3.x, m68k-amigaos-gcc with nix13, amitools and python-xlib.
No ROM, Workbench image, reference profile or existing run directory is modified.
Screenshots still need human review: log assertions alone are not qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

REPO = Path('/home/pgo/Projects/Ploos-AS/AmiGuard')


def command(args, **kw):
    return subprocess.run([str(a) for a in args], check=True, **kw)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(args):
    run = args.run_dir.resolve()
    run.mkdir(parents=True, exist_ok=False)
    work = run / 'work'
    evidence = run / 'evidence'
    for path in (work / 's', work / 'c', work / 'libs', evidence, run / 'screenshots'):
        path.mkdir(parents=True, exist_ok=True)
    inputs = {key: str(getattr(args, key).resolve()) for key in ('reference', 'rom', 'workbench')}
    original = {path: digest(Path(path)) for path in inputs.values()}
    # Build before staging; preserve the output and exact source identity.
    with (evidence / 'build.log').open('w') as log:
        for cmd in (['make', 'clean'], ['make', 'check'], ['make', f'CC={args.cc}']):
            command(cmd, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
    shutil.copyfile(REPO / 'AmiGuard', work / 'AmiGuard')
    with (evidence / 'binary-format.txt').open('w') as log:
        command(['file', work / 'AmiGuard'], stdout=log)
        command(['m68k-amigaos-objdump', '-f', work / 'AmiGuard'], stdout=log)
        command(['m68k-amigaos-nm', '-u', work / 'AmiGuard'], stdout=log)
    with (evidence / 'disassembly.txt').open('w') as log:
        command(['m68k-amigaos-objdump', '-dr', work / 'AmiGuard'], stdout=log)
    command([args.cc, '-O2', '-Wall', '-Wextra', '-Werror', '-m68000', '-mcrt=nix13',
             REPO / 'scripts/m03_probe.c', '-o', work / 'Probe'])
    shutil.copyfile(args.workbench, run / 'workbench12.adf')
    # Existing host-test fixture: non-executable 0x5a bootblock, never booted.
    (run / 'unknown.adf').write_bytes(bytes([0x5a]) * 1024 + bytes(901120 - 1024))
    for name in ('workbench12.adf', 'unknown.adf'):
        (run / name).chmod(0o444)
    for name in ('Assign', 'CD', 'Dir', 'Echo', 'Execute', 'FailAt', 'Type', 'Version'):
        command([args.xdftool, args.workbench, 'read', f'c/{name}', work / 'c' / name], stdout=subprocess.DEVNULL)
    command([args.xdftool, args.workbench, 'read', 'libs/version.library', work / 'libs/version.library'], stdout=subprocess.DEVNULL)
    (work / 's/startup-sequence').write_text('''DF0:c/Assign SYS: DF0:
DF0:c/Assign C: DF0:c
Assign LIBS: DF0:libs
Assign DEVS: DF0:devs
Assign L: DF0:l
Assign FONTS: DF0:fonts
LoadWB
NewCLI CON:0/12/640/190/AmiGuard FROM AGTest:setup
EndCLI
''')

    def stage(name, lines):
        # DOS 1.2 redirection belongs before command arguments. Each process
        # writes its own log; Execute's output redirection is not inherited.
        (work / name).write_text('\n'.join(['FailAt 21'] + lines +
            [f'Echo >AGTest:{name}.done "RETURNED"', f'Echo "{name.upper()} RETURNED"']) + '\n')

    stage('setup', ['Assign C: AGTest:c', 'Assign S: AGTest:s', 'Assign T: RAM:',
                   'CD AGTest:', 'Version', 'AmiGuard >AGTest:start.log',
                   'Probe >AGTest:start-probe.log', 'Type AGTest:start.log'])
    lines = []
    for name, target in [('dh0', 'DH0:'), ('df4', 'DF4:'), ('nonsense', 'nonsense')]:
        lines += [f'AmiGuard >AGTest:{name}.log {target}',
                  f'Probe >AGTest:{name}-probe.log', f'Type AGTest:{name}.log']
    stage('invalid', lines)
    for name in ('empty', 'clean', 'custom'):
        stage(name, [f'AmiGuard >AGTest:{name}.log DF0:',
                     f'Probe >AGTest:{name}-probe.log', f'Type AGTest:{name}.log'])
    lines = ['Probe >AGTest:repeat-before.log']
    for i in range(1, 11):
        lines += [f'AmiGuard >AGTest:repeat-{i:02d}.log DF0:',
                  f'Probe >AGTest:memory-{i:02d}.log', f'Echo "SCAN {i:02d} RETURNED"']
    stage('repeat', lines)
    stage('post', ['Dir >AGTest:df0-after.log DF0:', 'Probe >AGTest:post-probe.log',
                   'Type AGTest:df0-after.log'])
    # Append a storage/automation overlay to the unmodified reference settings.
    config = args.reference.read_text()
    config += f'''
# Disposable M0.3 storage and automation overlay
base_dir = {run}/fsuae
kickstart_file = {args.rom.resolve()}
floppy_drive_0 = {run}/workbench12.adf
floppy_image_0 = {run}/workbench12.adf
floppy_image_1 = {run}/unknown.adf
writable_floppy_images = 0
uae_floppy_write_protect = true
hard_drive_0 = {work}
hard_drive_0_label = AGTest
hard_drive_0_priority = 0
fullscreen = 0
window_hidden = 0
window_minimized = 0
window_width = 960
window_height = 720
screenshots_output_dir = {run}/screenshots
keyboard_key_f6 = action_eject_floppy_0
keyboard_key_f7 = action_drive_0_insert_floppy_0
keyboard_key_f8 = action_drive_0_insert_floppy_1
'''
    (run / 'runtime.fs-uae').write_text(config)
    sources = sorted((REPO / 'src').glob('*.[ch]')) + [REPO / 'Makefile']
    meta = {'date_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
            'status': subprocess.check_output(['git', 'status', '--short'], cwd=REPO, text=True),
            'inputs': inputs, 'original_sha256': original,
            'source_sha256': {str(p.relative_to(REPO)): digest(p) for p in sources},
            'media_before': {name: digest(run / name) for name in ('workbench12.adf', 'unknown.adf')},
            'binary_sha256': digest(work / 'AmiGuard'), 'binary_bytes': (work / 'AmiGuard').stat().st_size,
            'compiler': shutil.which(args.cc),
            'compiler_version': subprocess.check_output([args.cc, '--version'], text=True).splitlines()[0]}
    (evidence / 'manifest.json').write_text(json.dumps(meta, indent=2) + '\n')
    shutil.copyfile(run / 'runtime.fs-uae', evidence / 'runtime.fs-uae')
    print(f'Prepared {run}', flush=True)
    return run


def execute(run):
    work, evidence = run / 'work', run / 'evidence'
    meta = json.loads((evidence / 'manifest.json').read_text())
    log = (evidence / 'console.log').open('w')
    emulator = subprocess.Popen(['fs-uae', str(run / 'runtime.fs-uae')], stdout=log, stderr=subprocess.STDOUT)

    def gui(*args):
        command([sys.executable, REPO / 'scripts/m03_gui.py', '--screenshots-dir',
                 run / 'screenshots', *args], cwd=REPO)

    def wait_stage(name, timeout=90):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if emulator.poll() is not None:
                raise RuntimeError(f'FS-UAE exited during {name}: {emulator.returncode}')
            marker = work / f'{name}.done'
            if marker.exists() and marker.read_text().strip() == 'RETURNED':
                time.sleep(1)
                return
            time.sleep(0.5)
        raise RuntimeError(f'Timeout in {name}; inspect the visible emulator')

    def stage(name):
        gui('type', f'Execute AGTest:{name}\n')
        wait_stage(name)
        gui('shot', str(evidence / f'{name}.png'))

    def require(name, text, code):
        output = (work / f'{name}.log').read_text()
        probe = (work / f'{name}-probe.log').read_text()
        if text not in output or f'previous-rc={code}\n' not in probe:
            raise RuntimeError(f'Unexpected output/return code in {name}: {output} {probe}')
        if name in ('start', 'dh0', 'df4', 'nonsense') and 'Reading ' in output:
            raise RuntimeError(f'Invalid target reached read path: {name}')

    completed = False
    try:
        wait_stage('setup', 180)
        gui('shot', str(evidence / 'startup.png'))
        require('start', 'Usage: AmiGuard', 10)
        for name, expected, code in [('positive','TEST-SIGNATURE: AmiGuard synthetic file test marker',0),('nearmiss','NOT-HUNK:',0),('filevalid','VALID-HUNK:',0),('fileplain','NOT-HUNK:',0),('filemalformed','MALFORMED-HUNK:',0),('fileoversize','ERROR: file exceeds 128 KiB M2.1 limit',20),('filemissing','ERROR: cannot open file read-only',20)]:
            stage(name)
            require(name,expected,code)
        for name, expected in [('positiveseries','TEST-SIGNATURE:'),('nearmissseries','NOT-HUNK:'),('validseries','VALID-HUNK:'),('plainseries','NOT-HUNK:'),('malformedseries','MALFORMED-HUNK:')]:
            stage(name)
            for i in range(1,11):
                output=(work/f'{name}-{i:02d}.log').read_text()
                probe=(work/f'{name}-memory-{i:02d}.log').read_text()
                assert expected in output and 'previous-rc=0\n' in probe
        stage('invalid')
        for name in ('dh0', 'df4', 'nonsense'):
            require(name, 'Usage: AmiGuard', 10)
        gui('key', 'F6')
        time.sleep(3)
        stage('empty')
        require('empty', 'trackdisk.device read failed', 20)
        gui('key', 'F7')
        time.sleep(3)
        stage('clean')
        require('clean', 'STANDARD: Amiga DOS bootblock', 0)
        require('clean', 'read 1024 bytes at offset 0', 0)
        stage('repeat')
        import re
        memory = []
        baseline = int(re.search(r'free-chip=(\d+)', (work / 'repeat-before.log').read_text())[1])
        for i in range(1, 11):
            output = (work / f'repeat-{i:02d}.log').read_text()
            probe = (work / f'memory-{i:02d}.log').read_text()
            if 'STANDARD: Amiga DOS bootblock' not in output or 'read 1024 bytes at offset 0' not in output or 'previous-rc=0\n' not in probe:
                raise RuntimeError(f'Repeated scan {i} failed')
            memory.append(int(re.search(r'free-chip=(\d+)', probe)[1]))
        if any(value != baseline for value in memory):
            raise RuntimeError(f'Memory changed; investigate before qualification: {baseline} -> {memory}')
        gui('key', 'F10')
        time.sleep(3)
        for name in ('customone', 'customtwo'):
            stage(name)
            require(name, 'CUSTOM: custom bootblock (valid checksum)', 0)
        stage('customrepeat')
        for i in range(1,6):
            output = (work / f'custom-repeat-{i:02d}.log').read_text()
            probe = (work / f'custom-memory-{i:02d}.log').read_text()
            assert 'CUSTOM: custom bootblock (valid checksum)' in output
            assert 'read 1024 bytes at offset 0' in output and 'previous-rc=0\n' in probe
        gui('key', 'F9')
        time.sleep(3)
        for name in ('badone', 'badtwo'):
            stage(name)
            require(name, 'UNKNOWN: Amiga DOS bootblock (invalid checksum)', 0)
        gui('key', 'F8')
        time.sleep(3)
        stage('custom')
        require('custom', 'UNKNOWN: unknown bootblock', 0)
        gui('key', 'F7')
        time.sleep(3)
        stage('post')
        if 'Workbench' not in (work / 'start-probe.log').read_text() or 'System (dir)' not in (work / 'df0-after.log').read_text():
            raise RuntimeError('Missing Workbench identity or post-test DF0 directory evidence')
        if 'previous-rc=0\n' not in (work / 'post-probe.log').read_text():
            raise RuntimeError('DF0 directory command failed')
        identity = (work / 'start-probe.log').read_text()
        if 'Exec=33.' not in identity or 'Workbench=33.' not in identity:
            raise RuntimeError('Runtime is not Kickstart/Workbench 1.2')
        completed = True
    finally:
        for path in work.glob('*.log'):
            shutil.copyfile(path, evidence / path.name)
        if completed:
            gui('chord', 'F12', 'q')
            emulator.wait(timeout=20)
        # On failure keep the visible window for diagnosis; never auto-report PASS.
        log.close()
        logs = run / 'fsuae/Cache/Logs'
        for name in ('fs-uae.log.txt', 'debug.uae'):
            if (logs / name).exists():
                shutil.copyfile(logs / name, evidence / name)
        after = {name: digest(run / name) for name in meta['media_before']}
        originals = {path: digest(Path(path)) for path in meta['original_sha256']}
        result = {'completed_log_checks': completed, 'file_after': {name: digest(run/'fixtures'/name) for name in meta['file_before']}, 'media_after': after,
                  'original_after': originals, 'screenshots_require_human_review': True}
        (evidence / 'observations.json').write_text(json.dumps(result, indent=2) + '\n')
        if after != meta['media_before'] or originals != meta['original_sha256']:
            raise RuntimeError('A media or reference checksum changed')
    print(f'Log checks complete. Review screenshots and emulator configuration in {evidence}; no automatic M0.3 PASS.', flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('reference', 'rom', 'workbench', 'run-dir'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--cc', default='m68k-amigaos-gcc')
    p.add_argument('--xdftool', default='xdftool')
    p.add_argument('--prepare-only', action='store_true')
    args = p.parse_args()
    run = prepare(args)
    if not args.prepare_only:
        execute(run)


if __name__ == '__main__':
    execute(Path('/tmp/amiguard-m22b-run'))
