---
name: setup-design-studio
description: Start or resume a graphic design collection from a natural-language intent. Organize shared art direction and individual deliverables, show current drafts and approved versions, and route the next decision.
---

# Set up the studio

Start from what the user wants the collection to accomplish. Inventory the graphics, distinct uses, actual destinations and available source material. Reuse the user's nouns as graphic IDs; use lowercase words separated by hyphens. Choose one ID per independently planned piece. A different export size generally belongs to the same version. A result card and a pre-match card may both be final for different uses.

Use [studio.py](scripts/studio.py) in the **commission directory**. Run with Python 3.11+ and Pillow on macOS/Linux. The path below stands for this installed skill's actual script path. Running it from elsewhere requires `--project /path/to/commission` before the command. For other platforms follow the same on-disk organization manually, or use a Linux environment for these file operations.

```sh
python3 "$STUDIO_CLI" init --intent "A tournament identity for players and spectators" banner bracket scoreboard
python3 "$STUDIO_CLI" add role-icon
python3 "$STUDIO_CLI" status
```

On resume, open the board, collection plan, affected graphic’s brief, plan, gallery and exact current proof. The board and galleries are generated. Edit narrative plans directly. Use the helper for state, versions and delivery. A repeated initialization can add missing graphics while preserving prior decisions. Put reusable originals in `.graphic-design/library/` with the source, permitted role and usage notes. Keep rights-limited files local to the permitted workspace.

For each graphic fill its brief with purpose, target sizes, content and edge cases, required asset variants, creative freedom, and the actual proof surface. Hand off to `design-direction` for project-specific research and `plan-design-stages` for collection and per-graphic plans. Show the next meaningful choice. If the user requested setup or discussion only, stop there.

**Bring assets in at any stage.** Accept attachments, local files and source links. The agent handles filing. Use `library/supplied/`, `library/found/` or `library/created/` as needed, or retain an existing organized library. Keep an original intact and edit a working copy. Enter the path or source link, origin, intended use or reference-only status, credit and affected graphics in the board’s **Asset register**. Label an exact logo separately from a picture sent for inspiration. When an exact asset arrives late, save a child of each affected graphic, retain the previous option and verify the mark on the finished artwork. Declare the dependency with `save --shared` for future changes.

## Daily operations

Use the [studio command guide](references/commands.md) for saving options, combining studies, pinning, restoring to a new working folder, approving a separate final, packaging releases and tracing the consumers of a shared asset. Ask about intent only when it changes the result: “keep” pins a candidate, “continue from” selects a working parent, and “final” designates an approved use. Verify the reviewed version with the user’s selection before promotion.
