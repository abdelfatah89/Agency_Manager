def parse_float(value, default=0.0):
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(" ", "")
    if not text:
        return default

    # Normalize locale/thousands separators safely.
    # Examples handled: 1,234.56 | 1.234,56 | 1234,56 | 1,234,567.89
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            # Decimal separator is comma, dot is thousands separator.
            text = text.replace(".", "").replace(",", ".")
        else:
            # Decimal separator is dot, comma is thousands separator.
            text = text.replace(",", "")
    elif "," in text:
        parts = text.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Likely decimal comma.
            text = text.replace(",", ".")
        else:
            # Likely thousands commas.
            text = text.replace(",", "")
    elif text.count(".") > 1:
        # Keep only the last dot as decimal separator.
        head, tail = text.rsplit(".", 1)
        text = head.replace(".", "") + "." + tail

    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def compute_diff_percent(first_value: float, last_value: float) -> float:
    first = parse_float(first_value)
    last = parse_float(last_value)
    if first == 0:
        return 0.0
    return ((last - first) / first) * 100.0
