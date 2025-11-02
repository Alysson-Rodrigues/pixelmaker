"""Palette parsing helpers (pure logic, no PyQt imports).

Moved into `src` for better packaging.
"""

import re

HEX_REGEX = re.compile(r'#[0-9a-fA-F]{6}\b')


def parse_palette_line(text_line):
    """Extrai uma lista de códigos hexadecimais de uma string de texto.

    Args:
        text_line (str): Uma string como "#FF0000, #00FF00, #0000FF"

    Returns:
        list[str]: Uma lista de strings de cores, ex: ['#FF0000', '#00FF00', '#0000FF']
    """
    if not text_line:
        return []

    colors = HEX_REGEX.findall(text_line)

    return colors
