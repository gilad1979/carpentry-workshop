from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py", default_timeout=30).run()
assert not at.exception, at.exception
assert not at.warning, [w.value for w in at.warning]  # ברירות המחדל תקינות
n = len(at.session_state["items_df"])

# הכפתור בסרגל הצדי; הרכיב של החזית מופיע כ-UnknownElement ולא ניתן לדמות בו גרירה (נבדק ב-test_cabinet)
next(b for b in at.sidebar.button if "הוסף" in b.label).click()
at.run()
assert not at.exception, at.exception
assert len(at.session_state["items_df"]) == n + 1, at.session_state["items_df"]
print("OK")
