#!/usr/bin/env python3
"""Zero-cost, deterministic daily CEO briefing. No model/API calls or outbound contact."""
from pathlib import Path
import csv, datetime, json, os

root=Path(__file__).resolve().parents[1]
log=root/'data/experiment_log.csv'
rows=list(csv.DictReader(log.open(encoding='utf-8',newline='')))
today=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
done=sum(x.get('status','').lower() in ('done','completed','success') for x in rows)
spend=sum(int(x.get('new_spend_krw') or 0) for x in rows if (x.get('new_spend_krw') or '0').lstrip('-').isdigit())
tasks=[
 {'id':'ZH-NEXT-001','role':'Research','task':'Review replies to approved outreach','gate':'HUMAN_APPROVAL_REQUIRED_FOR_REPLY','execution':'manual_only'},
 {'id':'ZH-NEXT-002','role':'Product','task':'Review synthetic demo usability feedback and prioritize fixes','gate':'INTERNAL_ONLY','execution':'proposal_only'},
 {'id':'ZH-NEXT-003','role':'Auditor','task':'Review public repo for secrets and customer data','gate':'INTERNAL_ONLY','execution':'proposal_only'}
]
out={'date_utc':today,'recorded_tasks':len(rows),'recorded_completed_tasks':done,'recorded_new_spend_krw':spend,'next_tasks':tasks,'limitations':'No LLM invocation, no autonomous coding, no customer outreach, no Gmail access, no deployment. No verified revenue data in this log.'}
dest=Path(os.environ.get('ZERO_HUMAN_OUTPUT','daily-report.json'))
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
