"""guide/ch1.html~ch8.html을 이어 붙여 print.html과 ogc2026-guide.pdf를 만든다.

사용법: python3 guide/build_print.py
"""
import datetime
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HTML = HERE / "print.html"
PDF = HERE / "ogc2026-guide.pdf"

TITLES = [
    "문제 소개",
    "핵심 통찰과 전체 구조",
    "추상 사전최적화",
    "충돌 판정",
    "탐욕 삽입",
    "롤링 호라이즌",
    "SA와 이웃",
    "결과와 교훈",
]
LONG_PRE_LINES = 26
LONG_TABLE_ROWS = 15

PRINT_CSS = """
:root { color-scheme: light; --surface: #ffffff; padding: 0 !important; }
@page {
  size: A4; margin: 16mm 16mm 17mm;
  @bottom-right { content: counter(page); font: 8pt "Apple SD Gothic Neo", sans-serif; color: #56657a; }
}
@page cover { @bottom-right { content: none; } }
CHAPTER_PAGES
:root {
  --font-body: "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", sans-serif;
  --font-mono: Menlo, "SF Mono", ui-monospace, "Apple SD Gothic Neo", monospace;
}
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { background: #fff; }
body { padding: 0; font-size: 10pt; line-height: 1.55; orphans: 2; widows: 2; }
.wrap { display: block; max-width: none; }
.chapter { display: block; break-before: page; }
section { display: block; }
section > * + *, .chapter > * + * { margin-top: 7pt; }
.chapter > * + section, .chapter > section + * { margin-top: 12pt; }
p, ul.plain, ol.plain, .note, details { max-width: none; }
ul.plain, ol.plain { display: block; padding-left: 18pt; }
ul.plain li + li, ol.plain li + li { margin-top: 2pt; }

header { margin-bottom: 4pt; }
.kicker { font-size: 8pt; }
h1 { font-size: 19pt; line-height: 1.3; }
h2 { font-size: 13.5pt; line-height: 1.35; margin-top: 4pt; }
h3 { font-size: 11pt; margin-top: 4pt; }
.lead { font-size: 11pt; }
h1, h2, h3, .part, summary { break-after: avoid; page-break-after: avoid; }
.part { font-size: 8.5pt; margin-top: 18pt !important; padding-top: 6pt; break-after: avoid; }
.part + section { margin-top: 8pt !important; }

a[href^="#ch"] { color: inherit; text-decoration: none; }

.scroll { overflow: visible !important; max-height: none !important; }
figure { padding: 5px; border-radius: 4px; break-inside: avoid; }
figure svg { min-width: 0 !important; width: 100%; }
figure svg[viewBox="0 0 560 175"] { width: 70%; margin: 0 auto; }
figcaption { font-size: 8.5pt; margin-top: 4pt; line-height: 1.5; padding: 0 3px; }

table { min-width: 0 !important; font-size: 8.8pt; break-inside: avoid; }
table.long { break-inside: auto; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { font-size: 8.3pt; }
th, td { padding: 3pt 5pt; overflow-wrap: break-word; }
td:first-child { white-space: normal; }
td code, th code { overflow-wrap: break-word; }

pre {
  overflow: visible !important; white-space: pre-wrap; overflow-wrap: anywhere;
  font-size: 7.6pt; line-height: 1.5; padding: 6pt 8pt; tab-size: 4;
  break-inside: avoid;
}
pre.long { break-inside: auto; }
pre .ln { display: block; min-height: 1lh; }
code { padding: 0 3px; }
.note { padding: 7pt 10pt; break-inside: avoid; }
.formula { font-size: 10.5pt; padding: 6pt; break-inside: avoid; }
.src { font-size: 8.5pt; }
.obj { gap: 6pt; }
.obj > div { padding: 7pt 9pt; break-inside: avoid; }
.obj .f { font-size: 9pt; }
.obj p { font-size: 9pt; }

details { padding: 5pt 0; break-inside: avoid; }
summary { cursor: default; list-style: none; }
summary::-webkit-details-marker { display: none; }
summary::before { content: "Q. "; color: var(--steel); }
details p { margin-top: 3pt; }

.cover { page: cover; height: 255mm; display: flex; flex-direction: column; justify-content: center; }
.cover .kicker { font-size: 9pt; }
.cover h1 { font-size: 30pt; margin-top: 8pt; }
.cover .sub { font-size: 11pt; margin-top: 14pt; color: var(--muted); }
.cover .date { font-size: 10pt; margin-top: 40pt; color: var(--muted); }
.toc { page: cover; break-before: page; }
.toc h2 { font-size: 16pt; margin-bottom: 14pt; }
.toc ol { list-style: none; padding: 0; margin: 0; font-size: 11.5pt; }
.toc li { display: flex; gap: 8pt; padding: 7pt 0; border-bottom: 1px solid var(--line); }
.toc .n { width: 2.2em; color: var(--steel); font-weight: 500; }
.toc .t { flex: 1; }
.toc .p { font-variant-numeric: tabular-nums; color: var(--muted); }
"""


def pre_html(m):
    lines = m.group(1).removeprefix("\n").removesuffix("\n").split("\n")
    cls = ' class="long"' if len(lines) > LONG_PRE_LINES else ""
    spans = []
    for l in lines:
        hang = len(l) - len(l.lstrip(" ")) + 4
        spans.append(f'<span class="ln" style="padding-left:{hang}ch;text-indent:-{hang}ch">{l}</span>')
    return f"<pre{cls}>" + "".join(spans) + "</pre>"


def chapter_html(n):
    s = (HERE / f"ch{n}.html").read_text()
    s = re.sub(r'\s*<div class="pager">.*?</div>', "", s, flags=re.S)
    s = s.replace("<details>", "<details open>")
    s = re.sub(r"<pre>(.*?)</pre>", pre_html, s, flags=re.S)
    s = re.sub(
        r"<table([^>]*)>(.*?)</table>",
        lambda m: "<table" + m.group(1) + (' class="long"' if m.group(2).count("<tr") > LONG_TABLE_ROWS else "")
        + ">" + m.group(2) + "</table>",
        s,
        flags=re.S,
    )
    return s


def build_html(pages):
    index = (HERE / "index.html").read_text()
    start = index.index("/* layout:")
    base_css = index[start:index.index("</style>", start)]
    chapter_pages = "\n".join(
        f'@page ch{n} {{ @bottom-left {{ content: "{n}장 {t}"; font: 8pt "Apple SD Gothic Neo", sans-serif; color: #56657a; }} }}\n'
        f"#ch{n} {{ page: ch{n}; }}"
        for n, t in enumerate(TITLES, 1)
    )
    css = base_css + PRINT_CSS.replace("CHAPTER_PAGES", chapter_pages)
    toc = "\n".join(
        f'<li><span class="n">{n}장</span><span class="t">{t}</span><span class="p">{pages[n - 1] if pages else ""}</span></li>'
        for n, t in enumerate(TITLES, 1)
    )
    today = datetime.date.today().isoformat()
    body = "\n".join(chapter_html(n) for n in range(1, 9))
    return f"""<!doctype html>
<html lang="ko" data-theme="light">
<head>
<meta charset="utf-8">
<title>OGC 2026 1등 해법 해설</title>
<style>
{css}
</style>
</head>
<body>
<div class="wrap">
<section class="cover">
  <div class="kicker">OGC 2026 · 해설 자료</div>
  <h1>OGC 2026 1등 해법 해설</h1>
  <p class="sub">대상 저장소 github.com/tishii24/ogc2026 · 저자 tishii24의 1등 해법을 장별로 풀어 설명합니다.</p>
  <p class="date">{today} 작성</p>
</section>
<section class="toc">
  <h2>차례</h2>
  <ol>
{toc}
  </ol>
</section>
{body}
</div>
</body>
</html>
"""


def render():
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
             f"--user-data-dir={profile}", f"--print-to-pdf={PDF}", HTML.as_uri()],
            check=True, capture_output=True,
        )


def chapter_start_pages():
    text = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], check=True, capture_output=True, text=True).stdout
    pages = text.split("\f")
    found = []
    for n in range(1, 9):
        found.append(next(i + 1 for i, p in enumerate(pages) if i >= 2 and re.search(rf"^\s*{n} / 8\s*$", p, re.M)))
    return found


def main():
    HTML.write_text(build_html(None))
    render()
    pages = chapter_start_pages()
    HTML.write_text(build_html(pages))
    render()
    assert chapter_start_pages() == pages
    print("chapter start pages:", pages)


if __name__ == "__main__":
    main()
