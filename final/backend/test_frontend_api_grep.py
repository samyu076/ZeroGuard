import os
import re

api_pattern = re.compile(r'/api/[^\s\'\"\`]*')

matches = []
for root, dirs, files in os.walk('final/frontend/src'):
    for file in files:
        if file.endswith(('.js', '.jsx', '.html')):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                for line_no, line in enumerate(f, 1):
                    for match in api_pattern.findall(line):
                        matches.append((path, line_no, match))

print('=== ITEM #2 FRONTEND API PATH GREP CHECK ===')
print(f'Total API path string matches found: {len(matches)}')
unversioned = []
for path, line_no, match in matches:
    print(f'  {path}:{line_no} -> {match}')
    if not match.startswith('/api/v1'):
        unversioned.append((path, line_no, match))

print(f'\nTotal unversioned /api/ calls missing /v1/: {len(unversioned)}')
