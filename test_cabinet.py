from cabinet import build, first_free_z

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
print("OK")
