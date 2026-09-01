# Third-party notices
## ZMK PMW3610 driver

The `zmk-pmw3610-driver` directory is based on work by the ZMK contributors, ufan, inorichi, badjeff, and the Zephyr PMW3610 driver. Its source files retain their original copyright and SPDX license identifiers.

- Source: https://github.com/badjeff/zmk-pmw3610-driver
- License: MIT, except files that state another license

The applicable MIT License text is included in `LICENSES/MIT.txt`.

`zmk-pmw3610-driver/Kconfig` is licensed under `LicenseRef-Nordic-5-Clause`:
Copyright 2024, Nordic Semiconductor ASA

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form, except as embedded into a Nordic
   Semiconductor ASA integrated circuit in a product or a software update for
   such product, must reproduce the above copyright notice, this list of
   conditions and the following disclaimer in the documentation and/or other
   materials provided with the distribution.
3. Neither the name of Nordic Semiconductor ASA nor the names of its
   contributors may be used to endorse or promote products derived from this
   software without specific prior written permission.
4. This software, with or without modification, must only be used with a Nordic
   Semiconductor ASA integrated circuit.
5. Any software provided in binary form under this license must not be reverse
   engineered, decompiled, modified and/or disassembled.
THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
## Microsoft UF2 converter

`tools/uf2/uf2conv.py` and `tools/uf2/uf2families.json` are from Microsoft UF2.

- Source: https://github.com/microsoft/uf2
- License: MIT
- Copyright: Microsoft Corporation

The applicable MIT License text is included in `tools/uf2/LICENSE`.

## ZMK Firmware and reusable build workflow

ZMK Firmware and the reusable user-config build workflow are fetched from the
pinned ZMK revision listed in `config/west.yml` and `.github/workflows/build.yml`.

- License: MIT
- Copyright: Copyright (c) 2020 The ZMK Contributors

The applicable license text is included in `LICENSES/ZMK-MIT.txt`.

## Notice retention in firmware artifacts

The GitHub Actions packaging job includes this file, the repository `LICENSE`,
`NOTICE.md`, and the `LICENSES/` directory alongside the generated UF2 files.
