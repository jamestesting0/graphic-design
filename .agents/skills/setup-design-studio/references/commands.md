# Commission operations

Run these examples in the commission root with the standalone `graphic-design` command. For an agent-only installation, replace `graphic-design` with `uv run --script "$STUDIO_CLI"`, setting `STUDIO_CLI` to the absolute path of the installed setup skill’s `scripts/studio.py`. Both run the same code. The helper serializes local writes, generates the collection board from per-graphic state, and verifies package contents. IDs use letters, digits, hyphens or underscores. Open the paths printed by `status` relative to `.graphic-design/`.

```sh
graphic-design init --intent "A launch identity for shelf, feed and video" shelf-card social reveal
```

## Save and select

Prepare a clean **bundle folder** containing the editable master, relative linked assets, any export/reproduction instructions, a full raster proof, the intended destination preview, and requested exports. Include separate timed tracks and the timeline for motion work. Keep the source tree layout the master expects. Reopen it before saving. The helper can verify packaged files; the artist must identify what the editor actually loads. A bundle becomes the complete set copied into a release, so exclude private scratch files and assets without handoff permission. For a restricted dependency, supply an embedded/outlined distributable master where licensed and document the editable original's requirements. Mark unavailable reproduction checks explicitly.

```sh
graphic-design save bracket A --study layout --bundle work/left --master master.svg --proof proof.png --preview phone.png --note "Left-to-right route" --shared crest.svg=art/crest.svg
graphic-design keep bracket A
graphic-design select bracket A --next "Check the longest name against the champion slot"
graphic-design update bracket --stage composition --status 'awaiting selection' --next "Choose the open or framed layout"
graphic-design status
```

A save creates an immutable bundle under `graphics/bracket/versions/A/`. It makes a study gallery under `studies/layout/` and leaves the user's selection intact. The gallery keeps five recent previews, pinned older choices and links to all older versions. Put the design question and selection rationale in the study folder alongside the generated gallery. Use `--parent A --parent B` when combining two saved studies and explain which quality came from each. Save a new version after editing. The approved and working columns stay independent.

```sh
graphic-design restore bracket A --to work/recovered-A --next "Explore wider gutters"
graphic-design consumers crest.svg
```

Restore checks every packaged file and recreates the source tree in a new folder. Saving that directory under a new ID inherits its parent. Move the commission as a unit to preserve relative records. A later library change leaves snapshots self-contained. The consumers report lists each active working or approved version that declared the key, with the hash of the copy it used. Review those graphics and explicitly adopt the new asset only where warranted.

A child inherits an unchanged shared asset from its saved parent. If you move or update it, specify the new mapping with `--shared library/path=bundle/path`. If the design stops using it, record that with `--drop-shared library/path`. For a combined study, resolve conflicting copies explicitly.

## Review, approve and package

Save the review inside `graphics/<graphic>/reviews/` under `.graphic-design/`. Give the JSON record `graphic`, `version`, `proof_sha256` (the proof file digest in the saved version manifest), `reviewer`, `verdict` and `finding`. Use `advance` only after inspecting that proof and the required destinations. Include other fields for the baseline, marked crops, objections and any limitations. The review helper’s tile log can accompany the decision. A valid coverage log alone cannot approve a design.

```sh
graphic-design approve bracket A --by "client selection, 23 November" --review .graphic-design/graphics/bracket/reviews/A.json
graphic-design approve matchup Result-B --use result --by "client selection, 23 November" --review .graphic-design/graphics/matchup/reviews/Result-B.json
graphic-design sheet bracket/main matchup/main matchup/result --out collection-proof.png
graphic-design release tournament-v1 --reviewed-sheet collection-proof.png bracket/main matchup/main matchup/result
```

Inspect the labeled sheet of the intended uses alongside their native and destination proofs before release. Exact selected files, review decisions, shared dependencies and file hashes go into `deliverables/tournament-v1/manifest.json`. Existing releases retain their IDs and contents. A failed package check publishes no partial release; fix the input and retry the same unused ID. After interruption run `status` to rebuild the board and galleries from completed records. List available operations with `--help`.

The board links the current working proof, the approved proof for each use and its most recent delivery. Approving a successor keeps the previous dated decision in that use's `earlier_approvals` in `state.json`. Restoring a draft leaves both the approval and the delivered files available.
