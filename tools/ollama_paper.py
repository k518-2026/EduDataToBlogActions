"""Ollama のモデルに、Claude と同じ指示・同じ事実ファイルで論文を書かせる（比較実験用）。

    python -m tools.ollama_paper <dataset_id> <angle_id> <model> [<base_url>]

出力: temp/ollama_cmp/<model>__<dataset_id>.json（draft と同じ形）と、所要時間・トークン数のメモ。
指示書（temp/brief_<dataset_id>.md）は、ファイルを読ませる前提で書かれているので、必要な部分（書くもの・守ること・文献）
と事実ファイル・見本を、プロンプトに直接入れる。
"""
import json
import re
import sys
import time

import requests

from src.config import BASE_DIR, TEMP_DIR
from tools.make_brief import pick_exemplars



def build_prompt(dataset_id, angle_id):
    EXEMPLARS = pick_exemplars(dataset_id)  # 同じ題材の完成版は入れない（写してしまう）
    assert not any(dataset_id in e for e in EXEMPLARS), "見本に同じ題材の論文が入っている"
    brief = (TEMP_DIR / f"brief_{dataset_id}.md").read_text(encoding="utf-8")
    facts = (TEMP_DIR / f"facts_{dataset_id}.json").read_text(encoding="utf-8")
    sec = lambda n: re.search(rf"## {n}\..*?(?=\n## \d\.|\Z)", brief, re.S).group(0)
    head = brief.split("## 1.")[0]
    theme = re.search(r"- テーマ:.*?(?=- データの性質)", brief, re.S).group(0)
    nature = re.search(r"- データの性質.*?(?=\n## 2\.)", brief, re.S).group(0)
    examples = []
    for ex in EXEMPLARS:
        g = json.loads((BASE_DIR / ex).read_text(encoding="utf-8"))
        g["paper"].pop("references", None)
        examples.append(json.dumps({"paper": g["paper"], "insights": g["insights"]}, ensure_ascii=False))
    return (head + "\n## 資料\n" + theme + nature +
            "\n\n### 事実ファイル（使ってよい数値の一覧。これ以外の数値は書かない）\n" + facts +
            "\n\n### 見本1（完成済みの論文。語り口・構成・長さ・注意の払い方を真似る）\n" + examples[0] +
            "\n\n### 見本2\n" + examples[1] + "\n\n" + sec(2) + "\n" + sec(3) + "\n" + sec(4) +
            "\n\n出力は、上のスキーマのJSONだけ。説明文やコードブロックは付けない。")


def run(dataset_id, angle_id, model, base_url):
    prompt = build_prompt(dataset_id, angle_id)
    body = {"model": model, "stream": False, "format": "json", "think": False,
            "messages": [{"role": "system", "content": "あなたは教育データ分析の論文を書く執筆者です。指示と事実ファイルだけを根拠に、日本語で、正確に書きます。"},
                         {"role": "user", "content": prompt}],
            "options": {"num_ctx": 49152, "num_predict": 9000, "temperature": 0.3}}
    t0 = time.time()
    r = requests.post(base_url.rstrip("/") + "/api/chat", json=body, timeout=3600)
    r.raise_for_status()
    j = r.json()
    dt = time.time() - t0
    text = j["message"]["content"]
    out_dir = TEMP_DIR / "ollama_cmp"
    out_dir.mkdir(exist_ok=True)
    stem = f"{model.replace(':', '_')}__{dataset_id}"
    (out_dir / f"{stem}.raw.txt").write_text(text, encoding="utf-8")
    meta = {"model": model, "seconds": round(dt, 1), "prompt_tokens": j.get("prompt_eval_count"), "output_tokens": j.get("eval_count"),
            "done_reason": j.get("done_reason"), "prompt_chars": len(prompt)}
    try:
        data = json.loads(text)
        (out_dir / f"{stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        meta["json_ok"] = True
    except json.JSONDecodeError as e:
        meta["json_ok"] = False
        meta["json_error"] = str(e)
    (out_dir / f"{stem}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


if __name__ == "__main__":
    ds, ang, model = sys.argv[1:4]
    url = sys.argv[4] if len(sys.argv) > 4 else "http://192.168.128.62:11434"
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(run(ds, ang, model, url), ensure_ascii=False))
