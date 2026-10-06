"""python -m tools.merge_draft <dataset_id> <angle_id> <番号>

draft_<ds>.json（執筆）と review_<ds>.json（査読）を1つの generation.json にまとめ、引用から参考文献を作り、queue に入れる。"""
import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from src.academic_paper import AcademicPaper, synchronize_citations_and_references
from src.academic_contexts import get_all_angles_for_dataset

ds, angle_id, seq = sys.argv[1:4]
draft = json.load(open(rf"{ROOT}\temp\draft_{ds}.json", encoding="utf-8"))
review = json.load(open(rf"{ROOT}\temp\review_{ds}.json", encoding="utf-8"))["review"]
review["paper_title"] = draft["paper"]["title"]
angle = [a for a in get_all_angles_for_dataset(ds) if a.angle_id == angle_id][0]
paper = synchronize_citations_and_references(AcademicPaper(**draft["paper"]), ds, angle)
draft["paper"]["references"] = paper.references
gen = {"insights": draft["insights"], "paper": draft["paper"], "review": review}
name = f"{int(seq):02d}_{ds}.generation.json"
json.dump(gen, open(str(Path(ROOT) / "queue" / name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(name, "references:", len(paper.references))
for r in paper.references:
    print(" -", r[:110])
