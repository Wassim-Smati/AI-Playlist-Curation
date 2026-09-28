import re
import os
import subprocess
import markdown

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md_path = os.path.join(BASE_DIR, "docs", "technical_cheatsheet", "technical_cheatsheet_system_design.md")
html_path = os.path.join(BASE_DIR, "docs", "technical_cheatsheet", "technical_cheatsheet_system_design.html")
pdf_path = os.path.join(BASE_DIR, "docs", "technical_cheatsheet", "technical_cheatsheet_system_design.pdf")

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# Replace mermaid code blocks with <div class="mermaid">...</div>
def replace_mermaid(match):
    code = match.group(1).strip()
    return f'<div class="mermaid">\n{code}\n</div>'

md_content_processed = re.sub(r'```mermaid\s*\n(.*?)\n```', replace_mermaid, md_content, flags=re.DOTALL)

# Convert Markdown to HTML
html_body = markdown.markdown(md_content_processed, extensions=['extra', 'codehilite', 'tables', 'fenced_code'])

# Build complete HTML with Mermaid.js & GitHub PDF styling
html_full = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Technical Cheatsheet & System Design - AI Playlist Curation</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: 'basis' }}
        }});
    </script>
    <style>
        @page {{
            size: A4;
            margin: 15mm 15mm 15mm 15mm;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #24292e;
            line-height: 1.6;
            font-size: 14px;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            font-size: 24px;
            border-bottom: 2px solid #e1e4e8;
            padding-bottom: 8px;
            color: #0366d6;
            margin-top: 0;
        }}
        h2 {{
            font-size: 18px;
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 6px;
            margin-top: 24px;
            color: #1b1f23;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 15px;
            margin-top: 18px;
            color: #24292e;
            page-break-after: avoid;
        }}
        blockquote {{
            background: #f6f8fa;
            border-left: 4px solid #0366d6;
            color: #586069;
            margin: 12px 0;
            padding: 8px 16px;
            border-radius: 0 4px 4px 0;
        }}
        code {{
            background-color: #f3f3f3;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 85%;
        }}
        pre {{
            background-color: #f6f8fa;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 12px;
            line-height: 1.45;
            border: 1px solid #e1e4e8;
            page-break-inside: avoid;
        }}
        pre code {{
            background: transparent;
            padding: 0;
        }}
        .mermaid {{
            background: #ffffff;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            text-align: center;
            page-break-inside: avoid;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        table th, table td {{
            border: 1px solid #dfe2e5;
            padding: 8px 12px;
        }}
        table th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        ul, ol {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 4px;
        }}
        hr {{
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_full)

print(f"HTML saved to {html_path}")

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=6000",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    f"file:///{html_path.replace('\\', '/')}"
]

print("Running Edge PDF generation...")
result = subprocess.run(cmd, capture_output=True, text=True)
print("Exit code:", result.returncode)
if os.path.exists(pdf_path):
    print(f"SUCCESS: PDF generated ({os.path.getsize(pdf_path)} bytes) at {pdf_path}")
else:
    print("FAILED to generate PDF")
