#!/usr/bin/env python3
"""Select, convert, and verify the two MODU-C firmware build outputs."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from normalize_hex import HexFormatError, normalize
from verify_uf2 import MODU_C_FAMILY_ID, Uf2ValidationError, validate_uf2

TARGETS = ("modu_left", "modu_right")


class PackageError(RuntimeError):
    """Raised when build outputs are missing, ambiguous, or invalid."""


def _single_input(intermediate: Path, target: str) -> tuple[str, Path]:
    uf2_matches = sorted(intermediate.rglob(f"{target}.uf2"))
    hex_matches = sorted(intermediate.rglob(f"{target}.hex"))
    matches = [("uf2", path) for path in uf2_matches] + [
        ("hex", path) for path in hex_matches
    ]
    if len(matches) != 1:
        rendered = ", ".join(str(path) for _, path in matches) or "none"
        raise PackageError(
            f"expected exactly one {target}.uf2 or {target}.hex; "
            f"found {len(matches)} ({rendered})"
        )
    return matches[0]


def package_firmware(
    intermediate: Path,
    converter: Path,
    output: Path,
    family_id: int = MODU_C_FAMILY_ID,
) -> list[Path]:
    if not intermediate.is_dir():
        raise PackageError(f"intermediate build directory does not exist: {intermediate}")

    selections = {target: _single_input(intermediate, target) for target in TARGETS}
    needs_conversion = any(kind == "hex" for kind, _ in selections.values())
    if needs_conversion:
        if not converter.is_file():
            raise PackageError(f"UF2 converter does not exist: {converter}")
        if not (converter.parent / "uf2families.json").is_file():
            raise PackageError(
                f"UF2 converter companion file is missing: {converter.parent / 'uf2families.json'}"
            )

    output.mkdir(parents=True, exist_ok=True)
    results: list[Path] = []

    with tempfile.TemporaryDirectory(prefix="modu-c-hex-") as temporary:
        temporary_dir = Path(temporary)
        for target in TARGETS:
            kind, source = selections[target]
            destination = output / f"{target}.uf2"
            destination.unlink(missing_ok=True)

            if kind == "uf2":
                shutil.copy2(source, destination)
                print(f"Selected native UF2 for {target}: {source}")
            else:
                normalized = temporary_dir / f"{target}.hex"
                try:
                    normalize(source, normalized)
                except (OSError, HexFormatError) as exc:
                    raise PackageError(f"cannot normalize {source}: {exc}") from exc

                command = [
                    sys.executable,
                    str(converter),
                    "-f",
                    f"0x{family_id:08X}",
                    "-c",
                    "-o",
                    str(destination),
                    str(normalized),
                ]
                print(f"Converting validated HEX for {target}: {source}")
                try:
                    subprocess.run(command, check=True)
                except subprocess.CalledProcessError as exc:
                    raise PackageError(
                        f"UF2 converter failed for {target} with exit code {exc.returncode}"
                    ) from exc

            if not destination.is_file() or destination.stat().st_size == 0:
                raise PackageError(f"packaging did not create a non-empty {destination}")
            results.append(destination)

    try:
        summaries = [validate_uf2(path, family_id) for path in results]
    except (OSError, Uf2ValidationError) as exc:
        raise PackageError(str(exc)) from exc
    if summaries[0].sha256 == summaries[1].sha256:
        raise PackageError(
            "left and right UF2 files are byte-identical; the same build may have been selected twice"
        )

    for summary in summaries:
        print(
            f"Verified {summary.path.name}: {summary.block_count} blocks, "
            f"sha256={summary.sha256}"
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Package the exact MODU-C left/right build outputs as verified UF2 files."
    )
    parser.add_argument("--intermediate", required=True, type=Path)
    parser.add_argument("--converter", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--family",
        type=lambda value: int(value, 0),
        default=MODU_C_FAMILY_ID,
        help="UF2 family ID (default: 0xADA52840)",
    )
    args = parser.parse_args()

    try:
        package_firmware(args.intermediate, args.converter, args.output, args.family)
    except (OSError, PackageError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc


if __name__ == "__main__":
    main()
