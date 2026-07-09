from dataclasses import dataclass
from pathlib import Path


EXCLUDED_DIRS = {".vitepress", "node_modules", "public"}
SOURCE_PREFIX = "vitepress:"


@dataclass(frozen=True)
class VitePressDocument:
    source_id: str
    name: str
    content: str
    path: Path
    relative_path: str


class VitePressSource:
    def __init__(self, docs_dir: str | Path):
        self.docs_dir = Path(docs_dir).expanduser().resolve()

    def list_documents(self) -> list[VitePressDocument]:
        if not self.docs_dir.exists():
            return []

        documents = []
        for path in sorted(self.docs_dir.rglob("*.md")):
            if not self._is_manual(path):
                continue
            relative = path.relative_to(self.docs_dir)
            relative_posix = relative.as_posix()
            documents.append(
                VitePressDocument(
                    source_id=f"{SOURCE_PREFIX}{relative_posix}",
                    name=self._document_name(relative),
                    content=path.read_text(encoding="utf-8"),
                    path=path,
                    relative_path=relative_posix,
                )
            )
        return documents

    def _is_manual(self, path: Path) -> bool:
        relative = path.relative_to(self.docs_dir)
        if path.name.lower() == "index.md":
            return False
        return not any(part in EXCLUDED_DIRS for part in relative.parts)

    @staticmethod
    def _document_name(relative: Path) -> str:
        parts = list(relative.parts)
        parts[-1] = Path(parts[-1]).stem
        return " / ".join(parts)
