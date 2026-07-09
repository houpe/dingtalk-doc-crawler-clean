import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

BOOKSTACK_URL = os.getenv("BOOKSTACK_URL", "http://bookstack")
BOOKSTACK_TOKEN_ID = os.getenv("BOOKSTACK_TOKEN_ID", "")
BOOKSTACK_TOKEN_SECRET = os.getenv("BOOKSTACK_TOKEN_SECRET", "")

MAXKB_URL = os.getenv("MAXKB_URL", "http://maxkb:8080")
MAXKB_USERNAME = os.getenv("MAXKB_USERNAME", "admin")
MAXKB_PASSWORD = os.getenv("MAXKB_PASSWORD", "")
MAXKB_WORKSPACE_ID = os.getenv("MAXKB_WORKSPACE_ID", "default")
MAXKB_KNOWLEDGE_ID = os.getenv("MAXKB_KNOWLEDGE_ID", "")

SYNC_CRON = os.getenv("SYNC_CRON", "0 */2 * * *")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
STATE_FILE = os.getenv("STATE_FILE", os.path.join(BASE_DIR, "state.json"))
VITEPRESS_DOCS_DIR = os.getenv(
    "VITEPRESS_DOCS_DIR",
    os.path.join(DEFAULT_REPO_ROOT, "site", "docs"),
)

PAGE_SIZE = 500
PARAGRAPH_MAX_LENGTH = 3000
