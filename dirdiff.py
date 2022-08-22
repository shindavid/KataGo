"""
USAGE:

python dirdiff.py LIGHTVECTOR_REPO_ROOT HZYHHZY_REPO_ROOT
"""

import difflib
import os
import sys

git1 = 'lightvector:master'
git2 = 'hzyhhzy:Reversi2022'

dir1 = os.path.expanduser(sys.argv[1])
dir2 = os.path.expanduser(sys.argv[2])
if dir1[-1] != '/':
    dir1 += '/'
if dir2[-1] != '/':
    dir2 += '/'
diffdir = os.path.join(os.path.dirname(__file__), 'diffs')

common_files = []
rmdirs = set()
rm_summary = []

for root, dirs, files in os.walk(dir1):
    rel_root = root[len(dir1):]
    rel_root_parts = rel_root.split('/')
    if '.git' in rel_root_parts:
        continue
    root2 = os.path.join(dir2, rel_root)
    if os.path.isdir(root2):
        for filename in files:
            if filename.startswith('.'):
                continue
            rel_filename = os.path.join(rel_root, filename)
            filename1 = os.path.join(dir1, rel_filename)
            filename2 = os.path.join(dir2, rel_filename)
            assert os.path.isfile(filename1)
            if os.path.isfile(filename2):
                common_files.append(rel_filename)
            else:
                rm_summary.append(f'* rm {rel_filename}')
    else:
        rmdirs.add(rel_root)
        report = True
        for n in range(len(rel_root_parts)):
            partial_rel_root = '/'.join(rel_root_parts[:n])
            if partial_rel_root in rmdirs:
                report = False
                break

        if report:
            rm_summary.append(f'* rmdir {rel_root}')


if rm_summary:
    rm_summary_filename = os.path.join(diffdir, 'rm_summary.txt')
    with open(rm_summary_filename, 'w') as f:
        f.writelines(rm_summary)


for rel_filename in common_files:
    filename1 = os.path.join(dir1, rel_filename)
    filename2 = os.path.join(dir2, rel_filename)

    with open(filename1, 'r', encoding='utf-8', errors='ignore') as f1:
        lines1 = [line for line in f1]
    with open(filename2, 'r', encoding='utf-8', errors='ignore') as f2:
        lines2 = [line for line in f2]

    fromfile = f'{rel_filename} [{git1}]'
    tofile = f'{rel_filename} [{git2}]'
    out_lines = []
    for line in difflib.unified_diff(lines1, lines2, fromfile=fromfile, tofile=tofile, lineterm=''):
        out_lines.append(line)

    if out_lines:
        out_filename = os.path.join(diffdir, rel_filename + '.diff')
        os.makedirs(os.path.split(out_filename)[0], exist_ok=True)
        with open(out_filename, 'w') as f:
            f.writelines(out_lines)


for root, dirs, files in os.walk(dir2):
    rel_root = root[len(dir2):]
    rel_root_parts = rel_root.split('/')
    if '.git' in rel_root_parts:
        continue

    for filename in files:
        if filename.startswith('.'):
            continue
        rel_filename = os.path.join(rel_root, filename)
        filename1 = os.path.join(dir1, rel_filename)
        filename2 = os.path.join(dir2, rel_filename)
        assert os.path.isfile(filename2), (filename2, dir2, rel_root, filename, rel_filename)
        if os.path.isfile(filename1):
            continue

        with open(filename2, 'r', encoding='utf-8', errors='ignore') as f2:
            lines2 = [line for line in f2]

        fromfile = f'{rel_filename} [{git1}]'
        tofile = f'{rel_filename} [{git2}]'
        out_lines = []
        for line in difflib.unified_diff([], lines2, fromfile=fromfile, tofile=tofile, lineterm=''):
            out_lines.append(line)

        out_filename = os.path.join(diffdir, rel_filename + '.diff')
        os.makedirs(os.path.split(out_filename)[0], exist_ok=True)
        with open(out_filename, 'w') as f:
            f.writelines(out_lines)

