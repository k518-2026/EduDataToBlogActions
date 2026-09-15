"""
General utilities for EduDataToBlogActions.
Includes Japan Standard Time (JST) date handling, metric unit resolution, and text cleaning.
"""
from datetime import datetime
import re
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

    # Remove spaces between Japanese characters: '漢字　ひらがな' -> '漢字ひらがな'
    text = re.sub(r"([一-龥ぁ-んァ-ヶ])\s+([一-龥ぁ-んァ-ヶ])", r"\1\2", text)
    # Remove spaces between Japanese character and alphanumeric: '研究所 TIMSS' -> '研究所TIMSS', 'TIMSS 調査' -> 'TIMSS調査'
    text = re.sub(r"([一-龥ぁ-んァ-ヶ])\s+([A-Za-z0-9])", r"\1\2", text)
    text = re.sub(r"([A-Za-z0-9])\s+([一-龥ぁ-んァ-ヶ])", r"\1\2", text)

    # Remove spaces around Japanese punctuation
    text = re.sub(r"\s+([，．、。（）「」『』])", r"\1", text)
    text = re.sub(r"([（「『])\s+", r"\1", text)
    text = re.sub(r"\s+([）」』])", r"\1", text)
    return text


def format_title_two_lines(title: str) -> str:
    """
    Formats an academic paper title so that it cleanly breaks into at most 2 balanced lines.
    Inserts '<br/>' before common suffix markers like 'に関する' if the title is longer than 24 chars.
    """
    if not title:
        return ""
    clean = clean_text_spaces(title)
    if "<br/>" in clean or "<br>" in clean:
        return clean

    # Strip existing line breaks
    clean = clean.replace("\n", "").strip()

    # If title is short enough (<= 24 characters), keep it on 1 line
    if len(clean) <= 24:
        return clean

    # Break before 'に関する' or 'の推移'
    for marker in ("に関する", "における"):
        if marker in clean:
            parts = clean.split(marker, 1)
            # Ensure line 1 has substantial length
            if len(parts[0]) >= 10:
                return f"{parts[0]}<br/>{marker}{parts[1]}"

    # Break after midpoint at particle
    mid = len(clean) // 2
    for marker in ("の推移", "の比較", "と", "・"):
        idx = clean.find(marker, max(mid - 8, 8))
        if idx != -1 and idx < mid + 8:
            split_at = idx + len(marker)
            return f"{clean[:split_at]}<br/>{clean[split_at:]}"

    return clean


def clean_insight_text(text: str) -> str:
    """
    Sanitizes educational insight text to guarantee no raw JSON keys, braces,
    escaped quotes, or trailing fragments appear in blog posts or markdown documents.
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


