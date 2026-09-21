"""Render generated proposal PPTX bytes to a browser-friendly PDF preview."""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from contextlib import contextmanager
import json
from collections.abc import Callable
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from threading import RLock

from pypdf import PdfReader
from pypdf.errors import PdfReadError


PREVIEW_TIMEOUT_SECONDS = 180
PREVIEW_LOCK = RLock()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREVIEW_CACHE = PROJECT_ROOT / "storage" / "presentation_previews"


def _convert_with_libreoffice(source_path: Path, output_path: Path) -> bool:
    executable = shutil.which("soffice") or shutil.which("libreoffice")
    if not executable:
        return False
    subprocess.run(
        [
            executable,
            "--headless",
            f"-env:UserInstallation={(output_path.parent / 'office-profile').as_uri()}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_path.parent),
            str(source_path),
        ],
        check=True,
        capture_output=True,
        timeout=PREVIEW_TIMEOUT_SECONDS,
    )
    converted_path = output_path.parent / f"{source_path.stem}.pdf"
    if converted_path != output_path and converted_path.exists():
        converted_path.replace(output_path)
    return output_path.exists()


def _convert_with_powerpoint(source_path: Path, output_path: Path) -> bool:
    if os.name != "nt":
        return False
    script_path = Path(__file__).with_name("scripts") / "render_pptx_preview.ps1"
    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-SourcePath",
            str(source_path),
            "-OutputPath",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=PREVIEW_TIMEOUT_SECONDS,
    )
    return completed.returncode == 0 and output_path.exists()


def render_presentation_preview(pptx_bytes: bytes) -> tuple[bytes, int]:
    """Return cached PDF bytes and slide count for an exact PPTX payload."""
    digest = sha256(pptx_bytes).hexdigest()
    PREVIEW_CACHE.mkdir(parents=True, exist_ok=True)
    cached_pdf = PREVIEW_CACHE / f"{digest}.pdf"
    with _preview_slot():
        if not cached_pdf.is_file():
            with tempfile.TemporaryDirectory() as directory:
                workdir = Path(directory)
                source_path = workdir / "proposal.pptx"
                output_path = workdir / "proposal.pdf"
                source_path.write_bytes(pptx_bytes)
                try:
                    converted = _convert_with_libreoffice(source_path, output_path)
                    if not converted:
                        converted = _convert_with_powerpoint(source_path, output_path)
                except (OSError, subprocess.SubprocessError) as exc:
                    raise ValueError("PowerPoint 미리보기 변환에 실패했습니다.") from exc
                if not converted:
                    raise ValueError("미리보기를 만들려면 서버에 PowerPoint 또는 LibreOffice가 필요합니다.")
                pdf_bytes = output_path.read_bytes()
                slide_count = _page_count(pdf_bytes)
                _write_cache(cached_pdf, pdf_bytes)
                return pdf_bytes, slide_count
        pdf_bytes = cached_pdf.read_bytes()
        return pdf_bytes, _page_count(pdf_bytes)


def _page_count(pdf_bytes: bytes) -> int:
    try:
        count = len(PdfReader(BytesIO(pdf_bytes)).pages)
    except (PdfReadError, ValueError, KeyError, TypeError) as exc:
        raise ValueError("미리보기 PDF를 읽지 못했습니다.") from exc
    if count < 1:
        raise ValueError("미리보기 페이지를 확인하지 못했습니다.")
    return count


@contextmanager
def _preview_slot():
    # A second request must not queue forever behind a stuck Office conversion.
    if not PREVIEW_LOCK.acquire(timeout=15):
        raise ValueError("다른 미리보기를 변환 중입니다. 잠시 후 다시 불러와 주세요.")
    try:
        yield
    finally:
        PREVIEW_LOCK.release()


def _write_cache(path: Path, content: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.tmp', delete=False) as file:
        temp_path = Path(file.name)
        file.write(content)
    try:
        temp_path.replace(path)
    finally:
        temp_path.unlink(missing_ok=True)


def render_report_preview(payload: dict, version: str, build_presentation: Callable[[], bytes]) -> tuple[bytes, int]:
    """Stable report + template key avoids rerendering a timestamped PPTX on every visit."""
    key = json.dumps({'report': payload, 'version': version}, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    PREVIEW_CACHE.mkdir(parents=True, exist_ok=True)
    path = PREVIEW_CACHE / f"report-{sha256(key.encode('utf-8')).hexdigest()}.pdf"
    # Fast cache reads do not wait for unrelated Office conversions.
    if path.is_file():
        content = path.read_bytes()
        try:
            return content, _page_count(content)
        except ValueError:
            pass  # Rebuild corrupt derived cache; original reports are untouched.
    with _preview_slot():
        if path.is_file():
            try:
                content = path.read_bytes()
                return content, _page_count(content)
            except ValueError:
                pass
        content, count = render_presentation_preview(build_presentation())
        _write_cache(path, content)
        return content, count
