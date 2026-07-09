import hashlib
import json
import logging
import re
import threading
import config
from bookstack_client import BookStackClient
from maxkb_client import MaxKBClient
from vitepress_source import SOURCE_PREFIX, VitePressSource

logger = logging.getLogger(__name__)

_lock = threading.Lock()


class SyncService:
    def __init__(self, maxkb_client=None, source=None):
        self.bs = BookStackClient()
        self.mk = maxkb_client or MaxKBClient()
        self.source = source or VitePressSource(config.VITEPRESS_DOCS_DIR)
        self.state: dict = {}
        self._load_state()

    def _load_state(self):
        try:
            with open(config.STATE_FILE, "r", encoding="utf-8") as f:
                self.state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.state = {}

    def _save_state(self):
        with open(config.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _content_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _page_display_name(page: dict) -> str:
        book_name = page.get("_book_name", "")
        chapter_name = page.get("_chapter_name", "")
        parts = []
        if book_name:
            parts.append(book_name)
        if chapter_name:
            parts.append(chapter_name)
        parts.append(page.get("name", ""))
        return " / ".join(parts)

    @staticmethod
    def split_to_paragraphs(markdown: str) -> list[dict]:
        if not markdown or not markdown.strip():
            return [{"content": "(empty)"}]
        blocks = re.split(r"\n{2,}", markdown.strip())
        paragraphs = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            if len(block) > config.PARAGRAPH_MAX_LENGTH:
                sub_blocks = re.split(r"(?<=[。！？\n])", block)
                current = ""
                for sb in sub_blocks:
                    if len(current) + len(sb) > config.PARAGRAPH_MAX_LENGTH and current:
                        paragraphs.append(SyncService._parse_block(current))
                        current = sb
                    else:
                        current += sb
                if current.strip():
                    paragraphs.append(SyncService._parse_block(current))
            else:
                paragraphs.append(SyncService._parse_block(block))
        if not paragraphs:
            paragraphs.append({"content": markdown[:500]})
        return paragraphs

    @staticmethod
    def _parse_block(block: str) -> dict:
        lines = block.strip().split("\n")
        title = ""
        content_lines = lines
        if lines and re.match(r"^#{1,6}\s+", lines[0]):
            title = re.sub(r"^#{1,6}\s+", "", lines[0]).strip()
            content_lines = lines[1:]
        content = "\n".join(content_lines).strip()
        if not content:
            content = title
            title = ""
        return {"content": content, "title": title} if title else {"content": content}

    def dry_run(self) -> dict:
        documents = self.source.list_documents()
        return {
            "source": "vitepress",
            "manuals": len(documents),
            "docs_dir": str(self.source.docs_dir),
            "sample": [doc.name for doc in documents[:5]],
        }

    @staticmethod
    def _is_vitepress_state(source_id: str, entry: dict) -> bool:
        return source_id.startswith(SOURCE_PREFIX) or entry.get("source") == "vitepress"

    def sync_page(self, page_id: int):
        with _lock:
            try:
                page = self.bs.get_page(page_id)
                books = self.bs.list_books()
                book_map = {b["id"]: b["name"] for b in books}
                chapters = self.bs.list_chapters()
                chapter_map = {c["id"]: c["name"] for c in chapters}
                page["_book_name"] = book_map.get(page.get("book_id"), "")
                page["_chapter_name"] = chapter_map.get(page.get("chapter_id"), "")
                self._upsert_page(page)
                self._save_state()
            except Exception as e:
                logger.error(f"Sync page {page_id} failed: {e}", exc_info=True)

    def delete_page(self, page_id: int):
        with _lock:
            pid = str(page_id)
            if pid in self.state:
                doc_id = self.state[pid].get("document_id")
                if doc_id:
                    self.mk.delete_document(doc_id)
                    logger.info(f"Deleted MaxKB document {doc_id} for page {page_id}")
                del self.state[pid]
                self._save_state()
            else:
                logger.info(f"Page {page_id} not in state, skip delete")

    def _upsert_page(self, page: dict):
        pid = str(page["id"])
        name = self._page_display_name(page)
        markdown = self.bs.get_page_markdown(page["id"])
        content_hash = self._content_hash(markdown)

        if pid in self.state:
            existing = self.state[pid]
            if existing.get("hash") == content_hash:
                logger.info(f"Page {pid} unchanged, skip")
                return
            old_doc_id = existing.get("document_id")
            if old_doc_id:
                self.mk.delete_document(old_doc_id)

        paragraphs = self.split_to_paragraphs(markdown)
        doc = self.mk.create_document(name, paragraphs)
        self.state[pid] = {
            "document_id": doc["id"],
            "name": name,
            "hash": content_hash,
            "updated_at": page.get("updated_at", ""),
        }
        logger.info(f"Upserted page {pid} -> doc {doc['id']} ({name})")

    def full_sync(self) -> dict:
        with _lock:
            stats = {"created": 0, "updated": 0, "deleted": 0, "skipped": 0, "errors": 0}
            try:
                documents = self.source.list_documents()
            except Exception as e:
                logger.error(f"Failed to scan VitePress manuals: {e}")
                stats["errors"] = 1
                return stats

            logger.info(f"Found {len(documents)} VitePress manuals to sync")
            current_source_ids = set()

            for document in documents:
                source_id = document.source_id
                current_source_ids.add(source_id)
                try:
                    content_hash = self._content_hash(document.content)

                    if source_id in self.state:
                        if self.state[source_id].get("hash") == content_hash:
                            stats["skipped"] += 1
                            continue
                        old_doc_id = self.state[source_id].get("document_id")
                        if old_doc_id:
                            self.mk.delete_document(old_doc_id)
                        paragraphs = self.split_to_paragraphs(document.content)
                        doc = self.mk.create_document(document.name, paragraphs)
                        self.state[source_id] = {
                            "document_id": doc["id"],
                            "name": document.name,
                            "hash": content_hash,
                            "path": document.relative_path,
                            "source": "vitepress",
                        }
                        stats["updated"] += 1
                    else:
                        paragraphs = self.split_to_paragraphs(document.content)
                        doc = self.mk.create_document(document.name, paragraphs)
                        self.state[source_id] = {
                            "document_id": doc["id"],
                            "name": document.name,
                            "hash": content_hash,
                            "path": document.relative_path,
                            "source": "vitepress",
                        }
                        stats["created"] += 1
                except Exception as e:
                    logger.error(f"Error syncing manual {source_id}: {e}")
                    stats["errors"] += 1

            to_delete = [
                source_id
                for source_id, entry in self.state.items()
                if self._is_vitepress_state(source_id, entry) and source_id not in current_source_ids
            ]
            for source_id in to_delete:
                doc_id = self.state[source_id].get("document_id")
                if doc_id:
                    self.mk.delete_document(doc_id)
                del self.state[source_id]
                stats["deleted"] += 1

            self._save_state()
            logger.info(f"Full sync complete: {stats}")
            return stats
