#!/usr/bin/env python3
"""Build a single-file static wiki HTML from /wiki markdown files."""

import markdown
import os
import re
import json
from pathlib import Path

WIKI_DIR = Path("/home/fangqihang2/claude-task/my_game_coding/wiki")
OUTPUT_FILE = Path("/home/fangqihang2/claude-task/my_game_coding/wiki.html")

# Navigation structure: (display_name, rel_path, children)
# rel_path is the .md file path relative to wiki dir (without .md extension)
NAV_STRUCTURE = [
    ("首页", "首页", []),
    ("世界观", None, [
        ("概述", "世界观/概述"),
        ("轮盘系统详解", "世界观/轮盘系统详解"),
    ]),
    ("人物档案", None, [
        ("人物总览", "人物档案/人物总览"),
        ("叶默", "人物档案/叶默"),
    ]),
    ("地图与地点", None, [
        ("地点总览", "地图与地点/地点总览"),
        ("天都山庄", "地图与地点/天都山庄"),
    ]),
    ("怪物图鉴", None, [
        ("怪物总览", "怪物图鉴/怪物总览"),
        ("丧尸等级详解", "怪物图鉴/丧尸等级详解"),
    ]),
    ("情节概要", None, [
        ("情节总览", "情节概要/情节总览"),
    ]),
    ("组织与势力", None, [
        ("势力总览", "组织与势力/势力总览"),
    ]),
    ("道具与能力", None, [
        ("道具总览", "道具与能力/道具总览"),
    ]),
    ("附录", None, [
        ("附录总览", "附录/附录总览"),
        ("游戏化设计参考", "附录/游戏化设计参考"),
    ]),
]

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def resolve_link(link, current_file_rel):
    """Resolve a relative markdown link to an absolute wiki page ID."""
    current_dir = os.path.dirname(current_file_rel)
    # Remove .md extension if present
    link = link.strip()
    # Handle external links (http/https)
    if link.startswith("http://") or link.startswith("https://"):
        return None
    # Resolve relative path
    if link.startswith("../"):
        # Go up one level
        parent = os.path.dirname(current_dir)
        resolved = os.path.normpath(os.path.join(parent, link)).replace("\\", "/")
    elif link.startswith("./"):
        resolved = os.path.normpath(os.path.join(current_dir, link)).replace("\\", "/")
    else:
        resolved = os.path.normpath(os.path.join(current_dir, link)).replace("\\", "/")
    # Remove .md extension
    if resolved.endswith(".md"):
        resolved = resolved[:-3]
    return resolved

def convert_md_to_html(md_text, file_rel):
    """Convert markdown to HTML, handling internal wiki links."""
    # Pre-process: convert internal wiki links to special format
    def replace_link(match):
        text = match.group(1)
        link = match.group(2)
        resolved = resolve_link(link, file_rel)
        if resolved:
            return f'[{text}](wiki://{resolved})'
        else:
            return match.group(0)  # Keep external links as-is

    # Match [text](link.md) patterns
    md_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, md_text)

    # Convert to HTML using markdown library
    extensions = ['tables', 'fenced_code', 'codehilite', 'toc']
    html = markdown.markdown(md_text, extensions=extensions)

    # Post-process: convert wiki:// links to onclick handlers
    def replace_wiki_link(match):
        page_id = match.group(1)
        return f'onclick="navigateTo(\'{page_id}\')" class="wiki-link"'

    html = re.sub(r'href="wiki://([^"]+)"', replace_wiki_link, html)

    return html

def generate_nav_html():
    """Generate the sidebar navigation HTML."""
    parts = []
    for name, path, children in NAV_STRUCTURE:
        if children:
            # Category with children
            cat_id = name
            parts.append(f'<div class="nav-category">')
            parts.append(f'  <div class="nav-cat-title" onclick="toggleCategory(this)">')
            parts.append(f'    <span class="nav-arrow">▾</span> {name}')
            parts.append(f'  </div>')
            parts.append(f'  <div class="nav-cat-children">')
            for child_name, child_path in children:
                parts.append(f'    <a class="nav-item" onclick="navigateTo(\'{child_path}\')" data-page="{child_path}">{child_name}</a>')
            parts.append(f'  </div>')
            parts.append(f'</div>')
        else:
            # Top-level page
            parts.append(f'<a class="nav-item nav-top-item" onclick="navigateTo(\'{path}\')" data-page="{path}">{name}</a>')
    return "\n".join(parts)

def main():
    # Read and convert all markdown files
    pages = {}
    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        rel_path = str(md_file.relative_to(WIKI_DIR)).replace("\\", "/")
        page_id = rel_path[:-3]  # Remove .md extension
        md_content = read_file(md_file)
        html_content = convert_md_to_html(md_content, rel_path)
        pages[page_id] = html_content
        print(f"Converted: {page_id}")

    # Generate navigation
    nav_html = generate_nav_html()

    # Build pages JSON
    pages_json = json.dumps(pages, ensure_ascii=False, indent=2)

    # Read the template
    template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>轮盘世界 · 维基百科</title>
<style>
/* ===== CSS Reset & Variables ===== */
:root {
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
  --table-stripe: #1c1f2b;
  --table-header: #212433;
  --code-bg: #161822;
  --code-text: #c9d1d9;
  --link: #58a6ff;
  --warning: #d29922;
  --danger: #f85149;
  --success: #3fb950;
  --scrollbar-track: #161822;
  --scrollbar-thumb: #2a2d3a;
  --shadow: 0 2px 8px rgba(0,0,0,0.3);
}

/* ===== Layout ===== */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  display: flex;
  height: 100vh;
  overflow: hidden;
  line-height: 1.6;
}

/* ===== Sidebar ===== */
.sidebar {
  width: 260px;
  min-width: 260px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10;
}

.sidebar-header {
  padding: 20px 16px 12px;
  border-bottom: 1px solid var(--border);
}

.sidebar-header h2 {
  font-size: 18px;
  color: var(--text-bright);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar-header h2 .icon { font-size: 20px; }

.search-box {
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 8px 12px 8px 32px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: var(--accent);
}

.search-box .search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 14px;
  pointer-events: none;
}

.search-results {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 0 0 6px 6px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: var(--shadow);
}

.search-results.active { display: block; }

.search-result-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  border-bottom: 1px solid var(--border);
  transition: background 0.15s;
}

.search-result-item:hover { background: var(--accent-dim); }
.search-result-item:last-child { border-bottom: none; }
.search-result-item .match-title { color: var(--text-bright); font-weight: 500; }
.search-result-item .match-context { color: var(--text-muted); font-size: 12px; margin-top: 2px; }
.search-no-results { padding: 12px; color: var(--text-muted); font-size: 13px; text-align: center; }

/* ===== Navigation ===== */
.nav-tree {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.nav-tree::-webkit-scrollbar { width: 4px; }
.nav-tree::-webkit-scrollbar-track { background: var(--scrollbar-track); }
.nav-tree::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 2px; }

.nav-category { margin-bottom: 2px; }

.nav-cat-title {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  user-select: none;
  transition: color 0.15s;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-cat-title:hover { color: var(--text-bright); }

.nav-arrow {
  font-size: 10px;
  transition: transform 0.2s;
  display: inline-block;
}

.nav-category.collapsed .nav-arrow { transform: rotate(-90deg); }
.nav-category.collapsed .nav-cat-children { display: none; }

.nav-cat-children { padding: 2px 0 4px; }

.nav-item {
  display: block;
  padding: 6px 16px 6px 28px;
  font-size: 13px;
  color: var(--text);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.15s;
  border-left: 2px solid transparent;
}

.nav-item:hover {
  color: var(--text-bright);
  background: var(--accent-dim);
  border-left-color: var(--accent);
}

.nav-item.active {
  color: var(--accent);
  background: var(--accent-dim);
  border-left-color: var(--accent);
  font-weight: 500;
}

.nav-top-item {
  padding: 8px 16px;
  font-weight: 500;
  font-size: 14px;
  border-left: 2px solid transparent;
}

/* ===== Main Content ===== */
.main {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--bg-content);
  scroll-behavior: smooth;
}

.main::-webkit-scrollbar { width: 6px; }
.main::-webkit-scrollbar-track { background: transparent; }
.main::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 3px; }

.content-container {
  max-width: 860px;
  margin: 0 auto;
  padding: 32px 40px 80px;
}

.page-content { display: none; }
.page-content.active { display: block; }

/* ===== Top Bar ===== */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 20px;
  background: var(--bg-sidebar);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 5;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--text);
  font-size: 22px;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}

.breadcrumb {
  font-size: 13px;
  color: var(--text-muted);
}

.breadcrumb span { color: var(--text); }

.theme-toggle {
  background: none;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
}

.theme-toggle:hover { background: var(--accent-dim); border-color: var(--accent); }

/* ===== Typography ===== */
.page-content h1 {
  font-size: 28px;
  color: var(--heading);
  margin-bottom: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.page-content h2 {
  font-size: 22px;
  color: var(--heading);
  margin: 32px 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.page-content h3 {
  font-size: 18px;
  color: var(--text-bright);
  margin: 24px 0 12px;
}

.page-content h4 {
  font-size: 15px;
  color: var(--text-bright);
  margin: 20px 0 8px;
}

.page-content h5 {
  font-size: 14px;
  color: var(--text-muted);
  margin: 16px 0 8px;
}

.page-content p {
  margin: 12px 0;
  color: var(--text);
}

.page-content ul, .page-content ol {
  margin: 8px 0 8px 24px;
  color: var(--text);
}

.page-content li { margin: 4px 0; }

.page-content strong { color: var(--text-bright); font-weight: 600; }

.page-content blockquote {
  border-left: 3px solid var(--accent);
  padding: 8px 16px;
  margin: 16px 0;
  background: var(--accent-dim);
  border-radius: 0 6px 6px 0;
  color: var(--text-muted);
  font-style: italic;
}

.page-content blockquote p { margin: 4px 0; color: inherit; }

/* ===== Wiki Links ===== */
.wiki-link {
  color: var(--link);
  cursor: pointer;
  text-decoration: underline;
  text-decoration-style: dotted;
  text-underline-offset: 3px;
  transition: color 0.15s;
}

.wiki-link:hover { color: var(--text-bright); text-decoration-style: solid; }

/* ===== Tables ===== */
.page-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 13px;
  overflow-x: auto;
  display: block;
}

.page-content thead { background: var(--table-header); }

.page-content th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--text-bright);
  border: 1px solid var(--border);
  white-space: nowrap;
}

.page-content td {
  padding: 8px 12px;
  border: 1px solid var(--border);
  color: var(--text);
}

.page-content tbody tr:nth-child(even) { background: var(--table-stripe); }
.page-content tbody tr:hover { background: var(--accent-dim); }

/* ===== Code Blocks ===== */
.page-content code {
  background: var(--code-bg);
  color: var(--code-text);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
  font-family: "SF Mono", "Fira Code", "Cascadia Code", monospace;
}

.page-content pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
}

.page-content pre code {
  background: none;
  padding: 0;
  border-radius: 0;
}

/* ===== Horizontal Rule ===== */
.page-content hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 24px 0;
}

/* ===== Ascii-art diagrams ===== */
.page-content pre code:not([class]) {
  color: var(--text-muted);
}

/* ===== Scrollbar ===== */
.main::-webkit-scrollbar { width: 6px; }
.main::-webkit-scrollbar-track { background: transparent; }
.main::-webkit-scrollbar-thumb { background: #2a2d3a; border-radius: 3px; }

/* ===== Mobile Overlay ===== */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 8;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -280px;
    top: 0;
    bottom: 0;
    transition: left 0.3s;
    width: 280px;
    min-width: 280px;
  }
  .sidebar.open { left: 0; }
  .sidebar-overlay.active { display: block; }
  .menu-toggle { display: block; }
  .content-container { padding: 20px 16px 60px; }
  .page-content h1 { font-size: 22px; }
  .page-content h2 { font-size: 18px; }
  .page-content table { font-size: 12px; }
  .page-content th, .page-content td { padding: 6px 8px; }
}

/* ===== Print ===== */
@media print {
  .sidebar, .top-bar { display: none; }
  .main { overflow: visible; }
  .content-container { max-width: none; padding: 0; }
  .page-content { display: block !important; margin-bottom: 40px; }
}
</style>
</head>
<body>

<!-- Sidebar -->
<div class="sidebar-overlay" onclick="closeSidebar()"></div>
<aside class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <h2><span class="icon">🎰</span> 轮盘世界 Wiki</h2>
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input type="text" id="searchInput" placeholder="搜索..." oninput="onSearch(this.value)" onfocus="onSearch(this.value)" autocomplete="off">
      <div class="search-results" id="searchResults"></div>
    </div>
  </div>
  <nav class="nav-tree" id="navTree">
    NAV_PLACEHOLDER
  </nav>
</aside>

<!-- Main Content -->
<div class="main" id="mainContent">
  <div class="top-bar">
    <div class="top-bar-left">
      <button class="menu-toggle" onclick="toggleSidebar()" title="菜单">☰</button>
      <span class="breadcrumb" id="breadcrumb"><span>首页</span></span>
    </div>
    <button class="theme-toggle" onclick="toggleTheme()" title="切换亮色/暗色主题">☀️ 亮色</button>
  </div>
  <div class="content-container" id="contentContainer">
    CONTENT_PLACEHOLDER
  </div>
</div>

<script>
// ===== Page Data =====
const PAGES = PAGES_PLACEHOLDER;

// ===== Current State =====
let currentPage = "首页";
let isDark = true;

// ===== Navigation =====
function navigateTo(pageId) {
  if (!PAGES[pageId]) {
    console.warn("Page not found:", pageId);
    return;
  }

  // Update current page
  currentPage = pageId;

  // Update active states
  document.querySelectorAll(".page-content").forEach(el => el.classList.remove("active"));
  const pageEl = document.getElementById("page-" + pageId.replace(/[\\/]/g, "-"));
  if (pageEl) pageEl.classList.add("active");

  // Update nav active
  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  const navItem = document.querySelector(`.nav-item[data-page="${pageId}"]`);
  if (navItem) {
    navItem.classList.add("active");
    // Expand parent category
    const category = navItem.closest(".nav-category");
    if (category) category.classList.remove("collapsed");
  }

  // Update breadcrumb
  updateBreadcrumb(pageId);

  // Scroll to top
  document.getElementById("mainContent").scrollTop = 0;

  // Close sidebar on mobile
  closeSidebar();

  // Save to hash
  window.location.hash = encodeURIComponent(pageId);
}

function updateBreadcrumb(pageId) {
  const parts = pageId.split("/");
  const breadcrumb = document.getElementById("breadcrumb");
  breadcrumb.innerHTML = parts.map((p, i) => {
    const label = i === parts.length - 1 ? p : p;
    return i < parts.length - 1
      ? `<span>${label}</span> / `
      : `<span style="color:var(--accent)">${label}</span>`;
  }).join("");
}

// ===== Sidebar Toggle =====
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.querySelector(".sidebar-overlay");
  sidebar.classList.toggle("open");
  overlay.classList.toggle("active");
}

function closeSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.querySelector(".sidebar-overlay");
  sidebar.classList.remove("open");
  overlay.classList.remove("active");
}

// ===== Category Toggle =====
function toggleCategory(el) {
  el.parentElement.classList.toggle("collapsed");
}

// ===== Search =====
let searchTimeout;
function onSearch(query) {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => performSearch(query), 150);
}

function performSearch(query) {
  const resultsEl = document.getElementById("searchResults");
  const q = query.trim().toLowerCase();

  if (!q) {
    resultsEl.classList.remove("active");
    resultsEl.innerHTML = "";
    return;
  }

  const results = [];
  for (const [pageId, html] of Object.entries(PAGES)) {
    // Strip HTML tags for text search
    const text = html.replace(/<[^>]+>/g, " ");
    const lower = text.toLowerCase();
    const idx = lower.indexOf(q);
    if (idx >= 0) {
      // Get page title from first h1
      const titleMatch = html.match(/<h1[^>]*>(.*?)<\\/h1>/);
      const title = titleMatch ? titleMatch[1].replace(/<[^>]+>/g, "") : pageId;

      // Get context around match
      let start = Math.max(0, idx - 30);
      let end = Math.min(text.length, idx + q.length + 80);
      let context = text.substring(start, end).trim();
      if (start > 0) context = "…" + context;
      if (end < text.length) context = context + "…";

      // Highlight match in context
      const ctxLower = context.toLowerCase();
      const matchIdx = ctxLower.indexOf(q);
      if (matchIdx >= 0) {
        context = context.substring(0, matchIdx)
          + "<mark>" + context.substring(matchIdx, matchIdx + q.length) + "</mark>"
          + context.substring(matchIdx + q.length);
      }

      results.push({ pageId, title, context, idx });
    }
  }

  // Sort by match position (earlier = more relevant)
  results.sort((a, b) => a.idx - b.idx);

  if (results.length > 0) {
    resultsEl.innerHTML = results.slice(0, 20).map(r =>
      `<div class="search-result-item" onclick="navigateTo('${r.pageId}');document.getElementById('searchResults').classList.remove('active');document.getElementById('searchInput').value='';">
        <div class="match-title">${r.title}</div>
        <div class="match-context">${r.context}</div>
      </div>`
    ).join("");
    resultsEl.classList.add("active");
  } else {
    resultsEl.innerHTML = '<div class="search-no-results">未找到匹配结果</div>';
    resultsEl.classList.add("active");
  }
}

// Close search results on click outside
document.addEventListener("click", function(e) {
  const searchResults = document.getElementById("searchResults");
  const searchInput = document.getElementById("searchInput");
  if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
    searchResults.classList.remove("active");
  }
});

// ===== Theme Toggle =====
function toggleTheme() {
  isDark = !isDark;
  const btn = document.querySelector(".theme-toggle");
  if (isDark) {
    document.documentElement.style.setProperty("--bg", "#0f1117");
    document.documentElement.style.setProperty("--bg-sidebar", "#161822");
    document.documentElement.style.setProperty("--bg-content", "#1a1d28");
    document.documentElement.style.setProperty("--bg-card", "#212433");
    document.documentElement.style.setProperty("--border", "#2a2d3a");
    document.documentElement.style.setProperty("--text", "#c9d1d9");
    document.documentElement.style.setProperty("--text-muted", "#8b949e");
    document.documentElement.style.setProperty("--text-bright", "#e6edf3");
    document.documentElement.style.setProperty("--heading", "#f0883e");
    document.documentElement.style.setProperty("--table-stripe", "#1c1f2b");
    document.documentElement.style.setProperty("--table-header", "#212433");
    document.documentElement.style.setProperty("--code-bg", "#161822");
    document.documentElement.style.setProperty("--code-text", "#c9d1d9");
    document.documentElement.style.setProperty("--scrollbar-track", "#161822");
    document.documentElement.style.setProperty("--scrollbar-thumb", "#2a2d3a");
    document.documentElement.style.setProperty("--shadow", "0 2px 8px rgba(0,0,0,0.3)");
    btn.innerHTML = "☀️ 亮色";
  } else {
    document.documentElement.style.setProperty("--bg", "#f6f8fa");
    document.documentElement.style.setProperty("--bg-sidebar", "#ffffff");
    document.documentElement.style.setProperty("--bg-content", "#ffffff");
    document.documentElement.style.setProperty("--bg-card", "#ffffff");
    document.documentElement.style.setProperty("--border", "#d0d7de");
    document.documentElement.style.setProperty("--text", "#24292f");
    document.documentElement.style.setProperty("--text-muted", "#656d76");
    document.documentElement.style.setProperty("--text-bright", "#1f2328");
    document.documentElement.style.setProperty("--heading", "#d46407");
    document.documentElement.style.setProperty("--table-stripe", "#f6f8fa");
    document.documentElement.style.setProperty("--table-header", "#f6f8fa");
    document.documentElement.style.setProperty("--code-bg", "#f6f8fa");
    document.documentElement.style.setProperty("--code-text", "#24292f");
    document.documentElement.style.setProperty("--accent-dim", "#ddf4ff");
    document.documentElement.style.setProperty("--link", "#0969da");
    document.documentElement.style.setProperty("--scrollbar-track", "#f6f8fa");
    document.documentElement.style.setProperty("--scrollbar-thumb", "#d0d7de");
    document.documentElement.style.setProperty("--shadow", "0 1px 3px rgba(0,0,0,0.1)");
    btn.innerHTML = "🌙 暗色";
  }
}

// ===== Keyboard Shortcuts =====
document.addEventListener("keydown", function(e) {
  // Ctrl+K or / to focus search
  if ((e.ctrlKey && e.key === "k") || (e.key === "/" && document.activeElement === document.body)) {
    e.preventDefault();
    document.getElementById("searchInput").focus();
  }
  // Escape to close search
  if (e.key === "Escape") {
    document.getElementById("searchResults").classList.remove("active");
    document.getElementById("searchInput").blur();
  }
});

// ===== Initialize =====
function init() {
  // Check hash
  const hash = window.location.hash.slice(1);
  const pageFromHash = hash ? decodeURIComponent(hash) : null;

  // Navigate to hash or home
  if (pageFromHash && PAGES[pageFromHash]) {
    navigateTo(pageFromHash);
  } else {
    navigateTo("首页");
  }

  // Open search with Ctrl+K hint in placeholder
  document.getElementById("searchInput").placeholder = "搜索... (Ctrl+K)";
}

// Start
init();
</script>

</body>
</html>'''

    # Replace placeholders
    nav_html_clean = nav_html.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    template = template.replace("NAV_PLACEHOLDER", nav_html)
    template = template.replace("PAGES_PLACEHOLDER", pages_json)

    # Build content divs
    content_divs = []
    for page_id, html in pages.items():
        safe_id = page_id.replace("/", "-").replace("\\", "-")
        active_class = ' active' if page_id == '首页' else ''
        content_divs.append(f'<div class="page-content{active_class}" id="page-{safe_id}">\n{html}\n</div>')

    template = template.replace("CONTENT_PLACEHOLDER", "\n".join(content_divs))

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(template)

    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"\n✅ wiki.html generated: {OUTPUT_FILE} ({file_size:,} bytes)")
    print(f"   Pages: {len(pages)}")
    print(f"   Open in browser to view.")

if __name__ == "__main__":
    main()
