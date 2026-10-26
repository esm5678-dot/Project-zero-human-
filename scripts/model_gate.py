#!/usr/bin/env python3
"""Fail-closed feasibility gate for model use. No network, no API requests."""
import json, os, sys
from pathlib import Path

def evaluate(config):
    reasons=[]
    if config.get('enabled') is not True: reasons.append('model calls disabled by default')
    if config.get('max_new_spend_krw') != 0: reasons.append('additional spending cap must be zero')
    if config.get('verified_zero_cash_billing') is not True: reasons.append('free usage and billing not independently verified')
    if config.get('human_approved_provider') is not True: reasons.append('provider not explicitly approved')
    if config.get('daily_request_limit',0) not in range(1,11): reasons.append('daily request limit must be 1-10')
    if config.get('allow_external_data') is not False: reasons.append('external customer data must be prohibited')
    return {'allowed':not reasons,'reasons':reasons,'network_calls':0,'new_spend_krw':0}

if __name__=='__main__':
    p=Path(sys.argv[1] if len(sys.argv)>1 else 'config/model_policy.json')
    data=json.loads(p.read_text(encoding='utf-8'))
    result=evaluate(data)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    # A blocked call is the EXPECTED safe result, not a CI failure.
