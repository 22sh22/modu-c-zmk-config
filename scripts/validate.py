#!/usr/bin/env python3
"""Static consistency checks for the MODU-C Keymap Editor wrapper."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [
    *[(row, col) for row in range(5) for col in range(12)],
    (5, 0), (5, 1), (5, 2), (5, 6), (5, 7), (5, 8), (5, 9),
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def check_metadata() -> None:
    generic = json.loads((ROOT / "config/info.json").read_text(encoding="utf-8"))
    named = json.loads((ROOT / "config/modu.json").read_text(encoding="utf-8"))
    if generic != named:
        fail("config/info.json and config/modu.json differ")

    try:
        layout = named["layouts"]["default_transform"]["layout"]
    except KeyError as exc:
        fail(f"missing metadata key: {exc}")

    actual = [(item["row"], item["col"]) for item in layout]
    if actual != EXPECTED:
        fail(f"layout coordinate order differs from firmware transform: {actual!r}")
    if len(actual) != 67 or len(set(actual)) != 67:
        fail("layout must contain 67 unique matrix positions")

    placeholders = [item for item in layout if item["row"] == 4 and 3 <= item["col"] <= 8]
    if len(placeholders) != 6 or not all(item.get("w", 1) < 0.5 for item in placeholders):
        fail("the six row-4 placeholders must remain present and visually small")


def check_keymap() -> None:
    text = (ROOT / "config/modu.keymap").read_text(encoding="utf-8")
    blocks = re.findall(r"bindings\s*=\s*<(.*?)>;", text, flags=re.DOTALL)
    if len(blocks) != 2:
        fail(f"expected two layer binding blocks, found {len(blocks)}")

    counts = []
    for block in blocks:
        bindings = re.findall(r"(?<![A-Za-z0-9_])&[A-Za-z_][A-Za-z0-9_]*", block)
        counts.append(len(bindings))
    if counts != [67, 67]:
        fail(f"each layer must have 67 bindings; found {counts}")

    first = blocks[0]
    none_count = len(re.findall(r"(?<![A-Za-z0-9_])&none(?![A-Za-z0-9_])", first))
    if none_count != 6:
        fail(f"default layer must retain six &none placeholders; found {none_count}")


def check_build_files() -> None:
    build = (ROOT / "build.yaml").read_text(encoding="utf-8")
    for token in (
        "ms88sf3/nrf52840",
        "shield: modu_left",
        "shield: modu_right",
        "modu-module",
        "zmk-pmw3610-driver",
    ):
        if token not in build:
            fail(f"build.yaml is missing {token!r}")

    west = (ROOT / "config/west.yml").read_text(encoding="utf-8")
    for revision in (
        "641514a97db345f499dd50b0360e594270f008fe",
        "af7d209d8c2fe6c03ef38669f4114b69346ad31d",
    ):
        if revision not in west:
            fail(f"config/west.yml is missing pinned revision {revision}")

    workflow = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
    for token in (
        "fallback_binary: hex",
        "0xADA52840",
        "modu-c-firmware",
        "cp LICENSE NOTICE.md THIRD_PARTY_NOTICES.md uf2/",
        "cp -R LICENSES uf2/LICENSES",
        "path: uf2/**",
    ):
        if token not in workflow:
            fail(f"workflow is missing {token!r}")

    for required in (
        "LICENSE",
        "NOTICE.md",
        "THIRD_PARTY_NOTICES.md",
        "LICENSES/MIT.txt",
        "LICENSES/MICROSOFT-UF2-MIT.txt",
        "LICENSES/ZMK-MIT.txt",
    ):
        if not (ROOT / required).is_file():
            fail(f"required license or notice file is missing: {required}")


def main() -> None:
    check_metadata()
    check_keymap()
    check_build_files()
    print("OK: 67 layout positions match 67 bindings on both layers.")
    print("OK: left/right build targets, pinned modules, UF2 packaging, and notices are present.")


if __name__ == "__main__":
    main()
