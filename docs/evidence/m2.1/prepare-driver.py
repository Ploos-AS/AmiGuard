import sys,json,argparse
from pathlib import Path
sys.path.insert(0,'/home/pgo/Projects/Ploos-AS/AmiGuard/scripts')
import m03_runtime as m
old=json.loads(Path('/tmp/amiguard-m1-run/evidence/manifest.json').read_text())
a=argparse.Namespace(**{k:Path(v) for k,v in old['inputs'].items()},run_dir=Path('/tmp/amiguard-m21-final'),cc='/opt/amiga/bin/m68k-amigaos-gcc',xdftool='/tmp/amiguard-m03-tools/bin/xdftool')
r=m.prepare(a)
b=bytearray((r/'workbench12.adf').read_bytes()); b[100]^=1
(r/'invalid.adf').write_bytes(b); (r/'invalid.adf').chmod(0o444)
p=r/'runtime.fs-uae'; p.write_text(p.read_text()+f'\nfloppy_image_2 = {r}/invalid.adf\nkeyboard_key_f9 = action_drive_0_insert_floppy_2\n')
for name in ('badone','badtwo'):
 (r/'work'/name).write_text(f'FailAt 21\nAmiGuard >AGTest:{name}.log DF0:\nProbe >AGTest:{name}-probe.log\nType AGTest:{name}.log\nEcho >AGTest:{name}.done "RETURNED"\n')
p=r/'evidence/manifest.json'; meta=json.loads(p.read_text()); meta['media_before']['invalid.adf']=m.digest(r/'invalid.adf'); p.write_text(json.dumps(meta,indent=2)+'\n')
(r/'evidence/runtime.fs-uae').write_text((r/'runtime.fs-uae').read_text())

custom=bytes([255])*8+bytes(901120-8)
(r/'valid-custom.adf').write_bytes(custom); (r/'valid-custom.adf').chmod(0o444)
assert sum(int.from_bytes(custom[i:i+4], 'big') for i in range(0,1024,4)) % 0xffffffff == 0
p=r/'runtime.fs-uae'; p.write_text(p.read_text()+f'\nfloppy_image_3 = {r}/valid-custom.adf\nkeyboard_key_f10 = action_drive_0_insert_floppy_3\n')
for name in ['customone','customtwo']:
 (r/'work'/name).write_text(f'FailAt 21\nAmiGuard >AGTest:{name}.log DF0:\nProbe >AGTest:{name}-probe.log\nType AGTest:{name}.log\nEcho >AGTest:{name}.done "RETURNED"\n')
lines=['FailAt 21','Probe >AGTest:custom-before.log']
for i in range(1,6):
 lines += [f'AmiGuard >AGTest:custom-repeat-{i:02d}.log DF0:',f'Probe >AGTest:custom-memory-{i:02d}.log', f'Echo "CUSTOM SCAN {i} RETURNED"']
lines += ['Echo >AGTest:customrepeat.done "RETURNED"']
(r/'work/customrepeat').write_text('\n'.join(lines)+'\n')
p=r/'evidence/manifest.json'; meta=json.loads(p.read_text()); meta['media_before']['valid-custom.adf']=m.digest(r/'valid-custom.adf'); p.write_text(json.dumps(meta,indent=2)+'\n')
(r/'evidence/runtime.fs-uae').write_text((r/'runtime.fs-uae').read_text())

import struct
fixtures={'valid.hunk':struct.pack('>10I',1011,0,1,0,0,1,1001,1,0x4e754e75,1010),'plain.txt':b'Harmless ASCII fixture.\n','malformed.hunk':struct.pack('>I',1011),'oversize.bin':bytes(131073)}
f=r/'work/fixtures'; f.mkdir()
for name,data in fixtures.items():
 (f/name).write_bytes(data); (f/name).chmod(0o444)
meta=json.loads((r/'evidence/manifest.json').read_text()); meta['file_before']={n:m.digest(f/n) for n in fixtures}; meta['file_sizes']={n:len(b) for n,b in fixtures.items()}
(r/'evidence/manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
for name,target in [('filevalid','valid.hunk'),('fileplain','plain.txt'),('filemalformed','malformed.hunk'),('fileoversize','oversize.bin'),('filemissing','does-not-exist')]:
 (r/'work'/name).write_text(f'FailAt 21\nAmiGuard >AGTest:{name}.log FILE AGTest:fixtures/{target}\nProbe >AGTest:{name}-probe.log\nType AGTest:{name}.log\nEcho >AGTest:{name}.done "RETURNED"\n')
for name,target in [('validseries','valid.hunk'),('plainseries','plain.txt'),('malformedseries','malformed.hunk')]:
 lines=['FailAt 21',f'Probe >AGTest:{name}-before.log']
 for i in range(1,11):
  lines += [f'AmiGuard >AGTest:{name}-{i:02d}.log FILE AGTest:fixtures/{target}',f'Probe >AGTest:{name}-memory-{i:02d}.log',f'Echo "SCAN {i} RETURNED"']
 lines += [f'Echo >AGTest:{name}.done "RETURNED"']
 (r/'work'/name).write_text('\n'.join(lines)+'\n')

import shutil
shutil.move(str(r/'work/fixtures'),str(r/'fixtures'))
p=r/'runtime.fs-uae'; p.write_text(p.read_text()+f'\nhard_drive_1 = {r}/fixtures\nhard_drive_1_label = AGFiles\nhard_drive_1_read_only = 1\n')
for p in (r/'work').iterdir():
 if p.is_file() and (p.name.startswith('file') or p.name.endswith('series')):
  p.write_text(p.read_text().replace('AGTest:fixtures/','AGFiles:'))
(r/'evidence/runtime.fs-uae').write_text((r/'runtime.fs-uae').read_text())
