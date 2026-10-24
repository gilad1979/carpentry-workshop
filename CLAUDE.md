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

A course exercise (not a real business tool): a Hebrew, right-to-left Streamlit app ("הנגריה") for designing a carpentry cabinet.
You set the cabinet size and number of columns, add shelves and drawers, pick colors, drag items in a 2D front view, and see the cabinet in 3D (Plotly `Mesh3d`).

- `cabinet.py`: pure geometry and event logic. `build()` turns sizes + items into boxes (cm) and validation errors; `first_free_z()` finds the lowest free spot in a column; `clamp_move()` and `apply_event()` validate and apply move/delete events coming from the browser (untrusted input). Axes: x = width, y = depth (0 = front), z = height (0 = floor).
- `app.py`: the Streamlit UI. Items live in `st.session_state.items_df`; the sidebar "add" button and front-view events rebuild that DataFrame and reset the `data_editor` state (`items` key). The precise-edit table sits in an expander; layout containers are created first and filled after the table is read.
- `front_view.py` + `front_view.js` + `front_view.css`: the draggable front view, a `st.components.v2` component (isolated styles, JS is re-run on the same element when data changes, so it rebuilds the DOM and uses `onX` properties). It sends `move`/`delete` triggers. The files are read at import, so restart the server after editing them.
- `.streamlit/config.toml`: warm light theme and Google Fonts (Secular One, IBM Plex Sans Hebrew). `assets/`: logo and icon.
- `test_cabinet.py`: assert-based tests of `cabinet.py`, prints `OK`. `test_app.py`: AppTest smoke test (app loads, "add" button adds a row), prints `OK`.

## Running

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m streamlit run app.py
```

Opens at http://localhost:8501. `.claude/launch.json` has the same command for the preview pane (`cabinet-app`).

## Checking the app

1. `.venv/Scripts/python test_cabinet.py` and `.venv/Scripts/python test_app.py` both print `OK`.
2. Run the app and check in the browser: the logo shows, the layout is right-to-left, the front view and the 3D cabinet render, no warnings with the default items.
3. Drag a drawer in the front view up and to the other column: the 3D view and the table update. Arrow keys move the focused item, Delete removes it, and dropping onto another item shows a red outline plus a warning. The sidebar "➕ הוסף" button and a color change still work.

AppTest cannot fire the component's triggers, so event handling is tested through `apply_event` directly.

Gotchas:
- Streamlit reloads `app.py` on change but keeps an old `cabinet.py` in memory. After editing `cabinet.py`, restart the server.
- Streamlit "magic" prints bare expressions, also inside functions. Don't write expression statements like `a.append(x), b.append(y)`.
