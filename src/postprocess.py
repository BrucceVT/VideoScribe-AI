import re
from typing import List


# 7+ repeticiones de un mismo signo -> lo reducimos
_PUNCT_RUN_RE = re.compile(r"([!¡?¿.,…])\1{6,}")

# Líneas que son casi solo signos / separadores
_ONLY_PUNCT_RE = re.compile(r"^[\W_]+$")

# Alargamientos tipo "su-u-u-u" o "sooooo"
_ELONG_HYPHEN_RE = re.compile(r"([aeiouáéíóú])(?:-\1){2,}", flags=re.IGNORECASE)  # su-u-u
_ELONG_REPEAT_RE = re.compile(r"([aeiouáéíóú])\1{5,}", flags=re.IGNORECASE)       # soooo


def _normalize_punct_runs(text: str) -> str:
    # "!!!!!!!!" -> "!!!"
    def repl(m: re.Match) -> str:
        ch = m.group(1)
        return ch * 3
    return _PUNCT_RUN_RE.sub(repl, text)


def _normalize_elongations(text: str) -> str:
    # su-u-u-u -> su...
    text = _ELONG_HYPHEN_RE.sub(r"\1...", text)
    # soooo -> so...
    text = _ELONG_REPEAT_RE.sub(r"\1...", text)
    return text


def _split_lines(text: str) -> List[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [ln.strip() for ln in text.split("\n")]


def _drop_garbage_lines(lines: List[str]) -> List[str]:
    cleaned = []
    for ln in lines:
        if not ln:
            cleaned.append("")
            continue

        # Línea de solo signos muy larga -> basura típica
        if _ONLY_PUNCT_RE.match(ln) and len(ln) >= 12:
            continue

        # Si casi no hay letras/números y es demasiado larga, también es basura
        alnum = re.sub(r"[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]+", "", ln)
        if len(alnum) <= 1 and len(ln) >= 25:
            continue

        cleaned.append(ln)
    return cleaned


def _limit_consecutive_repeats(lines: List[str], max_repeat: int) -> List[str]:
    """
    Limita repeticiones consecutivas EXACTAS de una línea.
    Importante: NO elimina coros que se repiten con separación o con variaciones.
    """
    out = []
    prev = None
    count = 0

    for ln in lines:
        if ln == "":
            # dejamos un salto suave, y reiniciamos conteo para NO matar estrofas repetidas separadas
            if out and out[-1] != "":
                out.append("")
            prev = None
            count = 0
            continue

        if ln == prev:
            count += 1
            if count < max_repeat:
                out.append(ln)
        else:
            prev = ln
            count = 0
            out.append(ln)

    return out


def postprocess_transcript(
    text: str,
    *,
    clean_text: bool = True,
    normalize_elongations: bool = False,
    max_consecutive_repeats: int = 4,
) -> str:
    if not text:
        return ""

    if clean_text:
        text = _normalize_punct_runs(text)

    if normalize_elongations:
        text = _normalize_elongations(text)

    lines = _split_lines(text)

    if clean_text:
        lines = _drop_garbage_lines(lines)

    # Esto es el “seguro” anti loop, sin matar coros normales
    lines = _limit_consecutive_repeats(lines, max_repeat=max_consecutive_repeats)

    out = "\n".join(lines)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out
