# Titles Preview Page Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a standalone HTML preview page for the generated titles/flowcharts/menus Markdown so it can be opened from the built site.

**Architecture:** Extend the site builder with one small preview-page renderer that converts a Markdown source file into a styled standalone HTML page under `site/docs/`. Reuse the existing Markdown stack, add lightweight heading navigation plus Mermaid rendering, and keep the main manual pages unchanged.

**Tech Stack:** Python, Markdown, BeautifulSoup, existing site CSS output

---

### Task 1: Add the failing preview-page test

**Files:**
- Modify: `tests/test_manual_restructure.py`
- Test: `tests/test_manual_restructure.py`

**Step 1: Write the failing test**

Add a test that:
- creates a temporary Markdown file containing `##` and `###` headings, a menu bullet, and a Mermaid fence
- calls the new preview renderer
- asserts the output HTML file exists
- asserts the HTML contains the page title, Mermaid container, and the expected headings

**Step 2: Run test to verify it fails**

Run: `pytest -q tests/test_manual_restructure.py`

Expected: FAIL because the preview renderer function does not exist yet.

### Task 2: Implement the standalone preview renderer

**Files:**
- Modify: `dingtalk_docs_html/site_builder.py`

**Step 1: Add a small renderer**

Implement a helper that:
- reads a Markdown file
- converts it to HTML with fenced-code support
- rewrites Mermaid code fences into `<div class="mermaid">`
- builds a simple heading nav from `h2` and `h3`
- writes a standalone HTML page using the existing `assets/site.css` and a little inline preview-only CSS

**Step 2: Wire it into the build output**

Generate:
- `site/docs/dingtalk-titles-flowcharts-menus.html`

Only do this if:
- `docs/dingtalk-titles-flowcharts-menus.md` exists

### Task 3: Verify output

**Files:**
- Modify: `dingtalk_docs_html/site_builder.py`

**Step 1: Run tests**

Run: `pytest -q`

Expected: PASS

**Step 2: Build the site**

Run: `python3 build_site.py`

Expected: preview HTML file exists under `site/docs/`

**Step 3: Spot-check the preview page**

Confirm:
- headings render correctly
- Mermaid blocks are present
- menu bullet text renders
- page can be opened directly for preview
