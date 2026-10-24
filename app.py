import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from cabinet import build, first_free_z

COLORS = {"body": "#c8a165", "back": "#e3cfa6", "shelf": "#b8894a", "drawer": "#a0703a", "handle": "#444444"}
COLOR_LABELS = {"body": "גוף הארון", "back": "גב", "shelf": "מדפים", "drawer": "חזיתות מגירות", "handle": "ידיות"}
DEFAULT_ITEMS = pd.DataFrame({"סוג": ["מדף", "מדף", "מגירה", "מגירה"], "עמודה": [1, 1, 2, 2],
                              "גובה מהרצפה": [70.0, 140.0, 1.8, 26.0], "גובה מגירה": [None, None, 24.0, 24.0]})
# קודקודי קופסה: 0-3 תחתית, 4-7 עליון; 12 משולשים; 12 צלעות
TRI = [(0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
       (3, 2, 6), (3, 6, 7), (0, 3, 7), (0, 7, 4), (1, 2, 6), (1, 6, 5)]
EDGES = [0, 1, 2, 3, 0, 4, 5, 6, 7, 4, None, 1, 5, None, 2, 6, None, 3, 7]


def corners(b):
    return [(x, y, z) for z in (b["z0"], b["z1"])
            for x, y in ((b["x0"], b["y0"]), (b["x1"], b["y0"]), (b["x1"], b["y1"]), (b["x0"], b["y1"]))]


def figure(boxes, colors):
    fig = go.Figure()
    for kind, color in colors.items():
        xs, ys, zs, ii, jj, kk, names = [], [], [], [], [], [], []
        for b in (b for b in boxes if b["kind"] == kind):
            n = len(xs)
            c = corners(b)
            xs += [p[0] for p in c]
            ys += [p[1] for p in c]
            zs += [p[2] for p in c]
            names += [b["name"]] * 8
            ii += [n + i for i, _, _ in TRI]
            jj += [n + j for _, j, _ in TRI]
            kk += [n + k for _, _, k in TRI]
        if xs:
            fig.add_trace(go.Mesh3d(x=xs, y=ys, z=zs, i=ii, j=jj, k=kk, color=color, flatshading=True,
                                    hovertext=names, hoverinfo="text", showlegend=False))
    ex, ey, ez = [], [], []
    for b in boxes:
        c = corners(b)
        pts = [c[e] if e is not None else (None, None, None) for e in EDGES + [None]]
        ex += [p[0] for p in pts]
        ey += [p[1] for p in pts]
        ez += [p[2] for p in pts]
    fig.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode="lines", line=dict(color="#3b2a17", width=2),
                               hoverinfo="skip", showlegend=False))
    fig.update_layout(
        height=700, margin=dict(l=0, r=0, t=0, b=0), uirevision="keep",  # שומר זווית סיבוב בין עדכונים
        scene=dict(aspectmode="data", xaxis_title="רוחב", yaxis_title="עומק", zaxis_title="גובה",
                   camera=dict(eye=dict(x=1.3, y=-2.3, z=1.0))),  # מבט מהחזית (y=0)
    )
    return fig


st.set_page_config(page_title="מעצב ארונות", layout="wide")
st.title("מעצב ארונות")

with st.sidebar:
    st.header("מידות (ס\"מ)")
    W = st.number_input("רוחב", 30.0, 400.0, 100.0, 1.0)
    H = st.number_input("גובה", 30.0, 300.0, 200.0, 1.0)
    D = st.number_input("עומק", 20.0, 100.0, 60.0, 1.0)
    t = st.number_input("עובי לוח", 0.8, 5.0, 1.8, 0.1)
    cols = st.number_input("מספר עמודות", 1, 8, 2)

if "items_df" not in st.session_state:
    st.session_state.items_df = DEFAULT_ITEMS

left, right = st.columns([1, 1.1])
with left:
    st.subheader("מדפים ומגירות")
    st.caption("גובה מהרצפה = תחתית הרכיב. אפשר לשנות כל תא. למחיקה: לסמן שורה בעמודה השמאלית ולמחוק. "
               "להוספה נוחה: \"הוספת מדף או מגירה\" בצד.")
    items = st.data_editor(
        st.session_state.items_df, key="items", num_rows="dynamic", width="stretch",
        column_config={  # ברירות מחדל כדי ששורה חדשה לא תתחיל ריקה
            "סוג": st.column_config.SelectboxColumn(options=["מדף", "מגירה"], required=True, default="מגירה"),
            "עמודה": st.column_config.NumberColumn(min_value=1, step=1, default=1),
            "גובה מהרצפה": st.column_config.NumberColumn(min_value=0.0, step=0.5, format="%.1f"),
            "גובה מגירה": st.column_config.NumberColumn(min_value=0.0, step=0.5, format="%.1f", default=24.0,
                                                        help="רק למגירות"),
        },
    )
    rows = list(items.itertuples(index=False))
    boxes, errors = build(W, H, D, t, int(cols), rows)
    for e in errors:
        st.warning(e)

with st.sidebar:
    st.header("הוספת מדף או מגירה")
    kind = st.radio("סוג", ["מגירה", "מדף"], horizontal=True)
    col = st.selectbox("עמודה", range(1, int(cols) + 1))
    dh = st.number_input("גובה מגירה", 5.0, 100.0, 24.0, 0.5) if kind == "מגירה" else None
    free = first_free_z(rows, col, dh or t, t, H)
    # key משתנה כשהמקום הפנוי או מספר השורות משתנים, כדי שהשדה יתמלא מחדש אחרי כל הוספה
    z = st.number_input("מיקום — גובה מהרצפה", 0.0, float(H), free if free is not None else t, 0.5,
                        key=f"pos_{free}_{len(rows)}",
                        help="ממולא אוטומטית במקום הפנוי הראשון מלמטה. אפשר לשנות לכל גובה.")
    if free is None:
        st.caption("אין מקום פנוי בעמודה הזאת לרכיב בגובה הזה.")
    if st.button("➕ הוסף", width="stretch"):
        new = {"סוג": kind, "עמודה": col, "גובה מהרצפה": z, "גובה מגירה": dh}
        st.session_state.items_df = pd.concat([items, pd.DataFrame([new])], ignore_index=True)
        st.session_state.pop("items", None)  # העריכות כבר בתוך items_df; מאפס את מצב הטבלה
        st.rerun()

    st.header("צבעים")
    colors = {k: st.color_picker(COLOR_LABELS[k], v) for k, v in COLORS.items()}

with right:
    st.plotly_chart(figure(boxes, colors), width="stretch")
