"""GitHub Actions は、ローカルで作って push した論文を投稿するだけ。言語モデルは呼ばない。"""
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "daily_report.yml"


def test_workflow_only_posts_from_the_queue_and_has_no_model_keys():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "--from-queue" in text
    assert "QUEUE_ONLY: 'true'" in text
    for forbidden in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "OLLAMA", "--force", "INPUT_TOPIC", "INPUT_DATASET"):
        assert forbidden not in text, forbidden
    assert "vars.WP_PUBLISHING_PAUSED || 'true'" in text  # paused unless the variable says otherwise
    assert "queue/index.json" in text  # the queue state is committed after a post
