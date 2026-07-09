# VitePress Manuals to MaxKB Sync Design

## Goal

Sync the operation manual Markdown files under `site/docs` into a MaxKB knowledge base.

## Scope

- Include Markdown manuals under `site/docs`.
- Exclude `index.md`, `.vitepress`, `public`, `node_modules`, images, generated files, and site configuration.
- Keep each source Markdown file as one MaxKB document.
- Use the source folder path and file name as the MaxKB document name.
- Track only documents created by this sync source, so deleted source files only remove their matching synced documents.

## Data Flow

1. Scan `site/docs` recursively.
2. Build a stable source id from the Markdown path relative to `site/docs`.
3. Read the Markdown content.
4. Split content into MaxKB paragraphs using the existing paragraph splitter.
5. Create, update, skip, or delete MaxKB documents based on the saved state file.

## Trial Criteria

- A dry run can scan the real local manuals without calling MaxKB.
- Tests prove `index.md` and non-manual paths are skipped.
- Tests prove creates, updates, deletes, and skips are scoped to VitePress state entries.
