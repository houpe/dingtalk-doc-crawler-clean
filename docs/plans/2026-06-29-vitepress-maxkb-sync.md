# VitePress MaxKB Sync Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a trial-ready sync path that sends VitePress operation manuals from `site/docs` to MaxKB.

**Architecture:** Add a local Markdown source scanner and adapt the existing sync service so `full_sync()` reads VitePress manuals instead of BookStack by default. Keep MaxKB client behavior unchanged and preserve old BookStack-specific code where it does not block the new path.

**Tech Stack:** Python 3, FastAPI, pytest-style standard-library tests, existing MaxKB API client.

---

### Task 1: VitePress Source Scanner

**Files:**
- Create: `md_sys/sync-service/vitepress_source.py`
- Test: `md_sys/sync-service/test_vitepress_sync.py`

**Step 1:** Write tests for scanning manuals, skipping `index.md`, and deriving document names from folder paths.

**Step 2:** Run the scanner tests and confirm they fail because the scanner does not exist.

**Step 3:** Implement the scanner.

**Step 4:** Run the scanner tests and confirm they pass.

### Task 2: Sync Service Uses Manual Source

**Files:**
- Modify: `md_sys/sync-service/sync.py`
- Modify: `md_sys/sync-service/config.py`
- Test: `md_sys/sync-service/test_vitepress_sync.py`

**Step 1:** Write tests for create, update, skip, and delete behavior using fake MaxKB and fake local manuals.

**Step 2:** Run the tests and confirm they fail because `SyncService` still expects BookStack.

**Step 3:** Adapt `SyncService.full_sync()` to use the VitePress scanner by default.

**Step 4:** Run the tests and confirm they pass.

### Task 3: Trial Runner and Status

**Files:**
- Modify: `md_sys/sync-service/main.py`
- Test: `md_sys/sync-service/test_vitepress_sync.py`

**Step 1:** Add a dry-run method that reports local manual count without writing to MaxKB.

**Step 2:** Expose the source and tracked count in status.

**Step 3:** Run tests, syntax checks, and a real local dry run against `site/docs`.
