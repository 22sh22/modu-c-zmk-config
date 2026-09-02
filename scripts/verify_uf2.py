#!/usr/bin/env python3
"""Structural validation for the final MODU-C UF2 firmware files."""

from __future__ import annotations

import argparse
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

UF2_BLOCK_SIZE = 512
UF2_DATA_CAPACITY = 476
UF2_MAGIC_START0 = 0x0A324655
UF2_MAGIC_START1 = 0x9E5D5157
UF2_MAGIC_END = 0x0AB16F30
UF2_FLAG_NOFLASH = 0x00000001
UF2_FLAG_FAMILY_ID_PRESENT = 0x00002000
MODU_C_FAMILY_ID = 0xADA52840


class Uf2ValidationError(ValueError):
    """Raised when a generated UF2 file fails structural checks."""


@dataclass(frozen=True)
class Uf2Summary:
    path: Path
    block_count: int
    lowest_address: int
    highest_address: int
    sha256: str


def validate_uf2(path: Path, expected_family: int = MODU_C_FAMILY_ID) -> Uf2Summary:
    data = path.read_bytes()
    if not data:
        raise Uf2ValidationError(f"{path}: file is empty")
    if len(data) % UF2_BLOCK_SIZE:
        raise Uf2ValidationError(
            f"{path}: size {len(data)} is not a multiple of {UF2_BLOCK_SIZE}"
        )

    block_count = len(data) // UF2_BLOCK_SIZE
    seen_block_numbers: set[int] = set()
    ranges: list[tuple[int, int, int]] = []

    for physical_index in range(block_count):
        offset = physical_index * UF2_BLOCK_SIZE
        block = data[offset : offset + UF2_BLOCK_SIZE]
        (
            magic0,
            magic1,
            flags,
            target_address,
            payload_size,
            block_number,
            declared_blocks,
            family_or_size,
        ) = struct.unpack_from("<8I", block, 0)
        (magic_end,) = struct.unpack_from("<I", block, UF2_BLOCK_SIZE - 4)

        prefix = f"{path}: physical block {physical_index}"
        if magic0 != UF2_MAGIC_START0 or magic1 != UF2_MAGIC_START1:
            raise Uf2ValidationError(f"{prefix}: invalid UF2 start magic")
        if magic_end != UF2_MAGIC_END:
            raise Uf2ValidationError(f"{prefix}: invalid UF2 end magic")
        if flags & UF2_FLAG_NOFLASH:
            raise Uf2ValidationError(f"{prefix}: marked NOFLASH instead of firmware data")
        if not flags & UF2_FLAG_FAMILY_ID_PRESENT:
            raise Uf2ValidationError(f"{prefix}: family-ID-present flag is missing")
        if family_or_size != expected_family:
            raise Uf2ValidationError(
                f"{prefix}: family ID 0x{family_or_size:08X}, "
                f"expected 0x{expected_family:08X}"
            )
        if not 0 < payload_size <= UF2_DATA_CAPACITY:
            raise Uf2ValidationError(
                f"{prefix}: payload size {payload_size} is outside 1..{UF2_DATA_CAPACITY}"
            )
        if target_address % 4:
            raise Uf2ValidationError(f"{prefix}: target address is not 4-byte aligned")
        if target_address + payload_size > 0x1_0000_0000:
            raise Uf2ValidationError(f"{prefix}: payload address range exceeds 32 bits")
        if declared_blocks != block_count:
            raise Uf2ValidationError(
                f"{prefix}: declares {declared_blocks} blocks, file contains {block_count}"
            )
        if block_number >= block_count:
            raise Uf2ValidationError(
                f"{prefix}: block number {block_number} is outside the declared range"
            )
        if block_number in seen_block_numbers:
            raise Uf2ValidationError(f"{prefix}: duplicate block number {block_number}")

        seen_block_numbers.add(block_number)
        ranges.append((target_address, target_address + payload_size, block_number))

    expected_numbers = set(range(block_count))
    if seen_block_numbers != expected_numbers:
        missing = sorted(expected_numbers - seen_block_numbers)
        raise Uf2ValidationError(f"{path}: missing block numbers {missing}")

    ranges.sort()
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1]:
            raise Uf2ValidationError(
                f"{path}: payload ranges overlap between blocks "
                f"{previous[2]} and {current[2]}"
            )

    digest = hashlib.sha256(data).hexdigest()
    return Uf2Summary(
        path=path,
        block_count=block_count,
        lowest_address=ranges[0][0],
        highest_address=max(end for _, end, _ in ranges),
        sha256=digest,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify MODU-C left/right UF2 structure, family ID, and separation."
    )
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument(
        "--family",
        type=lambda value: int(value, 0),
        default=MODU_C_FAMILY_ID,
        help="expected UF2 family ID (default: 0xADA52840)",
    )
    args = parser.parse_args()

    try:
        summaries = [validate_uf2(path, args.family) for path in args.files]
    except (OSError, Uf2ValidationError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc

    if len(summaries) == 2 and summaries[0].sha256 == summaries[1].sha256:
        raise SystemExit(
            "ERROR: left and right UF2 files are byte-identical; packaging likely selected "
            "the same build twice"
        )

    for summary in summaries:
        print(
            f"OK: {summary.path.name}: {summary.block_count} blocks, "
            f"0x{summary.lowest_address:08X}..0x{summary.highest_address:08X}, "
            f"sha256={summary.sha256}"
        )


if __name__ == "__main__":
    main()
