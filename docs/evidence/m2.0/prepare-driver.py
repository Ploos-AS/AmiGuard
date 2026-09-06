import sys,json,argparse
from pathlib import Path
sys.path.insert(0,'/home/pgo/Projects/Ploos-AS/AmiGuard/scripts')
import m03_runtime as m
old=json.loads(Path('/tmp/amiguard-m1-run/evidence/manifest.json').read_text())
a=argparse.Namespace(**{k:Path(v) for k,v in old['inputs'].items()},run_dir=Path('/tmp/amiguard-m20-run'),cc='/opt/amiga/bin/m68k-amigaos-gcc',xdftool='/tmp/amiguard-m03-tools/bin/xdftool')
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
