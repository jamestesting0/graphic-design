# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=10"]
# ///
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import shutil
import sys
import tempfile
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageOps

from versions import digest, hashes, identifier, read, relative, restore, save, verified, versions, write, write_json


STATUSES = ("drafting", "awaiting selection", "in review", "changes requested", "complete")


def new_use():
    return {"stage": "brief", "status": "drafting", "working": None, "approval": None,
            "next": "Establish the audience, destination and first creative choice."}


def init_graphic(studio, key):
    graphic = studio / "graphics" / key
    if (graphic / "state.json").is_file():
        return
    if graphic.exists():
        raise ValueError(f"Existing unregistered folder: {graphic}")
    graphic.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=graphic.parent, prefix=".init-") as tmp:
        staged = Path(tmp) / key
        write(staged / "brief.md", f"# {key}\n\nAudience and use\n\nFormats and required content\n\nReferences, source roles and local art direction\n")
        write(staged / "plan.md", f"# Production plan for {key}\n\n| Stage | Artifact | Creative decision | Proof surface | Exit condition |\n|---|---|---|---|---|\n")
        write_json(staged / "state.json", {"uses": {"main": new_use()}, "pins": []})
        staged.rename(graphic)


def seed(path, contents):
    if not path.exists():
        write(path, contents)


def cell(value):
    return " ".join(value.split()).replace("|", "\\|")


def proof_link(graphic, version):
    if not version:
        return "—"
    entry = graphic / "versions" / version
    proof = relative(read(entry / "version.json")["roles"]["proof"])
    return f"[{version}](graphics/{graphic.name}/versions/{version}/bundle/{quote(proof)})"


def graphics(studio):
    return sorted(p.parent for p in studio.glob("graphics/[!.]*/state.json"))


def board(studio):
    seed(studio / "library/assets.md", "# Asset register\n\n"
         "Add an entry when a supplied, found or studio-created asset enters the commission. "
         "Use relative library paths for stored files. A reference can be a source link.\n\n"
         "| Asset | Origin and source | Intended use and credit | Graphics and role |\n"
         "|---|---|---|---|\n")
    delivered = {}
    for path in studio.parent.glob("deliverables/[!.]*/manifest.json"):
        try:
            package = read(path)
        except (UnicodeError, json.JSONDecodeError):
            print(f"Unreadable delivery manifest: {path}", file=sys.stderr)
            continue
        if not isinstance(package, dict) or package.get("format") != "graphic-design-release-v1":
            continue
        for item, entry in package["items"].items():
            stamp = (package["published_at"], path.parent.name, entry["version"])
            if item not in delivered or stamp > delivered[item]:
                delivered[item] = stamp
    lines = ["# Studio board", "", "[Collection plan](collection-plan.md) · [Shared direction](art-direction.md) · [Asset register](library/assets.md)", "",
             "| Graphic / use | Stage | Work status | Working | Approved | Last delivery | Next decision |",
             "|---|---|---|---|---|---|---|"]
    gallery_links = []
    for graphic in graphics(studio):
        state = read(graphic / "state.json")
        pinned = set(state["pins"])
        for use, work in state["uses"].items():
            approved = work["approval"]
            pinned.update(entry["version"] for entry in work.get("earlier_approvals", []))
            if approved:
                pinned.add(approved["version"])
            delivery = delivered.get(f"{graphic.name}/{use}")
            delivery_link = "—"
            next_step = work["next"]
            if delivery:
                _, release_id, shipped = delivery
                delivery_link = f"[{release_id} · {shipped}](../deliverables/{quote(release_id)}/manifest.json)"
                if approved and approved["version"] == shipped and next_step == "Ready for packaging.":
                    next_step = "Delivered."
            lines.append("| " + " | ".join([f"[{graphic.name}](graphics/{graphic.name}/plan.md) / {use}",
                cell(work["stage"]), work["status"], proof_link(graphic, work["working"]),
                proof_link(graphic, approved["version"] if approved else None), delivery_link, cell(next_step)]) + " |")
        history = versions(graphic)
        for study in sorted({r["study"] for r in history}):
            gallery_links.append(f"- [{graphic.name} / {study}](graphics/{graphic.name}/studies/{study}/gallery.md)")
            rows = [r for r in history if r["study"] == study]
            gallery = [f"# {study}", ""]
            older = rows[5:]
            for heading, group in (("Latest five", rows[:5]), ("Earlier favorites", [r for r in older if r["id"] in pinned]),
                                   ("Earlier versions", [r for r in older if r["id"] not in pinned])):
                if not group:
                    continue
                gallery += [f"## {heading}", ""]
                for r in group:
                    key = r["id"]
                    link = f"../../versions/{key}/bundle/"
                    roles = r["roles"]
                    pin = " (pinned)" if key in pinned else ""
                    gallery += [f"**{key}{pin}** · parents: {', '.join(r['parents']) or '—'} · {r['note']}",
                                "", f"[Master]({link}{quote(roles['master'])}) · [Proof]({link}{quote(roles['proof'])})", ""]
                    if heading != "Earlier versions":
                        gallery += [f"![{key}]({link}{quote(roles['preview'])})", ""]
            write(graphic / "studies" / study / "gallery.md", "\n".join(gallery))
    if gallery_links:
        lines.extend(["", "## Study galleries", "", *gallery_links])
    body = "\n".join(lines) + "\n"
    write(studio / "studio.md", body)
    return body


def selected(studio, items):
    result = []
    for item in dict.fromkeys(items):
        key, sep, use = item.partition("/")
        if not sep:
            raise ValueError("Select an approved graphic/use pair.")
        graphic = studio / "graphics" / identifier(key)
        approval = read(graphic / "state.json")["uses"][identifier(use)]["approval"]
        if not approval:
            raise ValueError(f"Approval missing: {item}")
        version = verified(graphic, approval["version"])
        result.append((item, graphic / "versions" / version["id"], version, approval))
    return result


def contact_sheet(selection, path):
    if path.suffix.lower() != ".png":
        raise ValueError("Use a .png contact-sheet path.")
    cols = min(3, len(selection))
    sheet = Image.new("RGB", (cols * 440, ((len(selection) + cols - 1) // cols) * 300), "#eeeeea")
    draw = ImageDraw.Draw(sheet)
    for index, (item, archive, r, _) in enumerate(selection):
        x, y = index % cols * 440, index // cols * 300
        with Image.open(archive / "bundle" / r["roles"]["preview"]) as preview:
            tile = ImageOps.contain(preview.convert("RGBA"), (420, 255))
            sheet.paste(tile, (x + (440 - tile.width) // 2, y + 8), tile)
        draw.text((x + 10, y + 269), f"{item}  |  {r['id']}", fill="#17191c")
    sheet.save(path)


def release(studio, key, selection, reviewed_sheet):
    folder = studio.parent / "deliverables"
    folder.mkdir(exist_ok=True)
    dest = folder / key
    if dest.exists():
        raise ValueError("Release already exists. Use a new ID.")
    with tempfile.TemporaryDirectory(prefix=".publish-", dir=folder) as tmp:
        stage = Path(tmp) / "release"
        stage.mkdir()
        manifest = {"format": "graphic-design-release-v1", "release": key,
                    "published_at": datetime.now(timezone.utc).isoformat(), "items": {}}
        for item, archive, version, approval in selection:
            target = stage / item
            shutil.copytree(archive / "bundle", target)
            if hashes(target) != version["files"]:
                raise ValueError(f"Packaged files differ: {item}")
            manifest["items"][item] = {"version": version["id"], "roles": version["roles"],
                "files": version["files"], "shared": version["shared"], "approval": approval}
        contact_sheet(selection, stage / "contact-sheet.png")
        manifest["contact_sheet_sha256"] = digest(stage / "contact-sheet.png")
        if manifest["contact_sheet_sha256"] != digest(reviewed_sheet):
            raise ValueError("The proposed release differs from the reviewed contact sheet. Recheck the selection.")
        write_json(stage / "manifest.json", manifest)
        stage.rename(dest)
    return dest


@contextmanager
def studio_lock(studio):
    with (studio / ".lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def execute(studio, args):
    op = args.command
    if op == "init":
        seed(studio / "collection-plan.md", f"# Collection plan\n\n{args.intent}\n\n## Deliverables, order and dependencies\n")
        seed(studio / "art-direction.md", "# Shared art direction\n\nAudience, destinations, references, materials and shared decisions.\n")
        (studio / "library").mkdir(exist_ok=True)
        for key in args.graphics:
            init_graphic(studio, key)
    elif op == "add":
        init_graphic(studio, args.graphic)
    elif op == "status":
        print(board(studio), end="")
        return
    elif op in ("release", "sheet"):
        selection = selected(studio, args.items)
        if op == "release":
            print(release(studio, args.release_id, selection, args.reviewed_sheet))
            board(studio)
        else:
            if args.out.exists():
                raise ValueError("Select an unused sheet path.")
            contact_sheet(selection, args.out)
        return
    elif op == "consumers":
        key = relative(args.asset)
        for graphic in graphics(studio):
            for use, work in read(graphic / "state.json")["uses"].items():
                approval = work["approval"]
                for role, version in (("working", work["working"]), ("approved", approval and approval["version"])):
                    if version:
                        dep = read(graphic / "versions" / version / "version.json")["shared"].get(key)
                        if dep:
                            print(graphic.name, use, role, version, dep["sha256"])
        return
    else:
        graphic = studio / "graphics" / args.graphic
        state = read(graphic / "state.json")
        use = getattr(args, "use", "main")
        if use not in state["uses"] and op not in ("approve", "select"):
            raise ValueError("Unknown use. Select a saved version to create the use.")
        work = state["uses"].setdefault(use, new_use())
        if op == "save":
            save(studio, graphic, args, work["working"])
        elif op == "keep":
            verified(graphic, args.version)
            if args.version not in state["pins"]:
                state["pins"].append(args.version)
        elif op == "update":
            work.update(stage=args.stage, status=args.status, next=args.next)
        elif op in ("restore", "select"):
            if op == "restore":
                restore(studio, graphic, args.version, args.to)
            else:
                verified(graphic, args.version)
            work.update(working=args.version, stage="revision", status="drafting", next=args.next)
        elif op == "approve":
            record = verified(graphic, args.version)
            review = read(args.review)
            proof_hash = record["files"][record["roles"]["proof"]]
            if (not isinstance(review, dict) or review.get("graphic") != graphic.name
                    or review.get("version") != args.version or review.get("proof_sha256") != proof_hash
                    or review.get("verdict") != "advance"
                    or not all(isinstance(review.get(k), str) and review[k].strip() for k in ("reviewer", "finding"))):
                raise ValueError("Approval requires an advance finding bound to this version and proof digest.")
            selector = args.by.strip()
            if not selector:
                raise ValueError("Name the person or delegated maker who selected this version.")
            approval = {"version": args.version, "selected_by": selector, "review": review}
            current = work["approval"]
            if current and all(current[k] == value for k, value in approval.items()):
                approval = current
            else:
                approval["selected_at"] = datetime.now(timezone.utc).isoformat()
                if current:
                    work.setdefault("earlier_approvals", []).append(current)
            work.update(working=args.version, approval=approval, stage="delivery", status="complete", next="Ready for packaging.")
        write_json(graphic / "state.json", state)
    board(studio)


def parser():
    cli = argparse.ArgumentParser(prog="graphic-design", description="Manage a local multi-graphic design studio (Python 3.11+, macOS/Linux).")
    cli.add_argument("--project", type=Path, default=Path.cwd())
    sub = cli.add_subparsers(dest="command", required=True)
    sub.add_parser("skills-path", help="print the directory containing the installed agent skills")
    init = sub.add_parser("init", help="start or resume a collection without replacing briefs")
    init.add_argument("--intent", required=True)
    init.add_argument("graphics", nargs="+", type=identifier)
    sub.add_parser("status", help="rebuild galleries and the board from saved records")
    sub.add_parser("consumers", help="list working and approved consumers of a library path").add_argument("asset")
    for op in ("add", "save", "keep", "select", "update", "restore", "approve"):
        cmd = sub.add_parser(op)
        cmd.add_argument("graphic", type=identifier)
        if op not in ("add", "update"):
            cmd.add_argument("version", type=identifier)
        if op not in ("add", "keep"):
            cmd.add_argument("--use", type=identifier, default="main")
        if op in ("restore", "select", "update"):
            cmd.add_argument("--next", required=True)
        if op == "save":
            cmd.add_argument("--bundle", required=True, type=Path)
            for role in ("master", "preview", "proof", "note"):
                cmd.add_argument("--" + role, required=True)
            cmd.add_argument("--study", required=True, type=identifier)
            cmd.add_argument("--parent", action="append", type=identifier)
            cmd.add_argument("--shared", action="append", default=[])
            cmd.add_argument("--drop-shared", action="append", default=[], type=relative)
        if op == "restore":
            cmd.add_argument("--to", type=Path, required=True)
        if op == "approve":
            cmd.add_argument("--by", required=True)
            cmd.add_argument("--review", required=True, type=Path)
        if op == "update":
            cmd.add_argument("--stage", required=True)
            cmd.add_argument("--status", choices=STATUSES, required=True)
    for op in ("release", "sheet"):
        cmd = sub.add_parser(op)
        if op == "release":
            cmd.add_argument("release_id", type=identifier)
            cmd.add_argument("--reviewed-sheet", type=Path, required=True)
        else:
            cmd.add_argument("--out", type=Path, required=True)
        cmd.add_argument("items", nargs="+", metavar="graphic/use")
    return cli


def main():
    cli = parser()
    args = cli.parse_args()
    if args.command == "skills-path":
        print(Path(__file__).resolve().parents[2])
        return
    studio = args.project.resolve() / ".graphic-design"
    try:
        if args.command == "init":
            studio.mkdir(exist_ok=True)
        if not studio.exists():
            raise ValueError("Run init in the commission directory first.")
        with studio_lock(studio):
            execute(studio, args)
    except (OSError, ValueError, KeyError) as exc:
        cli.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
