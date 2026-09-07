from pathlib import Path
import shutil,hashlib,json,subprocess
repo=Path('/home/pgo/Projects/Ploos-AS/AmiGuard'); old=Path('/tmp/amiguard-m22b-run'); run=Path('/tmp/amiguard-m22j-run')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','status','--porcelain'],cwd=repo)==b''
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()=='c420b945806d922c5dd8e667669d7b73f66e92e2'
assert sha(repo/'AmiGuard')=='72f123101cc54d5b96ee5f7b665c2848ce53a0fdd7c5d8bf2b01621be2b67fde'
eicar=Path('/home/pgo/Downloads/eicar.com.txt'); b=eicar.read_bytes()
assert len(b)==68 and sha(eicar)=='275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
run.mkdir()
for d in ['work','fixtures','evidence','screenshots']: (run/d).mkdir()
for p in (old/'work').iterdir():
 if p.is_dir(): shutil.copytree(p,run/'work'/p.name)
 elif p.suffix not in ['.log','.done']: shutil.copyfile(p,run/'work'/p.name)
shutil.copyfile(repo/'AmiGuard',run/'work/AmiGuard')
for name in ['valid.hunk','plain.txt','malformed.hunk','oversize.bin']: shutil.copyfile(old/'fixtures'/name,run/'fixtures'/name)
(run/'fixtures/eicar.com.txt').write_bytes(b)
(run/'fixtures/eicar-nearmiss.bin').write_bytes(b[:-1]+bytes([b[-1]^1]))
for p in (run/'fixtures').iterdir(): p.chmod(0o444)
for p in (run/'work').iterdir():
 if p.is_file() and p.name not in ['AmiGuard','Probe']:
  t=p.read_text().replace('AGFiles:positive.bin','AGFiles:eicar.com.txt').replace('AGFiles:nearmiss.bin','AGFiles:eicar-nearmiss.bin')
  p.write_text(t)
for name in ['workbench12.adf','unknown.adf','invalid.adf','valid-custom.adf']:
 shutil.copyfile(old/name,run/name); (run/name).chmod(0o444)
config=(repo/'docs/evidence/m2.2b/runtime.fs-uae').read_text().replace(str(old),str(run))
(run/'runtime.fs-uae').write_text(config)
meta=json.loads((repo/'docs/evidence/m2.2b/manifest.json').read_text())
for p,h in meta['original_sha256'].items(): assert sha(Path(p))==h
meta={k:meta[k] for k in ['inputs','original_sha256','media_before']}
meta.update(head='c420b945806d922c5dd8e667669d7b73f66e92e2',status='',binary_sha256=sha(run/'work/AmiGuard'),file_before={p.name:sha(p) for p in (run/'fixtures').iterdir()})
meta['original_sha256'][str(eicar)]=sha(eicar)
(run/'evidence/manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
shutil.copyfile(run/'runtime.fs-uae',run/'evidence/runtime.fs-uae')
driver=(repo/'docs/evidence/m2.2b/runtime-driver.py').read_text().replace(str(old),str(run)).replace('TEST-SIGNATURE: AmiGuard synthetic file test marker','TEST-SIGNATURE: EICAR Standard Anti-Virus Test File')
(run/'evidence/runtime-driver.py').write_text(driver)
print(json.dumps(meta,indent=2))
