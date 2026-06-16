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
    binary = "".join(format(ord(c), "08b") for c in spaced)
    encoded = binary[::-1] + "".join(format(ord(d), "08b") for d in pin)
    return encoded, f"{_SEPARATOR}{pin}"


def _decrypt(encoded: str, key: str) -> str:
    separator = key[0]
    binary = encoded[: -8 * _PIN_LENGTH][::-1]
    chars = [chr(int(binary[i:i + 8], 2)) for i in range(0, len(binary), 8)]
    return "".join(chars).replace(separator, "")


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
