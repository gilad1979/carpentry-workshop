"""תצוגת חזית אינטראקטיבית (גרירה) כרכיב Streamlit v2. ה-HTML/CSS/JS הם קבצים קבועים שלנו;
נתוני המשתמש עוברים רק כ-data (JSON)."""
import math
from pathlib import Path

import streamlit as st

_DIR = Path(__file__).parent
_component = st.components.v2.component(
    "front_view",
    html='<div class="fv-root"></div>',
    css=(_DIR / "front_view.css").read_text(encoding="utf-8"),
    js=(_DIR / "front_view.js").read_text(encoding="utf-8"),
)


def front_view(W, H, t, cols, rows, colors, key="front"):
    """מציג את החזית. מחזיר (סוג_אירוע, מטען) עבור "move"/"delete", או None.

    rows: (סוג, עמודה, גובה_מהרצפה, גובה_מגירה). שורות לא תקינות לא מצוירות,
    אבל ה-index נשאר האינדקס המקורי כדי שאירועים יחזרו לשורה הנכונה.
    """
    items = []
    for i, (kind, col, z, h) in enumerate(rows):
        try:
            col, z = int(col), float(z)
            h = float(h) if kind == "מגירה" else None
        except (TypeError, ValueError):
            continue
        if kind not in ("מדף", "מגירה") or not 1 <= col <= cols or not math.isfinite(z):
            continue
        if kind == "מגירה" and not (h is not None and math.isfinite(h) and h > 0):
            continue
        items.append({"index": i, "type": kind, "col": col, "z": z, "h": h})
    res = _component(
        key=key,
        data={"W": float(W), "H": float(H), "t": float(t), "cols": int(cols), "items": items, "colors": dict(colors)},
        on_move_change=lambda: None,
        on_delete_change=lambda: None,
    )
    for kind in ("move", "delete"):
        if res.get(kind) is not None:
            return kind, res[kind]
    return None
