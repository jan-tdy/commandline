"""File-conversion helpers used by the merge commands.

These functions funnel arbitrary input files through PDF as a common
intermediate so that any mix of formats can be combined:

* office/text documents are converted to PDF with LibreOffice (``soffice``);
* images are converted to PDF with Pillow;
* PDFs are used as-is.

The heavy third-party libraries (``pypdf``, ``Pillow``, ``pymupdf``) are
optional — they are imported lazily so the rest of the tool keeps working when
they are absent. The merge commands check availability up front and print a
clear install hint instead of failing with a traceback.
"""

from __future__ import annotations

import importlib
import shutil
import subprocess
import tempfile
from pathlib import Path
from types import ModuleType
from typing import List, Optional

# Extensions handled directly as images (everything else that is not a PDF is
# treated as a document and converted with LibreOffice).
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"}


class ConversionError(RuntimeError):
    """Raised when a file cannot be converted to the requested format."""


def optional_import(name: str) -> Optional[ModuleType]:
    """Import ``name`` and return the module, or ``None`` if it is unavailable.

    Catches not just :class:`ImportError` but any failure raised while importing
    (a broken optional dependency can fail in other ways), so a missing or
    misconfigured library degrades to a clean "install it" hint rather than
    crashing the shell.
    """
    try:
        return importlib.import_module(name)
    except BaseException:  # noqa: BLE001 - an optional import must never crash us.
        return None


def file_kind(path: Path) -> str:
    """Classify a path as ``"pdf"``, ``"image"`` or ``"document"`` by extension."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext in IMAGE_EXTS:
        return "image"
    return "document"


def _image_to_pdf(path: Path, tmpdir: Path) -> Path:
    Image = optional_import("PIL.Image")
    if Image is None:
        raise ConversionError("Pillow is required for image inputs")
    out = tmpdir / (path.stem + ".pdf")
    try:
        with Image.open(path) as img:
            img.convert("RGB").save(out, "PDF")
    except Exception as exc:  # noqa: BLE001 - surface any Pillow failure cleanly.
        raise ConversionError(f"could not convert image '{path.name}': {exc}") from exc
    return out


def _document_to_pdf(path: Path, tmpdir: Path) -> Path:
    if shutil.which("soffice") is None:
        raise ConversionError("LibreOffice (soffice) is required for document inputs")
    # A throwaway user profile lets soffice run even if a desktop instance is open.
    profile = (tmpdir / "loprofile").as_uri()
    try:
        subprocess.run(
            [
                "soffice", "--headless", f"-env:UserInstallation={profile}",
                "--convert-to", "pdf", "--outdir", str(tmpdir), str(path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or b"").decode(errors="replace").strip()
        raise ConversionError(f"LibreOffice failed to convert '{path.name}': {detail}") from exc
    out = tmpdir / (path.stem + ".pdf")
    if not out.exists():
        raise ConversionError(f"LibreOffice produced no PDF for '{path.name}'")
    return out


def to_pdf(path: Path, tmpdir: Path) -> Path:
    """Convert ``path`` to a PDF inside ``tmpdir`` and return the PDF path.

    PDFs are returned unchanged. Raises :class:`ConversionError` on failure.
    """
    kind = file_kind(path)
    if kind == "pdf":
        return path
    if kind == "image":
        return _image_to_pdf(path, tmpdir)
    return _document_to_pdf(path, tmpdir)


def merge_pdfs(pdf_paths: List[Path], output: Path) -> None:
    """Concatenate ``pdf_paths`` into a single PDF at ``output``."""
    pypdf = optional_import("pypdf")
    if pypdf is None:
        raise ConversionError("pypdf is required to merge PDFs")
    writer = pypdf.PdfWriter()
    try:
        for pdf in pdf_paths:
            writer.append(str(pdf))
        with open(output, "wb") as fh:
            writer.write(fh)
    finally:
        writer.close()


def pdf_to_images(pdf_path: Path, dpi: int = 150) -> list:
    """Render every page of ``pdf_path`` to a list of Pillow images."""
    fitz = optional_import("fitz")  # provided by the pymupdf package
    Image = optional_import("PIL.Image")
    if fitz is None or Image is None:
        raise ConversionError("pymupdf and Pillow are required to rasterise PDFs")
    images = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=dpi)
            images.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    return images


def stitch_vertical(images: list, output: Path) -> None:
    """Stack ``images`` top-to-bottom into a single PNG saved at ``output``."""
    Image = optional_import("PIL.Image")
    if Image is None:
        raise ConversionError("Pillow is required to stitch images")
    if not images:
        raise ConversionError("there is nothing to stitch")
    width = max(img.width for img in images)
    height = sum(img.height for img in images)
    canvas = Image.new("RGB", (width, height), "white")
    y = 0
    for img in images:
        rgb = img.convert("RGB")
        canvas.paste(rgb, (0, y))  # left-aligned; narrower pages keep their width
        y += rgb.height
    canvas.save(output, "PNG")


def load_image(path: Path):
    """Open an image file as an RGB Pillow image (used by the all-images fast path)."""
    Image = optional_import("PIL.Image")
    if Image is None:
        raise ConversionError("Pillow is required for image inputs")
    try:
        with Image.open(path) as img:
            return img.convert("RGB")
    except Exception as exc:  # noqa: BLE001 - surface any Pillow failure cleanly.
        raise ConversionError(f"could not open image '{path.name}': {exc}") from exc
