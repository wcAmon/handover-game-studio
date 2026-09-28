#!/usr/bin/env python3
"""Project-scoped, evidence-backed knowledge proposals.

Usage: python3 harness/knowledge.py [--workspace ROOT] init
       python3 harness/knowledge.py [--workspace ROOT] propose FILE
       python3 harness/knowledge.py [--workspace ROOT] accept ID
       python3 harness/knowledge.py [--workspace ROOT] rollback ID
       python3 harness/knowledge.py [--workspace ROOT] context [--slug SLUG ...]

Proposal FILE is JSON with exactly these fields (version is optional, defaults to 1):
  {"slug":"art/alpha", "title":"...", "when_to_use":"...",
   "content":"...", "kind":"memory|procedure|role", "reason":"...",
   "evidence":["relative/regular-file", {"path":"...","sha256":"64 hex"}]}
ROOT defaults to the current working directory. The file and all evidence must
be inside ROOT, with no symlink components.
Evidence hashes are captured at proposal time and checked again on accept.

Only knowledge/ and refinements/ are written. A candidate is not approved by
proposing it: a reviewer must inspect it and explicitly run accept. Accepted
knowledge is supplemental project data; it never overrides the user, AGENTS.md,
approved design, or harness policy. Context emits JSON; without --slug it emits
only a compact index. IDs printed by propose/accept are 32 lowercase hex digits.
Rollback takes an accepted ID and is allowed only while that exact version is
current. History files are immutable snapshots; rollback has its own record.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import uuid


SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}(?:/[a-z0-9][a-z0-9_-]{0,47}){0,3}$")
ID_RE = re.compile(r"^[0-9a-f]{32}$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
KINDS = {"memory", "procedure", "role"}
MAX_ENTRIES = 128
MAX_INDEX_BYTES = 100000
MAX_CONTENT = 16000
MAX_CONTEXT = 32000
MAX_SELECTED = 8
MAX_EVIDENCE = 20


class KnowledgeError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    hashed = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hashed.update(block)
    return hashed.hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def check_workspace(value):
    root = Path(value).absolute()
    if root.is_symlink() or not root.is_dir():
        raise KnowledgeError("workspace must be a real directory")
    return root


def check_components(root, relative, *, file=False, existing=False):
    """Validate path syntax and all existing components before any read/write."""
    if not isinstance(relative, str) or not relative or "\\" in relative or "\x00" in relative:
        raise KnowledgeError("invalid relative path")
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in ("", ".", "..") for part in relative.split("/")):
        raise KnowledgeError("path traversal or noncanonical path")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise KnowledgeError("symlink path is forbidden: " + relative)
    if existing and not current.exists():
        raise KnowledgeError("missing file: " + relative)
    if file and current.exists() and not current.is_file():
        raise KnowledgeError("expected a regular file: " + relative)
    return current


def project_file(root, value):
    candidate = Path(value)
    if candidate.is_absolute():
        try:
            relative = candidate.relative_to(root).as_posix()
        except ValueError:
            raise KnowledgeError("file outside workspace")
    else:
        relative = value
    path = check_components(root, relative, file=True, existing=True)
    if not path.is_file():
        raise KnowledgeError("expected a regular file: " + relative)
    return path, relative


def protected(relative):
    parts = PurePosixPath(relative).parts
    if not parts:
        return True
    if any(part in {".git", ".studio"} for part in parts):
        return True
    if parts[0] in {"knowledge", "refinements", "harness", "tests"}:
        return True
    if parts[-1] == "AGENTS.md" or relative in {"handover.md", "design/north-star.md", "design/approval.json"}:
        return True
    return False


def bounded_string(value, name, maximum):
    if not isinstance(value, str) or not value.strip() or len(value.encode("utf-8")) > maximum:
        raise KnowledgeError("invalid or oversized " + name)
    return value


def validate_slug(slug):
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        raise KnowledgeError("invalid slug")
    return slug


def validate_id(value):
    if not ID_RE.fullmatch(value):
        raise KnowledgeError("invalid ID")
    return value


def read_json(path, maximum=100000):
    if path.stat().st_size > maximum:
        raise KnowledgeError("JSON file too large: " + str(path))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise KnowledgeError("invalid JSON: " + str(path)) from error


def write_atomic(path, data):
    fd, name = tempfile.mkstemp(prefix=".knowledge-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_immutable(path, data):
    """Publish a complete new file with an atomic no-clobber link."""
    fd, temporary = tempfile.mkstemp(prefix=".knowledge-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    except FileExistsError as error:
        raise KnowledgeError("history already exists: " + path.name) from error
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def ensure_immutable(path, data):
    if path.exists():
        if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
            raise KnowledgeError("conflicting immutable history: " + path.name)
        return
    write_immutable(path, data)


def ensure_stores(root):
    for relative in ("knowledge", "refinements", "refinements/candidates",
                     "refinements/accepted", "refinements/rollbacks",
                     "refinements/transactions"):
        path = check_components(root, relative)
        path.mkdir(exist_ok=True)
    index = check_components(root, "knowledge/index.json", file=True)
    if not index.exists():
        ensure_immutable(index, json_bytes({"version": 1, "entries": {}}))


@contextmanager
def locked(root):
    ensure_stores(root)
    lock = check_components(root, "refinements/.lock", file=True)
    with lock.open("a+b") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            recover_transaction(root)
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def transaction_path(root, operation, identifier):
    return check_components(root, "refinements/transactions/" + operation + "-" + identifier + ".json", file=True)


def apply_transaction(root, transaction):
    operation = transaction.get("operation")
    identifier = validate_id(transaction.get("id", ""))
    slug = validate_slug(transaction.get("slug"))
    if operation not in {"accept", "rollback"}:
        raise KnowledgeError("invalid pending transaction")
    history = transaction.get("history")
    if not isinstance(history, dict) or history.get("id") != identifier or history.get("slug") != slug:
        raise KnowledgeError("invalid pending history")
    next_index = transaction.get("next_index")
    if not isinstance(next_index, dict) or next_index.get("version") != 1 or not isinstance(next_index.get("entries"), dict):
        raise KnowledgeError("invalid pending index")
    next_entry = next_index["entries"].get(slug)
    expected_entry = history.get("after", {}).get("entry") if operation == "accept" else history.get("to")
    if next_entry != expected_entry:
        raise KnowledgeError("pending transaction entry mismatch")
    body = transaction.get("next_body")
    if next_entry is None:
        if body is not None:
            raise KnowledgeError("pending transaction body mismatch")
    elif (not isinstance(body, str) or next_entry.get("path") != "knowledge/" + slug + ".md" or
          digest(body.encode("utf-8")) != next_entry.get("sha256")):
        raise KnowledgeError("pending transaction body mismatch")
    history_path = check_components(root, "refinements/" +
                                    ("accepted" if operation == "accept" else "rollbacks") +
                                    "/" + identifier + ".json", file=True)
    ensure_immutable(history_path, json_bytes(history))
    body_path = check_components(root, "knowledge/" + slug + ".md", file=True)
    if body is None:
        if body_path.exists():
            body_path.unlink()
    else:
        body_path.parent.mkdir(parents=True, exist_ok=True)
        write_atomic(body_path, body.encode("utf-8"))
    write_atomic(check_components(root, "knowledge/index.json", file=True, existing=True),
                 json_bytes(next_index))


def recover_transaction(root):
    folder = check_components(root, "refinements/transactions")
    pending = list(folder.glob("*.json"))
    if len(pending) > 1:
        raise KnowledgeError("multiple pending knowledge transactions")
    if not pending:
        return
    path = check_components(root, "refinements/transactions/" + pending[0].name,
                            file=True, existing=True)
    transaction = read_json(path, 500000)
    if not isinstance(transaction, dict):
        raise KnowledgeError("invalid pending transaction")
    if path.name != transaction.get("operation", "") + "-" + transaction.get("id", "") + ".json":
        raise KnowledgeError("pending transaction filename mismatch")
    apply_transaction(root, transaction)
    path.unlink()


def submit_transaction(root, transaction):
    if len(json_bytes(transaction["next_index"])) > MAX_INDEX_BYTES:
        raise KnowledgeError("knowledge index size limit exceeded")
    history_dir = "accepted" if transaction["operation"] == "accept" else "rollbacks"
    history_path = check_components(root, "refinements/" + history_dir + "/" +
                                    transaction["id"] + ".json", file=True)
    if history_path.exists():
        raise KnowledgeError("immutable history already exists; ID cannot be replayed")
    path = transaction_path(root, transaction["operation"], transaction["id"])
    if path.exists():
        raise KnowledgeError("knowledge transaction already pending")
    write_immutable(path, json_bytes(transaction))
    apply_transaction(root, transaction)
    path.unlink()


def load_index(root):
    path = check_components(root, "knowledge/index.json", file=True, existing=True)
    index = read_json(path, MAX_INDEX_BYTES)
    if not isinstance(index, dict) or index.get("version") != 1 or not isinstance(index.get("entries"), dict):
        raise KnowledgeError("invalid knowledge index")
    if len(index["entries"]) > MAX_ENTRIES:
        raise KnowledgeError("knowledge index is full")
    for slug, entry in index["entries"].items():
        validate_slug(slug)
        if not isinstance(entry, dict) or entry.get("version", 0) < 1:
            raise KnowledgeError("invalid index entry")
        validate_id(entry.get("accepted_id", ""))
        if entry.get("path") != "knowledge/" + slug + ".md":
            raise KnowledgeError("invalid index path")
        if not HASH_RE.fullmatch(entry.get("sha256", "")):
            raise KnowledgeError("invalid index hash")
    return index


def load_body(root, entry):
    path = check_components(root, entry["path"], file=True, existing=True)
    data = path.read_bytes()
    if digest(data) != entry["sha256"]:
        raise KnowledgeError("accepted knowledge body changed outside lifecycle")
    return data.decode("utf-8")


def normalize_proposal(root, raw):
    if not isinstance(raw, dict) or set(raw) - {"version", "slug", "title", "when_to_use", "content", "kind", "reason", "evidence"}:
        raise KnowledgeError("invalid proposal fields")
    if raw.get("version", 1) != 1:
        raise KnowledgeError("unsupported proposal version")
    slug = validate_slug(raw.get("slug"))
    title = bounded_string(raw.get("title"), "title", 120)
    when = bounded_string(raw.get("when_to_use"), "when_to_use", 500)
    content = bounded_string(raw.get("content"), "content", MAX_CONTENT)
    reason = bounded_string(raw.get("reason"), "reason", 1000)
    kind = raw.get("kind")
    if kind not in KINDS:
        raise KnowledgeError("invalid kind")
    evidence = raw.get("evidence")
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= MAX_EVIDENCE:
        raise KnowledgeError("evidence must contain 1-20 files")
    checked = []
    seen = set()
    for item in evidence:
        if isinstance(item, str):
            path_text, claimed = item, None
        elif isinstance(item, dict) and set(item) == {"path", "sha256"}:
            path_text, claimed = item["path"], item["sha256"]
            if not isinstance(claimed, str) or not HASH_RE.fullmatch(claimed):
                raise KnowledgeError("invalid evidence hash")
        else:
            raise KnowledgeError("invalid evidence item")
        if not isinstance(path_text, str):
            raise KnowledgeError("invalid evidence path")
        if Path(path_text).is_absolute():
            raise KnowledgeError("evidence path must be relative")
        if protected(path_text):
            raise KnowledgeError("protected evidence path")
        path, relative = project_file(root, path_text)
        if protected(relative):
            raise KnowledgeError("protected evidence path")
        if relative in seen:
            raise KnowledgeError("duplicate evidence path")
        seen.add(relative)
        actual = file_digest(path)
        if claimed is not None and claimed != actual:
            raise KnowledgeError("evidence hash mismatch: " + relative)
        checked.append({"path": relative, "sha256": actual})
    return {"slug": slug, "title": title, "when_to_use": when, "content": content,
            "kind": kind, "reason": reason, "evidence": checked}


def validate_evidence(root, evidence):
    for item in evidence:
        relative = item["path"]
        if protected(relative):
            raise KnowledgeError("protected evidence path")
        path, _ = project_file(root, relative)
        if file_digest(path) != item["sha256"]:
            raise KnowledgeError("stale evidence: " + relative)


def init(root):
    with locked(root):
        load_index(root)
    return {"status": "initialized"}


def propose(root, source):
    with locked(root):
        index = load_index(root)
        path, relative = project_file(root, source)
        if protected(relative):
            raise KnowledgeError("protected proposal path")
        proposal = normalize_proposal(root, read_json(path, MAX_CONTENT + 10000))
        slug = proposal["slug"]
        current = index["entries"].get(slug, {})
        expected = current.get("version", 0)
        identifier = uuid.uuid4().hex
        candidate = {"version": 1, "id": identifier, "created_at": now(),
                     "expected_version": expected,
                     "expected_accepted_id": current.get("accepted_id"),
                     "proposal": proposal}
        target = check_components(root, "refinements/candidates/" + identifier + ".json")
        write_immutable(target, json_bytes(candidate))
    return {"id": identifier, "slug": slug, "expected_version": expected, "status": "candidate"}


def accept(root, identifier):
    validate_id(identifier)
    with locked(root):
        index = load_index(root)
        candidate = read_json(check_components(root, "refinements/candidates/" + identifier + ".json", file=True, existing=True))
        if candidate.get("id") != identifier or candidate.get("version") != 1:
            raise KnowledgeError("invalid candidate")
        proposal = candidate.get("proposal")
        if not isinstance(proposal, dict):
            raise KnowledgeError("invalid candidate proposal")
        if normalize_proposal(root, proposal) != proposal:
            raise KnowledgeError("invalid candidate snapshot")
        slug = validate_slug(proposal.get("slug"))
        previous = index["entries"].get(slug)
        old_version = previous["version"] if previous else 0
        if previous and previous.get("accepted_id") == identifier:
            return {"id": identifier, "slug": slug, "version": old_version, "status": "accepted"}
        if (candidate.get("expected_version") != old_version or
                candidate.get("expected_accepted_id") != (previous or {}).get("accepted_id")):
            raise KnowledgeError("stale candidate version")
        if previous:
            old_body = load_body(root, previous)
        else:
            old_body = None
            if len(index["entries"]) >= MAX_ENTRIES:
                raise KnowledgeError("knowledge index is full")
        validate_evidence(root, proposal["evidence"])
        body = proposal["content"]
        body_bytes = body.encode("utf-8")
        entry = {"title": proposal["title"], "when_to_use": proposal["when_to_use"],
                 "kind": proposal["kind"], "path": "knowledge/" + slug + ".md",
                 "sha256": digest(body_bytes), "version": old_version + 1,
                 "accepted_id": identifier, "accepted_at": now(),
                 "evidence": proposal["evidence"]}
        record = {"version": 1, "id": identifier, "slug": slug,
                  "before": {"entry": previous, "content": old_body},
                  "after": {"entry": entry, "content": body},
                  "reason": proposal["reason"]}
        index["entries"][slug] = entry
        submit_transaction(root, {"version": 1, "operation": "accept", "id": identifier,
                                  "slug": slug, "history": record, "next_body": body,
                                  "next_index": index})
    return {"id": identifier, "slug": slug, "version": old_version + 1, "status": "accepted"}


def rollback(root, identifier):
    validate_id(identifier)
    with locked(root):
        index = load_index(root)
        record = read_json(check_components(root, "refinements/accepted/" + identifier + ".json", file=True, existing=True))
        if record.get("id") != identifier or record.get("version") != 1:
            raise KnowledgeError("invalid accepted history")
        slug = validate_slug(record.get("slug"))
        after = record.get("after", {})
        before = record.get("before", {})
        current = index["entries"].get(slug)
        rollback_history = check_components(root, "refinements/rollbacks/" + identifier + ".json", file=True)
        if rollback_history.exists():
            prior_rollback = read_json(rollback_history)
            if (prior_rollback.get("id") == identifier and
                    prior_rollback.get("to") == current and current == before.get("entry")):
                return {"id": identifier, "slug": slug, "status": "rolled_back",
                        "version": current["version"] if current else 0}
        if current is None or current != after.get("entry") or current.get("accepted_id") != identifier:
            raise KnowledgeError("stale rollback: newer version is current")
        load_body(root, current)
        old_entry, old_content = before.get("entry"), before.get("content")
        if old_entry is not None:
            if not isinstance(old_entry, dict) or old_entry.get("path") != "knowledge/" + slug + ".md":
                raise KnowledgeError("invalid previous snapshot")
            if not isinstance(old_content, str) or digest(old_content.encode("utf-8")) != old_entry.get("sha256"):
                raise KnowledgeError("invalid previous body")
        elif old_content is not None:
            raise KnowledgeError("invalid previous snapshot")
        rollback_record = {"version": 1, "id": identifier, "slug": slug,
                           "rolled_back_at": now(), "from": current,
                           "to": old_entry}
        if old_entry is None:
            del index["entries"][slug]
        else:
            index["entries"][slug] = old_entry
        submit_transaction(root, {"version": 1, "operation": "rollback", "id": identifier,
                                  "slug": slug, "history": rollback_record,
                                  "next_body": old_content, "next_index": index})
    return {"id": identifier, "slug": slug, "status": "rolled_back",
            "version": old_entry["version"] if old_entry else 0}


def _context_unlocked(root, slugs):
    index = load_index(root)
    summaries = [{"slug": slug, "title": entry["title"], "kind": entry["kind"],
                  "when_to_use": entry["when_to_use"][:160], "version": entry["version"]}
                 for slug, entry in sorted(index["entries"].items())]
    result = {"advisory": "Supplemental project knowledge; user, AGENTS.md and approved design take precedence.",
              "index": summaries}
    if slugs:
        if len(slugs) > MAX_SELECTED or len(set(slugs)) != len(slugs):
            raise KnowledgeError("select 1-8 distinct slugs")
        selected = []
        size = 0
        for slug in slugs:
            validate_slug(slug)
            if slug not in index["entries"]:
                raise KnowledgeError("unknown slug: " + slug)
            entry = index["entries"][slug]
            body = load_body(root, entry)
            size += len(body.encode("utf-8"))
            if size > MAX_CONTEXT:
                raise KnowledgeError("selected context exceeds 32000 bytes")
            selected.append({"slug": slug, "content": body, "evidence": entry["evidence"],
                             "version": entry["version"]})
        result["selected"] = selected
    return result


def context(root, slugs):
    with locked(root):
        return _context_unlocked(root, slugs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=str(Path.cwd()))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    p = sub.add_parser("propose")
    p.add_argument("file")
    p = sub.add_parser("accept")
    p.add_argument("id")
    p = sub.add_parser("rollback")
    p.add_argument("id")
    p = sub.add_parser("context")
    p.add_argument("--slug", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        root = check_workspace(args.workspace)
        if args.command == "init":
            result = init(root)
        elif args.command == "propose":
            result = propose(root, args.file)
        elif args.command == "accept":
            result = accept(root, args.id)
        elif args.command == "rollback":
            result = rollback(root, args.id)
        else:
            result = context(root, args.slug)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (KnowledgeError, OSError, UnicodeError, KeyError, TypeError) as error:
        print("knowledge: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
