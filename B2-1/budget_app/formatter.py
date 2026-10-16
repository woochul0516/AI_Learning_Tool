def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """[보너스] 외부 라이브러리 없이 한글/영문 전각 문자 폭을 계산해 표를 정렬하는 포맷터"""
    def get_width(text: str) -> int:
        return sum(2 if ord(c) > 0x7F else 1 for c in str(text))

    col_widths = [get_width(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], get_width(str(val)))

    def pad_str(text: str, width: int) -> str:
        curr_w = get_width(text)
        return text + " " * (width - curr_w)

    line = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_str = "| " + " | ".join(pad_str(h, col_widths[i]) for i, h in enumerate(headers)) + " |"
    
    body = []
    for row in rows:
        body.append("| " + " | ".join(pad_str(str(v), col_widths[i]) for i, v in enumerate(row)) + " |")

    return "\n".join([line, header_str, line] + body + [line])