import importlib.util
from pathlib import Path
root=Path(__file__).resolve().parent
skill=Path('C:/Users/Admin/.codex/plugins/cache/openai-primary-runtime/documents/26.909.12148/skills/documents/render_docx.py')
spec=importlib.util.spec_from_file_location('render_docx',skill)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Windows bundle has no LibreOffice. Reuse the PDF rendered by native Word;
# retain the packaged render_docx rasterization step and its page naming.
m.convert_to_pdf=lambda *args,**kwargs:(str(root/'word.pdf'),'Native Microsoft Word read-only PDF export')
m.rasterize(str(root/'제주시_기획서_디자인최종.docx'),str(root/'render'),120,False,False)
print('Rendered PNGs')

