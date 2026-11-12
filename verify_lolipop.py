import os
import re
from pathlib import Path

dist = Path('dist_lolipop')
html_files = list(dist.glob('*.html'))
errors = []

for hf in html_files:
    text = hf.read_text(encoding='utf-8')
    
    # 1. Check for unexpanded Jinja2 tags
    jinja_matches = re.findall(r'(\{\{.*?\}\}|\{%.*?%\})', text)
    if jinja_matches:
        errors.append(f'{hf.name}: Unexpanded Jinja2 tags found: {jinja_matches}')
        
    # 2. Check for absolute /static/ or /api/ references
    static_matches = re.findall(r'[\"\']/(static|api)/[^\"]*[\"\']', text)
    if static_matches:
        errors.append(f'{hf.name}: Unexpected absolute /static or /api reference: {static_matches}')
        
    # 3. Check for absolute page links (/policies, /issues, etc.)
    abs_links = re.findall(r'href=[\"\']/(policies|issues|profile|supporters|index)[\"\']', text)
    if abs_links:
        errors.append(f'{hf.name}: Absolute page links found: {abs_links}')

print(f'Checked {len(html_files)} HTML files.')
if errors:
    print('ERRORS FOUND:')
    for e in errors:
        print(' -', e)
else:
    print('ALL CHECKS PASSED: No unexpanded Jinja2 tags, no broken absolute links.')
