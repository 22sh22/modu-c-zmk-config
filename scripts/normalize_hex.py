#!/usr/bin/env python3
"""Validate and normalize an Intel HEX file for the pinned UF2 converter.

The upstream converter splits on ``\n`` and indexes every resulting line. A
terminal newline therefore leaves an empty final item. This helper verifies the
Intel HEX records and writes a canonical copy with LF separators and no final
newline before conversion.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


class HexFormatError(ValueError):
    """Raised when an Intel HEX file is malformed or unsafe to convert."""


def _parse_record(line: str, line_number: int) -> bytes:
    if not line.startswith(":"):
        raise HexFormatError(f"line {line_number}: record does not start with ':'")

    encoded = line[1:]
    if not encoded or len(encoded) % 2:
        raise HexFormatError(f"line {line_number}: record has an invalid hex length")
    if re.fullmatch(r"[0-9A-Fa-f]+", encoded) is None:
        raise HexFormatError(f"line {line_number}: record contains non-hex data")

    record = bytes.fromhex(encoded)

    if len(record) < 5:
        raise HexFormatError(f"line {line_number}: record is shorter than five bytes")

    byte_count = record[0]
    expected_length = byte_count + 5
    if len(record) != expected_length:
        raise HexFormatError(
            f"line {line_number}: byte count says {byte_count}, "
            f"but record length implies {len(record) - 5}"
        )

    if sum(record) & 0xFF:
        raise HexFormatError(f"line {line_number}: checksum mismatch")

    address = (record[1] << 8) | record[2]
    record_type = record[3]
    if record_type not in {0, 1, 2, 3, 4, 5}:
        raise HexFormatError(f"line {line_number}: unsupported record type {record_type}")

    if record_type != 0 and address != 0:
        raise HexFormatError(
            f"line {line_number}: record type {record_type} must use address 0x0000"
        )
    if record_type == 0 and address + byte_count > 0x10000:
        raise HexFormatError(
            f"line {line_number}: data record crosses the 16-bit address boundary"
        )

    required_lengths = {1: 0, 2: 2, 3: 4, 4: 2, 5: 4}
    required = required_lengths.get(record_type)
    if required is not None and byte_count != required:
        raise HexFormatError(
            f"line {line_number}: record type {record_type} must contain "
            f"{required} data bytes, found {byte_count}"
        )

    return record


def normalize(source: Path, destination: Path) -> int:
    try:
        text = source.read_bytes().decode("ascii")
    except UnicodeDecodeError as exc:
        raise HexFormatError("input is not ASCII Intel HEX text") from exc

    canonical: list[str] = []
    eof_seen = False
    data_records = 0

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if eof_seen:
            raise HexFormatError(f"line {line_number}: record appears after EOF")

        record = _parse_record(line, line_number)
        record_type = record[3]
        if record_type == 0:
            data_records += 1
        elif record_type == 1:
            eof_seen = True

        canonical.append(":" + record.hex().upper())

    if not canonical:
        raise HexFormatError("input contains no Intel HEX records")
    if data_records == 0:
        raise HexFormatError("input contains no data records")
    if not eof_seen:
        raise HexFormatError("input does not contain an EOF record")

    destination.parent.mkdir(parents=True, exist_ok=True)
    # Deliberately omit a terminal newline for compatibility with the pinned
    # upstream uf2conv.py parser.
    destination.write_bytes("\n".join(canonical).encode("ascii"))
    return len(canonical)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate Intel HEX and remove blank/trailing lines before UF2 conversion."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    try:
        count = normalize(args.source, args.destination)
    except (OSError, HexFormatError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc

    print(f"OK: normalized {count} Intel HEX records -> {args.destination}")


if __name__ == "__main__":
    main()
