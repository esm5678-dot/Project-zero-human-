#!/usr/bin/env python3
"""Zero-cost autonomous internal work queue. No LLM/API calls or external writes."""
from pathlib import Path
import csv, datetime, json, os, sys

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/'data/work_queue.json'
REPORT=Path(os.environ.get('ZERO_HUMAN_OUTPUT','artifacts/agent-run.json'))
ALLOWED={'audit_repository','validate_mvp','summarize_experiment'}
def run():
    tasks=json.loads(QUEUE.read_text(encoding='utf-8'))
    assert isinstance(tasks,list)
    results=[]
    for task in tasks:
        tid=task['id']; kind=task['type']
        if kind not in ALLOWED or task.get('approval')!='internal_only':
            results.append({'id':tid,'status':'blocked','reason':'Not allowlisted or requires approval'})
            continue
        try:
            if kind=='audit_repository':
                prohibited=[]
                for path in ROOT.rglob('*'):
                    if not path.is_file() or '.git' in path.parts: continue
                    if path.name in ('.env','.env.local') or path.suffix in ('.pem','.key'):
                        prohibited.append(str(path.relative_to(ROOT)))
                assert not prohibited, f'Forbidden secret-like files: {prohibited}'
                detail='No forbidden secret-like files found (not a comprehensive secret scan)'
            elif kind=='validate_mvp':
                import subprocess
                subprocess.run([sys.executable,str(ROOT/'tests/check_mvp.py')],cwd=ROOT,check=True,capture_output=True,text=True,timeout=40)
                detail='MVP source and JS syntax checks passed'
            elif kind=='summarize_experiment':
                with (ROOT/'data/experiment_log.csv').open(encoding='utf-8',newline='') as f:
                    rows=list(csv.DictReader(f))
                detail=f'{len(rows)} experiment log entries (does not verify revenue)'
            results.append({'id':tid,'status':'completed','detail':detail})
        except Exception as e:
            results.append({'id':tid,'status':'failed','reason':str(e)[:300]})
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    report={'utc_date':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),'results':results,'new_spend_krw':0,'external_actions':0,'llm_calls':0}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    return 1 if any(r['status']=='failed' for r in results) else 0
if __name__=='__main__':sys.exit(run())
