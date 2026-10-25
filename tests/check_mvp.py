#!/usr/bin/env python3
"""Dependency-free source checks; not a substitute for browser acceptance tests."""
from html.parser import HTMLParser
from pathlib import Path
import re, subprocess, tempfile

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.scripts=[]
        self.in_script=False
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, 'duplicate HTML id'
            self.ids.add(attrs['id'])
        if tag=='script':
            assert 'src' not in attrs, 'remote or external script not allowed'
            self.in_script=True
    def handle_endtag(self, tag):
        if tag=='script': self.in_script=False
    def handle_data(self, data):
        if self.in_script: self.scripts.append(data)

html=Path('prototype/index.html').read_text(encoding='utf-8')
p=Inspect()
p.feed(html)
required={'alias','message','add','demo','notice','stats','rows','export','clear'}
assert required.issubset(p.ids), f'missing controls: {required-p.ids}'
assert not re.search(r'<script[^>]+src=|fetch\s*\(|XMLHttpRequest|sendBeacon',html,re.I), 'network operation detected'
assert "textContent" in html, 'safe text rendering missing'
assert "confirm(" in html, 'delete confirmation missing'
assert "zero-ops-inquiries.csv" in html, 'CSV export missing'
script='\n'.join(p.scripts)
with tempfile.TemporaryDirectory() as d:
    f=Path(d)/'app.js'
    f.write_text(script,encoding='utf-8')
    subprocess.run(['node','--check',str(f)],check=True)
print('PASS: HTML controls, offline-only static checks, JavaScript syntax')
