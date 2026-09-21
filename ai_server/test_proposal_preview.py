"""Preview cache and error paths without Office, database or LLM calls."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch
from pypdf import PdfWriter
from ai_server.app import proposal_preview as preview


def pdf():
    writer = PdfWriter(); writer.add_blank_page(width=160, height=90)
    stream = BytesIO(); writer.write(stream); return stream.getvalue()


class ProposalPreviewTests(TestCase):
    def test_report_and_version_cache_and_concurrent_requests(self):
        with TemporaryDirectory() as directory, patch.object(preview, 'PREVIEW_CACHE', Path(directory)), patch.object(preview, 'render_presentation_preview', return_value=(pdf(), 1)) as convert:
            build = Mock(return_value=b'ppt')
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda _: preview.render_report_preview({'title': 'A'}, 'v1', build), range(2)))
            self.assertEqual(results[0], results[1]); build.assert_called_once()
            preview.render_report_preview({'title': 'B'}, 'v1', build)
            preview.render_report_preview({'title': 'B'}, 'v2', build)
            self.assertEqual(convert.call_count, 3)

    def test_converter_failure_does_not_poison_cache(self):
        with TemporaryDirectory() as directory, patch.object(preview, 'PREVIEW_CACHE', Path(directory)), patch.object(preview, '_convert_with_libreoffice', side_effect=OSError('missing')):
            with self.assertRaisesRegex(ValueError, '실패'):
                preview.render_presentation_preview(b'new')
            self.assertEqual(list(Path(directory).glob('*.pdf')), [])

    def test_bad_pdf_is_not_published(self):
        def invalid(source, output):
            output.write_bytes(b'invalid pdf'); return True
        with TemporaryDirectory() as directory, patch.object(preview, 'PREVIEW_CACHE', Path(directory)), patch.object(preview, '_convert_with_libreoffice', side_effect=invalid):
            with self.assertRaises(ValueError): preview.render_presentation_preview(b'ppt')
            self.assertEqual(list(Path(directory).glob('*.pdf')), [])

    def test_wait_for_busy_converter_is_bounded(self):
        lock = Mock(); lock.acquire.return_value = False
        with patch.object(preview, 'PREVIEW_LOCK', lock):
            with self.assertRaisesRegex(ValueError, '변환 중'):
                with preview._preview_slot(): pass
        lock.acquire.assert_called_once_with(timeout=15)
        lock.release.assert_not_called()
