#!/usr/bin/env python3
"""Run configured validations and retain conservative, content-addressed evidence.

Configuration is <workspace>/validation.json. Receipts and logs are stored in
<workspace>/docs/runs/validation; completed receipts and logs are never
overwritten. Each run creates a pending receipt before launching the command,
then atomically finalizes it. A receipt is
reusable only when it is the newest receipt for its group and all recorded
inputs, tools, environment selections, log and outputs still match.
"""

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
import time
import uuid


class VerifyError(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_digest(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def safe_path(root, name, *, required=False):
    if not isinstance(name, str) or not name or Path(name).is_absolute() or ".." in Path(name).parts:
        raise VerifyError("invalid relative path: %r" % name)
    path = root
    for part in Path(name).parts:
        path = path / part
        if path.is_symlink():
            raise VerifyError("symlink path rejected: %s" % name)
    if required and not path.exists():
        raise VerifyError("missing input path: %s" % name)
    return path


def tree_hash(path):
    if path.is_symlink():
        raise VerifyError("symlink path rejected: %s" % path)
    if path.is_file():
        with path.open("rb") as stream:
            h = hashlib.sha256()
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        return {"type": "file", "sha256": h.hexdigest(), "executable_bits": path.stat().st_mode & 0o111}
    if path.is_dir():
        children = {}
        for child in sorted(path.iterdir(), key=lambda p: p.name):
            children[child.name] = tree_hash(child)
        return {"type": "directory", "executable_bits": path.stat().st_mode & 0o111,
                "children": children}
    raise VerifyError("missing or unsupported path: %s" % path)


def argv(value, field):
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x for x in value):
        raise VerifyError("%s must be a nonempty argv list" % field)
    return value


def load_group(root, name):
    config_path = safe_path(root, "validation.json", required=True)
    try:
        config = json.loads(config_path.read_text())
    except (ValueError, OSError) as exc:
        raise VerifyError("invalid validation.json: %s" % exc)
    if not isinstance(config, dict) or config.get("version") != 1 or not isinstance(config.get("groups"), dict):
        raise VerifyError("validation.json requires version 1 and groups object")
    group = config["groups"].get(name)
    if not isinstance(group, dict):
        raise VerifyError("unknown validation group: %s" % name)
    cwd = group.get("cwd", ".")
    safe_path(root, cwd, required=True)
    command = argv(group.get("command"), "command")
    inputs = group.get("inputs")
    if not isinstance(inputs, list) or not inputs or any(not isinstance(x, str) for x in inputs):
        raise VerifyError("inputs must be a nonempty path list")
    outputs = group.get("outputs", [])
    env_keys = group.get("env_keys", [])
    tools = group.get("tool_versions", [])
    if not isinstance(outputs, list) or any(not isinstance(x, str) for x in outputs):
        raise VerifyError("outputs must be a path list")
    if not isinstance(env_keys, list) or any(not isinstance(x, str) or not x for x in env_keys):
        raise VerifyError("env_keys must be a name list")
    if not isinstance(tools, list):
        raise VerifyError("tool_versions must be an argv list")
    for tool in tools:
        argv(tool, "tool_versions entry")
    for entry in inputs:
        safe_path(root, entry, required=True)
    for entry in outputs:
        safe_path(root, entry)
    timeout = group.get("timeout_seconds", 900)
    max_age = group.get("max_age_seconds", 86400)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise VerifyError("timeout_seconds must be positive")
    if isinstance(max_age, bool) or not isinstance(max_age, (int, float)) or max_age < 0:
        raise VerifyError("max_age_seconds must be nonnegative")
    if not isinstance(group.get("cache", True), bool):
        raise VerifyError("cache must be boolean")
    return {"cwd": cwd, "command": command, "inputs": inputs, "outputs": outputs,
            "env_keys": env_keys, "tool_versions": tools, "cache": group.get("cache", True),
            "timeout_seconds": timeout, "max_age_seconds": max_age}


def fingerprint(root, group):
    cwd = safe_path(root, group["cwd"], required=True)
    if not cwd.is_dir():
        raise VerifyError("cwd must be a directory")
    inputs = {name: tree_hash(safe_path(root, name, required=True)) for name in group["inputs"]}
    tools = []
    for command in group["tool_versions"]:
        try:
            result = subprocess.run(command, cwd=str(cwd), capture_output=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise VerifyError("tool version command failed: %s" % type(exc).__name__)
        if result.returncode:
            raise VerifyError("tool version command exited %s" % result.returncode)
        tools.append({"argv": command, "stdout_sha256": digest(result.stdout), "stderr_sha256": digest(result.stderr)})
    material = {"group": group, "inputs": inputs,
                "env_sha256": {key: digest(os.environ[key].encode()) if key in os.environ else None
                               for key in group["env_keys"]},
                "tools": tools, "platform": [platform.system(), platform.release(), platform.machine()],
                "verifier_sha256": digest(Path(__file__).read_bytes())}
    return json_digest(material)


def evidence_dir(root, create=False):
    path = safe_path(root, "docs/runs/validation")
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def latest_receipt(folder, group):
    if not folder.exists():
        return None
    paths = sorted(folder.glob(digest(group.encode()) + "-*.json"), reverse=True)
    if not paths:
        return None
    path = paths[0]
    try:
        record = json.loads(path.read_text())
    except (OSError, ValueError):
        return {"state": "invalid", "path": path.name}
    if (not isinstance(record, dict) or record.get("version") != 1 or
            record.get("group") != group or record.get("id") != path.stem or
            record.get("state") not in ("passed", "failed")):
        # A damaged newest receipt cannot authorize falling back to an older pass.
        return {"state": "invalid", "path": path.name}
    return record


def output_hashes(root, names):
    result = {}
    for name in names:
        path = safe_path(root, name)
        if not path.exists():
            return None
        result[name] = json_digest(tree_hash(path))
    return result


def reusable(root, folder, group, receipt, current):
    if not receipt or receipt.get("state") != "passed" or not group["cache"]:
        return False
    finished_at = receipt.get("finished_at")
    if (receipt.get("fingerprint") != current or
            isinstance(finished_at, bool) or not isinstance(finished_at, (int, float)) or
            time.time() - finished_at > group["max_age_seconds"]):
        return False
    log = receipt.get("log")
    if not isinstance(log, str) or Path(log).name != log:
        return False
    log_path = safe_path(folder, log)
    if not log_path.is_file() or digest(log_path.read_bytes()) != receipt.get("log_sha256"):
        return False
    return output_hashes(root, group["outputs"]) == receipt.get("outputs")


@contextlib.contextmanager
def run_lock(folder):
    lock_path = safe_path(folder, "run.lock")
    with lock_path.open("a+b") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


@contextlib.contextmanager
def captured_interrupts():
    received = []
    previous = {signum: signal.getsignal(signum) for signum in (signal.SIGTERM, signal.SIGINT)}

    def capture(signum, _frame):
        if not received:
            received.append(signum)

    for signum in previous:
        signal.signal(signum, capture)
    try:
        yield received
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)


def stop_process_group(process):
    for signum in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            pass
        if signum == signal.SIGTERM:
            try:
                process.wait(timeout=0.3)
            except subprocess.TimeoutExpired:
                pass
    process.wait()


def execute(root, folder, name, group, before):
    run_id = "%s-%020d-%s" % (digest(name.encode()), time.time_ns(), uuid.uuid4().hex)
    log_name = run_id + ".log"
    log_path = folder / log_name
    receipt_path = folder / (run_id + ".json")
    started_at = time.time()
    started_monotonic = time.monotonic()
    pending = {"version": 1, "id": run_id, "group": name, "state": "running",
               "fingerprint": before, "started_at": started_at}
    with receipt_path.open("x") as stream:
        json.dump(pending, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    timed_out = False
    with captured_interrupts() as interrupted:
        with log_path.open("xb") as log:
            process = None
            try:
                process = subprocess.Popen(group["command"], cwd=str(root / group["cwd"]),
                                           stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                deadline = time.monotonic() + group["timeout_seconds"]
                returncode = None
                while returncode is None and not interrupted:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        timed_out = True
                        break
                    try:
                        returncode = process.wait(timeout=min(0.1, remaining))
                    except subprocess.TimeoutExpired:
                        pass
            except OSError as exc:
                log.write(("launch error: %s\n" % exc).encode())
                returncode = 127
            finally:
                if process is not None:
                    stop_process_group(process)
            if interrupted:
                returncode = 128 + interrupted[0]
            elif timed_out:
                returncode = 124
            log.flush()
            os.fsync(log.fileno())
        if interrupted:
            outputs = None
            reason = "interrupted by signal %s" % interrupted[0]
        else:
            try:
                after = fingerprint(root, group)
                outputs = output_hashes(root, group["outputs"])
                reason = ("timeout" if timed_out else "command exited %s" % returncode if returncode else
                          "inputs, tools or environment changed during validation" if after != before else
                          "required output missing" if outputs is None else None)
            except VerifyError as exc:
                outputs = None
                reason = "post-run fingerprint failed: %s" % exc
        if interrupted:
            reason = "interrupted by signal %s" % interrupted[0]
            returncode = 128 + interrupted[0]
        state = "failed" if reason else "passed"
        finished_at = time.time()
        record = {"version": 1, "id": run_id, "group": name, "state": state,
                  "fingerprint": before, "started_at": started_at, "finished_at": finished_at,
                  "elapsed_seconds": time.monotonic() - started_monotonic, "exit_code": returncode,
                  "timed_out": timed_out, "interrupted": bool(interrupted), "reason": reason, "log": log_name,
                  "log_sha256": digest(log_path.read_bytes()), "outputs": outputs}
        with tempfile.NamedTemporaryFile(mode="w", dir=str(folder), prefix=".receipt-", delete=False) as stream:
            temp = Path(stream.name)
            json.dump(record, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        if json.loads(receipt_path.read_text()).get("state") != "running":
            raise VerifyError("pending receipt was altered before finalization")
        os.replace(str(temp), str(receipt_path))
        return {"group": name, "state": state, "receipt": receipt_path.name,
                "timed_out": timed_out, "interrupted": bool(interrupted),
                "reason": reason, "exit_code": returncode}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    actions = parser.add_subparsers(dest="action", required=True)
    run = actions.add_parser("run")
    run.add_argument("group")
    run.add_argument("--force", action="store_true")
    status = actions.add_parser("status")
    status.add_argument("group")
    args = parser.parse_args()
    root = args.workspace.resolve()
    try:
        group = load_group(root, args.group)
        folder = evidence_dir(root, create=args.action == "run")
        if args.action == "status":
            current = fingerprint(root, group)
            receipt = latest_receipt(folder, args.group)
            inspect_group = dict(group, cache=True, max_age_seconds=float("inf"))
            intact = reusable(root, folder, inspect_group, receipt, current)
            state = ("missing" if receipt is None else
                     "cached-passed" if intact and reusable(root, folder, group, receipt, current) else
                     "current" if intact else "stale")
            result = {"group": args.group, "state": state, "latest": receipt.get("state") if receipt else None,
                      "receipt": receipt.get("id") if receipt else None}
        else:
            with run_lock(folder):
                current = fingerprint(root, group)
                receipt = latest_receipt(folder, args.group)
                if not args.force and reusable(root, folder, group, receipt, current):
                    result = {"group": args.group, "state": "cached-passed", "receipt": receipt["id"] + ".json"}
                else:
                    result = execute(root, folder, args.group, group, current)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["state"] in ("passed", "cached-passed", "missing", "current", "stale") else 1
    except VerifyError as exc:
        print("verify: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
