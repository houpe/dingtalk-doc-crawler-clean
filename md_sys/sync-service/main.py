import logging
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import uvicorn
import config
from sync import SyncService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="VitePress Manuals → MaxKB Sync Service")
sync_service = SyncService()

PAGE_EVENTS = {"page_create", "page_update", "page_restore", "page_move"}
DELETE_EVENTS = {"page_delete"}
BOOK_EVENTS = {"book_create", "book_update", "book_delete", "book_sort"}
SHELF_EVENTS = {"bookshelf_create", "bookshelf_update", "bookshelf_delete"}
CHAPTER_EVENTS = {"chapter_create", "chapter_update", "chapter_delete", "chapter_move"}
FULL_SYNC_EVENTS = BOOK_EVENTS | SHELF_EVENTS | CHAPTER_EVENTS


class SyncResponse(BaseModel):
    status: str
    detail: str = ""


@app.on_event("startup")
def startup():
    cron = config.SYNC_CRON.strip()
    parts = cron.split()
    if len(parts) == 5:
        trigger = CronTrigger(
            minute=parts[0], hour=parts[1], day=parts[2], month=parts[3], day_of_week=parts[4]
        )
    else:
        trigger = CronTrigger(hour="*/2")
    scheduler = BackgroundScheduler()
    scheduler.add_job(_scheduled_sync, trigger=trigger, id="full_sync", replace_existing=True)
    scheduler.start()
    app.state.scheduler = scheduler
    logger.info(f"Scheduled full sync with cron: {cron}")
    threading.Thread(target=_initial_sync, daemon=True).start()


def _initial_sync():
    logger.info("Running initial full sync...")
    try:
        stats = sync_service.full_sync()
        logger.info(f"Initial sync result: {stats}")
    except Exception as e:
        logger.error(f"Initial sync failed: {e}")


def _scheduled_sync():
    logger.info("Running scheduled full sync...")
    try:
        stats = sync_service.full_sync()
        logger.info(f"Scheduled sync result: {stats}")
    except Exception as e:
        logger.error(f"Scheduled sync failed: {e}")


@app.post("/webhook/bookstack", response_model=SyncResponse)
async def bookstack_webhook(request: Request):
    if config.WEBHOOK_SECRET:
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {config.WEBHOOK_SECRET}":
            raise HTTPException(status_code=401, detail="Invalid webhook secret")

    body = await request.json()
    event = body.get("event", "")
    related = body.get("related_item", {}) or {}
    page_id = related.get("id")

    logger.info(f"Received webhook event: {event}, page_id={page_id}")

    if event in DELETE_EVENTS and page_id:
        threading.Thread(target=sync_service.delete_page, args=(page_id,), daemon=True).start()
        return SyncResponse(status="ok", detail=f"page {page_id} delete queued")

    if event in PAGE_EVENTS and page_id:
        threading.Thread(target=sync_service.sync_page, args=(page_id,), daemon=True).start()
        return SyncResponse(status="ok", detail=f"page {page_id} sync queued")

    if event in FULL_SYNC_EVENTS:
        threading.Thread(target=_scheduled_sync, daemon=True).start()
        return SyncResponse(status="ok", detail=f"event {event} triggered full sync")

    return SyncResponse(status="ignored", detail=f"event {event} not handled")


@app.post("/sync/full", response_model=SyncResponse)
async def trigger_full_sync():
    threading.Thread(target=_scheduled_sync, daemon=True).start()
    return SyncResponse(status="ok", detail="full sync triggered")


@app.get("/sync/status")
async def sync_status():
    return {
        "source": "vitepress",
        "tracked_documents": len([
            entry for key, entry in sync_service.state.items()
            if sync_service._is_vitepress_state(key, entry)
        ]),
        "knowledge_id": config.MAXKB_KNOWLEDGE_ID,
        "cron": config.SYNC_CRON,
        "docs_dir": config.VITEPRESS_DOCS_DIR,
    }


@app.get("/sync/dry-run")
async def dry_run():
    return sync_service.dry_run()


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
