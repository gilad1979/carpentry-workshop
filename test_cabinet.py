from cabinet import apply_event, build, clamp_move, first_free_z

# ארון 100 רוחב, 2 עמודות, לוח 2 ס"מ: רוחב פנימי של עמודה = (100-4-2)/2 = 47
boxes, errors = build(100, 200, 60, 2, 2, [
    ("מדף", 1, 100, None),
    ("מגירה", 2, 2, 20),
    ("מדף", 2, 10, None),     # מתנגש במגירה
    ("מדף", 3, 50, None),     # אין עמודה 3
    ("מדף", 1, 199, None),    # מעל התקרה
    ("מגירה", 1, 50, None),   # מגירה בלי גובה
    ("מדף", None, 50, None),  # שורה חסרה
    ("מגירה", 1, float("nan"), 24),  # גובה ריק בטבלה
])
shelf = next(b for b in boxes if b["kind"] == "shelf")
assert (shelf["x0"], shelf["x1"]) == (2, 49), shelf
divider = next(b for b in boxes if b["name"] == "מחיצה 1")
assert (divider["x0"], divider["x1"]) == (49, 51), divider
assert sum(b["kind"] == "drawer" for b in boxes) == 1
assert [e.split(":")[0] for e in errors] == ["שורה 3", "שורה 4", "שורה 5", "שורה 6", "שורה 7", "שורה 8"], errors
assert "חסרים נתונים" in errors[-1], errors

# מקום פנוי ראשון: מגירות 2–26 ו-26–50 בעמודה 2 → הבאה ב-50; בעמודה 1 (מדף ב-100) מגירה של 24 נכנסת על התחתית
items = [("מגירה", 2, 2, 24), ("מגירה", 2, 26, 24), ("מדף", 1, 100, None), ("מדף", None, 5, None)]
assert first_free_z(items, 2, 24, 2, 200) == 50
assert first_free_z(items, 1, 24, 2, 200) == 2
assert first_free_z(items, 1, 99, 2, 200) is None  # 2–100 קצר מדי, ומעל המדף נשארו 96
# שלוש מגירות צמודות (גבולות עשרוניים) לא נחשבות התנגשות
_, errors = build(100, 200, 60, 1.8, 1, [("מגירה", 1, 1.8, 24), ("מגירה", 1, 25.8, 24), ("מגירה", 1, 49.8, 24)])
assert errors == [], errors

# גרירה: הצמדה ל-0.5, חיתוך לגבולות (מדף: 2–196, מגירה 24: 2–174), עמודה בטווח
nan, inf = float("nan"), float("inf")
assert clamp_move("מדף", 70.3, None, 2, 200, 2, 1) == (1, 70.5)
assert clamp_move("מדף", -5, None, 2, 200, 2, 1) == (1, 2)
assert clamp_move("מדף", 500, None, 2, 200, 2, 1) == (1, 196)
assert clamp_move("מגירה", 500, 24, 2, 200, 2, 2) == (2, 174)
assert clamp_move("מגירה", 10, 24, 2, 200, 2, 9) == (2, 10)
assert clamp_move("מגירה", 10, 24, 2, 200, 2, -3) == (1, 10)
for bad in (nan, inf, -inf, "5", None, True):
    assert clamp_move("מדף", bad, None, 2, 200, 2, 1) is None, bad
    assert clamp_move("מדף", 10, None, 2, 200, 2, bad) is None, bad
assert clamp_move("מגירה", 10, None, 2, 200, 2, 1) is None  # מגירה בלי גובה

rows = [("מדף", 1, 70.0, None), ("מגירה", 2, 2.0, 24.0), ("מדף", 2, 100.0, nan)]
assert apply_event(rows, "move", {"index": 1, "col": 1, "z": 50.2}, 2, 200, 2) ==     [rows[0], ("מגירה", 1, 50.0, 24.0), rows[2]]
assert apply_event(rows, "move", {"index": 1.0, "col": 2, "z": 999}, 2, 200, 2)[1] == ("מגירה", 2, 174.0, 24.0)
assert apply_event(rows, "delete", {"index": 0}, 2, 200, 2) == rows[1:]
assert rows[0] == ("מדף", 1, 70.0, None)  # הקלט לא משתנה
for bad_idx in (3, -1, True, 1.5, "1", None):
    assert apply_event(rows, "move", {"index": bad_idx, "col": 1, "z": 5}, 2, 200, 2) is None, bad_idx
    assert apply_event(rows, "delete", {"index": bad_idx}, 2, 200, 2) is None, bad_idx
assert apply_event(rows, "move", {"index": 0, "col": 1, "z": "5"}, 2, 200, 2) is None
assert apply_event(rows, "move", {"index": 0, "col": nan, "z": 5}, 2, 200, 2) is None
assert apply_event(rows, "move", {"index": 0}, 2, 200, 2) is None
assert apply_event(rows, "rename", {"index": 0}, 2, 200, 2) is None
assert apply_event(rows, "move", "oops", 2, 200, 2) is None
print("OK")
