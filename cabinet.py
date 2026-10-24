"""גיאומטריית הארון: הופכת מידות ורשימת רכיבים לרשימת לוחות (קופסאות) בס"מ.

צירים: x = רוחב (משמאל לימין), y = עומק (0 = חזית), z = גובה (0 = רצפה).
"""

BACK = 0.5  # עובי גב (סנדוויץ'/MDF דק)
GAP = 0.2   # מרווח סביב חזית מגירה
EPS = 1e-6  # רכיבים צמודים (25.8 מול 1.8+24) לא נחשבים התנגשות


def first_free_z(items, col, need, t, H):
    """הגובה הנמוך ביותר בעמודה שיש מעליו מקום פנוי בגובה need, או None אם אין."""
    spans = []
    for kind, c, z, h in items:
        try:
            if int(c) == col:
                spans.append((float(z), float(z) + (float(h) if kind == "מגירה" else t)))
        except (TypeError, ValueError):
            pass  # שורה חסרה; build כבר מדווח עליה
    z = t
    for a, b in sorted(s for s in spans if s[0] == s[0] and s[1] == s[1]):  # מדלג על NaN
        if a - z >= need - EPS:
            return round(z, 2)
        z = max(z, b)
    return round(z, 2) if z + need <= H - t + EPS else None


def box(name, kind, x0, x1, y0, y1, z0, z1):
    return {"name": name, "kind": kind, "x0": x0, "x1": x1, "y0": y0, "y1": y1, "z0": z0, "z1": z1}


def build(W, H, D, t, cols, items):
    """items: רשימת (סוג, עמודה, גובה_מהרצפה, גובה_מגירה). מחזיר (לוחות, שגיאות)."""
    w = (W - 2 * t - (cols - 1) * t) / cols  # רוחב פנימי של כל עמודה
    boxes = [
        box("דופן שמאל", "body", 0, t, 0, D, 0, H),
        box("דופן ימין", "body", W - t, W, 0, D, 0, H),
        box("תקרה", "body", t, W - t, 0, D, H - t, H),
        box("תחתית", "body", t, W - t, 0, D, 0, t),
        box("גב", "back", t, W - t, D - BACK, D, t, H - t),
    ]
    for i in range(1, cols):
        x = t + i * w + (i - 1) * t
        boxes.append(box(f"מחיצה {i}", "body", x, x + t, 0, D - BACK, t, H - t))

    errors, used = [], {}
    for row, (kind, col, z, h) in enumerate(items, start=1):
        try:
            col, z, h = int(col), float(z), float(h or 0)
            if z != z:  # NaN = תא ריק בטבלה
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"שורה {row}: חסרים נתונים — צריך למלא עמודה וגובה מהרצפה")
            continue
        if not 1 <= col <= cols:
            errors.append(f"שורה {row}: אין עמודה {col} (יש {cols})")
            continue
        top = z + (h if kind == "מגירה" else t)
        if kind == "מגירה" and not h > 0:
            errors.append(f"שורה {row}: למגירה חייב להיות גובה")
            continue
        if not (t <= z and top <= H - t):  # כולל NaN
            errors.append(f"שורה {row}: הרכיב יוצא מגבולות הארון ({t:g}–{H - t:g} ס\"מ)")
            continue
        clash = next((r for r, (a, b) in used.get(col, []) if z < b - EPS and a < top - EPS), None)
        if clash:
            errors.append(f"שורה {row}: מתנגש בשורה {clash}")
            continue
        used.setdefault(col, []).append((row, (z, top)))

        x0 = t + (col - 1) * (w + t)
        if kind == "מדף":
            boxes.append(box(f"מדף (שורה {row})", "shelf", x0, x0 + w, 0, D - BACK, z, z + t))
        else:
            boxes.append(box(f"חזית מגירה (שורה {row})", "drawer",
                             x0 + GAP, x0 + w - GAP, 0, t, z + GAP, z + h - GAP))
            mid_x, mid_z = x0 + w / 2, z + h - min(5, h / 2)
            boxes.append(box(f"ידית (שורה {row})", "handle",
                             mid_x - 6, mid_x + 6, -2.5, 0, mid_z - 0.6, mid_z + 0.6))
    return boxes, errors
