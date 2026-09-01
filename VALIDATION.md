# Validation report

Generated: 2026-09-01

## Passed locally

- JSON metadata parses successfully.
- `config/modu.json` and `config/info.json` are identical.
- Layout contains 67 unique `(row, col)` positions in the exact original `default_transform` order.
- Both keymap layers contain 67 behavior bindings.
- The default layer retains the six central `&none` placeholders.
- Build configuration contains left and right targets for `ms88sf3/nrf52840`.
- Build configuration includes both the MODU module and PMW3610 driver paths.
- West manifest pins both ZMK and MODU-C upstream commits.
- Workflow contains nRF52840 UF2 family ID `0xADA52840` and final artifact checks.

## Not executed locally

- `west update`
- Full ZMK/Zephyr compilation
- GitHub-hosted reusable workflow
- Flashing or hardware testing on a physical MODU-C

The first successful GitHub Actions run is therefore the integration-build check. Hardware behavior must still be confirmed on the keyboard.

## License packaging

The final GitHub Actions artifact includes `LICENSE`, `NOTICE.md`, `THIRD_PARTY_NOTICES.md`, and `LICENSES/` alongside both UF2 files.
