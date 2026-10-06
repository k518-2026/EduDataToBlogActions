"""論文の本文にある数値が、事実ファイル（tools/make_facts.py の出力）にあるかを検査する。

    python -m tools.check_numbers <generation.json> <facts.json>

事実ファイルにない数値は「未照合」として一覧にする。未照合が残るものは，人が元データに当たって確かめるか，事実ファイルに足してから通す。
符号は無視する。".31" と "0.31"，"1,000" と "1000"，"10.0" と "10" は同じとみなす。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

NUM = re.compile(r"(?<![\w.])-?(?:\d{1,3}(?:,\d{3})+|\d+)?\.?\d+(?:\.\d+)?")
SECTIONS = ["abstract", "background", "objectives", "methodology", "results_text", "discussion"]
ALWAYS_OK = {"1.96", "0.05", "0.01", "0.001", "95", "1000", "0", "1", "2", "3", "0.33", "0.3"}  # 方法の定数と，ごく小さい整数


def norm(tok):
    t = tok.replace(",", "").lstrip("-+")
    if t.startswith("."):
        t = "0" + t
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t or "0"


def fact_tokens(obj):
    out = set()
    text = json.dumps(obj, ensure_ascii=False)
    for m in NUM.finditer(text):
        out.add(norm(m.group()))
    # 全角・小数の丸め違い（.31 と 0.305 のような差）は認めない。そのまま照合する
    return out


def strip_markup(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[（(][A-Za-z぀-ヿ一-龯\s.\-・＆&]+?[，,]\s*[12]\d{3}[）)]", "", s)   # （著者，年）
    s = re.sub(r"[A-Za-z぀-ヿ一-龯.\-・＆&]+(?: et al\.| and [A-Z][a-z]+)? ?[（(][12]\d{3}[）)]", "", s)  # 著者 (年)
    s = re.sub(r"[（(]\d{1,2}[）)]", "", s)          # (1) (2) の列挙
    s = re.sub(r"RQ\d|H\d|BF\s*10|BF10|<sub>\d+</sub>|\bK=|ISCED ?\d", "", s)
    s = re.sub(r"[12]\d{3}年度?|令和\d+年度?|平成\d+年度?|\d{1,2}月|\d{1,2}日", "", s)           # 年・月・日
    s = re.sub(r"\d+本|\d+つ", "", s)
    return s


def check(gen_path, facts_path, extra_text=""):
    gen = json.loads(open(gen_path, encoding="utf-8").read())
    facts = json.loads(open(facts_path, encoding="utf-8").read())
    known = fact_tokens(facts) | fact_tokens(extra_text) | ALWAYS_OK
    unmatched = []
    for sec in SECTIONS:
        text = strip_markup(gen["paper"].get(sec, ""))
        for m in NUM.finditer(text):
            tok = norm(m.group())
            if tok not in known:
                ctx = text[max(0, m.start() - 18): m.end() + 14].replace("\n", " ")
                unmatched.append((sec, m.group(), ctx))
    return unmatched


if __name__ == "__main__":
    gen, facts = sys.argv[1:3]
    extra = open(sys.argv[3], encoding="utf-8").read() if len(sys.argv) > 3 else ""
    un = check(gen, facts, extra)
    for sec, tok, ctx in un:
        print(f"[未照合] {sec}: {tok}  …{ctx}…")
    print(f"未照合 {len(un)} 件")
    sys.exit(1 if un else 0)
