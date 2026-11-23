import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

from PIL import Image


def identifier(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", value):
        raise ValueError(f"Invalid ID: {value!r}")
    return value


def relative(value):
    p = Path(value)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError(f"Expected a relative bundle path: {value!r}")
    return p.as_posix()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as temp:
        temp.write(body)
    Path(temp.name).replace(path)


def write_json(path, value):
    write(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def versions(graphic):
    paths = graphic.glob("versions/[!.]*/version.json")
    return sorted((read(p) for p in paths), key=lambda v: v["sequence"], reverse=True)


def hashes(folder):
    files = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Package linked content as real files: {path}")
        if path.is_file():
            files[path.relative_to(folder).as_posix()] = digest(path)
    return files


def verified(graphic, key):
    archive = graphic / "versions" / identifier(key)
    record = read(archive / "version.json")
    if (record["id"] != key or hashes(archive / "bundle") != record["files"]
            or any(path not in record["files"] for path in record["roles"].values())):
        raise ValueError(f"Missing or altered snapshot files: {graphic.name}/{key}")
    return record


def save(studio, graphic, args, working):
    archive = graphic / "versions"
    archive.mkdir(exist_ok=True)
    target = archive / args.version
    if target.exists():
        raise ValueError("Choose an unused version ID.")
    bundle = args.bundle.resolve(strict=True)
    if not bundle.is_dir() or archive.resolve().is_relative_to(bundle):
        raise ValueError("Supply a self-contained working bundle outside the archive.")
    parents = list(dict.fromkeys(args.parent or ([working] if working else [])))
    origin = bundle / ".studio-origin.json"
    if origin.is_file():
        restored = read(origin)
        if restored["graphic"] != graphic.name:
            raise ValueError("Restored bundle belongs to another graphic.")
        if not args.parent:
            parents = [restored["version"]]
    ancestors = [verified(graphic, parent) for parent in parents]
    before = hashes(bundle)
    before.pop(".studio-origin.json", None)
    roles = {"master": relative(args.master), "proof": relative(args.proof),
             "preview": relative(args.preview)}
    if not all(path in before for path in roles.values()):
        raise ValueError("Master, proof and destination preview must exist in the bundle.")
    for role in ("preview", "proof"):
        with Image.open(bundle / roles[role]) as im:
            im.verify()
    deps = {}
    inherited = {}
    for parent in ancestors:
        for key, dep in parent["shared"].items():
            inherited.setdefault(key, []).append(dep)
    for spec in args.shared:
        key, sep, path = spec.partition("=")
        if not sep:
            raise ValueError("Use --shared library/path=bundle/path.")
        key, path = relative(key), relative(path)
        actual = before.get(path)
        if not actual or (not any(dep["sha256"] == actual for dep in inherited.get(key, []))
                          and actual != digest(studio / "library" / key)):
            raise ValueError(f"Bundled shared asset differs from library: {key}")
        deps[key] = {"path": path, "sha256": actual}
    dropped = set(args.drop_shared)
    if dropped.intersection(deps) or dropped.difference(inherited):
        raise ValueError("Drop only a previously used dependency that is no longer declared.")
    for key, candidates in inherited.items():
        if key in deps or key in dropped:
            continue
        matches = [dep for dep in candidates if before.get(dep["path"]) == dep["sha256"]]
        if not matches or any(dep != matches[0] for dep in matches):
            raise ValueError(f"Resolve changed dependency {key} with --shared or --drop-shared.")
        deps[key] = matches[0]
    history = versions(graphic)
    with tempfile.TemporaryDirectory(prefix=".stage-", dir=archive) as tmp:
        stage = Path(tmp) / "version"
        payload = stage / "bundle"
        shutil.copytree(bundle, payload, ignore=shutil.ignore_patterns(".studio-origin.json"))
        if hashes(payload) != before:
            raise ValueError("Bundle changed while saving.")
        record = dict(id=args.version, sequence=history[0]["sequence"] + 1 if history else 1,
                      study=args.study, parents=parents, note=args.note, roles=roles,
                      files=before, shared=deps)
        write_json(stage / "version.json", record)
        stage.rename(target)


def restore(studio, graphic, version, destination):
    verified(graphic, version)
    if destination.is_symlink():
        raise ValueError("Restore into a new folder, not a symbolic link.")
    destination = destination.resolve()
    if destination.exists() or destination.is_relative_to(studio.resolve()) or destination.is_relative_to((studio.parent / "deliverables").resolve()):
        raise ValueError("Restore into a new working folder outside studio records and releases.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    archive = graphic / "versions" / version
    with tempfile.TemporaryDirectory(prefix=".restore-", dir=destination.parent) as tmp:
        copy = Path(tmp) / "bundle"
        shutil.copytree(archive / "bundle", copy)
        if hashes(copy) != read(archive / "version.json")["files"]:
            raise ValueError("Restored files differ from the snapshot.")
        write_json(copy / ".studio-origin.json", {"graphic": graphic.name, "version": version})
        copy.rename(destination)
