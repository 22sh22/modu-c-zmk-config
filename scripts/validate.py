#!/usr/bin/env python3
"""Static consistency checks for the MODU-C Keymap Editor wrapper."""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ZMK_REVISION = "641514a97db345f499dd50b0360e594270f008fe"
MODU_REVISION = "af7d209d8c2fe6c03ef38669f4114b69346ad31d"
BOARD = "ms88sf3/nrf52840"
EXPECTED_COORDINATES = [
    *[(row, col) for row in range(5) for col in range(12)],
    (5, 0),
    (5, 1),
    (5, 2),
    (5, 6),
    (5, 7),
    (5, 8),
    (5, 9),
]
PLACEHOLDER_INDICES = tuple(range(51, 57))
REQUIRED_LICENSE_FILES = (
    "LICENSE",
    "NOTICE.md",
    "THIRD_PARTY_NOTICES.md",
    "LICENSES/MIT.txt",
    "LICENSES/MICROSOFT-UF2-MIT.txt",
    "LICENSES/ZMK-MIT.txt",
)


class DuplicateJsonKey(ValueError):
    """Raised when a JSON object repeats a key."""


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKey(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)
    except (OSError, json.JSONDecodeError, DuplicateJsonKey) as exc:
        fail(f"cannot parse {path.relative_to(ROOT)}: {exc}")


def check_metadata() -> None:
    generic = load_json(ROOT / "config/info.json")
    named = load_json(ROOT / "config/modu.json")
    if generic != named:
        fail("config/info.json and config/modu.json differ")
    if not isinstance(named, dict):
        fail("layout metadata root must be a JSON object")
    if named.get("id") != "modu" or named.get("name") != "MODU-C":
        fail("layout metadata must retain id='modu' and name='MODU-C'")
    if named.get("sensors") != []:
        fail("layout metadata sensors must be an empty array")

    try:
        layout = named["layouts"]["default_transform"]["layout"]
    except (KeyError, TypeError) as exc:
        fail(f"missing layout metadata key: {exc}")
    if not isinstance(layout, list):
        fail("default_transform.layout must be an array")

    coordinates: list[tuple[int, int]] = []
    for index, item in enumerate(layout):
        if not isinstance(item, dict):
            fail(f"layout item {index} is not an object")
        for key in ("row", "col"):
            if type(item.get(key)) is not int:
                fail(f"layout item {index} has a non-integer {key}")
        for key in ("x", "y"):
            value = item.get(key)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                fail(f"layout item {index} has a non-numeric {key}")
        for key in ("w", "h"):
            if key in item:
                value = item[key]
                if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                    fail(f"layout item {index} has an invalid {key}")
        coordinates.append((item["row"], item["col"]))

    if coordinates != EXPECTED_COORDINATES:
        fail("layout coordinate order differs from the upstream default_transform")
    if len(coordinates) != 67 or len(set(coordinates)) != 67:
        fail("layout must contain 67 unique matrix positions")

    placeholders = [layout[index] for index in PLACEHOLDER_INDICES]
    expected_placeholder_coordinates = [(4, col) for col in range(3, 9)]
    actual_placeholder_coordinates = [(item["row"], item["col"]) for item in placeholders]
    if actual_placeholder_coordinates != expected_placeholder_coordinates:
        fail("placeholder positions are not exactly row 4, columns 3 through 8")
    if not all(item.get("w", 1) < 0.5 and item.get("h", 1) < 0.5 for item in placeholders):
        fail("the six row-4 placeholders must remain visually small")


def _strip_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.DOTALL)


def _matching_brace(text: str, opening_index: int) -> int:
    depth = 0
    for index in range(opening_index, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    fail("unbalanced braces in config/modu.keymap")
    raise AssertionError("unreachable")


def _keymap_layers(text: str) -> list[tuple[str, list[str]]]:
    stripped = _strip_comments(text)
    match = re.search(r"\bkeymap\s*\{", stripped)
    if not match:
        fail("config/modu.keymap has no keymap node")
    opening = stripped.find("{", match.start())
    body = stripped[opening + 1 : _matching_brace(stripped, opening)]

    layers: list[tuple[str, list[str]]] = []
    node_pattern = re.compile(
        r"(?:[A-Za-z_][A-Za-z0-9_]*\s*:\s*)?"
        r"([A-Za-z_][A-Za-z0-9_,@-]*)\s*\{"
    )
    position = 0
    while True:
        node_match = node_pattern.search(body, position)
        if not node_match:
            break
        node_opening = body.find("{", node_match.start())
        node_closing = _matching_brace(body, node_opening)
        node_body = body[node_opening + 1 : node_closing]
        binding_match = re.search(r"\bbindings\s*=\s*<(.*?)>\s*;", node_body, re.DOTALL)
        if binding_match:
            behavior_names = re.findall(
                r"(?<![A-Za-z0-9_])&([A-Za-z_][A-Za-z0-9_]*)",
                binding_match.group(1),
            )
            layers.append((node_match.group(1), behavior_names))
        position = node_closing + 1
    return layers


def check_keymap() -> None:
    path = ROOT / "config/modu.keymap"
    text = path.read_text(encoding="utf-8")
    for include in (
        "#include <behaviors.dtsi>",
        "#include <dt-bindings/zmk/keys.h>",
        "#include <dt-bindings/zmk/bt.h>",
        "#include <dt-bindings/zmk/pointing.h>",
    ):
        if include not in text:
            fail(f"config/modu.keymap is missing {include}")

    layers = _keymap_layers(text)
    if len(layers) < 2:
        fail(f"expected at least two keymap layers, found {len(layers)}")
    if layers[0][0] != "default_layer" or layers[1][0] != "lower_layer":
        fail("the first two keymap nodes must remain default_layer and lower_layer")

    wrong_sizes = [(name, len(bindings)) for name, bindings in layers if len(bindings) != 67]
    if wrong_sizes:
        fail(f"every keymap layer must contain 67 behavior bindings; found {wrong_sizes}")

    default_bindings = layers[0][1]
    none_indices = tuple(index for index, name in enumerate(default_bindings) if name == "none")
    if none_indices != PLACEHOLDER_INDICES:
        fail(
            "default-layer &none placeholders must be exactly zero-based indices "
            f"{PLACEHOLDER_INDICES}; found {none_indices}"
        )


def _parse_build_entries(text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r"(?ms)^  - board:\s*(?P<board>\S+)\s*$\n"
        r"^    shield:\s*(?P<shield>\S+)\s*$\n"
        r"^    cmake-args:\s*>-\s*$\n"
        r"^      (?P<cmake>[^\n]+)\s*$\n"
        r"^    artifact-name:\s*(?P<artifact>\S+)\s*$"
    )
    return [match.groupdict() for match in pattern.finditer(text)]


def _manifest_project(text: str, name: str) -> dict[str, str]:
    match = re.search(
        rf"(?ms)^    - name:\s*{re.escape(name)}\s*$\n"
        r"(?P<body>(?:^      [^\n]*\n?)*)",
        text,
    )
    if not match:
        fail(f"config/west.yml has no project named {name!r}")
    values: dict[str, str] = {}
    for line in match.group("body").splitlines():
        item = re.match(r"^\s{6}([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if item:
            key, value = item.groups()
            if key in values:
                fail(f"config/west.yml repeats {key!r} in project {name!r}")
            values[key] = value
    return values


def check_build_files() -> None:
    build_text = (ROOT / "build.yaml").read_text(encoding="utf-8")
    if not re.search(r"(?m)^include:\s*$", build_text):
        fail("build.yaml is missing the include matrix")
    entries = _parse_build_entries(build_text)
    expected_targets = [
        (BOARD, "modu_left", "modu_left"),
        (BOARD, "modu_right", "modu_right"),
    ]
    actual_targets = [
        (entry["board"], entry["shield"], entry["artifact"]) for entry in entries
    ]
    if actual_targets != expected_targets:
        fail(f"build.yaml targets differ from expected left/right targets: {actual_targets}")

    expected_cmake = (
        "-DZMK_EXTRA_MODULES=${GITHUB_WORKSPACE}/modu-c-firmware/modu-module;"
        "${GITHUB_WORKSPACE}/modu-c-firmware/zmk-pmw3610-driver"
    )
    for entry in entries:
        try:
            parsed = shlex.split(entry["cmake"])
        except ValueError as exc:
            fail(f"invalid cmake-args quoting for {entry['shield']}: {exc}")
        if parsed != [expected_cmake]:
            fail(
                f"cmake-args for {entry['shield']} must be one quoted CMake-list argument"
            )

    west_text = (ROOT / "config/west.yml").read_text(encoding="utf-8")
    zmk = _manifest_project(west_text, "zmk")
    modu = _manifest_project(west_text, "modu-c-firmware")
    if zmk.get("remote") != "zmkfirmware":
        fail("ZMK project must use the zmkfirmware remote")
    if zmk.get("revision") != ZMK_REVISION or zmk.get("import") != "app/west.yml":
        fail("ZMK project revision/import differs from the audited pinned configuration")
    if modu.get("remote") != "modu-c-upstream":
        fail("MODU-C project must use the modu-c-upstream remote")
    if modu.get("revision") != MODU_REVISION or modu.get("path") != "modu-c-firmware":
        fail("MODU-C project revision/path differs from the audited pinned configuration")
    for token in (
        "url-base: https://github.com/zmkfirmware",
        "url-base: https://github.com/22sh22",
        "self:\n    path: config",
    ):
        if token not in west_text:
            fail(f"config/west.yml is missing {token!r}")

    workflow = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
    required_workflow_tokens = (
        f"build-user-config.yml@{ZMK_REVISION}",
        "build_matrix_path: build.yaml",
        "config_path: config",
        "fallback_binary: hex",
        "archive_name: modu-c-intermediate",
        "python3 scripts/package_firmware.py",
        "--family 0xADA52840",
        "python3 scripts/verify_uf2.py uf2/modu_left.uf2 uf2/modu_right.uf2",
        "cp LICENSE NOTICE.md THIRD_PARTY_NOTICES.md uf2/",
        "cp -R LICENSES uf2/LICENSES",
        "name: modu-c-firmware",
        "path: uf2/",
    )
    for token in required_workflow_tokens:
        if token not in workflow:
            fail(f"workflow is missing {token!r}")

    for trigger_path in (
        '      - "config/**"',
        '      - "scripts/**"',
        '      - "build.yaml"',
        '      - ".github/workflows/build.yml"',
        '      - "LICENSE"',
        '      - "NOTICE.md"',
        '      - "THIRD_PARTY_NOTICES.md"',
        '      - "LICENSES/**"',
    ):
        if workflow.count(trigger_path) != 2:
            fail(f"workflow push/pull_request paths must both include {trigger_path.strip()}")

    for required in REQUIRED_LICENSE_FILES:
        path = ROOT / required
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"required license or notice file is missing/empty: {required}")

    for script in (
        "scripts/normalize_hex.py",
        "scripts/verify_uf2.py",
        "scripts/package_firmware.py",
        "scripts/selftest.py",
    ):
        source = (ROOT / script).read_text(encoding="utf-8")
        try:
            compile(source, script, "exec")
        except SyntaxError as exc:
            fail(f"{script} has a syntax error: {exc}")


def main() -> None:
    check_metadata()
    check_keymap()
    check_build_files()
    print("OK: metadata matches the 67-position upstream default_transform.")
    print("OK: every keymap layer has 67 bindings; default placeholders are at 51..56 only.")
    print("OK: left/right build targets, pinned source revisions, and module paths are exact.")
    print("OK: deterministic HEX normalization, UF2 structural checks, and notices are wired in.")


if __name__ == "__main__":
    main()
