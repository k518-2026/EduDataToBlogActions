"""蓄積した論文の投稿キュー。

queue/index.json に並べた論文を，古いものから順に，一定の間隔（既定は2日）をあけて投稿する。
各論文の本文は queue/<file> に生成済みのテキスト（insights / paper / review）として置く。
本文を直したいときは，その JSON を直すだけでよい（次の投稿から反映される）。

status: "ready"（投稿待ち）／"hold"（保留。順番を飛ばす）／"posted"（投稿済み）
"""
import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from src.config import BASE_DIR

QUEUE_DIR = BASE_DIR / "queue"
INDEX_PATH = QUEUE_DIR / "index.json"


def load_index(path: Path = INDEX_PATH) -> dict:
    if not path.exists():
        return {"min_interval_days": 2, "items": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_index(index: dict, path: Path = INDEX_PATH) -> None:
    path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _parse(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def days_since_last_post(index: dict, today: date) -> Optional[int]:
    posted = [_parse(i["posted_on"]) for i in index["items"] if i.get("status") == "posted" and i.get("posted_on")]
    return (today - max(posted)).days if posted else None


def pick_next(index: dict, today: date, min_interval_days: Optional[int] = None) -> Optional[dict]:
    """次に投稿する論文。前回の投稿から間隔が足りない，または待ちがなければ None。"""
    gap = index.get("min_interval_days", 2) if min_interval_days is None else min_interval_days
    since = days_since_last_post(index, today)
    if since is not None and since < gap:
        return None
    for item in index["items"]:
        if item.get("status") == "ready":
            return item
    return None


def mark_posted(index: dict, item_id: str, today: date) -> None:
    for item in index["items"]:
        if item["id"] == item_id:
            item["status"] = "posted"
            item["posted_on"] = today.isoformat()
            return
    raise KeyError(item_id)
