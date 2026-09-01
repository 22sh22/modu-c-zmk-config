# Unofficial modification notice

This repository is an unofficial, modified, non-commercial ZMK user-config wrapper created on 2026-09-01.

It is **not** an official EKS Inc. or MODU release.

## Original work

- Project: `22sh22/modu-c-firmware`
- Original firmware copyright: Copyright (c) 2026 EKS Inc.
- Original firmware creator: Ryu
- Pinned upstream revision: `af7d209d8c2fe6c03ef38669f4114b69346ad31d`
- Original license: EKS NON-COMMERCIAL SOURCE LICENSE 1.0

## Modifications in this wrapper

- Copied the original `modu.keymap` into the conventional user-config path `config/modu.keymap`; its bindings were not intentionally changed.
- Added Keymap Editor layout metadata for the 67-position `default_transform`.
- Added a pinned west manifest that fetches the original MODU-C board, shield, custom scanning code, and PMW3610 driver.
- Added GitHub Actions automation for left/right builds and the same nRF52840 HEX-to-UF2 conversion family used by the original build scripts.
- Added static consistency validation and Korean setup documentation.

No trademark rights, patent rights, warranty, or endorsement are provided.
