#!/usr/bin/env python3
"""Select up to three safe tasks deterministically, without external calls."""
from pathlib import Path
import json, os, subprocess, sys, datetime, csv

ROOT=Path(__file__).resolve().parents[1]
ALLOW={'audit_repository','validate_mvp','summarize_experiment'}
tasks=json.loads((ROOT/'data/task_backlog.json').read_text(encoding='utf-8'))
assert isinstance(tasks,list)
assert len({t['id'] for t in tasks})==len(tasks),'Duplicate task ID'
eligible=sorted((t for t in tasks if t.get('approval')=='internal_only' and t.get('action') in ALLOW),key=lambda t:(int(t['priority']),t['id']))[:3]
results=[]
for t in eligible:
    try:
        action=t['action']
        if action=='audit_repository':
            forbidden=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and (p.name in {'.env','.env.local'} or p.suffix in {'.pem','.key'}) and '.git' not in p.parts]
            if forbidden: raise RuntimeError('Forbidden secret-like filenames detected')
            detail='No forbidden secret-like filenames detected'
        elif action=='validate_mvp':
            subprocess.run([sys.executable,str(ROOT/'tests/check_mvp.py')],cwd=ROOT,check=True,timeout=40,capture_output=True,text=True)
            detail='MVP static checks passed'
        else:
            with (ROOT/'data/experiment_log.csv').open(encoding='utf-8',newline='') as f: count=len(list(csv.DictReader(f)))
            detail=f'{count} logged rows; no revenue verification'
        results.append({'id':t['id'],'owner':t['owner'],'status':'completed','detail':detail})
    except Exception as e:
        results.append({'id':t['id'],'owner':t['owner'],'status':'failed','detail':str(e)[:240]})
blocked=[{'id':t['id'],'reason':'human approval or unsupported action'} for t in tasks if t not in eligible]
report={'utc_date':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),'selected':results,'not_executed':blocked,'paid_api_calls':0,'external_actions':0}
out=Path(os.environ.get('ZERO_HUMAN_OUTPUT','artifacts/decision-run.json'));out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
sys.exit(1 if any(r['status']=='failed' for r in results) else 0)
