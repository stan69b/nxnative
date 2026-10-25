# Open pull requests on seedds/nxnative

Owner's notes, kept on the fork's `notes` branch only. This branch has no common history with `main`, so it can never be part of a pull request to seedds/nxnative. Snapshot of 2026-10-25. Refresh it with `gh pr list --repo seedds/nxnative --state open`.

## Mine

| PR | Branch | State | What | Notes |
|---|---|---|---|---|
| [#150](https://github.com/seedds/nxnative/pull/150) | `stan69b:mac-app` | draft | `--platform mac-app`: a self-contained, double-clickable Mac app of a game (`dm/mac/launcher.c`, `dm/mac/pack_app.py`) | Checked on Echoes of Wisdom: the app is on the SMART drive, signed with my Developer ID, 57.7 fps. Overlaps #104 (see below). I commented on both PRs and offered to rebase #150 onto #104 if #104 is merged first. Not checked: a Vulkan or GL game, another Mac. |
| (not opened yet) | `game-echoes-of-wisdom` | — | Session B: Echoes of Wisdom (`01008CF01BAAC000`) as a supported game | Worked in `/Volumes/SMART/TheSTouch/custom-repos/nxnative-eow`; not on the fork yet at this snapshot. |

## Others that touch the same areas

| PR | Author | Overlap with my work |
|---|---|---|
| [#104](https://github.com/seedds/nxnative/pull/104) | jamessturges | Mac app bundle plus an AppKit front end: menus, preferences, P1–4 controller mapping. The packing overlaps #150. Its packing lacks `c1_full.tsv`, `cb_extent.tsv` and `pso_manifest.tsv`; its standalone mode copies `cas/`; in its default "thin" mode the bundle is symlinks into `<id>_build`. The front end is worth keeping. The two disagree on the save folder: `NxNative/<Game Name>` vs `nxnative/<title ID>`. |
| [#102](https://github.com/seedds/nxnative/pull/102) | SilverFT | Mac: Xbox letter-based controller mapping. Small; #104 also has a Nintendo/Xbox layout. |
| [#33](https://github.com/seedds/nxnative/pull/33) | MeNass89 | Mac: MetalFX upscaling at present, drawable follows the window. Mac present path. |
| [#87](https://github.com/seedds/nxnative/pull/87) | v0lumehi | Mac: present snapshots (`DM_PRESENT_SNAP=1`). Mac present path. |

## All open (19 at the snapshot)

| PR | Author | Updated | Size | Title |
|---|---|---|---|---|
| [#151](https://github.com/seedds/nxnative/pull/151) | b4f8abbb24dbf56a7d0280f296e16eeb | 2026-10-25 | +2294/−90, 13 files | Add shared address-region management and MapMemory source ownership |
| [#150](https://github.com/seedds/nxnative/pull/150) | stan69b | 2026-10-25 | +559/−26, 6 files | A self-contained Mac app of a game (`--platform mac-app`) |
| [#138](https://github.com/seedds/nxnative/pull/138) | Nishikori-Yui | 2026-10-24 | +18789/−4, 11 files | Add Ghost Trick: Phantom Detective support |
| [#135](https://github.com/seedds/nxnative/pull/135) | v0lumehi | 2026-10-25 | +6474/−134, 29 files | Prepare shaders before the first frame, with a progress screen (and a prewarm list for Breath of the Wild) |
| [#133](https://github.com/seedds/nxnative/pull/133) | v0lumehi | 2026-10-24 | +12766/−8200, 42 files | Split `nvn_mtl.m` into topic parts (mechanical, identical machine code) |
| [#127](https://github.com/seedds/nxnative/pull/127) | nocmt | 2026-10-24 | +126/−1, 3 files | Fail fast when SetHeapSize cannot change host page protections |
| [#126](https://github.com/seedds/nxnative/pull/126) | huangzhuangchao | 2026-10-24 | +85756/−0, 9 files | FINAL FANTASY RESONANCE HK 1.0.1 (`0100B8A026F14000`): the game profile |
| [#125](https://github.com/seedds/nxnative/pull/125) | v0lumehi | 2026-10-25 | +4462/−75, 24 files | Pipeline prebuild, with the pairs of agl's BAHS programs (`pso_pairs.tsv`) |
| [#124](https://github.com/seedds/nxnative/pull/124) | v0lumehi | 2026-10-25 | +1231/−66, 19 files | Hybrid pipelines: draw with the pair's pulling pipeline while the draw's own pipeline is built |
| [#123](https://github.com/seedds/nxnative/pull/123) | v0lumehi | 2026-10-25 | +879/−32, 18 files | Pulling vertex shader variants in the translation chain (`<key>_bp`) |
| [#122](https://github.com/seedds/nxnative/pull/122) | v0lumehi | 2026-10-25 | +387/−20, 6 files | Render pipelines through MTL4Compiler, with a per-game pipeline archive |
| [#117](https://github.com/seedds/nxnative/pull/117) | v0lumehi | 2026-10-24 | +142/−22, 16 files | iPhone: Hades fills the screen edge to edge (general output size, profile key `aspect any`) |
| [#104](https://github.com/seedds/nxnative/pull/104) | jamessturges | 2026-10-25 | +1695/−130, 9 files | Mac: native AppKit app bundle, preferences, and controller mapping |
| [#102](https://github.com/seedds/nxnative/pull/102) | SilverFT | 2026-10-24 | +10/−4, 2 files | Mac: add optional Xbox letter-based controller mapping |
| [#87](https://github.com/seedds/nxnative/pull/87) | v0lumehi | 2026-10-25 | +107/−7, 6 files | Mac: present snapshots (`DM_PRESENT_SNAP=1`) |
| [#76](https://github.com/seedds/nxnative/pull/76) | v0lumehi | 2026-10-25 | +256/−30, 15 files | Breath of the Wild above 60 fps and above 1080p (reworked from #62) |
| [#33](https://github.com/seedds/nxnative/pull/33) | MeNass89 | 2026-10-23 | +44/−2, 3 files | Mac: MetalFX spatial upscaling at present, drawable follows the window |
| [#32](https://github.com/seedds/nxnative/pull/32) | MeNass89 | 2026-10-23 | +71/−16, 4 files | NVN: alpha test through a fragment variant; parallel prewarm; alpha-tested pipelines built in the background |
| [#29](https://github.com/seedds/nxnative/pull/29) | Roylam23 | 2026-10-21 | +3228/−40, 28 files | Rhythm Heaven Groove: A16 legacy support, touch pad and ambient bars |

Groups worth knowing:
- **#122 → #123 → #124 → #125 → #135** (v0lumehi, branches `pso-a` … `pso-e`): one stacked series on pipeline building; each builds on the one before.
- **#133** moves `nvn_mtl.m` into topic files. Any PR that edits `nvn_mtl.m` conflicts with it, whichever of them goes in second.
- None of the others edits `scripts/build_ipa_from_nsp.py`'s Mac branch or `dm/mac/`, which #150 does; only #104 does.
