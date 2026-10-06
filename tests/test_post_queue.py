import json
from datetime import date

from src import post_queue


def _index(*statuses):
    return {"min_interval_days": 2, "items": [
        {"id": f"i{n}", "status": st, "posted_on": on} for n, (st, on) in enumerate(statuses)]}


def test_pick_next_respects_interval_and_order():
    idx = _index(("posted", "2026-10-06"), ("ready", None), ("ready", None))
    assert post_queue.pick_next(idx, date(2026, 10, 7)) is None  # 1 day since the last post
    assert post_queue.pick_next(idx, date(2026, 10, 8))["id"] == "i1"  # 2 days: oldest ready item
    idx["items"][1]["status"] = "hold"
    assert post_queue.pick_next(idx, date(2026, 10, 8))["id"] == "i2"  # held items are skipped


def test_pick_next_with_nothing_ready_or_nothing_posted_yet():
    assert post_queue.pick_next(_index(("posted", "2026-10-01")), date(2026, 10, 9)) is None
    assert post_queue.pick_next(_index(("ready", None)), date(2026, 10, 6))["id"] == "i0"


def test_mark_posted_and_the_real_queue_is_loadable():
    idx = _index(("ready", None))
    post_queue.mark_posted(idx, "i0", date(2026, 10, 6))
    assert idx["items"][0] == {"id": "i0", "status": "posted", "posted_on": "2026-10-06"}
    real = post_queue.load_index()
    assert real["items"], "queue/index.json must list the stockpiled papers"
    from src.academic_paper import AcademicPaper
    from src.insights import EducationalInsights
    from src.peer_review import PeerReviewReport

    for item in real["items"]:  # the saved texts must load into the real classes
        data = json.loads((post_queue.QUEUE_DIR / item["file"]).read_text(encoding="utf-8"))
        review = dict(data["review"])
        review["scores"] = {k: tuple(v) for k, v in review["scores"].items()}
        EducationalInsights(**data["insights"])
        paper = AcademicPaper(**data["paper"])
        assert PeerReviewReport(**review).decision
        assert len(paper.references) >= 7 and paper.title
