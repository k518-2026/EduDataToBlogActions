"""
General utilities for EduDataToBlogActions.
Includes Japan Standard Time (JST) date handling, metric unit resolution, and text cleaning.
"""
from datetime import datetime
import re
from typing import Optional
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def get_jst_now() -> datetime:
    """
    Returns current datetime in Japan Standard Time (JST, UTC+9).
    Falls back to system datetime if zoneinfo database is missing.
    """
    try:
        return datetime.now(JST)
    except Exception:
        return datetime.now()


def format_bayes_factor(val: Optional[float]) -> str:
    """
    Formats Bayes Factor (BF10) according to academic reporting standards (JASP, Wagenmakers et al.).
    Caps massive values at '>1000' and tiny values at '<0.001' to prevent awkward numbers.
    """
    if val is None:
        return "-"
    if not isinstance(val, (int, float)):
        return str(val)
    if val >= 1000.0:
        return ">1000"
    elif val < 0.001:
        return "<0.001"
    else:
        return f"{val:.2f}"


def format_bayes_factor_short_interpretation(val: Optional[float]) -> str:
    """
    Returns a concise academic label (4-6 chars) for Bayes Factor (BF10)
    to fit compactly into academic paper tables.
    Follows Jeffreys (1961) / Lee & Wagenmakers (2013) classification.
    """
    if val is None:
        return "-"
    if not isinstance(val, (int, float)):
        return "-"
    if val >= 100.0:
        return "極めて強い"
    elif val >= 30.0:
        return "非常に強い"
    elif val >= 10.0:
        return "強い証拠"
    elif val >= 3.0:
        return "中程度"
    elif val >= 1.0:
        return "弱い証拠"
    elif val >= 1.0 / 3.0:
        return "弱い(H0)"
    elif val >= 1.0 / 10.0:
        return "中程度(H0)"
    elif val >= 1.0 / 30.0:
        return "強い(H0)"
    else:
        return "極強(H0)"


def resolve_metric_unit(metric: str, dataset_unit: str = "%") -> str:
    """
    Returns a clean singular unit for a given metric name.
    Prevents composite slash units like '点 / %' or '人 / %' from appearing in prose and charts.
    """
    m = metric.lower()
    if any(k in m for k in ("率", "割合", "比率", "pct", "percent")):
        return "%"
    if any(k in m for k in ("得点", "点数", "スコア", "score", "math", "pisa", "timss")):
        return "点"
    if any(k in m for k in ("人数", "学生数", "入学者数", "生徒数", "教員数", "人員")):
        return "人"
    if any(k in m for k in ("校数", "学校数")):
        return "校"
    if "/" in dataset_unit:
        parts = [p.strip() for p in dataset_unit.split("/")]
        if any(k in m for k in ("率", "割合", "比率")):
            return "%"
        return parts[0]
    clean = dataset_unit.replace("Score (点)", "点").replace("score", "点").strip()
    return clean if clean else "%"


def clean_text_spaces(text: str) -> str:
    """
    Removes awkward English-style spaces inside Japanese sentences and around punctuation/slashes.
    Prevents ReportLab from prematurely breaking lines before CJK/Latin boundaries.
    Safely cleans composite units like '点 / %' and slashes without breaking HTML tags or URLs.
    """
    if not text:
        return ""
    # Clean composite units
    text = re.sub(r"点\s*[/／]\s*%", "点", text)
    text = re.sub(r"人\s*[/／]\s*%", "人", text)
    text = re.sub(r"\b点\s*/\s*%", "点", text)
    text = re.sub(r"\s*[/／]\s*%", "%", text)

    # Replace isolated slashes surrounded by whitespace: ' / ' or ' ／ ' -> '・'
    text = re.sub(r"\s+[/／]\s+", "・", text)
    # Replace full-width slashes between words: 'A／B' -> 'A・B'
    text = re.sub(r"／", "・", text)

    # Standardize formula variable notations
    text = re.sub(r"\bBF\s*10\b", "<i>BF</i><sub>10</sub>", text)
    text = re.sub(r"\bR\s*2\b", "<i>R</i><sup>2</sup>", text)
    text = re.sub(r"R\^2", "<i>R</i><sup>2</sup>", text)

    # Prevent large unformatted floats for Bayes Factor (e.g. BF10 = 8169073518445.85 -> BF10>1000)
    text = re.sub(
        r"(<i>BF</i><sub>10</sub>|BF₁₀|BF10)\s*([=＝])\s*(?:\d{4,}(?:\.\d+)?|8\d{6,}(?:\.\d+)?)",
        r"\1>1000",
        text,
    )

    # Remove spaces around operators in statistical expressions (preventing line breaks between var, =, and val)
    text = re.sub(
        r"([<i>]*[A-Za-z]+[</i>]*(?:<sub>\w+</sub>|<sup>\w+</sup>)?|[A-Za-z]+値|p値)\s*([=＝><＜＞])\s*",
        r"\1\2",
        text,
    )

    # Prevent separation of numbers and units (e.g. '534.00 点' -> '534.00点')
    text = re.sub(r"(\d+(?:\.\d+)?)\s*(点|%|％|人|台|校|年|度|回|名|歳|万|千)", r"\1\2", text)

    # Normalize half-width commas and colons in Japanese text context to full-width
    text = re.sub(r"([一-龥ぁ-んァ-ヶ％点人校度年）\]｝」』])\s*,\s*", r"\1，", text)
    text = re.sub(r"\s*,\s*([一-龥ぁ-んァ-ヶ（［｛「『])", r"，\1", text)
    text = re.sub(r"([一-龥ぁ-んァ-ヶ])\s+,", r"\1，", text)

    # Remove spaces or stray single newlines between Japanese characters: '漢字　ひらがな' -> '漢字ひらがな'
    text = re.sub(r"([一-龥ぁ-んァ-ヶ])\s+([一-龥ぁ-んァ-ヶ])", r"\1\2", text)
    # Remove spaces between Japanese character and alphanumeric: '研究所 TIMSS' -> '研究所TIMSS', 'TIMSS 調査' -> 'TIMSS調査'
    text = re.sub(r"([一-龥ぁ-んァ-ヶ])\s+([A-Za-z0-9])", r"\1\2", text)
    text = re.sub(r"([A-Za-z0-9])\s+([一-龥ぁ-んァ-ヶ])", r"\1\2", text)

    # Remove spaces around Japanese and ASCII brackets/punctuation (prevents starting lines with punctuation)
    text = re.sub(r"\s+([，．、。（）「」『』)\]｝}〕〉》】!?！？:：;；])", r"\1", text)
    text = re.sub(r"([（「『(\[{｛〔〈《【])\s+", r"\1", text)
    text = re.sub(r"\s+([）」』)\]｝}〕〉》】])", r"\1", text)
    return text


def contains_japanese(text: str) -> bool:
    """Returns True if the text contains any Japanese characters (Kanji, Hiragana, Katakana)."""
    if not text:
        return False
    return bool(re.search(r"[\u3040-\u309f\u30a0-\u30ff\u3400-\u4dbf\u4e00-\u9fff]", text))


def clean_english_text(text: str) -> str:
    """
    Standardizes English text to ensure strict ASCII punctuation and clean typography.
    - Converts full-width punctuation (，．％：（）など) to standard ASCII (, . % : () etc.).
    - Ensures a single space after punctuation (commas, periods, colons) when followed by a word.
    - Prevents orphan spaces before punctuation.
    - Collapses multiple whitespace characters to single spaces.
    """
    if not text:
        return ""

    # Replace HTML line breaks or newlines with spaces
    text = re.sub(r"<br\s*/?>", " ", text)
    text = text.replace("\n", " ").replace("\r", " ")

    # Normalize full-width punctuation and brackets to ASCII
    replacements = {
        "，": ", ",
        "．": ". ",
        "％": "%",
        "：": ": ",
        "；": "; ",
        "（": " (",
        "）": ") ",
        "［": " [",
        "］": "] ",
        "｛": " {",
        "｝": "} ",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "－": "-",
        "ー": "-",
        "〜": "~",
        "・": " / ",
        "　": " ",
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)

    # Standardize formula notations
    text = re.sub(r"\bBF\s*10\b", "BF10", text)
    text = re.sub(r"\bR\s*2\b", "R2", text)

    # Clean whitespace around punctuation
    text = re.sub(r"\s+([,.:;!?)\]}%])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)

    # Ensure space after punctuation (commas, colons, semicolons) if followed by an alphanumeric character
    text = re.sub(r"([,;:!?])([A-Za-z0-9])", r"\1 \2", text)
    # Ensure space after periods if followed by an uppercase letter (sentence boundary)
    text = re.sub(r"(\.)([A-Z])", r"\1 \2", text)

    # Normalize multiple spaces
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def format_title_two_lines(title: str) -> str:
    """
    Formats an academic paper title so that it cleanly breaks into at most 2 balanced lines.
    Always finds a natural phrase boundary near the midpoint outside quotes/brackets so neither
    line exceeds the printable width or wraps a single trailing character onto a 3rd line.
    """
    if not title:
        return ""
    clean = clean_text_spaces(title)
    clean = re.sub(r"<br\s*/?>", "", clean).replace("\n", "").strip()
    n = len(clean)
    if n <= 25:
        return clean

    # Track bracket depth so we never split inside quotes or parentheses
    open_chars = set("「『（(【［[")
    close_chars = set("」』）)】］]")
    depth = [0] * (n + 1)
    d = 0
    for idx, ch in enumerate(clean):
        if ch in open_chars:
            d += 1
        depth[idx] = d
        if ch in close_chars and d > 0:
            d -= 1
    depth[n] = 0

    mid = n / 2.0
    max_line_len = 30 if n <= 56 else (n // 2 + 4)
    min_pos = max(8, n - max_line_len)
    max_pos = min(n - 7, max_line_len)
    if min_pos > max_pos:
        min_pos, max_pos = max(8, int(n * 0.30)), min(n - 7, int(n * 0.70))

    candidates = []
    # 1. Break AFTER multi-char or single-char phrase markers
    after_markers = [
        ("における", 0.0),
        ("に伴う", 0.0),
        ("に基づく", 0.0),
        ("を通じた", 0.0),
        ("から見た", 0.0),
        ("：", 0.0),
        ("―", 0.0),
        ("—", 0.0),
        ("および", 0.5),
        ("ならびに", 0.5),
        ("と", 1.0),
        ("・", 1.5),
        ("による", 1.5),
        ("から", 2.0),
        ("での", 2.0),
        ("への", 2.0),
        ("の", 2.5),
        ("や", 2.5),
    ]
    for marker, penalty in after_markers:
        start = 0
        while True:
            idx = clean.find(marker, start)
            if idx == -1:
                break
            pos = idx + len(marker)
            if min_pos <= pos <= max_pos and depth[pos - 1] == 0:
                candidates.append((abs(pos - mid) + penalty, pos))
            start = idx + 1

    # 2. Break BEFORE relational markers (only when reasonably balanced)
    before_markers = [
        ("に関する", 0.0),
        ("における", 0.5),
        ("に伴う", 0.5),
        ("に基づく", 0.5),
        ("を通じた", 0.5),
        ("および", 1.0),
    ]
    for marker, penalty in before_markers:
        start = 0
        while True:
            idx = clean.find(marker, start)
            if idx == -1:
                break
            pos = idx
            if min_pos <= pos <= max_pos and (pos == 0 or depth[pos - 1] == 0):
                candidates.append((abs(pos - mid) + penalty, pos))
            start = idx + 1

    if candidates:
        candidates.sort(key=lambda x: x[0])
        best_pos = candidates[0][1]
        return f"{clean[:best_pos]}<br/>{clean[best_pos:]}"

    # Fallback: split near midpoint outside brackets
    best_pos = int(mid)
    for offset in range(0, n // 2):
        for cand in (int(mid) + offset, int(mid) - offset):
            if 8 <= cand <= n - 7 and depth[cand - 1] == 0:
                best_pos = cand
                return f"{clean[:best_pos]}<br/>{clean[best_pos:]}"
    return f"{clean[:best_pos]}<br/>{clean[best_pos:]}"


def sanitize_html_for_wordpress(html_text: str) -> str:
    """
    Sanitizes HTML and text content for WordPress posts (both Post by Email and REST API):
    1. Converts <a href="https://doi.org/10.xxxx/...">...</a> to plain text 'DOI: 10.xxxx/...'.
    2. Converts <a href="...">DOI: 10.xxxx/...</a> to 'DOI: 10.xxxx/...'.
    3. Strips all remaining <a href="...">...</a> tags while preserving their inner text.
    4. Converts Markdown links [text](https://doi.org/10.xxxx/...) to 'DOI: 10.xxxx/...' and [text](url) to 'text'.
    5. Converts bare DOI URLs (https://doi.org/10.xxxx/...) to plain text 'DOI: 10.xxxx/...'.
    6. Deduplicates accidental 'DOI: DOI: ' prefixes.
    """
    if not html_text:
        return ""

    cleaned = str(html_text)

    # 1. Convert <a href="...doi.org/10.xxx">...</a> to DOI: 10.xxx
    cleaned = re.sub(
        r'<a\b[^>]*href=["\']https?://(?:dx\.)?doi\.org/(10\.[^"\'\s>]+)["\'][^>]*>.*?</a>',
        r"DOI: \1",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # 2. Convert <a href="...">DOI: 10.xxx</a> or <a href="...">10.xxx</a> to DOI: 10.xxx
    cleaned = re.sub(
        r"<a\b[^>]*>\s*(?:DOI:\s*)?(10\.\d{4,9}/[^\s<]+)\s*</a>",
        r"DOI: \1",
        cleaned,
        flags=re.IGNORECASE,
    )

    # 3. Strip any remaining <a ...>...</a> tags, preserving inner text
    cleaned = re.sub(
        r"<a\b[^>]*>(.*?)</a>",
        r"\1",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # 4. Convert Markdown DOI links [text](https://doi.org/10.xxx) -> DOI: 10.xxx
    cleaned = re.sub(
        r"(?<!\!)\[[^\]]*\]\(\s*https?://(?:dx\.)?doi\.org/(10\.[^\s\)]+)\s*\)",
        r"DOI: \1",
        cleaned,
        flags=re.IGNORECASE,
    )
    # Strip other Markdown links [text](http...) -> text (preserving ![alt](img))
    cleaned = re.sub(
        r"(?<!\!)\[([^\]]+)\]\(\s*https?://[^\s\)]+\s*\)",
        r"\1",
        cleaned,
    )

    # 5. Convert bare DOI URLs (https://doi.org/10.xxxx) to plain 'DOI: 10.xxxx'
    cleaned = re.sub(
        r"(?:DOI:\s*)?https?://(?:dx\.)?doi\.org/(10\.[^\s<>\"\'\)\]】』，．]+)",
        r"DOI: \1",
        cleaned,
        flags=re.IGNORECASE,
    )

    # 6. Clean up any accidental duplicate "DOI: DOI: "
    cleaned = re.sub(r"(?:DOI:\s*){2,}", "DOI: ", cleaned, flags=re.IGNORECASE)

    return cleaned


def clean_insight_text(text: str) -> str:
    """
    Sanitizes educational insight text to guarantee no raw JSON keys, braces,
    escaped quotes, <a href="..."> links, or trailing fragments appear in blog posts or markdown documents.
    """
    if not text:
        return ""
    t = str(text).strip()

    # Strip markdown code blocks if the whole field or fragment is wrapped
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()

    # Strip leading JSON residue e.g. {"executive_summary":" or "executive_summary":" or partial ns":"
    t = re.sub(r'^\s*\{?\s*"?[a-zA-Z0-9_]*"?\s*:\s*"?', '', t)
    # Strip leading isolated quotes or braces
    t = re.sub(r'^[{\["\']+\s*', '', t)

    # Strip trailing JSON residue e.g. ","pedagogical_implicatio... or "," or "
    t = re.sub(r'",\s*"?[a-zA-Z0-9_]*.*$', '', t)
    # Strip trailing quotes, braces, brackets, commas
    t = re.sub(r'[,}\]"\'\s]+$', '', t)

    # Clean unescaped sequences
    t = t.replace(r'\r\n', '\n').replace(r'\n', '\n').replace(r'\"', '"').replace(r'\/', '/')

    # Strip <a href="..."> links and normalize DOI URLs to plain 'DOI: 10.xxxx/...'
    t = sanitize_html_for_wordpress(t)
    return t.strip()




def get_available_anthropic_models(api_key: str) -> list[str]:
    """
    Fetches the list of active model IDs available to this API key from https://api.anthropic.com/v1/models.
    Returns empty list if request fails or key is missing.
    """
    if not api_key:
        return []
    import json
    import urllib.request
    try:
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/models",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "user-agent": "EduDataToBlogActions/1.0",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [m["id"] for m in data.get("data", []) if "id" in m]
    except Exception:
        return []


def resolve_anthropic_model(api_key: str, preferred_model: str = "") -> str:
    """
    Resolves a valid, available Anthropic model ID.
    If preferred_model is specified and confirmed available in the user's account, uses it.
    Otherwise dynamically queries /v1/models to select the most capable Sonnet/Opus model,
    preventing 404 NOT FOUND errors caused by deprecated model snapshots.
    """
    models = get_available_anthropic_models(api_key)
    if not models:
        return preferred_model or "claude-sonnet-5"

    if preferred_model and preferred_model in models:
        return preferred_model

    # Priority 1: Sonnet 5 or any Sonnet model
    for m in models:
        if "sonnet-5" in m.lower() or ("sonnet" in m.lower() and "5" in m):
            return m
    for m in models:
        if "sonnet" in m.lower():
            return m

    # Priority 2: Opus model
    for m in models:
        if "opus" in m.lower():
            return m

    # Priority 3: First available model
    return models[0]




def extract_anthropic_text(res_data: dict) -> str:
    """Return the text of a Messages API response.

    Newer models can put a thinking block before the text block, so content[0] is not always
    the text. A reply cut off by max_tokens is an error (the JSON would be truncated).
    """
    if res_data.get("stop_reason") == "max_tokens":
        raise ValueError("Claude の応答が max_tokens で途中で切れました")
    parts = [b.get("text", "") for b in res_data.get("content", []) if b.get("type") == "text"]
    text = "".join(parts).strip()
    if not text:
        raise ValueError("Claude の応答に text ブロックがありません: " + str([b.get("type") for b in res_data.get("content", [])]))
    return text
