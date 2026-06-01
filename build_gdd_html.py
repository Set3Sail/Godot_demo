#!/usr/bin/env python3
"""Convert GDD markdown to a single self-contained HTML page."""

import markdown
import re
from pathlib import Path

GDD_FILE = Path("/home/fangqihang2/claude-task/my_game_coding/docs/superpowers/specs/2026-05-31-轮盘世界卡牌游戏-gdd.md")
OUTPUT_FILE = Path("/home/fangqihang2/claude-task/my_game_coding/docs/superpowers/specs/2026-05-31-轮盘世界卡牌游戏-gdd.html")

def convert_md_to_html(md_text):
    """Convert markdown to HTML with extensions."""
    extensions = ['tables', 'fenced_code', 'codehilite', 'toc']
    html = markdown.markdown(md_text, extensions=extensions)

    # Add IDs to headings for TOC linking
    def add_id_to_heading(match):
        level = len(match.group(1))
        text = match.group(2).strip()
        # Generate ID from text
        slug = re.sub(r'[^\w一-鿿]+', '-', text).strip('-').lower()
        return f'<h{level} id="{slug}">{text}</h{level}>'

    html = re.sub(r'<h(\d)>(.*?)</h\d>', add_id_to_heading, html)

    return html

def extract_toc(html):
    """Extract headings and generate table of contents."""
    headings = re.findall(r'<h(\d)\s+id="([^"]+)"[^>]*>(.*?)</h\d>', html)
    if not headings:
        return ""

    toc_parts = ['<ul class="toc-list">']
    current_level = 1
    stack = [1]

    for level_str, slug, text in headings:
        level = int(level_str)
        if level == 1:
            continue  # Skip document title

        adjusted_level = level - 1  # Normalize so h2 = level 1 in TOC

        while adjusted_level > stack[-1]:
            toc_parts.append('<ul>')
            stack.append(adjusted_level)
        while adjusted_level < stack[-1]:
            toc_parts.append('</ul></li>')
            stack.pop()

        toc_parts.append(f'<li><a href="#{slug}" class="toc-link">{text}</a>')

        # Close will be handled at end or next iteration
        stack[-1] = adjusted_level

    # Close remaining
    while len(stack) > 1:
        toc_parts.append('</ul></li>')
        stack.pop()
    toc_parts.append('</li></ul>')

    return '\n'.join(toc_parts)

def main():
    md_content = Path(GDD_FILE).read_text(encoding="utf-8")
    html_content = convert_md_to_html(md_content)
    toc_html = extract_toc(html_content)

    template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>轮盘世界 · 卡牌Roguelike 游戏设计文档 (GDD)</title>
<style>
/* ===== Variables (Dark Theme) ===== */
:root {{
  --bg: #0f1117;
  --bg-sidebar: #161822;
  --bg-content: #1a1d28;
  --bg-card: #212433;
  --border: #2a2d3a;
  --text: #c9d1d9;
  --text-muted: #8b949e;
  --text-bright: #e6edf3;
  --accent: #58a6ff;
  --accent-dim: #1f6feb44;
  --heading: #f0883e;
  --h2-color: #f0883e;
  --h3-color: #e6edf3;
  --table-stripe: #1c1f2b;
  --table-header: #212433;
  --code-bg: #161822;
  --code-text: #c9d1d9;
  --link: #58a6ff;
  --scrollbar-track: #161822;
  --scrollbar-thumb: #2a2d3a;
  --shadow: 0 2px 8px rgba(0,0,0,0.3);
}}

/* ===== Reset ===== */
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  display: flex;
  height: 100vh;
  overflow: hidden;
  line-height: 1.7;
}}

/* ===== Sidebar TOC ===== */
.sidebar {{
  width: 280px;
  min-width: 280px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10;
}}

.sidebar-header {{
  padding: 20px 16px 12px;
  border-bottom: 1px solid var(--border);
}}

.sidebar-header h2 {{
  font-size: 16px;
  color: var(--text-bright);
  margin-bottom: 4px;
}}

.sidebar-header .subtitle {{
  font-size: 12px;
  color: var(--text-muted);
}}

.toc-scroll {{
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}}

.toc-scroll::-webkit-scrollbar {{ width: 4px; }}
.toc-scroll::-webkit-scrollbar-track {{ background: var(--scrollbar-track); }}
.toc-scroll::-webkit-scrollbar-thumb {{ background: var(--scrollbar-thumb); border-radius: 2px; }}

.toc-list {{
  list-style: none;
  padding: 0;
  margin: 0;
}}

.toc-list ul {{
  list-style: none;
  padding-left: 16px;
}}

.toc-list li {{
  margin: 0;
}}

.toc-link {{
  display: block;
  padding: 5px 16px;
  font-size: 13px;
  color: var(--text-muted);
  text-decoration: none;
  transition: all 0.15s;
  border-left: 2px solid transparent;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

.toc-link:hover {{
  color: var(--text-bright);
  background: var(--accent-dim);
  border-left-color: var(--accent);
}}

.toc-link.active {{
  color: var(--accent);
  background: var(--accent-dim);
  border-left-color: var(--accent);
}}

/* Top-level TOC items */
.toc-list > li > .toc-link {{
  font-weight: 600;
  color: var(--text);
  font-size: 14px;
  padding: 7px 16px;
}}

/* ===== Main Content ===== */
.main {{
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--bg-content);
  scroll-behavior: smooth;
}}

.main::-webkit-scrollbar {{ width: 6px; }}
.main::-webkit-scrollbar-track {{ background: transparent; }}
.main::-webkit-scrollbar-thumb {{ background: var(--scrollbar-thumb); border-radius: 3px; }}

/* ===== Top Bar ===== */
.top-bar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 20px;
  background: var(--bg-sidebar);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 5;
}}

.top-bar-title {{
  font-size: 14px;
  color: var(--text-bright);
  font-weight: 600;
}}

.top-bar-actions {{
  display: flex;
  gap: 8px;
  align-items: center;
}}

.btn {{
  background: none;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
}}

.btn:hover {{ background: var(--accent-dim); border-color: var(--accent); }}

/* ===== Content Container ===== */
.content-container {{
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 40px 80px;
}}

/* ===== Typography ===== */
.content-container h1 {{
  font-size: 28px;
  color: var(--heading);
  margin-bottom: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}}

.content-container h2 {{
  font-size: 22px;
  color: var(--heading);
  margin: 36px 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}}

.content-container h3 {{
  font-size: 18px;
  color: var(--h3-color);
  margin: 28px 0 12px;
}}

.content-container h4 {{
  font-size: 15px;
  color: var(--text-bright);
  margin: 20px 0 8px;
}}

.content-container h5 {{
  font-size: 14px;
  color: var(--text-muted);
  margin: 16px 0 8px;
}}

.content-container p {{
  margin: 10px 0;
  color: var(--text);
}}

.content-container ul, .content-container ol {{
  margin: 8px 0 8px 24px;
  color: var(--text);
}}

.content-container li {{ margin: 3px 0; }}

.content-container strong {{ color: var(--text-bright); font-weight: 600; }}

.content-container blockquote {{
  border-left: 3px solid var(--accent);
  padding: 10px 16px;
  margin: 16px 0;
  background: var(--accent-dim);
  border-radius: 0 6px 6px 0;
  color: var(--text-muted);
}}

.content-container blockquote p {{ margin: 4px 0; color: inherit; }}

.content-container a {{ color: var(--link); text-decoration: underline; text-underline-offset: 3px; }}

/* ===== Tables ===== */
.content-container table {{
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  font-size: 13px;
}}

.content-container thead {{ background: var(--table-header); }}

.content-container th {{
  padding: 9px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--text-bright);
  border: 1px solid var(--border);
  white-space: nowrap;
}}

.content-container td {{
  padding: 7px 10px;
  border: 1px solid var(--border);
  color: var(--text);
}}

.content-container tbody tr:nth-child(even) {{ background: var(--table-stripe); }}
.content-container tbody tr:hover {{ background: var(--accent-dim); }}

/* ===== Code ===== */
.content-container code {{
  background: var(--code-bg);
  color: var(--code-text);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
  font-family: "SF Mono", "Fira Code", "Cascadia Code", monospace;
}}

.content-container pre {{
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 14px;
  margin: 14px 0;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
}}

.content-container pre code {{
  background: none;
  padding: 0;
  border-radius: 0;
  font-size: 12px;
}}

.content-container hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 24px 0;
}}

/* ===== Back to Top ===== */
.back-to-top {{
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 50%;
  color: var(--text-muted);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 50;
  opacity: 0.7;
}}

.back-to-top:hover {{
  opacity: 1;
  border-color: var(--accent);
  color: var(--text-bright);
}}

/* ===== Responsive ===== */
@media (max-width: 768px) {{
  .sidebar {{ display: none; }}
  .content-container {{ padding: 16px 16px 60px; }}
  .content-container h1 {{ font-size: 22px; }}
  .content-container h2 {{ font-size: 18px; }}
  .content-container table {{ font-size: 11px; }}
  .content-container th, .content-container td {{ padding: 5px 6px; }}
}}

/* ===== Print ===== */
@media print {{
  .sidebar, .top-bar, .back-to-top {{ display: none; }}
  .main {{ overflow: visible; }}
  .content-container {{ max-width: none; padding: 0; }}
}}
</style>
</head>
<body>

<!-- Sidebar -->
<aside class="sidebar">
  <div class="sidebar-header">
    <h2>📋 GDD 目录</h2>
    <p class="subtitle">轮盘世界 · 卡牌Roguelike</p>
  </div>
  <nav class="toc-scroll">
    {toc_html}
  </nav>
</aside>

<!-- Main Content -->
<div class="main" id="mainContent">
  <div class="top-bar">
    <span class="top-bar-title">🎰 轮盘世界 · 游戏设计文档 (GDD) v1.0</span>
    <div class="top-bar-actions">
      <button class="btn" onclick="scrollToTop()" title="回到顶部">⬆ 顶部</button>
    </div>
  </div>
  <div class="content-container">
    {html_content}
  </div>
</div>

<!-- Back to Top -->
<button class="back-to-top" onclick="scrollToTop()" title="回到顶部">⬆</button>

<script>
// Scroll to top
function scrollToTop() {{
  document.getElementById("mainContent").scrollTo({{ top: 0, behavior: "smooth" }});
}}

// TOC active state on scroll
const mainEl = document.getElementById("mainContent");
const tocLinks = document.querySelectorAll(".toc-link");
const headings = [];

// Collect all heading positions
document.querySelectorAll(".content-container h2, .content-container h3").forEach(h => {{
  headings.push({{ id: h.id, el: h }});
}});

function updateActiveLink() {{
  const scrollTop = mainEl.scrollTop + 80;
  let activeId = null;

  for (const h of headings) {{
    if (h.el.offsetTop <= scrollTop) {{
      activeId = h.id;
    }}
  }}

  tocLinks.forEach(link => {{
    link.classList.toggle("active", link.getAttribute("href") === "#" + activeId);
  }});
}}

mainEl.addEventListener("scroll", updateActiveLink);

// Smooth scroll for TOC links
tocLinks.forEach(link => {{
  link.addEventListener("click", function(e) {{
    e.preventDefault();
    const targetId = this.getAttribute("href").slice(1);
    const target = document.getElementById(targetId);
    if (target) {{
      mainEl.scrollTo({{ top: target.offsetTop - 60, behavior: "smooth" }});
    }}
  }});
}});
</script>

</body>
</html>'''

    # Write output
    Path(OUTPUT_FILE).write_text(template, encoding="utf-8")
    file_size = Path(OUTPUT_FILE).stat().st_size
    print(f"✅ GDD HTML generated: {OUTPUT_FILE} ({file_size:,} bytes)")

if __name__ == "__main__":
    main()
