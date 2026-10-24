// תצוגת חזית של הארון עם גרירה. הפונקציה נקראת שוב על אותו parentElement בכל שינוי data,
// בלי ניקוי קודם, ולכן היא בונה הכול מחדש ומחברת אירועים כמאפיינים (onX) ולא כ-addEventListener.
const NS = "http://www.w3.org/2000/svg";
const GAP = 0.2, EPS = 1e-6, STEP = 0.5;
const ML = 46, MR = 14, MT = 26, MB = 28; // שוליים ב-viewBox: משמאל סרגל גובה, מלמטה קו רוחב
const HEX = /^#[0-9a-f]{3,8}$/i;
const DRAWER = "מגירה";

const fmt = (v) => String(Math.round(v * 10) / 10);
const snap = (z) => Math.round(z / STEP) * STEP;
const finite = (v) => typeof v === "number" && Number.isFinite(v);

function el(tag, attrs, parent) {
  const n = document.createElementNS(NS, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(n);
  return n;
}

export default function ({ data, parentElement, setTriggerValue }) {
  let root = parentElement.querySelector(".fv-root");
  if (!root) {
    root = document.createElement("div");
    root.className = "fv-root";
    parentElement.appendChild(root);
  }
  root._send = setTriggerValue;
  if (root._st && root._st.drag) return; // באמצע גרירה: לא מחליפים DOM מתחת לאצבע
  const items = (data.items || []).filter(
    (i) => Number.isInteger(i.index) && finite(i.col) && finite(i.z) && (i.type !== DRAWER || finite(i.h)),
  );
  root._st = { d: data, items: items.map((i) => ({ ...i })), sel: root._st ? root._st.sel : null, drag: null };
  render(root);
}

function render(root) {
  const st = root._st, { W, H, t, cols } = st.d;
  if (![W, H, t, cols].every(finite) || cols < 1) return;
  const col = {};
  for (const k of ["body", "back", "shelf", "drawer", "handle"]) {
    const c = st.d.colors && st.d.colors[k];
    col[k] = typeof c === "string" && HEX.test(c) ? c : "#c8a165";
  }
  const w = (W - 2 * t - (cols - 1) * t) / cols;
  const colX0 = (c) => t + (c - 1) * (w + t);
  const s = Math.min(6, 600 / H, 520 / W);
  const VW = ML + W * s + MR, VH = MT + H * s + MB;
  const X = (x) => ML + x * s, Y = (z) => MT + (H - z) * s;
  const ih = (it) => (it.type === DRAWER ? it.h : t);

  const clampTo = (it, c, z) => [
    Math.min(Math.max(Math.round(c), 1), cols),
    Math.min(Math.max(snap(z), t), Math.max(t, H - t - ih(it))),
  ];
  const clashes = (it, c, z) =>
    st.items.some((o) => o !== it && o.col === c && z < o.z + ih(o) - EPS && o.z < z + ih(it) - EPS);

  const a = root.getRootNode().activeElement;
  const focusIdx = a && root.contains(a) ? a.getAttribute("data-index") : null;

  const svg = el("svg", { viewBox: `0 0 ${VW} ${VH}`, role: "group", "aria-label": "חזית הארון" });
  const rect = (x0, x1, z0, z1, cls, fill) =>
    el("rect", { x: X(x0), y: Y(z1), width: (x1 - x0) * s, height: (z1 - z0) * s, class: cls, fill }, svg);

  rect(t, W - t, t, H - t, "back", col.back);
  for (let i = 1; i < cols; i++) rect(t + i * w + (i - 1) * t, t + i * w + i * t, t, H - t, "edge", col.body);
  rect(0, t, 0, H, "edge", col.body);
  rect(W - t, W, 0, H, "edge", col.body);
  rect(t, W - t, H - t, H, "edge", col.body);
  rect(t, W - t, 0, t, "edge", col.body);

  // סרגל גובה: סימון כל 10 ס"מ, מספר כל 50
  const rule = el("g", { class: "rule" }, svg);
  el("line", { x1: ML - 8, x2: ML - 8, y1: Y(0), y2: Y(H) }, rule);
  for (let v = 0; v <= H; v += 10) {
    const big = v % 50 === 0;
    el("line", { x1: ML - 8 - (big ? 6 : 3), x2: ML - 8, y1: Y(v), y2: Y(v) }, rule);
    if (big) el("text", { x: ML - 17, y: Y(v) }, rule).textContent = String(v);
  }
  el("text", { class: "dim", x: X(W / 2), y: VH - 8 }, svg).textContent = `${fmt(W)} ס"מ`;

  const place = (g, it, c, z) => {
    const x0 = colX0(c), h = ih(it), P = g._p;
    if (it.type === DRAWER) {
      P.body.setAttribute("x", X(x0 + GAP)); P.body.setAttribute("y", Y(z + h - GAP));
      P.body.setAttribute("width", (w - 2 * GAP) * s); P.body.setAttribute("height", (h - 2 * GAP) * s);
      const hz = z + h - Math.min(5, h / 2);
      P.handle.setAttribute("x", X(x0 + w / 2 - 6)); P.handle.setAttribute("y", Y(hz + 0.6));
      P.handle.setAttribute("width", 12 * s); P.handle.setAttribute("height", 1.2 * s);
    } else {
      P.body.setAttribute("x", X(x0)); P.body.setAttribute("y", Y(z + t));
      P.body.setAttribute("width", w * s); P.body.setAttribute("height", t * s);
    }
    const hh = Math.max(h * s, 16); // אזור לכידה נוח גם למדף דק
    P.hit.setAttribute("x", X(x0)); P.hit.setAttribute("width", w * s);
    P.hit.setAttribute("y", Y(z + h / 2) - hh / 2); P.hit.setAttribute("height", hh);
    P.del.setAttribute("transform", `translate(${X(x0 + w) - 12} ${Y(z + h / 2)})`);
    const bad = clashes(it, c, z);
    P.lab.setAttribute("x", X(x0 + w / 2)); P.lab.setAttribute("y", Y(z + h) - 6);
    P.lab.textContent = bad ? `מתנגש (${fmt(z)})` : fmt(z);
    g.classList.toggle("clash", bad);
    g.setAttribute("aria-label", `${it.type}, עמודה ${c}, גובה ${fmt(z)} ס"מ${bad ? ", מתנגש" : ""}`);
  };
  const select = (idx) => {
    st.sel = idx;
    svg.querySelectorAll(".item").forEach((n) => n.classList.toggle("sel", Number(n.getAttribute("data-index")) === idx));
  };
  const send = (kind, payload) => root._send && root._send(kind, payload);
  const colAt = (xcm) => Math.min(Math.max(Math.floor((xcm - t) / (w + t)) + 1, 1), cols);
  const toCm = (e) => {
    const p = svg.createSVGPoint();
    p.x = e.clientX; p.y = e.clientY;
    const q = p.matrixTransform(svg.getScreenCTM().inverse());
    return { x: (q.x - ML) / s, z: H - (q.y - MT) / s };
  };
  const removeItem = (it) => {
    send("delete", { index: it.index });
    st.items = st.items.filter((o) => o !== it);
    for (const o of st.items) if (o.index > it.index) o.index -= 1; // שורות אחרי המחוקה זזות
    st.sel = null;
    render(root);
  };

  for (const it of st.items) {
    const isD = it.type === DRAWER;
    const g = el("g", { class: "item", tabindex: "0", role: "button", "data-index": it.index }, svg);
    const hit = el("rect", { class: "hit" }, g);
    const body = el("rect", { class: "body", fill: isD ? col.drawer : col.shelf }, g);
    const handle = isD ? el("rect", { class: "handle", fill: col.handle }, g) : null;
    const del = el("g", { class: "del", role: "button", "aria-label": "מחיקת הרכיב" }, g);
    el("circle", { r: 8 }, del);
    el("text", {}, del).textContent = "×";
    const lab = el("text", { class: "lab" }, g);
    g._p = { hit, body, handle, del, lab };
    place(g, it, it.col, it.z);

    g.onfocus = () => select(it.index);
    g.onblur = (e) => { if (!st.rendering && !st.drag && !root.contains(e.relatedTarget)) select(null); };
    del.onpointerdown = (e) => { e.stopPropagation(); e.preventDefault(); };
    del.onclick = (e) => { e.stopPropagation(); removeItem(it); };

    g.onpointerdown = (e) => {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      e.preventDefault();
      e.stopPropagation(); // שלא יגיע לרקע (שמבטל בחירה)
      g.setPointerCapture(e.pointerId);
      g.focus({ preventScroll: true });
      select(it.index);
      st.drag = { id: e.pointerId, dz: toCm(e).z - it.z, col: it.col, z: it.z };
      g.classList.add("drag");
    };
    g.onpointermove = (e) => {
      const d = st.drag;
      if (!d || d.id !== e.pointerId) return;
      const p = toCm(e);
      [d.col, d.z] = clampTo(it, colAt(p.x), p.z - d.dz);
      place(g, it, d.col, d.z);
    };
    const finish = (e, commit) => {
      const d = st.drag;
      if (!d || d.id !== e.pointerId) return;
      st.drag = null;
      g.classList.remove("drag");
      if (commit && (d.col !== it.col || d.z !== it.z)) {
        it.col = d.col; it.z = d.z;
        send("move", { index: it.index, col: it.col, z: it.z });
        render(root);
      } else {
        place(g, it, it.col, it.z);
      }
    };
    g.onpointerup = (e) => finish(e, true);
    g.onpointercancel = (e) => finish(e, false);

    g.onkeydown = (e) => {
      const big = e.shiftKey ? 10 : 1; // 5 ס"מ עם Shift, אחרת 0.5
      let dc = 0, dz = 0;
      if (e.key === "ArrowUp") dz = STEP * big;
      else if (e.key === "ArrowDown") dz = -STEP * big;
      else if (e.key === "ArrowRight") dc = 1; // ימין במסך = עמודה גבוהה יותר (x גדל ימינה)
      else if (e.key === "ArrowLeft") dc = -1;
      else if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); removeItem(it); return; }
      else if (e.key === "Escape") { g.blur(); return; }
      else return;
      e.preventDefault();
      const [c, z] = clampTo(it, it.col + dc, it.z + dz);
      if (c === it.col && z === it.z) return;
      it.col = c; it.z = z;
      send("move", { index: it.index, col: c, z });
      render(root);
    };
  }

  svg.onpointerdown = () => select(null); // לחיצה על הרקע מבטלת בחירה
  st.rendering = true;
  root.replaceChildren(svg);
  st.rendering = false;
  select(st.sel);
  if (focusIdx !== null) {
    const f = svg.querySelector(`.item[data-index="${focusIdx}"]`);
    if (f) f.focus({ preventScroll: true });
  }
}
