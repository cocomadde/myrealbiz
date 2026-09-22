#!/usr/bin/env python3
"""Build a styled, self-contained HTML reading view from the investment report markdown.

Converting at build time (rather than shipping a markdown parser to the browser)
keeps the published page fast, printable and free of runtime dependencies beyond
KaTeX (math) and Mermaid (the ownership-history flowchart).

Handles the constructs actually used by the report:
  headings, GFM tables with alignment, blockquotes + GitHub alerts,
  nested bullet/ordered lists, fenced code (mermaid + plain), thematic breaks,
  bold/italic/inline-code/links, and $inline$ / $$display$$ math.
"""
import argparse
import html
import re
import pathlib

# ── Raw inline HTML the source document is allowed to emit verbatim ──────────
RAW_HTML_OK = re.compile(r'</?br\s*/?>|<span style="[^"]*">|</span>', re.I)

TOKEN = '\x00RAW{}\x00'


def protect_raw(text, store):
    """Swap allowed raw HTML out for placeholders so escaping won't mangle it."""
    def sub(m):
        store.append(m.group(0))
        return TOKEN.format(len(store) - 1)
    return RAW_HTML_OK.sub(sub, text)


def restore_raw(text, store):
    for i, raw in enumerate(store):
        text = text.replace(TOKEN.format(i), raw)
    return text


def inline(text):
    """Convert inline markdown to HTML, preserving allowed raw tags and math."""
    store = []
    text = protect_raw(text, store)

    # Protect math so escaping/emphasis rules never touch its contents.
    math = []

    def keep_math(m):
        math.append(m.group(0))
        return f'\x01M{len(math) - 1}\x01'

    text = re.sub(r'\$\$.+?\$\$', keep_math, text, flags=re.S)
    text = re.sub(r'(?<!\$)\$(?!\s)[^$\n]+?(?<!\s)\$(?!\$)', keep_math, text)

    # Protect inline code next (its contents are literal).
    codes = []

    def keep_code(m):
        codes.append(html.escape(m.group(1)))
        return f'\x02C{len(codes) - 1}\x02'

    text = re.sub(r'`([^`]+)`', keep_code, text)

    text = html.escape(text, quote=False)

    # Links: [label](url)
    text = re.sub(
        r'\[([^\]]+)\]\(([^)\s]+)\)',
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        text)

    # Emphasis (bold before italic so ** isn't eaten by *).
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)

    for i, c in enumerate(codes):
        text = text.replace(f'\x02C{i}\x02', f'<code>{c}</code>')
    for i, m in enumerate(math):
        text = text.replace(f'\x01M{i}\x01', m)

    return restore_raw(text, store)


def slugify(text, used):
    s = re.sub(r'<[^>]+>', '', text)
    s = re.sub(r'[^\w가-힣ぁ-んァ-ン一-龯 .\-]', '', s).strip()
    s = re.sub(r'[\s.]+', '-', s).lower() or 'section'
    base, n = s, 2
    while s in used:
        s, n = f'{base}-{n}', n + 1
    used.add(s)
    return s


ALERT_STYLES = {
    'NOTE':      ('note', 'ℹ️', '참고'),
    'TIP':       ('tip', '💡', '팁'),
    'IMPORTANT': ('important', '📌', '중요'),
    'WARNING':   ('warning', '⚠️', '경고'),
    'CAUTION':   ('caution', '🚨', '주의'),
}


TOTAL_ROW = re.compile(
    r'합\s*계|총\s*계|종합\s*평점|소\s*계|合計|総計|\bTotal\b', re.I)


def render_table(rows, aligns):
    """rows[0] is the header; aligns holds 'left'|'right'|'center' per column.

    The final row is only styled as a totals row when its leading cell actually
    reads like one (합계 / 総計 / Total / 종합 평점), so ordinary tables whose last
    line is just another data row are not falsely emphasised.
    """
    def cells(cols, tag):
        out = []
        for i, c in enumerate(cols):
            a = aligns[i] if i < len(aligns) else 'left'
            out.append(f'<{tag} class="ta-{a}">{inline(c.strip())}</{tag}>')
        return ''.join(out)

    head = f'<thead><tr>{cells(rows[0], "th")}</tr></thead>'

    body = []
    for idx, r in enumerate(rows[1:], start=1):
        is_last = idx == len(rows) - 1
        lead = re.sub(r'[*`\s]', '', r[0]) if r else ''
        cls = ' class="total-row"' if is_last and TOTAL_ROW.search(lead) else ''
        body.append(f'<tr{cls}>{cells(r, "td")}</tr>')

    return (f'<div class="table-wrap"><table>{head}'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def split_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    # Split on | that is not escaped.
    return re.split(r'(?<!\\)\|', line)


def parse_align(sep_cells):
    aligns = []
    for c in sep_cells:
        c = c.strip()
        if c.startswith(':') and c.endswith(':'):
            aligns.append('center')
        elif c.endswith(':'):
            aligns.append('right')
        else:
            aligns.append('left')
    return aligns


def is_sep_row(line):
    return bool(re.fullmatch(r'\|?[\s:|-]+\|?', line.strip())) and '-' in line


def convert(md):
    lines = md.split('\n')
    out, toc, used = [], [], set()
    i, n = 0, len(lines)
    list_stack = []  # list of (indent, tag)

    def close_lists(to_indent=-1):
        while list_stack and list_stack[-1][0] > to_indent:
            out.append(f'</{list_stack.pop()[1]}>')

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # ── Fenced code ──────────────────────────────────────────────
        if stripped.startswith('```'):
            close_lists()
            lang = stripped[3:].strip().lower()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            body = html.escape('\n'.join(buf))
            if lang == 'mermaid':
                out.append(f'<div class="diagram"><pre class="mermaid">{body}</pre></div>')
            else:
                out.append(f'<pre class="codeblock"><code>{body}</code></pre>')
            continue

        # ── Blank ────────────────────────────────────────────────────
        if not stripped:
            close_lists()
            i += 1
            continue

        # ── Horizontal rule ──────────────────────────────────────────
        if re.fullmatch(r'-{3,}', stripped):
            close_lists()
            out.append('<hr>')
            i += 1
            continue

        # ── Heading ──────────────────────────────────────────────────
        m = re.match(r'(#{1,6})\s+(.*)', stripped)
        if m:
            close_lists()
            level = len(m.group(1))
            content = inline(m.group(2))
            sid = slugify(m.group(2), used)
            if level <= 3:
                toc.append((level, sid, re.sub(r'<[^>]+>', '', content)))
            anchor = (f'<a class="anchor" href="#{sid}" aria-label="link">#</a>')
            out.append(f'<h{level} id="{sid}">{content}{anchor}</h{level}>')
            i += 1
            continue

        # ── Table ────────────────────────────────────────────────────
        if stripped.startswith('|') and i + 1 < n and is_sep_row(lines[i + 1]):
            close_lists()
            header = split_row(lines[i])
            aligns = parse_align(split_row(lines[i + 1]))
            rows = [header]
            i += 2
            while i < n and lines[i].strip().startswith('|'):
                rows.append(split_row(lines[i]))
                i += 1
            out.append(render_table(rows, aligns))
            continue

        # ── Blockquote (incl. GitHub alerts) ─────────────────────────
        if stripped.startswith('>'):
            close_lists()
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1

            kind, icon, label = 'note', '', ''
            if buf and re.match(r'\s*\[!(\w+)\]', buf[0]):
                key = re.match(r'\s*\[!(\w+)\]', buf[0]).group(1).upper()
                if key in ALERT_STYLES:
                    kind, icon, label = ALERT_STYLES[key]
                    buf = buf[1:]

            inner = convert_fragment('\n'.join(buf))
            head = (f'<div class="alert-head">{icon} {label}</div>'
                    if icon else '')
            out.append(f'<div class="alert alert-{kind}">{head}{inner}</div>')
            continue

        # ── Lists ────────────────────────────────────────────────────
        indent = len(line) - len(line.lstrip())
        ul = re.match(r'[-*+]\s+(.*)', stripped)
        ol = re.match(r'(\d+)[.)]\s+(.*)', stripped)
        if ul or ol:
            tag = 'ul' if ul else 'ol'
            content = ul.group(1) if ul else ol.group(2)

            while list_stack and list_stack[-1][0] > indent:
                out.append(f'</{list_stack.pop()[1]}>')
            if not list_stack or list_stack[-1][0] < indent:
                list_stack.append((indent, tag))
                out.append(f'<{tag}>')
            elif list_stack[-1][1] != tag:
                out.append(f'</{list_stack.pop()[1]}>')
                list_stack.append((indent, tag))
                out.append(f'<{tag}>')

            out.append(f'<li>{inline(content)}</li>')
            i += 1
            continue

        # ── Paragraph ────────────────────────────────────────────────
        close_lists()
        buf = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(('#', '>', '|', '```'))
                    or re.fullmatch(r'-{3,}', nxt)
                    or re.match(r'[-*+]\s+', nxt) or re.match(r'\d+[.)]\s+', nxt)):
                break
            buf.append(nxt)
            i += 1
        out.append(f'<p>{inline(" ".join(buf))}</p>')

    close_lists()
    return '\n'.join(out), toc


def convert_fragment(md):
    """Convert nested markdown (used inside blockquotes) without collecting TOC."""
    body, _ = convert(md)
    return body


def build_toc(toc):
    items = []
    for level, sid, text in toc:
        if level == 1:
            items.append(f'<a class="toc-h1" href="#{sid}" data-target="{sid}">{text}</a>')
        elif level == 3:
            items.append(f'<a class="toc-h3" href="#{sid}" data-target="{sid}">{text}</a>')
    return '\n'.join(items)


TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800;900&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<style>
:root {{
  --bg: #f8fafc; --surface: #fff; --ink: #1e293b; --muted: #64748b;
  --line: #e2e8f0; --brand: #0369a1; --brand-soft: #e0f2fe;
  --accent: #b45309; --ok: #047857; --bad: #be123c;
  --sidebar: 300px;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 90px; }}
body {{
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: 'Pretendard', 'Noto Sans JP', -apple-system, system-ui, sans-serif;
  font-size: 15px; line-height: 1.75; -webkit-font-smoothing: antialiased;
}}

/* ── Top bar ───────────────────────────────────────────── */
.topbar {{
  position: sticky; top: 0; z-index: 60; background: #0f172a; color: #fff;
  border-bottom: 1px solid #1e293b;
}}
.topbar-inner {{
  max-width: 1500px; margin: 0 auto; padding: 0 20px; height: 60px;
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
}}
.brand {{ display: flex; align-items: center; gap: 10px; min-width: 0; }}
.brand-badge {{
  width: 34px; height: 34px; border-radius: 9px; flex: none;
  background: linear-gradient(135deg, #0ea5e9, #4f46e5);
  display: grid; place-items: center; font-size: 17px;
}}
.brand-text {{ min-width: 0; }}
.brand-title {{
  font-weight: 800; font-size: 15px; letter-spacing: -.01em;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.brand-sub {{ font-size: 11px; color: #94a3b8; }}
.tools {{ display: flex; align-items: center; gap: 8px; flex: none; }}
.btn {{
  display: inline-flex; align-items: center; gap: 6px; cursor: pointer;
  padding: 7px 12px; border-radius: 9px; font-size: 12px; font-weight: 600;
  background: #1e293b; color: #e2e8f0; border: 1px solid #334155;
  text-decoration: none; transition: .15s; white-space: nowrap;
}}
.btn:hover {{ background: #334155; color: #fff; }}
.btn-primary {{
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #1c1917; border-color: transparent;
}}
.btn-primary:hover {{ filter: brightness(1.08); color: #1c1917; }}
.progress {{
  position: absolute; left: 0; bottom: -1px; height: 3px; width: 0;
  background: linear-gradient(90deg, #38bdf8, #f59e0b);
}}

/* ── Layout ────────────────────────────────────────────── */
.shell {{
  max-width: 1500px; margin: 0 auto; padding: 0 20px;
  display: grid; grid-template-columns: var(--sidebar) minmax(0, 1fr); gap: 36px;
  align-items: start;
}}
.sidebar {{
  position: sticky; top: 60px; max-height: calc(100vh - 60px);
  overflow-y: auto; padding: 24px 8px 40px 0;
}}
.toc-label {{
  font-size: 11px; font-weight: 800; letter-spacing: .09em; color: var(--muted);
  text-transform: uppercase; padding: 0 10px; margin-bottom: 10px;
}}
.sidebar a {{
  display: block; text-decoration: none; color: var(--muted);
  border-left: 2px solid transparent; transition: .12s;
}}
.toc-h1 {{
  font-size: 13px; font-weight: 700; color: #334155;
  padding: 7px 10px; margin-top: 4px;
}}
.toc-h3 {{ font-size: 12px; padding: 4px 10px 4px 22px; }}
.sidebar a:hover {{ color: var(--brand); background: #f1f5f9; }}
.sidebar a.active {{
  color: var(--brand); border-left-color: var(--brand);
  background: var(--brand-soft); font-weight: 700;
}}

/* ── Article ───────────────────────────────────────────── */
.article {{
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 18px; padding: 44px 52px 64px; margin: 24px 0 56px;
  box-shadow: 0 1px 3px rgba(15,23,42,.05);
}}
.article > h1:first-of-type {{ margin-top: 0; }}
h1, h2, h3, h4, h5 {{
  line-height: 1.35; letter-spacing: -.015em; scroll-margin-top: 90px;
  position: relative;
}}
h1 {{
  font-size: 27px; font-weight: 900; margin: 60px 0 20px;
  padding-bottom: 14px; border-bottom: 3px solid #0f172a;
}}
h2 {{ font-size: 21px; font-weight: 800; margin: 44px 0 16px; }}
h3 {{
  font-size: 17px; font-weight: 800; margin: 38px 0 14px;
  padding-left: 13px; border-left: 4px solid var(--brand);
}}
h4 {{ font-size: 15px; font-weight: 700; margin: 28px 0 10px; color: #334155; }}
h5 {{ font-size: 14px; font-weight: 700; margin: 22px 0 8px; color: var(--muted); }}
.anchor {{
  position: absolute; left: -22px; color: var(--line); text-decoration: none;
  opacity: 0; transition: .12s; font-weight: 400;
}}
h1:hover .anchor, h2:hover .anchor, h3:hover .anchor {{ opacity: 1; }}
.anchor:hover {{ color: var(--brand); }}

p {{ margin: 12px 0; }}
strong {{ font-weight: 700; color: #0f172a; }}
a {{ color: var(--brand); text-decoration-thickness: 1px; text-underline-offset: 2px; }}
hr {{ border: 0; border-top: 1px solid var(--line); margin: 40px 0; }}
ul, ol {{ margin: 12px 0; padding-left: 24px; }}
li {{ margin: 6px 0; }}
li > ul, li > ol {{ margin: 6px 0; }}
code {{
  background: #f1f5f9; border: 1px solid var(--line); border-radius: 5px;
  padding: 1.5px 5px; font-size: .87em;
  font-family: 'SF Mono', ui-monospace, Menlo, Consolas, monospace;
}}
.codeblock {{
  background: #0f172a; color: #e2e8f0; border-radius: 12px;
  padding: 20px 22px; overflow-x: auto; font-size: 13px; line-height: 1.7;
}}
.codeblock code {{ background: none; border: 0; padding: 0; color: inherit; }}

/* ── Tables ────────────────────────────────────────────── */
.table-wrap {{
  overflow-x: auto; margin: 18px 0; border: 1px solid var(--line);
  border-radius: 12px; background: #fff;
}}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ padding: 10px 13px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{
  background: #f1f5f9; font-weight: 700; color: #334155; white-space: nowrap;
  position: sticky; top: 0; border-bottom: 2px solid #cbd5e1;
}}
tbody tr:last-child td {{ border-bottom: 0; }}
tbody tr:hover {{ background: #f8fafc; }}
tbody tr.total-row {{ background: #fffbeb; }}
tbody tr.total-row td {{
  font-weight: 700; color: #92400e; border-top: 2px solid #fcd34d;
}}
.ta-left {{ text-align: left; }}
.ta-right {{ text-align: right; font-variant-numeric: tabular-nums; }}
.ta-center {{ text-align: center; }}

/* ── Alerts ────────────────────────────────────────────── */
.alert {{
  margin: 20px 0; padding: 16px 20px; border-radius: 12px;
  border: 1px solid var(--line); border-left-width: 4px; background: #f8fafc;
}}
.alert p:first-child {{ margin-top: 0; }}
.alert p:last-child, .alert ul:last-child {{ margin-bottom: 0; }}
.alert-head {{ font-weight: 800; font-size: 13px; margin-bottom: 6px; }}
.alert-caution {{ border-left-color: var(--bad); background: #fff1f2; }}
.alert-caution .alert-head {{ color: var(--bad); }}
.alert-warning {{ border-left-color: #d97706; background: #fffbeb; }}
.alert-warning .alert-head {{ color: #b45309; }}
.alert-important {{ border-left-color: #7c3aed; background: #f5f3ff; }}
.alert-important .alert-head {{ color: #6d28d9; }}
.alert-tip {{ border-left-color: var(--ok); background: #ecfdf5; }}
.alert-tip .alert-head {{ color: var(--ok); }}
.alert-note {{ border-left-color: var(--brand); background: #f0f9ff; }}
.alert-note .alert-head {{ color: var(--brand); }}

/* ── Diagram ───────────────────────────────────────────── */
.diagram {{
  margin: 24px 0; padding: 24px; background: #f8fafc;
  border: 1px solid var(--line); border-radius: 14px; overflow-x: auto;
}}
.diagram pre {{ margin: 0; text-align: center; }}

/* ── Math ──────────────────────────────────────────────── */
.katex-display {{
  margin: 18px 0; padding: 16px; background: #f8fafc;
  border: 1px solid var(--line); border-radius: 10px; overflow-x: auto;
}}

/* ── Floating back-to-top ──────────────────────────────── */
#toTop {{
  position: fixed; right: 26px; bottom: 26px; width: 44px; height: 44px;
  border-radius: 50%; border: 1px solid var(--line); background: #fff;
  color: var(--brand); font-size: 18px; cursor: pointer; display: none;
  box-shadow: 0 6px 20px rgba(15,23,42,.14); z-index: 50;
}}
#toTop.show {{ display: block; }}

/* ── Language Toggle ────────────────────────────────────── */
.lang-toggle {{
  display: inline-flex; align-items: center; background: #0b1329;
  padding: 3px; border-radius: 10px; border: 1px solid #334155; margin-right: 4px;
}}
.lang-btn {{
  display: inline-block; padding: 5px 10px; border-radius: 7px; font-size: 11px;
  font-weight: 700; text-decoration: none; color: #94a3b8; transition: .15s;
}}
.lang-btn:hover {{ color: #fff; }}
.lang-btn.active {{
  background: #0284c7; color: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.3);
}}

/* ── Responsive ────────────────────────────────────────── */
@media (max-width: 1080px) {{
  .shell {{ grid-template-columns: 1fr; gap: 0; }}
  .sidebar {{
    position: static; max-height: none; padding: 18px 0 0;
    border-bottom: 1px solid var(--line);
  }}
  .sidebar-scroll {{ max-height: 210px; overflow-y: auto; }}
  .toc-h3 {{ display: none; }}
  .article {{ padding: 28px 20px 48px; border-radius: 14px; }}
  h1 {{ font-size: 22px; }}
  .brand-sub {{ display: none; }}
}}

/* ── Print ─────────────────────────────────────────────── */
@media print {{
  .topbar, .sidebar, #toTop {{ display: none !important; }}
  body {{ background: #fff; font-size: 10.5pt; }}
  .shell {{ display: block; padding: 0; max-width: none; }}
  .article {{ border: 0; border-radius: 0; padding: 0; margin: 0; box-shadow: none; }}
  h1 {{ page-break-before: always; font-size: 17pt; }}
  .article > h1:first-of-type {{ page-break-before: avoid; }}
  h2, h3, h4 {{ page-break-after: avoid; }}
  .table-wrap, .diagram, .alert {{ page-break-inside: avoid; }}
  th {{ position: static; }}
  a {{ color: inherit; text-decoration: none; }}
}}
</style>
</head>
<body>

<header class="topbar">
  <div class="topbar-inner">
    <div class="brand">
      <div class="brand-badge">📑</div>
      <div class="brand-text">
        <div class="brand-title">{brand_title}</div>
        <div class="brand-sub">{brand_sub}</div>
      </div>
    </div>
    <div class="tools">
      <div class="lang-toggle">
        <a class="lang-btn {ko_active}" href="{ko_href}" onclick="localStorage.setItem('myrealbiz_lang', 'ko')">한국어</a>
        <a class="lang-btn {ja_active}" href="{ja_href}" onclick="localStorage.setItem('myrealbiz_lang', 'ja')">日本語</a>
      </div>
      <a class="btn" href="../">{portfolio_text}</a>
      <a class="btn btn-primary" href="./">{simulator_text}</a>
      <button class="btn" onclick="window.print()">{print_text}</button>
    </div>
  </div>
  <div class="progress" id="progress"></div>
</header>

<div class="shell">
  <nav class="sidebar">
    <div class="toc-label">{toc_title}</div>
    <div class="sidebar-scroll">
{toc}
    </div>
  </nav>
  <article class="article">
{body}
  </article>
</div>

<button id="toTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" aria-label="Top">↑</button>

<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{
    startOnLoad: true,
    theme: 'base',
    themeVariables: {{
      primaryColor: '#e0f2fe', primaryTextColor: '#0f172a',
      primaryBorderColor: '#0369a1', lineColor: '#64748b',
      fontFamily: 'Pretendard, sans-serif', fontSize: '13px'
    }}
  }});
</script>
<script>
// Language preference auto-redirect
(function() {{
  const PAGE_LANG = '{html_lang}';
  const savedLang = localStorage.getItem('myrealbiz_lang');
  if (savedLang && savedLang !== PAGE_LANG) {{
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('stay')) {{
      const target = PAGE_LANG === 'ko' ? './report_ja.html' : './report.html';
      window.location.replace(target);
    }}
  }}
}})();

// Math
document.addEventListener('DOMContentLoaded', function () {{
  if (window.renderMathInElement) {{
    renderMathInElement(document.querySelector('.article'), {{
      delimiters: [
        {{ left: '$$', right: '$$', display: true }},
        {{ left: '$',  right: '$',  display: false }}
      ],
      throwOnError: false
    }});
  }}
}});

// Reading progress + back-to-top
const bar = document.getElementById('progress');
const toTop = document.getElementById('toTop');
function onScroll() {{
  const h = document.documentElement;
  const max = h.scrollHeight - h.clientHeight;
  bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
  toTop.classList.toggle('show', h.scrollTop > 700);
}}
window.addEventListener('scroll', onScroll, {{ passive: true }});
onScroll();

// TOC scroll-spy
const links = [...document.querySelectorAll('.sidebar a')];
const byId = new Map(links.map(a => [a.dataset.target, a]));
const targets = links
  .map(a => document.getElementById(a.dataset.target))
  .filter(Boolean);

const spy = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    if (!e.isIntersecting) return;
    links.forEach(a => a.classList.remove('active'));
    const a = byId.get(e.target.id);
    if (a) {{
      a.classList.add('active');
      const box = a.closest('.sidebar-scroll');
      if (box && window.innerWidth > 1080) {{
        const top = a.offsetTop - box.clientHeight / 2;
        box.scrollTo({{ top, behavior: 'smooth' }});
      }}
    }}
  }});
}}, {{ rootMargin: '-80px 0px -70% 0px', threshold: 0 }});
targets.forEach(t => spy.observe(t));
</script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        description='Convert a property investment report markdown file into a '
        'styled, self-contained HTML reading page.')
    parser.add_argument('source', help='input markdown file')
    parser.add_argument('dest', help='output html file')
    parser.add_argument(
        '--title',
        default=None,
        help='report title shown in the sticky header and browser tab')
    parser.add_argument(
        '--subtitle',
        default=None,
        help='one-line property summary shown under the title')
    parser.add_argument(
        '--lang',
        choices=['ko', 'ja'],
        default='ko',
        help='page language (ko or ja)')
    args = parser.parse_args()

    src = pathlib.Path(args.source)
    dst = pathlib.Path(args.dest)

    md = src.read_text(encoding='utf-8')
    body, toc = convert(md)

    if args.lang == 'ja':
        title = args.title or '精密投資分析レポート'
        subtitle = args.subtitle or 'MyRealBiz 不動産投資分析アーカイブ'
        portfolio_text = '🏠 ポートフォリオ'
        simulator_text = '🧮 融資シミュレーター'
        print_text = '🖨️ 印刷 / PDF'
        toc_title = '目次 (Contents)'
        ko_active = ''
        ja_active = 'active'
        ko_href = './report.html'
        ja_href = './report_ja.html'
    else:
        title = args.title or '종합분석 보고서'
        subtitle = args.subtitle or 'MyRealBiz 부동산 투자 분석 아카이브'
        portfolio_text = '🏠 포트폴리오'
        simulator_text = '🧮 융자 시뮬레이터'
        print_text = '🖨️ 인쇄 / PDF'
        toc_title = '목차 (Contents)'
        ko_active = 'active'
        ja_active = ''
        ko_href = './report.html'
        ja_href = './report_ja.html'

    dst.write_text(
        TEMPLATE.format(
            html_lang=args.lang,
            title=f'{title} | MyRealBiz',
            brand_title=title,
            brand_sub=subtitle,
            ko_active=ko_active,
            ja_active=ja_active,
            ko_href=ko_href,
            ja_href=ja_href,
            portfolio_text=portfolio_text,
            simulator_text=simulator_text,
            print_text=print_text,
            toc_title=toc_title,
            toc=build_toc(toc),
            body=body),
        encoding='utf-8')

    print(f'built [{args.lang}] {dst}')
    print(f'  source : {len(md.splitlines())} md lines')
    print(f'  output : {len(dst.read_text(encoding="utf-8").splitlines())} html lines')
    print(f'  toc    : {len(toc)} entries')


if __name__ == '__main__':
    main()

