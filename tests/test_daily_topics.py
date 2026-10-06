"""毎日1本の題材の一覧（queue/topics.json）が、実在するデータセット・研究角度を指していること。"""
import json

from src.academic_contexts import get_all_angles_for_dataset
from src.config import CATALOG_DIR
from src.post_queue import QUEUE_DIR


def test_topics_point_at_real_datasets_and_angles_and_queue_files_exist():
    topics = json.loads((QUEUE_DIR / "topics.json").read_text(encoding="utf-8"))["topics"]
    assert topics
    seen = set()
    for t in topics:
        assert (CATALOG_DIR / f"{t['dataset_id']}.json").exists(), t
        assert t["angle_id"] in {a.angle_id for a in get_all_angles_for_dataset(t["dataset_id"])}, t
        assert t["status"] in ("todo", "done", "failed", "skip")
        key = (t["dataset_id"], t["angle_id"])
        assert key not in seen, key
        seen.add(key)
    index = json.loads((QUEUE_DIR / "index.json").read_text(encoding="utf-8"))["items"]
    for item in index:
        assert (QUEUE_DIR / item["file"]).exists(), item
