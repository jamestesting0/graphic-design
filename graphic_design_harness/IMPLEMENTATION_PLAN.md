# Implementation plan for a multi-graphic design studio

## Outcome

Implemented and exercised in November 2026. The [six-skill release review](examples/collection-release-review.md) records the plan gate, transfer commission, regression results and verification limits.

A user can open an empty project, describe a collection, and work with the agent from investigation through delivery. Each graphic has its own art brief, production plan, selectable studies, editable versions, review record, and approved uses. The collection shares source assets and art direction. At any point the user can ask “What is final, what is still drafting, and what needs my decision?” and get an answer with the relevant proofs.

Keep the reusable package in `graphic_design_harness/`. A commission owns its own `.graphic-design/` workspace and visible `deliverables/` folder. Develop and verify the new workflow in a scratch commission. Use this studio’s artwork and history as read-only evidence.

## Six skills and their responsibilities

Retain the four existing skill IDs so existing invocations continue to work. Add two skills and revise the [entry guide](AGENTS.md) to route a new commission through setup, investigation, and planning.

| Skill | Implementation | Required result |
|---|---|---|
| `setup-design-studio` | Add. Inventory the requested set, supplied assets, destination, and existing studio state. Initialize or resume. | A collection board, initial graphic entries, and the first useful decision. Repeated setup preserves user edits. |
| `design-direction` | Extend into art investigation. Identify reference roles, source variants, permitted transformations, missing assets, use-size constraints, typography, lighting, material, and composition. | One shared direction for the set plus specific requirements and visual studies for each graphic. Record what the user values or rejects in each reference. |
| `plan-design-stages` | Add. Plan the order of the collection, then plan the stages and decisions for each graphic. Identify any representative graphic worth resolving first and why. | A collection plan and one working plan per graphic, each naming the next artifact, creative question, review surface, and exit condition. |
| `design-in-layers` | Extend the existing production workflow with graphic, study, parent version, and selected dependencies. | Editable components and registered proofs. A local change preserves chosen pose, copy, effects, and neighboring assets where required. |
| `design-effects-and-sound` | Retain the visual finishing and optional timed-media workflow. Tie passes and cues to the selected picture version. | Adjustable effects and matched comparisons. Timed work also has a cue sheet, editable tracks, and an export checked in playback. |
| `design-proof-review` | Extend proof review to cover graphic approval, separate final uses, and collection delivery. Retain the tested review helpers. | A version-specific verdict, traceable resolution of objections, and verified release packages. |

## Workspace and status

```text
.graphic-design/
  studio.md                 generated collection board with proof links
  collection-plan.md        deliverable list, dependencies and order of work
  art-direction.md          shared visual decisions and reference roles
  library/                  original assets and versioned shared components
  graphics/<graphic-id>/
    brief.md                audience, use, formats, art and content requirements
    plan.md                 stages, decision points and required proofs
    state.json              stage, disposition, working version, approved uses, next decision
    studies/<question>/     visual options, selections and reasons
    components/             editable local parts
    versions/<version-id>/  restorable source bundle, proofs, manifest and lineage
    reviews/                objections and decisions against an exact version
deliverables/<release-id>/  selected files by graphic and use, plus collection manifest
```

Create folders as real work needs them. Keep the human-written plans separate from the generated board. Each graphic’s state record is authoritative for its working stage and approved version per use. Version manifests are authoritative for saved files, parentage and dependency versions. Rebuild the board from those records so the agent never has to reconcile two hand-maintained status lists.

The board shows one row per graphic/use, with **stage**, **work status**, **working proof**, **approved proof**, and **next decision**. Stage identifies the work, such as composition or finishing. Work status identifies who acts next, such as drafting, awaiting selection, in review, changes requested, or complete. Approval names an exact version. For example, while the scoreboard’s Daylight lighting study is under review, Surge-Grip-Destruction can still be the approved scoreboard. The VS matchup and the centered-score result have separate approved entries. Golden, compact, blank, and populated exports belong to the appropriate version. [Actual delivery index](../final/README.md)

## Guided decisions, from brief to layers

At each meaningful creative fork, the agent states the question, shows comparable drafts, recommends one with a visible reason, and records the outcome. Present alternatives on the actual piece at the intended size. Keep unrelated layers fixed so the choice is legible. Offer the current version or an omission when that answers the question. The user can select, combine qualities, delegate the choice, or stop. An explicit request for drafts ends at selection; a delegated choice can advance with its rationale recorded.

For example, a leaderboard plan might first compare two crops with actual ranking rows, then resolve figures and footing, test foreground occlusion, build the editable board, and finish with light and particles. The bracket might start by tracing one entrant all the way to champion before drawing its figures. A role icon might need only silhouette, color, and an in-chat proof. The agent should choose stages from the graphic’s purpose.

## Build sequence

| Phase | Work | Exit check |
|---|---|---|
| 1. Setup and inventory | Implement setup templates, a small file-based helper for initialization and status, and the entry guide. Support adding a graphic to an existing commission. | Start with three graphics from a single brief. Add a fourth later. Reopen the project, regenerate the board, and recover all four stages and next decisions without rewriting edited briefs. |
| 2. Investigation and plans | Extend art direction and implement the planning skill. Record shared rules once, with per-graphic departures and source requirements alongside each brief. | The same commission yields different, usable plans for a banner, bracket, and small icon. A user can see which decision affects the whole set and which affects one piece. |
| 3. Studies and version recovery | Adapt the existing [version helper](../tools/variant_log.py) and its [behavioral tests](../tests/test_variant_log.py) inside the portable harness. Retain preview, full proof, source, parent ID, pins, latest-five gallery, and hash-verified restore to a fresh working copy. Record selected option IDs when combining studies. Package linked dependencies or identify and verify required external originals. Replace the current absolute gallery identity with a project-relative identity for new studios. Account for the existing POSIX file lock on supported platforms. | Save six options, pin the first, restore it after moving the scratch project, make a child version, and reopen its editable master. A corrupt or missing dependency prevents a successful restore. Existing saved versions and approvals survive a failed save. |
| 4. Review, approval and releases | Connect production and review to state updates. Distinguish saving, pinning, selecting for further work, approving for a use, and delivering a release. Record who selected the version and the supporting proof. Stage and verify all release files before publishing the local release manifest. Regenerate derived views after interrupted operations. | “Keep B” pins it. “Continue from B” changes the working parent. “Make B final” updates its named use. “Keep this as a separate final” adds a use. A failed package operation leaves the last complete delivery usable. |
| 5. Collection review and handoff | Produce a labeled contact sheet from the exact proposed release versions, alongside the actual destination previews. Check hierarchy, type, materials and accents as a family. Track consumers of a changed shared asset and recheck the affected graphics before adopting the change. | A shared type change identifies the affected templates. A scoreboard-only mask edit reopens its local checks. A release manifest identifies each graphic, use, version, shared dependencies, and export files needed to reproduce the set. |

Use the existing local Python/Pillow tooling where it serves these operations. Keep creative judgment in the skills and reviews. Each implementation phase must work through the agent’s normal entry point, including after a fresh session.

## Acceptance and final gate

1. **Empty-project rehearsal.** In a clean directory, give only an intent and sample assets. Run setup, investigate the art, plan the set, present the first meaningful options, and resume from the recorded selection in another session. The procedural skills and tools must work with the reusable package alone.
2. **Selection and rollback.** Keep two graphics at different stages. Restore an older bracket as a new draft while its final remains available. Approve two head-to-head uses. Confirm the board, gallery, editable files, and release manifest agree. Retry a failed operation and check for partial or duplicate releases.
3. **Historical visual regressions.** Extend the [review exercises](examples/review-lab.md) with the later decisions: level geometry that appears tilted at posted size, a crystal whose best treatment was removal, and a resized figure whose grip and visual weight must survive. Check the named defect, its neighbors, and the collection contact sheet where relevant. Preserve historical approvals as dated decisions.
4. **Transfer beyond game artwork.** Exercise the same workflow on a small non-game set, such as a product shelf card, social image, and six-second reveal. Check print geometry, small-screen legibility, and the actual encoded reveal with sound. Identify simulated viewing conditions in the report.
5. **Release the harness.** Validate all six skills and internal links. Run relevant existing tests, the new targeted state/version tests, and the end-to-end rehearsals. Record the artifacts, failures, fixes, and remaining limitations. The prior independent gate applies to the four-skill harness it inspected. The six-skill implementation earns its own release verdict against these scenarios.

### Execution details for the release gate

- Use the setup skill’s bundled Python CLI, `studio.py`, from a scratch commission. Phase 1 exercises `init`, `add`, `status` and `update`. Inspect the generated board and compare user-edited briefs before and after resume. Phase 2 follows the direction and planning skill entry points and opens the three distinct per-graphic plans. Phase 3 exercises `save`, `keep`, `select` and `restore`. Verify parent IDs and decoded proof/source hashes after moving the project. Phase 4 exercises `approve` with two named uses, records the selector and exact reviewed proof, then `release`. In a scratch copy remove a saved export from the selected bundle, retry packaging, and require the previous release manifest to remain byte-identical and the new destination absent. Restore the export and retry the same release ID successfully. Phase 5 exercises `consumers` on a shared asset and `sheet` on the selected uses; compare all sheet labels and release-manifest versions with the board.
- At 500 pixels wide compare scoreboard **Surge-Grip-Destruction → Daylight** for continuous brass edges at the avatar medallions; inspect the rim detail at native size. The earlier under-review example illustrates that historical transition. Compare **Fine-Cut → Open-Sky** for space beneath the title, and **AI → AJ → AK** for comparative head height, rear grip clearance and the drill silhouette. Use the archived galleries [scoreboard](../outputs/review/variants/scoreboard/abilities/README.md), [title](../outputs/review/variants/wizard-duel/title-crystal/README.md) and [bracket](../outputs/review/variants/bracket/abilities/README.md).
- Transfer brief: launch “Harbor Tea” with an original tea mark, a 4 × 6 inch shelf card, a square social tile, and a six-second reveal. Render a 1200 × 1800 card at 300 ppi and open its simulated trim proof. At a simulated 360-pixel feed width read “Harbor Tea” and “Jasmine green tea” on the tile. Use an original audio cue. With FFprobe verify one video stream, one audio stream and six seconds; play the exported clip, check the reveal accent at 4.0 seconds, the readable last hold and its decaying tail. Disclose any unavailable physical or acoustic playback check.
- From the studio root run `python3 -m unittest discover -s tests -v` and `python3 -m unittest discover -s graphic_design_harness/tests -v` with Pillow available. Run the installed skill-creator `scripts/quick_validate.py` on each of the six skill directories with PyYAML available. Check all local links, including the integrated examples, at their documented locations.

The organizational precedents are Adobe’s separation of campaign projects from reusable creative libraries and IBM Carbon’s use of evidence to establish an asset’s maturity. The collection board, approval-by-use model, and version-recovery checks above are specific to this studio. [Adobe creative asset organization](https://helpx.adobe.com/creative-cloud/apps/create-and-manage-libraries/organize-manage-creative-cloud-assets.html) · [IBM Carbon component lifecycle](https://www.carbondesignsystem.com/getting-started/contributing/product-development-lifecycle)
