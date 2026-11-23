# Six-skill studio release review

**Verdict, 23 November 2026.** The independent recheck passed the implementation plan. The maker’s release review passed the portable six-skill harness for the local collection workflows exercised below. The first plan review returned it for revision because the scenarios lacked exact entry points, failure and retry conditions, named historical proofs, and measurable print and timed-media checks. Those conditions were added before implementation began.

## Open the transfer commission

Unpack the [Harbor Tea commission](harbor-tea/commission.zip). Open `Harbor Tea/.graphic-design/studio.md` for the board, linked proofs and study galleries. The released card, tile and video sit under `Harbor Tea/deliverables/launch-v1/`. The [contact sheet](harbor-tea/contact-sheet.png) shows the versions selected for those three uses.

| Piece | Creative decision | Observed result |
|---|---|---|
| Shelf card | A aligns the type to the left. B centers the leaf and name on the same axis as the tile. The maker chose B for this exercise and pinned A. | The card rendered at 1200 × 1800 pixels, 4 × 6 inches at 300 ppi. In a newly unpacked commission, restoring A reopened the editable SVG and its dependencies. Rendering it again matched the saved proof pixel for pixel. B remained approved and delivered. Print trim was inspected on screen. |
| Social tile | Retain the variety as the second read under the wordmark at feed size. | “Harbor Tea” and “Jasmine green tea” were readable at a simulated width of 360 pixels. The collection sheet allowed comparison with the shelf card and closing video frame. |
| Six-second reveal | Lead with the leaf, reveal the wordmark on the musical accent at 4.0 seconds, then hold the variety through the end. | FFprobe identified a six-second H.264 video with AAC audio. The decoded image changed between frames 95 and 96 at 24 fps and held through frame 143. The decoded 660 Hz accent arrived with the change and decayed. FFplay ran the entire encoded file with headless audio and video drivers. Speaker playback and physical print remain unverified. |

The editable picture, opening art, cue sheet, original WAV and reproduction command accompany the video. The approved sheet matched the sheet inside the release. All 18 packaged files matched their recorded hashes across the three uses. The rehearsal selections are attributed to the maker.

## Workflow checks

- **Resume.** Initialized banner, bracket and matchup together, then added a role icon. The banner plan compared two crops around four ranking rows. The bracket plan traced the longest name to champion. The icon plan compared silhouettes in a 40-pixel chat circle. A fresh process recovered all four entries and preserved the three authored plans, their stages and next decisions.
- **Versions and approvals.** Exercised six options in a study, an older pin, combined parentage, restoration after moving the commission and separate approvals for pre-match and result graphics. Regression tests exposed a lost shared-asset declaration in a child restored after a library change, an earlier approval disappearing from the pinned preview group, and acceptance of a blank selector. The corrected helper retains the inherited asset digest, shows approved history in the gallery and requires a named selector. [Collection tests](../tests/test_collection.py)
- **Failed delivery.** Temporarily removed the selected reveal MP4 from a disposable copy of its snapshot. Packaging stopped, the new release directory was absent and the previous manifest remained byte-identical. After restoring the MP4, the same new release ID succeeded. The automated suite also exercises a missing source dependency, a stale approval record and an incorrect reviewed sheet.
- **Historical visual review.** Reopened seven archived proofs. Compared Surge-Grip-Destruction and Daylight at 500 pixels and inspected the brass rim at native size. Compared Fine-Cut with Open-Sky beneath the leaderboard title. Compared AI, AJ and AK for figure scale, the rear grip and the drill silhouette. The exercises identify the original false approval and the observation needed to close each objection. [Review drills](review-lab.md#collection-review-drills-from-later-selections)

All five portable harness tests passed, and all six skill definitions validated. The surrounding tournament studio suite passed 28 of 29 tests. Its existing skill-count assertion expects three skills in the parent studio, which also contains PhotoCraft. The portable harness lives in its own directory. [Parent assertion](../../tests/test_harness.py)
