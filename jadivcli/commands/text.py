"""The toy 'cipher' command.

This is a reversible obfuscation for fun, NOT real cryptography — do not use it
to protect anything sensitive. It interleaves the text with a separator
character, encodes the result as reversed binary, and appends a binary-encoded
random PIN. The decrypt key is the separator character followed by that PIN.
"""

from __future__ import annotations

import random
import string
from typing import List

from ..registry import command

_SEPARATOR = "*"
_PIN_LENGTH = 4


def _encrypt(text: str) -> tuple[str, str]:
    pin = "".join(random.choices(string.digits, k=_PIN_LENGTH))
    spaced = _SEPARATOR.join(text)
    binary = "".join(format(byte, "08b") for byte in spaced.encode("utf-8"))
    encoded = binary[::-1] + "".join(format(ord(d), "08b") for d in pin)
    return encoded, f"{_SEPARATOR}{pin}"


def _decrypt(encoded: str, key: str) -> str:
    if len(key) != len(_SEPARATOR) + _PIN_LENGTH or not key.startswith(_SEPARATOR):
        raise ValueError("Invalid decrypt key.")
    pin = key[len(_SEPARATOR):]
    if not pin.isdigit():
        raise ValueError("Invalid decrypt key.")
    pin_bits = "".join(format(ord(d), "08b") for d in pin)
    if len(encoded) < len(pin_bits) or not encoded.endswith(pin_bits):
        raise ValueError("Invalid decrypt key.")

    binary = encoded[:-len(pin_bits)][::-1]
    if len(binary) % 8 or set(binary) - {"0", "1"}:
        raise ValueError("Invalid encrypted text.")
    raw = bytes(int(binary[i:i + 8], 2) for i in range(0, len(binary), 8))
    # Original characters are at even indices after join(); do not strip '*'
    # with replace(), which would also drop '*' from the plaintext.
    return raw.decode("utf-8")[::2]


@command("cipher", category="Text",
         usage="cipher encrypt <text> | cipher decrypt <text> <key>",
         help="Toy reversible text obfuscation (NOT secure).")
def cipher(shell, args: List[str]) -> None:
    if not args or args[0] not in ("encrypt", "decrypt"):
        print("Usage: cipher encrypt <text> | cipher decrypt <text> <key>")
        return

    if args[0] == "encrypt":
        if len(args) < 2:
            print("Error: provide the text to encrypt.")
            return
        encoded, key = _encrypt(" ".join(args[1:]))
        print(f"Encrypted: {encoded}")
        print(f"Decrypt key: {key}")
        return

    # decrypt
    if len(args) < 3:
        print("Error: provide the encrypted text and the decrypt key.")
        return
    try:
        print(f"Decrypted: {_decrypt(args[1], args[2])}")
    except (ValueError, IndexError):
        print("Error: could not decrypt — check the text and key.")
