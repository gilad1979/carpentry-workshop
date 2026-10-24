# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## כללי עבודה (גלעד, 24.10.2026)

1. **מודלים:** התכנון נעשה ב-Opus 5.5 (`claude-opus-5-5`), והביצוע (כתיבת הקוד) ב-Sonnet 5.5
   (`claude-sonnet-5-5`), דרך סוכן משנה עם `model: "sonnet"`.
2. **ענפים:** עובדים ב-`dev`, ומעבירים ל-`main` רק קוד שנבדק.
3. **בסוף כל שינוי קוד, בסדר הזה:**
   1. בדיקות לקוד החדש (להוסיף ל-`test_cabinet.py`).
   2. בדיקות רגרסיה: `python test_cabinet.py` כולו, ואז הבדיקה באפליקציה שבסעיף "Checking the app".
   3. בדיקת אבטחה עם הכישור `security-review`. מתקנים את מה שנמצא ומדווחים לגלעד.
   4. commit, ואז push.
4. **תיעוד:** בסוף העבודה מתעדים באובסידאן כל עדכון, בפתק
   `פרויקטים/מעצב ארונות/מעצב ארונות.md`, ביומן העדכונים.
   הכספת היא התיקייה שמעל המאגר (`AI Course`). כותבים לפתק דרך `mcp__obsidian__*`.

## What this is

A course exercise (not a real business tool): a Hebrew Streamlit app for designing a carpentry cabinet.
You set the cabinet size and number of columns, add shelves and drawers, pick colors, and see it in 3D (Plotly `Mesh3d`).

- `cabinet.py`: pure geometry. `build()` turns sizes + items into boxes (cm) and validation errors; `first_free_z()` finds the lowest free spot in a column. Axes: x = width, y = depth (0 = front), z = height (0 = floor).
- `app.py`: the Streamlit UI. Items live in `st.session_state.items_df`; the sidebar "add" button appends a row and resets the `data_editor` state (`items` key).
- `test_cabinet.py`: assert-based tests, prints `OK`.

## Running

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m streamlit run app.py
```

Opens at http://localhost:8501. `.claude/launch.json` has the same command for the preview pane (`cabinet-app`).

## Checking the app

1. `.venv/Scripts/python test_cabinet.py` prints `OK`.
2. Run the app and check in the browser: the 3D cabinet renders, no warnings with the default items, the sidebar "➕ הוסף" button stacks drawers in a column, and a color change updates the 3D view.

Gotchas:
- Streamlit reloads `app.py` on change but keeps an old `cabinet.py` in memory. After editing `cabinet.py`, restart the server.
- Streamlit "magic" prints bare expressions, also inside functions. Don't write expression statements like `a.append(x), b.append(y)`.
