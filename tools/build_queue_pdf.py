r"""キューの論文を、LuaLaTeX で組んで PDF にする。

    python -m tools.build_queue_pdf <キューの項目の id>      例: 04_oecd_talis_teacher_survey
    python -m tools.build_queue_pdf --all                     ready と hold の全項目

出力: queue/pdf/<id>.pdf（投稿のときに使う PDF）と、queue/latex/<id>/（paper.tex と図。再組版用）。
GitHub Actions は LaTeX を持たないので、PDF はここで作って push する。src/main.py は、queue/pdf/<id>.pdf があれば reportlab 版の代わりに使う。
4ページを超えたときは、警告を出す（本文を短くする）。3ページでもよい（4ページ以内）。
"""
import json
import shutil
import sys

from src.config import BASE_DIR
from tools.latex_paper import build

QUEUE = BASE_DIR / "queue"


def build_item(item):
    gen = QUEUE / item["file"]
    out = QUEUE / "latex" / item["id"]
    res = build(str(gen), item["dataset_id"], item["angle_id"], str(out))
    if res.get("pdf"):
        (QUEUE / "pdf").mkdir(exist_ok=True)
        shutil.copyfile(res["pdf"], QUEUE / "pdf" / f"{item['id']}.pdf")
    # 組版の作業ファイルは小さくする（ログ・補助ファイルは残さない）
    for ext in (".aux", ".log", ".out"):
        f = out / f"paper{ext}"
        if f.exists():
            f.unlink()
    return res


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    index = json.loads((QUEUE / "index.json").read_text(encoding="utf-8"))["items"]
    want = [i for i in index if sys.argv[1] == "--all" or i["id"] == sys.argv[1]]
    if not want:
        sys.exit(f"キューにない項目: {sys.argv[1]}")
    for it in want:
        r = build_item(it)
        flag = "" if r["pages"] and r["pages"] <= 4 else "  ← 4ページではない"
        print(f"{it['id']}: {r['pages']}ページ（returncode {r['returncode']}）{flag}")
        if r["returncode"]:
            print(r["log_tail"])
