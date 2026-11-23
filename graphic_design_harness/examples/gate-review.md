# Harness review, 21 November 2026

**Gate verdict: APPROVE.** The independent reviewer reproduced the counterexamples and regression checks, verified the selected release files, and found no blocking issue. [Independent findings and limits](independent-review.md)

Scope: updated Banner history through the final Centered Palms handoff, the four portable skills, their counterexamples and their two raster review helpers. This is a review of the design workflow. The final-art comparison below identifies the exact fixtures used.

| Maker check | Artifact and observation | Result |
|---|---|---|
| Reconstruct the missed objection | Compared the Balanced Cast, Original Stance and Centered Palms views in [exercise 7](review-lab.md). The earlier fit turns the casting palm out. The later local comparison retains the original hand gesture. The final lit/unlit pairs expose the core and the pad separately. The historical reviewer noticed proximity to the folded fingers before the user reopened the issue. | Separate shoulder acceptance, gesture preservation and emitter centering in the review record. |
| Bind the example to the selected final | Compared Centered Palms master, populated proof, blank and short-format PNG to their release counterparts byte for byte. Calculated distances from the archived golden-format center/centroid pairs: 0.37 and 0.39 native pixels. These numbers use the artist's recorded landmarks. The short-format fingertip clearance is a historical visual finding. | Four file pairs matched. No universal tolerance inferred. |
| Try the workflow outside this project | Rendered the portable SVG at 540 × 336 and inspected all three rows. In A a second amber point survives on the route at the old terminal. In B the single light crowds the upper-right ring edge. | Each candidate fails a different part of the same brief. The SVG travels without external images or fonts. |
| Exercise both helper entry points | The current Centered Palms record passed on its golden proof and failed on Original Stance. On the archived Miner Y→AB pair, permitting the actual left edit passed; permitting only the opposite side returned changed bounds (168, 219, 1170, 958). | Expected positive and negative outcomes reproduced. |
| Challenge false passes | Ran the two [regression tests](../tests/test_review_helpers.py) before and after the fixes. Previously, a reviewer encoded as a list containing null passed, and two 16-bit RGB PNGs differing by one low bit were declared identical after decoding. | Both failed for the intended reason before the fixes and passed afterward. All three existing studio detail-review tests passed. |
| Package checks | Ran the installed skill validator on all four skills and resolved the local Markdown links. | Four valid skill entry points and all linked targets present. |

The timed-media exercise remains a proposed listening test. This round inspected static artwork, records and the proof tools.
