#!/usr/bin/env python3
"""Offline guided demo source checks. No network, no paid API."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess,tempfile

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.scripts=[];self.in_script=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids
            self.ids.add(a['id'])
        if tag=='script':
            assert 'src' not in a
            self.in_script=True
    def handle_endtag(self,tag):
        if tag=='script':self.in_script=False
    def handle_data(self,data):
        if self.in_script:self.scripts.append(data)

html=Path('prototype/demo.html').read_text(encoding='utf-8')
p=Inspect();p.feed(html)
assert {'one','two','status','out1','out2','out3','progress','reset'}.issubset(p.ids)
assert 'fetch(' not in html and 'XMLHttpRequest' not in html and 'sendBeacon' not in html
assert 'textContent' in html and '실제 AI 호출' in html
with tempfile.TemporaryDirectory() as d:
    js=Path(d)/'demo.js';js.write_text('\n'.join(p.scripts),encoding='utf-8')
    subprocess.run(['node','--check',str(js)],check=True)
print('PASS: guided demo static and JavaScript syntax checks')
