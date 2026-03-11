"""Вспомогательные функции"""
# ✅ УДАЛИТЕ эту строку: from modules.utils import FONTS
# FONTS не нужен для работы wrap_text!

def wrap_text(text: str, max_chars: int = 20, max_lines: int = 2) -> list[str]:
    """
    Умный перенос текста с ограничением по символам и строкам.
    НЕ использует pygame/FONTS — работает только со строками.
    """
    if not text:
        return []

    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + word + " "
        if len(test.strip()) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current.strip())
            current = word + " "
            if len(lines) >= max_lines:
                break

    if current and len(lines) < max_lines:
        lines.append(current.strip())

    # Обрезаем и добавляем многоточие если нужно
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines and len(lines[-1]) > max_chars - 3:
            lines[-1] = lines[-1][:max_chars - 3] + "..."

    return lines