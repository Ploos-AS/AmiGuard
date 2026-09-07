from pathlib import Path
import hashlib,json,re
r=Path('/tmp/amiguard-m22j-run'); w=r/'work'; e=r/'evidence'
m=json.loads((e/'manifest.json').read_text()); o=json.loads((e/'observations.json').read_text())
assert o['completed_log_checks']
for before,after in [('file_before','file_after'),('media_before','media_after'),('original_sha256','original_after')]: assert m[before]==o[after]
assert hashlib.sha256((w/'AmiGuard').read_bytes()).hexdigest()==m['binary_sha256']
expected={'positive':'TEST-SIGNATURE: EICAR Standard Anti-Virus Test File','nearmiss':'NOT-HUNK:','filevalid':'VALID-HUNK:','fileplain':'NOT-HUNK:','filemalformed':'MALFORMED-HUNK:','filemissing':'ERROR: cannot open file read-only','fileoversize':'ERROR: file exceeds 128 KiB','clean':'STANDARD:','customone':'CUSTOM:','customtwo':'CUSTOM:','badone':'UNKNOWN:','badtwo':'UNKNOWN:','custom':'UNKNOWN:'}
for name,s in expected.items():
 t=(w/f'{name}.log').read_text(); assert s in t and 'INFECTED' not in t
 if name!='positive': assert 'TEST-SIGNATURE' not in t
memory={}
for series,verdict in [('positiveseries',expected['positive']),('nearmissseries','NOT-HUNK:'),('validseries','VALID-HUNK:'),('plainseries','NOT-HUNK:'),('malformedseries','MALFORMED-HUNK:')]:
 before=int(re.search(r'free-chip=(\d+)',(w/f'{series}-before.log').read_text())[1]); values=[]
 for i in range(1,11):
  t=(w/f'{series}-{i:02}.log').read_text(); p=(w/f'{series}-memory-{i:02}.log').read_text()
  assert verdict in t and 'INFECTED' not in t and 'previous-rc=0\n' in p
  if series!='positiveseries': assert 'TEST-SIGNATURE' not in t
  values.append(int(re.search(r'free-chip=(\d+)',p)[1]))
 assert values==[before]*10
 memory[series]={'before':before,'after_each':values,'passes':10}
for p in w.glob('*.log'): assert 'INFECTED' not in p.read_text()
result={'required_gates':'PASS','memory':memory,'read_only':'all fixture, media and original hashes unchanged','binary_sha256':m['binary_sha256'],'screenshots_reviewed':['startup','positive','nearmiss','filevalid','fileplain','filemalformed','fileoversize','filemissing','positiveseries','clean','customone','custom','post']}
(e/'verified-results.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
