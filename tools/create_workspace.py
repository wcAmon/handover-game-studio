#!/usr/bin/env python3
"""Create an independent handover-shift workspace from tracked framework files.

Does not initialize Git, start agents, install cron, or copy local runtime/config.
"""
import argparse
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def create_workspace(destination, example=None):
    destination = Path(destination).expanduser().absolute()
    resolved = destination.resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError('destination must be outside the framework repository')
    if destination.exists() or destination.is_symlink():
        raise ValueError('destination already exists; refusing to overwrite')
    if example not in (None, 'swarm-agent'):
        raise ValueError('unknown example')
    tracked = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z']).decode().split('\0')
    files = {}
    for name in filter(None, tracked):
        # Runtime state and machine-local credentials never belong to an export.
        parts = Path(name).parts
        if any(p in ('.studio', '.git', 'node_modules', '__pycache__') for p in parts):
            continue
        if Path(name).name.startswith('.env') or name.endswith('.local.sh'):
            continue
        if name.startswith(('harness/', '.claude/', 'templates/')) or name in (
            'CLAUDE.md', '.gitignore', 'tools/imagegen.py', 'tools/concept_board.py',
            'docs/WORKFLOW.md', 'docs/CONTINUOUS.md', 'docs/NATIVE-TEAMS.md',
            'docs/validation/native-team-smoke-2026-09-28.md',
            'docs/DESIGN.md', 'docs/GAME-STUDIO-ORIGIN.md', 'docs/lessons.md'):
            files[name] = ROOT / name
        prefix = 'examples/' + example + '/' if example else None
        if prefix and name.startswith(prefix):
            files[name[len(prefix):]] = ROOT / name
    files['AGENTS.md'] = ROOT / 'templates/workspace-AGENTS.md'
    if not example:
        files['handover.md'] = ROOT / 'templates/initial-handover.md'
        files['inbox.md'] = ROOT / 'templates/workspace-inbox.md'
        files['README.md'] = ROOT / 'templates/workspace-README.md'
    for source in files.values():
        if not source.is_file() or source.is_symlink():
            raise ValueError('export source missing or symlink: ' + str(source.relative_to(ROOT)))
    if example and 'design/north-star.md' not in files:
        raise ValueError('example files are not tracked; use a committed framework checkout')
    destination.mkdir(parents=True, exist_ok=False)
    try:
        for relative, source in files.items():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        (destination / 'design').mkdir(exist_ok=True)
    except Exception:
        # Only remove the new directory owned by this invocation.
        shutil.rmtree(destination)
        raise
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--example', choices=['swarm-agent'])
    args = parser.parse_args()
    try:
        result = create_workspace(args.destination, args.example)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')
    print('Created workspace: ' + str(result))
    print('Next: review AGENTS.md and handover.md, initialize Git, finish planning before running shifts.')


if __name__ == '__main__':
    main()
