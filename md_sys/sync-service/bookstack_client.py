import logging
import requests
import config

logger = logging.getLogger(__name__)


class BookStackClient:
    def __init__(self):
        self.base_url = config.BOOKSTACK_URL.rstrip("/")
        self.headers = {
            "Authorization": f"Token {config.BOOKSTACK_TOKEN_ID}:{config.BOOKSTACK_TOKEN_SECRET}"
        }

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self.base_url}/api/{path.lstrip('/')}"
        resp = requests.get(url, headers=self.headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _get_all(self, path: str, params: dict = None) -> list:
        items = []
        page = 1
        params = dict(params or {})
        while True:
            params["page"] = page
            data = self._get(path, params)
            items.extend(data.get("data", data if isinstance(data, list) else []))
            if not data.get("has_more", False) and not data.get("next_page_url"):
                break
            page += 1
        return items

    def list_books(self) -> list[dict]:
        return self._get_all("/books", {"count": config.PAGE_SIZE})

    def get_book(self, book_id: int) -> dict:
        return self._get(f"/books/{book_id}")

    def list_shelves(self) -> list[dict]:
        return self._get_all("/shelves", {"count": config.PAGE_SIZE})

    def list_pages(self, book_id: int = None) -> list[dict]:
        params = {"count": config.PAGE_SIZE}
        if book_id is not None:
            params["filter[book_id]"] = book_id
        return self._get_all("/pages", params)

    def get_page(self, page_id: int) -> dict:
        return self._get(f"/pages/{page_id}")

    def get_page_markdown(self, page_id: int) -> str:
        page = self._get(f"/pages/{page_id}")
        return page.get("markdown", "") or page.get("html", "")

    def list_chapters(self, book_id: int = None) -> list[dict]:
        params = {"count": config.PAGE_SIZE}
        if book_id is not None:
            params["filter[book_id]"] = book_id
        return self._get_all("/chapters", params)

    def get_all_pages_with_books(self) -> list[dict]:
        pages = self.list_pages()
        books = self.list_books()
        book_map = {b["id"]: b["name"] for b in books}
        chapters = self.list_chapters()
        chapter_map = {c["id"]: c["name"] for c in chapters}
        for p in pages:
            p["_book_name"] = book_map.get(p.get("book_id"), "")
            p["_chapter_name"] = chapter_map.get(p.get("chapter_id"), "")
        return pages
