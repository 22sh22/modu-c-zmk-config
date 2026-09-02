#!/usr/bin/env python3
"""Dependency-free tests for the wrapper's HEX/UF2 packaging safeguards."""

from __future__ import annotations

import shutil
import struct
import tempfile
from pathlib import Path
from typing import Callable

from normalize_hex import HexFormatError, normalize
from package_firmware import PackageError, package_firmware
from verify_uf2 import (
    MODU_C_FAMILY_ID,
    UF2_BLOCK_SIZE,
    UF2_FLAG_FAMILY_ID_PRESENT,
    UF2_MAGIC_END,
    UF2_MAGIC_START0,
    UF2_MAGIC_START1,
    Uf2ValidationError,
    validate_uf2,
)


def ihex_record(address: int, record_type: int, payload: bytes = b"") -> str:
    content = bytes(
        [len(payload), (address >> 8) & 0xFF, address & 0xFF, record_type]
    ) + payload
    checksum = (-sum(content)) & 0xFF
    return ":" + (content + bytes([checksum])).hex().upper()


def write_hex(path: Path, seed: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [
        ihex_record(0, 4, b"\x00\x00"),
        ihex_record(0x1000, 0, bytes((seed + i) & 0xFF for i in range(16))),
        ihex_record(0, 1),
    ]
    # CRLF, terminal newline, and an extra blank line intentionally exercise
    # the normalization required by the pinned upstream converter.
    path.write_bytes(("\r\n".join(records) + "\r\n\r\n").encode("ascii"))


def write_uf2(path: Path, seed: int, family: int = MODU_C_FAMILY_ID) -> None:
    blocks: list[bytes] = []
    block_count = 2
    for block_number in range(block_count):
        payload = bytes(
            (seed + block_number + index) & 0xFF for index in range(256)
        )
        header = struct.pack(
            "<8I",
            UF2_MAGIC_START0,
            UF2_MAGIC_START1,
            UF2_FLAG_FAMILY_ID_PRESENT,
            0x1000 + block_number * 0x100,
            len(payload),
            block_number,
            block_count,
            family,
        )
        padding = bytes(UF2_BLOCK_SIZE - len(header) - len(payload) - 4)
        blocks.append(header + payload + padding + struct.pack("<I", UF2_MAGIC_END))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(blocks))


def mutate_u32(source: Path, destination: Path, block: int, offset: int, value: int) -> None:
    data = bytearray(source.read_bytes())
    struct.pack_into("<I", data, block * UF2_BLOCK_SIZE + offset, value)
    destination.write_bytes(data)


def expect_error(exception: type[Exception], function: Callable, *args) -> None:
    try:
        function(*args)
    except exception:
        return
    raise AssertionError(f"expected {exception.__name__} from {function.__name__}")


def write_fake_converter(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """#!/usr/bin/env python3
import argparse
import struct
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='family', required=True)
parser.add_argument('-c', action='store_true')
parser.add_argument('-o', dest='output', required=True)
parser.add_argument('input')
args = parser.parse_args()
source = Path(args.input).read_bytes()
if source.endswith((b'\\n', b'\\r')):
    raise SystemExit('input still has a terminal newline')
seed = 17 if 'left' in Path(args.output).name else 91
family = int(args.family, 0)
blocks = []
for number in range(2):
    payload = bytes((seed + number + i) & 0xff for i in range(256))
    header = struct.pack('<8I', 0x0A324655, 0x9E5D5157, 0x2000,
                         0x1000 + number * 0x100, 256, number, 2, family)
    blocks.append(header + payload + bytes(220) + struct.pack('<I', 0x0AB16F30))
Path(args.output).write_bytes(b''.join(blocks))
""",
        encoding="utf-8",
    )
    (path.parent / "uf2families.json").write_text("[]\n", encoding="utf-8")


def test_hex(root: Path) -> None:
    raw_hex = root / "raw.hex"
    normalized_hex = root / "normalized.hex"
    write_hex(raw_hex, 3)
    normalize(raw_hex, normalized_hex)
    normalized_bytes = normalized_hex.read_bytes()
    assert normalized_bytes and not normalized_bytes.endswith((b"\n", b"\r"))
    assert len(normalized_bytes.splitlines()) == 3

    bad_checksum = root / "bad-checksum.hex"
    bad_checksum.write_text(ihex_record(0, 1)[:-1] + "0", encoding="ascii")
    expect_error(HexFormatError, normalize, bad_checksum, root / "discard.hex")

    non_hex = root / "non-hex.hex"
    non_hex.write_text(ihex_record(0, 1)[:-1] + "G", encoding="ascii")
    expect_error(HexFormatError, normalize, non_hex, root / "discard.hex")

    after_eof = root / "after-eof.hex"
    after_eof.write_text(
        "\n".join(
            [
                ihex_record(0x1000, 0, b"\x01"),
                ihex_record(0, 1),
                ihex_record(0x1001, 0, b"\x02"),
            ]
        ),
        encoding="ascii",
    )
    expect_error(HexFormatError, normalize, after_eof, root / "discard.hex")

    bad_control_address = root / "bad-control-address.hex"
    bad_control_address.write_text(
        "\n".join(
            [
                ihex_record(1, 4, b"\x00\x00"),
                ihex_record(0x1000, 0, b"\x01"),
                ihex_record(0, 1),
            ]
        ),
        encoding="ascii",
    )
    expect_error(HexFormatError, normalize, bad_control_address, root / "discard.hex")

    crossing = root / "crossing.hex"
    crossing.write_text(
        "\n".join(
            [
                ihex_record(0xFFF8, 0, bytes(range(16))),
                ihex_record(0, 1),
            ]
        ),
        encoding="ascii",
    )
    expect_error(HexFormatError, normalize, crossing, root / "discard.hex")


def test_uf2(root: Path) -> None:
    left = root / "left.uf2"
    right = root / "right.uf2"
    write_uf2(left, 11)
    write_uf2(right, 37)
    left_summary = validate_uf2(left)
    right_summary = validate_uf2(right)
    assert left_summary.sha256 != right_summary.sha256

    wrong_family = root / "wrong-family.uf2"
    write_uf2(wrong_family, 55, 0x12345678)
    expect_error(Uf2ValidationError, validate_uf2, wrong_family)

    bad_magic = root / "bad-magic.uf2"
    bad_magic.write_bytes(b"\x00" * UF2_BLOCK_SIZE)
    expect_error(Uf2ValidationError, validate_uf2, bad_magic)

    declared_count = root / "bad-declared-count.uf2"
    mutate_u32(left, declared_count, 0, 24, 3)
    expect_error(Uf2ValidationError, validate_uf2, declared_count)

    duplicate_number = root / "duplicate-number.uf2"
    mutate_u32(left, duplicate_number, 1, 20, 0)
    expect_error(Uf2ValidationError, validate_uf2, duplicate_number)

    overlap = root / "overlap.uf2"
    mutate_u32(left, overlap, 1, 12, 0x1080)
    expect_error(Uf2ValidationError, validate_uf2, overlap)

    unaligned = root / "unaligned.uf2"
    mutate_u32(left, unaligned, 1, 12, 0x1101)
    expect_error(Uf2ValidationError, validate_uf2, unaligned)

    overflow = root / "overflow.uf2"
    mutate_u32(left, overflow, 1, 12, 0xFFFFFFFC)
    expect_error(Uf2ValidationError, validate_uf2, overflow)


def test_packaging(root: Path) -> None:
    native_inputs = root / "native-inputs"
    write_uf2(native_inputs / "a/modu_left.uf2", 13)
    write_uf2(native_inputs / "b/modu_right.uf2", 71)
    native_output = root / "native-output"
    package_firmware(native_inputs, root / "unused-converter.py", native_output)
    validate_uf2(native_output / "modu_left.uf2")
    validate_uf2(native_output / "modu_right.uf2")

    hex_inputs = root / "hex-inputs"
    hex_inputs.mkdir()
    write_hex(hex_inputs / "modu_left.hex", 19)
    write_hex(hex_inputs / "modu_right.hex", 83)
    fake_converter = root / "fake-tools/uf2conv.py"
    write_fake_converter(fake_converter)
    hex_output = root / "hex-output"
    package_firmware(hex_inputs, fake_converter, hex_output)
    validate_uf2(hex_output / "modu_left.uf2")
    validate_uf2(hex_output / "modu_right.uf2")

    missing = root / "missing"
    write_uf2(missing / "modu_left.uf2", 5)
    expect_error(
        PackageError,
        package_firmware,
        missing,
        fake_converter,
        root / "missing-output",
    )

    ambiguous = root / "ambiguous"
    write_hex(ambiguous / "one/modu_left.hex", 1)
    write_hex(ambiguous / "two/modu_left.hex", 2)
    write_hex(ambiguous / "modu_right.hex", 3)
    expect_error(
        PackageError,
        package_firmware,
        ambiguous,
        fake_converter,
        root / "ambiguous-output",
    )

    identical = root / "identical"
    write_uf2(identical / "modu_left.uf2", 29)
    shutil.copy2(identical / "modu_left.uf2", identical / "modu_right.uf2")
    expect_error(
        PackageError,
        package_firmware,
        identical,
        fake_converter,
        root / "identical-output",
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="modu-c-selftest-") as temporary:
        root = Path(temporary)
        test_hex(root / "hex")
        test_uf2(root / "uf2")
        test_packaging(root / "packaging")

    print("OK: HEX normalization rejects corruption and removes terminal blank lines.")
    print("OK: UF2 magic, family ID, block tables, ranges, and address limits are enforced.")
    print("OK: native/HEX packaging rejects missing, duplicate, and identical half outputs.")


if __name__ == "__main__":
    main()
