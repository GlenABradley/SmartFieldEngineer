"""Page extraction/replacement without signature invention. pip install pypdf==6.10.0"""
import argparse
from pathlib import Path
from pypdf import PdfReader, PdfWriter
p=argparse.ArgumentParser();p.add_argument('mode',choices=['extract','replace']);p.add_argument('input');p.add_argument('page',type=int);p.add_argument('output');p.add_argument('--signed-page');a=p.parse_args()
r=PdfReader(a.input);w=PdfWriter()
if not 1<=a.page<=len(r.pages):raise SystemExit('Page out of range')
if Path(a.output).exists():raise SystemExit('Output exists; use a new version')
if a.mode=='extract':w.add_page(r.pages[a.page-1])
else:
    if not a.signed_page:raise SystemExit('--signed-page required')
    signed=PdfReader(a.signed_page)
    if len(signed.pages)!=1:raise SystemExit('Signed page file must contain exactly one page')
    for i,page in enumerate(r.pages):w.add_page(signed.pages[0] if i==a.page-1 else page)
with open(a.output,'xb') as out:w.write(out)
print('Created',a.output,'Review job identity, page size, version and legibility before use.')
