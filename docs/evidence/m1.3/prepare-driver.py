import sys,json,argparse
from pathlib import Path
sys.path.insert(0,'/home/pgo/Projects/Ploos-AS/AmiGuard/scripts')
import m03_runtime as m
old=json.loads(Path('/tmp/amiguard-m1-run/evidence/manifest.json').read_text())
a=argparse.Namespace(**{k:Path(v) for k,v in old['inputs'].items()},run_dir=Path('/tmp/amiguard-m13-run'),cc='/opt/amiga/bin/m68k-amigaos-gcc',xdftool='/tmp/amiguard-m03-tools/bin/xdftool')
r=m.prepare(a)
b=bytearray((r/'workbench12.adf').read_bytes()); b[100]^=1
(r/'invalid.adf').write_bytes(b); (r/'invalid.adf').chmod(0o444)
p=r/'runtime.fs-uae'; p.write_text(p.read_text()+f'\nfloppy_image_2 = {r}/invalid.adf\nkeyboard_key_f9 = action_drive_0_insert_floppy_2\n')
for name in ('badone','badtwo'):
 (r/'work'/name).write_text(f'FailAt 21\nAmiGuard >AGTest:{name}.log DF0:\nProbe >AGTest:{name}-probe.log\nType AGTest:{name}.log\nEcho >AGTest:{name}.done "RETURNED"\n')
p=r/'evidence/manifest.json'; meta=json.loads(p.read_text()); meta['media_before']['invalid.adf']=m.digest(r/'invalid.adf'); p.write_text(json.dumps(meta,indent=2)+'\n')
(r/'evidence/runtime.fs-uae').write_text((r/'runtime.fs-uae').read_text())
