"""
Generate PDF from geometry_mastery_report.md using:
- Python markdown library for proper MD→HTML conversion
- Base64 image embedding for all local images
- Chrome headless for PDF rendering with CJK support
"""
import os, re, base64, subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_FILE = os.path.join(BASE_DIR, 'geometry_mastery_report.md')
PDF_FILE = os.path.join(BASE_DIR, 'geometry_mastery_report.pdf')
HTML_FILE = os.path.join(BASE_DIR, '.temp_report.html')

# 1. Read markdown and embed images as base64
with open(MD_FILE, 'r', encoding='utf-8') as f:
    md = f.read()

def img_to_b64(path):
    full = os.path.join(BASE_DIR, path)
    if not os.path.exists(full):
        print(f"  WARN: not found {full}")
        return path
    with open(full, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lower()
    mime = {'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg'}.get(ext[1:],'image/png')
    return f'data:{mime};base64,{b64}'

md = re.sub(
    r'!\[([^\]]*)\]\(model_assets/([^)]+)\)',
    lambda m: f'![{m.group(1)}]({img_to_b64(f"model_assets/{m.group(2)}")})',
    md
)

# 2. Convert MD to HTML using python markdown library
from markdown import markdown

html_body = markdown(md, extensions=['tables', 'fenced_code'])

# 3. Wrap in complete HTML with print-optimized CSS
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 1.8cm 2cm; }}
  body {{
    font-family: "PingFang SC", "Heiti SC", "STHeiti", "Hiragino Sans GB", sans-serif;
    font-size: 10.5pt; line-height: 1.75; color: #1e293b;
  }}
  h1 {{ font-size: 19pt; border-bottom: 3px solid #2563eb; padding-bottom: 6px;
        margin-top: 0; color: #1e3a5f; }}
  h2 {{ font-size: 14pt; border-bottom: 2px solid #93c5fd; padding-bottom: 3px;
        margin-top: 24px; color: #1e40af; page-break-after: avoid; }}
  h3 {{ font-size: 12pt; margin-top: 18px; color: #334155; page-break-after: avoid; }}
  h4 {{ font-size: 10.5pt; margin-top: 14px; color: #475569; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9pt; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 4px 7px; text-align: left; }}
  th {{ background: #f1f5f9; font-weight: bold; color: #1e3a5f; }}
  tr:nth-child(even) td {{ background: #fafbfc; }}
  code {{ background: #f1f5f9; padding: 1px 4px; border-radius: 3px;
          font-family: Menlo, Monaco, monospace; font-size: 8.5pt; }}
  pre {{ background: #f8fafc; border: 1px solid #e2e8f0; border-left: 3px solid #2563eb;
         padding: 8px 12px; font-size: 8.5pt; line-height: 1.5; white-space: pre-wrap; }}
  blockquote {{ border-left: 3px solid #f59e0b; background: #fffbeb;
                margin: 10px 0; padding: 6px 12px; color: #92400e; }}
  img {{ max-width: 100%; height: auto; display: block; margin: 12px auto; }}
  hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 18px 0; }}
  strong {{ color: #1e3a5f; }}
  p {{ margin: 5px 0; }}
</style></head>
<body>{html_body}</body>
</html>'''

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

# 4. Find Chrome
chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
if not os.path.exists(chrome):
    result = subprocess.run(['mdfind', 'kMDItemCFBundleIdentifier == "com.google.Chrome"'],
                          capture_output=True, text=True)
    chrome = os.path.join(result.stdout.strip().split('\n')[0],
                         'Contents/MacOS/Google Chrome') if result.stdout.strip() else None
if not chrome or not os.path.exists(chrome):
    print("ERROR: Chrome not found"); exit(1)

# 5. Print to PDF
print("Generating PDF with Chrome headless...")
r = subprocess.run([
    chrome, '--headless', '--disable-gpu', '--no-sandbox',
    '--no-pdf-header-footer',
    f'--print-to-pdf={PDF_FILE}',
    f'file://{HTML_FILE}'
], capture_output=True, text=True, timeout=30)

os.remove(HTML_FILE)

if r.returncode != 0:
    print(f"ERROR: {r.stderr}"); exit(1)

sz = os.path.getsize(PDF_FILE)
print(f"Done: {PDF_FILE} ({sz/1024:.0f} KB, PDF-valid: {open(PDF_FILE,'rb').read(4)==b'%PDF'})")
