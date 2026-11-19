"""guide-hs/ch0.html~ch9.html과 style.css를 합쳐 index.html을 만든다.

사용법: python3 guide-hs/build_index.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = [
    (0, "준비"),
    (1, "문제 소개"),
    (2, "핵심 통찰과 전체 구조"),
    (3, "추상 사전최적화"),
    (4, "충돌 판정"),
    (5, "탐욕 삽입"),
    (6, "롤링 호라이즌"),
    (7, "SA와 이웃"),
    (8, "결과와 교훈"),
    (9, "용어 풀이"),
]
PATTERNS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<pattern id="pat-crane" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" style="fill:var(--crane-soft)"/><line x1="0" y1="0" x2="0" y2="6" style="stroke:var(--crane)" stroke-width="1.4"/></pattern>
<pattern id="pat-hull" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" style="fill:var(--hull-soft)"/><circle cx="3" cy="3" r="0.9" style="fill:var(--hull)"/></pattern>
</defs></svg>"""
SCRIPT = """<script>
(function () {
  var chapters = [].slice.call(document.querySelectorAll('.chapter'));
  var links = [].slice.call(document.querySelectorAll('.chapters a'));
  function show(scroll) {
    var id = (location.hash || '').slice(1);
    if (!/^ch\\d+$/.test(id) || !document.getElementById(id)) { id = 'ch0'; }
    chapters.forEach(function (c) { c.hidden = c.id !== id; });
    links.forEach(function (a) { a.classList.toggle('now', a.getAttribute('data-ch') === id); });
    if (scroll) { window.scrollTo(0, 0); }
  }
  window.addEventListener('hashchange', function () { show(true); });
  show(false);
})();
</script>"""


def label(n, title):
    return title if n == 9 else f"{n} {title}"


def main():
    css = (HERE / "style.css").read_text()
    nav = "\n".join(f'    <a href="#ch{n}" data-ch="ch{n}">{label(n, t)}</a>' for n, t in CHAPTERS)
    body = "\n".join((HERE / f"ch{n}.html").read_text() for n, _ in CHAPTERS)
    (HERE / "index.html").write_text(f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OGC 2026 1등 해법 해설 (입문판)</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
{css}
</style>
</head>
<body>
{PATTERNS}
<div class="wrap">
  <div class="kicker">OGC 2026 · tishii24 해법 해설 · 입문판</div>
  <nav class="chapters" aria-label="전체 구성">
{nav}
  </nav>
{body}
</div>
{SCRIPT}
</body>
</html>
""")


if __name__ == "__main__":
    main()
