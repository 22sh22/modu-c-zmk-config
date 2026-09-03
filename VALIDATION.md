# Validation report

Audited: 2026-09-02

## Upstream correspondence checked

- `config/modu.keymap` is based on MODU-C upstream revision `bee0bb4b812f63f279eb67e928accc89600b5904` and keeps 67 behavior bindings in every customized layer.
- Layout metadata contains the exact 67 `(row, col)` entries from the upstream `default_transform`: rows 0–4, columns 0–11, followed by row 5 columns 0, 1, 2, 6, 7, 8, and 9.
- The build matrix uses the upstream board and shield names exactly: `ms88sf3/nrf52840`, `modu_left`, and `modu_right`.
- The additional module paths match the original build script: `modu-module` and `zmk-pmw3610-driver`.
- The fallback conversion uses the same nRF52840 UF2 family ID as the original build script: `0xADA52840`.
- The west manifest and reusable workflow use fixed ZMK and MODU-C source revisions rather than moving branch names.

## Automated local checks passed

- Strict JSON parsing, including duplicate-key detection.
- `config/modu.json` and `config/info.json` semantic equality.
- 67 unique layout coordinates in exact firmware-transform order.
- Six tiny visual placeholders at row 4, columns 3–8.
- Every keymap layer contains exactly 67 behavior references.
- Default-layer `&none` entries occur only at zero-based binding positions 51–56.
- Exact left/right matrix targets, artifact names, source revisions, module paths, and CMake-list quoting.
- Python syntax compilation for all validation and packaging scripts.
- YAML parsing for `build.yaml`, `config/west.yml`, and the GitHub Actions workflow.
- Shell syntax checking for every workflow shell block.
- ZIP path safety, duplicate-entry detection, archive CRC testing, hidden `.github` retention, and extracted-byte comparison.

## Packaging safeguards tested

The dependency-free `scripts/selftest.py` exercises both success and failure paths:

- Valid Intel HEX with CRLF, a terminal newline, and an extra blank line is validated and normalized.
- Corrupt Intel HEX checksums, non-hex characters, invalid control-record addresses, and data records crossing a 16-bit segment boundary are rejected.
- Native UF2 selection works for both halves.
- HEX conversion routing works with a test converter and verifies that the converter receives no terminal blank line.
- Missing or duplicate left/right build outputs are rejected instead of being guessed.
- UF2 start/end magic, block numbering, declared block count, payload size, address alignment, non-overlap, 32-bit address bounds, family flag, and family ID are checked.
- Wrong-family and malformed UF2 files are rejected.
- Byte-identical left/right outputs are rejected as a likely packaging mistake.

## Hardening applied during this audit

- Replaced count-only `&none` validation with exact-position validation.
- Replaced “find any two files” packaging with exact per-half filename selection.
- Added Intel HEX canonicalization before using the pinned upstream converter. This prevents a terminal blank line from reaching a converter parser that indexes every split line.
- Added final UF2 binary validation and a second verification step before artifact upload.
- Added workflow triggers for every script and license/notice file that affects the final artifact.
- Corrected the Microsoft UF2 license-file path in `THIRD_PARTY_NOTICES.md`.

## Not executed in this environment

- `west update` and the complete ZMK/Zephyr compilation.
- The GitHub-hosted reusable workflow itself.
- Flashing or functional testing on a physical MODU-C.

The first successful GitHub Actions run is therefore still the integration-build proof. A successful build plus the automatic UF2 checks gives strong evidence that the files are correctly assembled, but only a physical flash can confirm bootloader compatibility, scanning, Bluetooth, LEDs, and both trackballs on the actual keyboard.
