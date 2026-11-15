"""Apply French spacing to text, never to markup, code or URLs."""

import re


def french(text):
    text = re.sub(r'[ \u00a0\u202f]*([;!?%])', '\u202f' + r'\1', text)
    text = re.sub(r'(?<!https)(?<!http)[ \u00a0\u202f]*:(?!/)', '\u00a0:', text)
    text = re.sub(r'«[ \u00a0\u202f]*', '«\u00a0', text)
    return re.sub(r'[ \u00a0\u202f]*»', '\u00a0»', text)
