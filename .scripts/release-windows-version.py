#!/usr/bin/env python3

import os
import argparse
import re


def get_template_filepath(opts):
    version_base = opts.base
    major, minor, patch = 999999, 999999, 999999
    if re.match(r'^v\d+\.\d+\.\d+$', version_base):
        major, minor, patch = version_base.replace('v', '').split('.')
        major, minor, patch = int(major), int(minor), int(patch)
    if re.match(r'v\d+\.\d+.*-testing-.*', version_base):
        major, minor = version_base.replace('v', '').split('-')[0].split('.')[:2]

    lookup_seqs = [f'@{major}.{minor}.{patch}', f'@{major}.{minor}', f'@{major}', '']
    for name in lookup_seqs:
        template_file = os.path.join(os.path.dirname(__file__), f'release_windows{name}.yml')
        if os.path.isfile(template_file):
            return template_file
    return None


def load_data(opts):
    data = {}
    with open(get_template_filepath(opts), 'r', encoding='utf-8') as template_file:
        data['template'] = template_file.read()
    return data


def system_call(cmd):
    if os.system(cmd) != 0:
        raise RuntimeError(f"command failed: {cmd} !!!")


def do_release(opts):
    data = load_data(opts)
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    system_call('git fetch --all')
    system_call(f'git checkout {opts.base}')
    system_call('git rm .github/workflows/*')
    system_call('mkdir -p .github/workflows')
    with open('.github/workflows/release.yml', 'w', encoding='utf-8') as fp:
        fp.write(data['template'])
    system_call('git add .github') 
    system_call(f'git commit -s -m "Windows release action for {opts.base}"')
    if opts.force:
        try:
            system_call(f'git tag -d windows-{opts.base}')
            system_call(f'git push --delete origin windows-{opts.base}')
        except RuntimeError:
            pass
    system_call(f'git tag windows-{opts.base}')
    system_call(f'git push origin windows-{opts.base}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True, type=str)
    parser.add_argument('--force', default=False, action='store_true')
    opts = parser.parse_args()
    try:
        do_release(opts)
    except RuntimeError:
        pass
    system_call('git checkout main')


if __name__ == '__main__':
    main()
