"""校正の指示書が、パスを壊さずに作れること（過去に、バックスラッシュが制御文字に化けた）。"""
import re

from tools.make_brief import make as make_brief
from tools.make_facts import make as make_facts
from tools.make_proof_brief import make


def test_proof_brief_has_clean_paths_and_the_rules():
    make_facts("oecd_talis_teacher_survey", "talis_collaboration_ict")
    make_brief("oecd_talis_teacher_survey", "talis_collaboration_ict")
    text = make("oecd_talis_teacher_survey", "talis_collaboration_ict").read_text(encoding="utf-8")
    assert not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text.replace("\t", "")), "制御文字が混ざっている"
    assert "\t" not in text
    assert "絶対に守ること" in text and "使ってよい文献" in text and "4,940字以内" in text
    for path in re.findall(r"`([A-Z]:\[^`]+)`", text):
        if path.endswith(".json") and "proof_changes" not in path and "draft_" not in path and "gemma4_12b__" not in path:
            from pathlib import Path

            assert Path(path.split("`")[0]).exists(), path
