"""Commands that merge several files (any mix of formats) into one output file.

``merge_pdf`` combines the inputs into a single PDF; ``merge_png`` combines them
into a single tall PNG. Both accept images, PDFs and office/text documents and
funnel everything through PDF as a common intermediate (see
:mod:`jadivcli.convert`). When a required converter is missing, the command
prints a clear install hint and stops.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List, Tuple

from .. import convert, proc
from ..registry import command

_PIP_HINT = "pip install pypdf Pillow pymupdf"


def _missing(needs_soffice: bool, modules: List[Tuple[str, str]]) -> List[str]:
    """Return human-readable hints for every required tool that is unavailable."""
    hints: List[str] = []
    if needs_soffice and not proc.has_binary("soffice"):
        hints.append("LibreOffice — try: sudo apt install libreoffice")
    missing_mods = [label for mod, label in modules if convert.optional_import(mod) is None]
    if missing_mods:
        hints.append(f"{', '.join(missing_mods)} — try: {_PIP_HINT}")
    return hints


def _collect_inputs(args: List[str], usage: str) -> Tuple[Path, List[Path]] | None:
    """Validate ``args`` into (output, inputs); print errors and return None on failure."""
    if len(args) < 2:
        print(f"Usage: {usage}")
        return None
    output = Path(args[0])
    inputs = [Path(a) for a in args[1:]]
    missing = [str(p) for p in inputs if not p.is_file()]
    if missing:
        print(f"Input file(s) not found: {', '.join(missing)}")
        return None
    try:
        output_abs = output.resolve()
        if any(p.resolve() == output_abs for p in inputs):
            print("The output file cannot also be one of the inputs.")
            return None
    except OSError:
        pass  # if a path cannot be resolved, fall through and let the merge report it
    return output, inputs


@command("merge_pdf", category="Documents", usage="merge_pdf <output.pdf> <input...>",
         help="Merge files (images, PDFs, office/text docs) into one PDF.")
def merge_pdf(shell, args: List[str]) -> None:
    collected = _collect_inputs(args, "merge_pdf <output.pdf> <input...>")
    if collected is None:
        return
    output, inputs = collected

    kinds = {convert.file_kind(p) for p in inputs}
    hints = _missing(
        needs_soffice="document" in kinds,
        modules=[("pypdf", "pypdf")] + ([("PIL.Image", "Pillow")] if "image" in kinds else []),
    )
    if hints:
        print("Cannot merge — missing tools:")
        for hint in hints:
            print(f"  - {hint}")
        return

    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            pdfs = [convert.to_pdf(p, tmpdir) for p in inputs]
            convert.merge_pdfs(pdfs, output)
    except convert.ConversionError as exc:
        print(f"Merge failed: {exc}")
        return
    except OSError as exc:
        print(f"Could not write '{output}': {exc}")
        return
    print(f"Saved {output} ({len(inputs)} file(s) merged).")


@command("merge_png", category="Documents", usage="merge_png <output.png> <input...>",
         help="Merge files into one tall PNG (pages stacked vertically).")
def merge_png(shell, args: List[str]) -> None:
    collected = _collect_inputs(args, "merge_png <output.png> <input...>")
    if collected is None:
        return
    output, inputs = collected

    kinds = {convert.file_kind(p) for p in inputs}
    all_images = kinds == {"image"}
    if all_images:
        hints = _missing(needs_soffice=False, modules=[("PIL.Image", "Pillow")])
    else:
        # Non-image inputs are rendered via the PDF pipeline, then rasterised.
        hints = _missing(
            needs_soffice="document" in kinds,
            modules=[("pypdf", "pypdf"), ("fitz", "pymupdf"), ("PIL.Image", "Pillow")],
        )
    if hints:
        print("Cannot merge — missing tools:")
        for hint in hints:
            print(f"  - {hint}")
        return

    try:
        if all_images:
            images = [convert.load_image(p) for p in inputs]
        else:
            with tempfile.TemporaryDirectory() as tmp:
                tmpdir = Path(tmp)
                pdfs = [convert.to_pdf(p, tmpdir) for p in inputs]
                merged = tmpdir / "merged.pdf"
                convert.merge_pdfs(pdfs, merged)
                images = convert.pdf_to_images(merged)
        convert.stitch_vertical(images, output)
    except convert.ConversionError as exc:
        print(f"Merge failed: {exc}")
        return
    except OSError as exc:
        print(f"Could not write '{output}': {exc}")
        return
    print(f"Saved {output} ({len(inputs)} file(s) merged).")
