"""Content-based delivery stagnation detection, independent of handover churn."""
import hashlib
import json
from pathlib import Path, PurePosixPath


def load(root):
    file = root / 'delivery.json'
    if not file.exists():
        return None
    if file.is_symlink():
        raise ValueError('delivery policy cannot be a symlink')
    data = json.loads(file.read_text())
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('delivery.json requires version 1')
    if set(data) - {'version', 'watch', 'stagnation_shifts', 'replan_shifts'}:
        raise ValueError('unknown delivery policy field')
    if not isinstance(data.get('watch'), list) or not data['watch']:
        raise ValueError('delivery watch must contain product paths')
    for key, default in [('stagnation_shifts', 3), ('replan_shifts', 1)]:
        data.setdefault(key, default)
        if type(data[key]) is not int or not 1 <= data[key] <= 20:
            raise ValueError('invalid ' + key)
    fingerprint(root, data)  # also validate paths
    return data


def fingerprint(root, policy):
    root = Path(root).resolve()
    records = {}
    for name in policy['watch']:
        if not isinstance(name, str) or not name:
            raise ValueError('invalid delivery path')
        relative = PurePosixPath(name)
        if relative.is_absolute() or any(x in ('.', '..', '.git', '.studio') for x in name.split('/')):
            raise ValueError('invalid delivery path: ' + name)
        path = root / name
        for parent in [path, *path.parents]:
            if parent == root:
                break
            if parent.is_symlink():
                raise ValueError('symlinks cannot be delivery inputs')
        if not path.exists():
            records[name] = 'missing'
            continue
        paths = sorted(path.rglob('*')) if path.is_dir() else [path]
        for item in paths:
            if item.is_symlink():
                raise ValueError('symlinks cannot be delivery inputs')
            if item.is_file():
                records[item.relative_to(root).as_posix()] = hashlib.sha256(item.read_bytes()).hexdigest()
            elif not item.is_dir():
                raise ValueError('nonregular delivery input')
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def advance(previous, before, after, policy):
    count = previous.get('stagnant_shifts', 0) + 1 if before == after else 0
    limit = policy['stagnation_shifts']
    action = 'pause' if count >= limit + policy['replan_shifts'] else 'replan' if count >= limit else 'continue'
    return {'fingerprint': after, 'stagnant_shifts': count, 'action': action}
