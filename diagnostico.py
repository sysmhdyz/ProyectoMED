import tkinter as tk
from tkinter import messagebox, ttk
import db
from motor_inferencia import diagnosticar

# ── PALETA ───────────────────────────────────────────
COLOR_BG      = "#f0f4f8"
COLOR_WHITE   = "#ffffff"
COLOR_ACCENT  = "#2c7be5"
COLOR_TEXT    = "#2d3748"
COLOR_SUBTEXT = "#718096"
COLOR_GREEN   = "#17a589"
COLOR_YELLOW  = "#e67e22"
COLOR_RED     = "#e74c3c"
COLOR_PURPLE  = "#8e44ad"

FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_BODY  = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_BTN   = ("Segoe UI", 11, "bold")

COLORES_LINEA = [
    "#2c7be5","#17a589","#e74c3c","#f39c12",
    "#8e44ad","#1abc9c","#e67e22","#3498db",
]


# ═══════════════════════════════════════════════════
# HELPER: GRÁFICA DE LÍNEAS EN CANVAS PURO
# ═══════════════════════════════════════════════════
def _dibujar_lineas(canvas, series: dict, titulo: str):
    """
    series = { "nombre_serie": [(fecha_str, valor), ...], ... }
    """
    canvas.delete("all")
    canvas.update_idletasks()
    W = canvas.winfo_width()  or 680
    H = canvas.winfo_height() or 320
    if W < 120: W = 680
    if H < 100: H = 320

    ML, MR, MT, MB = 54, 30, 30, 70

    # Recopilar todos los puntos
    all_dates = sorted(set(
        d for pts in series.values() for d, _ in pts
    ))
    all_vals  = [v for pts in series.values() for _, v in pts]

    if not all_dates or not all_vals:
        canvas.create_text(W//2, H//2,
                           text="No hay datos suficientes para graficar.",
                           font=("Segoe UI", 10), fill=COLOR_SUBTEXT)
        return

    max_val = max(all_vals) or 1
    n_dates = len(all_dates)

    area_w = W - ML - MR
    area_h = H - MT - MB

    # Fondo
    canvas.create_rectangle(ML, MT, W - MR, H - MB, fill="#f8fafc", outline="#e2e8f0")

    # Guías horizontales
    pasos = 4
    for i in range(pasos + 1):
        y   = MT + area_h * (1 - i / pasos)
        val = round(max_val * i / pasos)
        canvas.create_line(ML, y, W - MR, y, fill="#e2e8f0", dash=(4, 3))
        canvas.create_text(ML - 6, y, text=f"{val}%",
                           font=("Segoe UI", 8), fill=COLOR_SUBTEXT, anchor="e")

    # Ejes
    canvas.create_line(ML, MT, ML, H - MB, fill="#94a3b8", width=2)
    canvas.create_line(ML, H - MB, W - MR, H - MB, fill="#94a3b8", width=2)

    # Etiquetas de eje X (fechas)
    for idx, d in enumerate(all_dates):
        x = ML + idx * area_w / max(n_dates - 1, 1) if n_dates > 1 else ML + area_w / 2
        canvas.create_line(x, H - MB, x, H - MB + 4, fill="#94a3b8")
        label = d[5:] if len(d) == 10 else d   # muestra MM-DD
        canvas.create_text(x, H - MB + 14, text=label,
                           font=("Segoe UI", 7), fill=COLOR_SUBTEXT, angle=30)

    # Serie de datos
    date_idx = {d: i for i, d in enumerate(all_dates)}
    for s_idx, (nombre, puntos) in enumerate(series.items()):
        if not puntos:
            continue
        color = COLORES_LINEA[s_idx % len(COLORES_LINEA)]
        pts_ordenados = sorted(puntos, key=lambda x: x[0])

        coords = []
        for d, v in pts_ordenados:
            xi = date_idx[d]
            x  = ML + xi * area_w / max(n_dates - 1, 1) if n_dates > 1 else ML + area_w / 2
            y  = MT + area_h * (1 - v / max_val)
            coords.append((x, y))

        # Línea con suavizado (segmentos)
        if len(coords) >= 2:
            for i in range(len(coords) - 1):
                x0, y0 = coords[i]
                x1, y1 = coords[i + 1]
                # Sombra
                canvas.create_line(x0+1, y0+1, x1+1, y1+1,
                                   fill="#d4dbe6", width=2, smooth=True)
                # Línea
                canvas.create_line(x0, y0, x1, y1,
                                   fill=color, width=2.5, smooth=True)

        # Puntos
        for x, y in coords:
            canvas.create_oval(x-5, y-5, x+5, y+5, fill=COLOR_WHITE, outline=color, width=2)
            canvas.create_oval(x-2, y-2, x+2, y+2, fill=color, outline="")

    # Leyenda
    leyenda_x = ML + 10
    leyenda_y = MT + 8
    for s_idx, nombre in enumerate(series.keys()):
        color = COLORES_LINEA[s_idx % len(COLORES_LINEA)]
        canvas.create_rectangle(leyenda_x, leyenda_y, leyenda_x + 20, leyenda_y + 10,
                                 fill=color, outline="")
        lbl = nombre if len(nombre) <= 22 else nombre[:21] + "…"
        canvas.create_text(leyenda_x + 26, leyenda_y + 5, text=lbl,
                           font=("Segoe UI", 8), fill=COLOR_TEXT, anchor="w")
        leyenda_x += max(160, len(lbl) * 7 + 36)
        if leyenda_x > W - MR - 100:
            leyenda_x = ML + 10
            leyenda_y += 18


# ═══════════════════════════════════════════════════
# VENTANA ANALÍTICA – HISTORIAL DE DIAGNÓSTICOS
# ═══════════════════════════════════════════════════
def ventana_analitica(parent=None):
    db.cargar_todo()
    hist = db.historial

    win = tk.Toplevel(parent)
    win.title("📈 Analítica de Diagnósticos")
    win.geometry("950x680")
    win.configure(bg=COLOR_BG)
    win.resizable(True, True)

    header = tk.Frame(win, bg=COLOR_WHITE, height=52)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="📈  Analítica y Histórico de Diagnósticos",
             font=FONT_TITLE, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(side="left", padx=24, pady=12)

    if not hist:
        tk.Label(win, text="📭\n\nNo hay diagnósticos registrados aún.\nGenera un diagnóstico para ver la analítica.",
                 font=("Segoe UI", 13), bg=COLOR_BG, fg=COLOR_SUBTEXT,
                 justify="center").pack(expand=True)
        return

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=16, pady=12)

    tab_evo   = tk.Frame(notebook, bg=COLOR_BG)
    tab_sint  = tk.Frame(notebook, bg=COLOR_BG)
    tab_paciente = tk.Frame(notebook, bg=COLOR_BG)
    notebook.add(tab_evo,      text="  Evolución por Enfermedad  ")
    notebook.add(tab_sint,     text="  Síntomas vs Diagnóstico  ")
    notebook.add(tab_paciente, text="  Historial por Paciente  ")

    # ══════════════════════════════════════════
    # TAB 1 – Gráfica de líneas: prob. promedio
    # por enfermedad a lo largo del tiempo
    # ══════════════════════════════════════════
    wrap1 = tk.Frame(tab_evo, bg=COLOR_WHITE)
    wrap1.pack(fill="both", expand=True, padx=20, pady=16)
    tk.Label(wrap1, text="Probabilidad promedio por enfermedad en el tiempo",
             font=("Segoe UI", 12, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT).pack(pady=(12, 4))
    tk.Label(wrap1, text="Cada punto representa el promedio de probabilidad de esa enfermedad en esa fecha.",
             font=("Segoe UI", 8), bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack()

    cvs1 = tk.Canvas(wrap1, bg=COLOR_WHITE, highlightthickness=0, height=320)
    cvs1.pack(fill="both", expand=True, padx=16, pady=(6, 10))

    # Construir series: enfermedad → [(fecha, prob_promedio_dia)]
    from collections import defaultdict
    enf_fechas = defaultdict(lambda: defaultdict(list))
    for h in hist:
        enf_fechas[h["enfermedad"]][h["fecha"]].append(h["probabilidad"])

    series_evo = {}
    for enf, fechas in enf_fechas.items():
        series_evo[enf] = [(f, round(sum(vs)/len(vs), 1)) for f, vs in sorted(fechas.items())]

    wrap1.update_idletasks()
    _dibujar_lineas(cvs1, series_evo, "")
    cvs1.bind("<Configure>", lambda e: _dibujar_lineas(cvs1, series_evo, ""))

    # ══════════════════════════════════════════
    # TAB 2 – Síntomas usados vs enfermedad diagnosticada
    # ══════════════════════════════════════════
    wrap2 = tk.Frame(tab_sint, bg=COLOR_BG)
    wrap2.pack(fill="both", expand=True, padx=16, pady=12)

    tk.Label(wrap2, text="Síntomas registrados por diagnóstico",
             font=("Segoe UI", 12, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w", pady=(0, 6))
    tk.Label(wrap2,
             text="Tabla de todos los diagnósticos con los síntomas usados y la enfermedad resultante.",
             font=("Segoe UI", 8), bg=COLOR_BG, fg=COLOR_SUBTEXT).pack(anchor="w", pady=(0, 8))

    frame_tbl = tk.Frame(wrap2, bg=COLOR_BG)
    frame_tbl.pack(fill="both", expand=True)

    sb2y = ttk.Scrollbar(frame_tbl, orient="vertical")
    sb2y.pack(side="right", fill="y")
    sb2x = ttk.Scrollbar(frame_tbl, orient="horizontal")
    sb2x.pack(side="bottom", fill="x")

    cols2 = ("Fecha", "Paciente", "Enfermedad", "Probabilidad", "Síntomas utilizados")
    style = ttk.Style()
    style.configure("Diag.Treeview.Heading", font=("Segoe UI", 9, "bold"))
    style.configure("Diag.Treeview", font=FONT_SMALL, rowheight=28)

    tbl2 = ttk.Treeview(frame_tbl, columns=cols2, show="headings",
                          yscrollcommand=sb2y.set, xscrollcommand=sb2x.set,
                          style="Diag.Treeview")
    w2 = {"Fecha": 90, "Paciente": 130, "Enfermedad": 140, "Probabilidad": 90, "Síntomas utilizados": 360}
    for c in cols2:
        tbl2.heading(c, text=c)
        tbl2.column(c, width=w2[c], anchor="center" if c == "Probabilidad" else "w")
    tbl2.pack(side="left", fill="both", expand=True)
    sb2y.config(command=tbl2.yview)
    sb2x.config(command=tbl2.xview)

    # Colores alternos por nivel de probabilidad
    tbl2.tag_configure("alta",   background="#fef2f2")
    tbl2.tag_configure("media",  background="#fffbeb")
    tbl2.tag_configure("baja",   background="#f0fdf4")

    for h in sorted(hist, key=lambda x: x["fecha"], reverse=True):
        prob = h["probabilidad"]
        tag  = "alta" if prob >= 70 else "media" if prob >= 40 else "baja"
        sint = h.get("sintomas_usados", "") or "—"
        tbl2.insert("", "end",
                    values=(h["fecha"], h["paciente"], h["enfermedad"],
                            f"{prob}%", sint),
                    tags=(tag,))

    # ══════════════════════════════════════════
    # TAB 3 – Historial por paciente con línea
    # ══════════════════════════════════════════
    wrap3 = tk.Frame(tab_paciente, bg=COLOR_BG)
    wrap3.pack(fill="both", expand=True, padx=16, pady=12)

    top3 = tk.Frame(wrap3, bg=COLOR_BG)
    top3.pack(fill="x", pady=(0, 8))
    tk.Label(top3, text="Paciente:", font=FONT_BOLD,
             bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left")

    pac_var3 = tk.StringVar()
    nombres_pac = sorted(set(h["paciente"] for h in hist))
    combo_pac3  = ttk.Combobox(top3, textvariable=pac_var3,
                                values=nombres_pac, state="readonly",
                                font=FONT_BODY, width=24)
    combo_pac3.pack(side="left", padx=(8, 0), ipady=4)

    grafica_frame3 = tk.Frame(wrap3, bg=COLOR_WHITE)
    grafica_frame3.pack(fill="both", expand=True, pady=(0, 6))
    tk.Frame(grafica_frame3, bg=COLOR_PURPLE, height=3).pack(fill="x")

    tk.Label(grafica_frame3,
             text="Evolución de probabilidad por enfermedad para el paciente seleccionado",
             font=("Segoe UI", 9), bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(pady=(6, 2))

    cvs3 = tk.Canvas(grafica_frame3, bg=COLOR_WHITE, highlightthickness=0, height=280)
    cvs3.pack(fill="both", expand=True, padx=16, pady=(0, 10))

    def actualizar_grafica_paciente(*_):
        pac = pac_var3.get()
        datos_pac = [h for h in hist if h["paciente"] == pac]
        enf_fechas_pac = defaultdict(lambda: defaultdict(list))
        for h in datos_pac:
            enf_fechas_pac[h["enfermedad"]][h["fecha"]].append(h["probabilidad"])
        series_pac = {}
        for enf, fechas in enf_fechas_pac.items():
            series_pac[enf] = [(f, round(sum(vs)/len(vs),1)) for f, vs in sorted(fechas.items())]
        _dibujar_lineas(cvs3, series_pac, "")

    pac_var3.trace_add("write", actualizar_grafica_paciente)
    cvs3.bind("<Configure>", lambda e: actualizar_grafica_paciente())
    if nombres_pac:
        combo_pac3.current(0)
        actualizar_grafica_paciente()

    win.mainloop()


# ═══════════════════════════════════════════════════
# VENTANA PRINCIPAL DE DIAGNÓSTICO
# ═══════════════════════════════════════════════════
def ventana_diagnostico():
    win = tk.Toplevel()
    win.title("Diagnóstico Médico")
    win.geometry("920x660")
    win.configure(bg=COLOR_BG)
    win.resizable(True, True)

    # ── HEADER ──────────────────────────────────
    header = tk.Frame(win, bg=COLOR_WHITE, height=52)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="🧠  Diagnóstico Médico por Síntomas",
             font=FONT_TITLE, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(side="left", padx=20, pady=12)
    tk.Button(header, text="📈 Histórico / Analítica",
              command=lambda: ventana_analitica(win),
              bg=COLOR_PURPLE, fg=COLOR_WHITE, font=("Segoe UI", 9, "bold"),
              relief="flat", padx=12, pady=5, cursor="hand2").pack(side="right", padx=16, pady=10)

    # ── LAYOUT ──────────────────────────────────
    body = tk.Frame(win, bg=COLOR_BG)
    body.pack(fill="both", expand=True, padx=16, pady=12)

    left  = tk.Frame(body, bg=COLOR_BG, width=360)
    right = tk.Frame(body, bg=COLOR_BG)
    left.pack(side="left", fill="both", padx=(0, 8))
    left.pack_propagate(False)
    right.pack(side="right", fill="both", expand=True, padx=(8, 0))

    # ── PACIENTE ─────────────────────────────────
    pac_card = tk.Frame(left, bg=COLOR_WHITE)
    pac_card.pack(fill="x", pady=(0, 8))
    tk.Frame(pac_card, bg=COLOR_ACCENT, height=3).pack(fill="x")
    tk.Label(pac_card, text="Paciente", font=FONT_SMALL,
             bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x", padx=14, pady=(10, 2))

    db.cargar_todo()
    paciente_var = tk.StringVar()
    combo_pac = ttk.Combobox(pac_card, textvariable=paciente_var,
                              state="readonly", font=FONT_BODY)
    combo_pac["values"] = [p["nombre"] for p in db.pacientes]
    combo_pac.pack(fill="x", padx=14, pady=(0, 12), ipady=4)

    # ── PANEL DE SÍNTOMAS – lista plana, sin agrupar ─
    sint_outer = tk.Frame(left, bg=COLOR_WHITE)
    sint_outer.pack(fill="both", expand=True)
    tk.Frame(sint_outer, bg=COLOR_GREEN, height=3).pack(fill="x")

    header_sint = tk.Frame(sint_outer, bg=COLOR_WHITE)
    header_sint.pack(fill="x", padx=14, pady=(10, 2))
    tk.Label(header_sint, text="Síntomas del paciente",
             font=FONT_BOLD, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(side="left")

    # Buscador
    buscar_var = tk.StringVar()
    buscar_entry = tk.Entry(header_sint, textvariable=buscar_var,
                            font=FONT_SMALL, relief="solid", bd=1, width=14)
    buscar_entry.pack(side="right")
    tk.Label(header_sint, text="🔍", font=FONT_SMALL,
             bg=COLOR_WHITE).pack(side="right", padx=(0, 2))

    tk.Label(sint_outer,
             text="Marca los síntomas presentes — el sistema buscará la enfermedad más probable.",
             font=("Segoe UI", 8), bg=COLOR_WHITE, fg=COLOR_SUBTEXT,
             wraplength=330, justify="left", anchor="w").pack(fill="x", padx=14, pady=(0, 6))

    # Botones seleccionar todos / limpiar
    btn_sel_frame = tk.Frame(sint_outer, bg=COLOR_WHITE)
    btn_sel_frame.pack(fill="x", padx=14, pady=(0, 4))

    canvas = tk.Canvas(sint_outer, bg=COLOR_WHITE, highlightthickness=0)
    sb = ttk.Scrollbar(sint_outer, orient="vertical", command=canvas.yview)
    check_frame = tk.Frame(canvas, bg=COLOR_WHITE)
    check_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=check_frame, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True, padx=(14, 0), pady=(0, 14))
    sb.pack(side="right", fill="y", pady=(0, 14))
    canvas.bind_all("<MouseWheel>",
        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    check_vars = {}   # nombre_sintoma → BooleanVar

    def cargar_checkboxes(filtro=""):
        for w in check_frame.winfo_children():
            w.destroy()
        check_vars.clear()

        db.cargar_todo()
        # Obtener todos los síntomas únicos del catálogo
        todos = db.get_catalogo_sintomas()
        if filtro:
            todos = [s for s in todos if filtro.lower() in s["nombre"].lower()]

        if not todos:
            tk.Label(check_frame,
                     text="No hay síntomas en el catálogo." if not filtro
                          else "Ningún síntoma coincide con la búsqueda.",
                     font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT
                     ).pack(anchor="w", padx=4, pady=8)
            return

        # Letras separadoras A–Z
        letra_actual = ""
        for s in todos:
            primera = s["nombre"][0].upper()
            if primera != letra_actual:
                letra_actual = primera
                sep = tk.Frame(check_frame, bg=COLOR_BG)
                sep.pack(fill="x", pady=(6, 1))
                tk.Label(sep, text=f" {primera} ", font=("Segoe UI", 8, "bold"),
                         bg="#e2e8f0", fg=COLOR_SUBTEXT).pack(side="left")
                tk.Frame(sep, bg="#e2e8f0", height=1).pack(side="left", fill="x", expand=True)

            var = tk.BooleanVar()
            check_vars[s["nombre"]] = var

            row = tk.Frame(check_frame, bg=COLOR_WHITE)
            row.pack(fill="x")
            tk.Checkbutton(
                row, text=f"  {s['nombre']}",
                variable=var, bg=COLOR_WHITE,
                font=FONT_SMALL, fg=COLOR_TEXT,
                activebackground=COLOR_WHITE, anchor="w",
                selectcolor="#dbeafe"
            ).pack(side="left", fill="x", pady=1)

    def seleccionar_todos():
        for v in check_vars.values():
            v.set(True)

    def limpiar_todos():
        for v in check_vars.values():
            v.set(False)

    tk.Button(btn_sel_frame, text="☑ Todos", command=seleccionar_todos,
              bg="#e2e8f0", fg=COLOR_TEXT, font=("Segoe UI", 8),
              relief="flat", padx=6, pady=2, cursor="hand2").pack(side="left", padx=(0, 4))
    tk.Button(btn_sel_frame, text="✕ Limpiar", command=limpiar_todos,
              bg="#fff0f0", fg=COLOR_RED, font=("Segoe UI", 8),
              relief="flat", padx=6, pady=2, cursor="hand2").pack(side="left")

    cargar_checkboxes()
    buscar_var.trace_add("write", lambda *_: cargar_checkboxes(buscar_var.get()))

    # ── PANEL DERECHO – RESULTADOS ────────────────
    res_card = tk.Frame(right, bg=COLOR_WHITE)
    res_card.pack(fill="both", expand=True)
    tk.Frame(res_card, bg=COLOR_YELLOW, height=3).pack(fill="x")
    tk.Label(res_card, text="Resultados del diagnóstico",
             font=FONT_BOLD, bg=COLOR_WHITE, fg=COLOR_TEXT, anchor="w").pack(fill="x", padx=14, pady=(10, 4))

    res_canvas = tk.Canvas(res_card, bg=COLOR_WHITE, highlightthickness=0)
    res_sb = ttk.Scrollbar(res_card, orient="vertical", command=res_canvas.yview)
    res_inner = tk.Frame(res_canvas, bg=COLOR_WHITE)
    res_inner.bind("<Configure>",
        lambda e: res_canvas.configure(scrollregion=res_canvas.bbox("all")))
    res_canvas.create_window((0, 0), window=res_inner, anchor="nw")
    res_canvas.configure(yscrollcommand=res_sb.set)
    res_canvas.pack(side="left", fill="both", expand=True, padx=14, pady=(0, 14))
    res_sb.pack(side="right", fill="y", pady=(0, 14))

    placeholder = tk.Label(res_inner,
        text="🩺\n\nSelecciona síntomas y presiona\n'Generar Diagnóstico'",
        font=("Segoe UI", 11), bg=COLOR_WHITE, fg="#cbd5e0", justify="center")
    placeholder.pack(expand=True, pady=60)

    # ── FUNCIÓN DIAGNÓSTICO ──────────────────────
    def generar():
        paciente = paciente_var.get()
        if not paciente:
            messagebox.showerror("Error", "Selecciona un paciente.", parent=win)
            return

        sintomas_sel = [nombre for nombre, var in check_vars.items() if var.get()]
        if not sintomas_sel:
            messagebox.showerror("Error", "Marca al menos un síntoma.", parent=win)
            return

        resultados = diagnosticar(sintomas_sel)

        for w in res_inner.winfo_children():
            w.destroy()

        if not resultados:
            tk.Label(res_inner,
                     text="⚠️  Sin coincidencias\n\nNinguna enfermedad coincide\ncon los síntomas seleccionados.\n\nVerifica que las enfermedades\ntengan síntomas registrados.",
                     font=FONT_BODY, bg=COLOR_WHITE, fg=COLOR_SUBTEXT,
                     justify="center").pack(pady=40)
            return

        # Guardar diagnóstico (con síntomas usados)
        mejor = resultados[0]
        db.agregar_diagnostico(paciente, mejor["enfermedad"],
                                mejor["probabilidad"], sintomas_sel)

        # Cabecera del resultado
        info = tk.Frame(res_inner, bg="#f0f7ff")
        info.pack(fill="x", pady=(4, 10), padx=4)
        tk.Frame(info, bg=COLOR_ACCENT, width=4).pack(side="left", fill="y")
        inner_i = tk.Frame(info, bg="#f0f7ff")
        inner_i.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        tk.Label(inner_i, text=f"Paciente: {paciente}",
                 font=FONT_BOLD, bg="#f0f7ff", fg=COLOR_TEXT).pack(anchor="w")
        tk.Label(inner_i,
                 text=f"Síntomas evaluados: {len(sintomas_sel)}  •  Enfermedades posibles: {len(resultados)}",
                 font=FONT_SMALL, bg="#f0f7ff", fg=COLOR_SUBTEXT).pack(anchor="w", pady=(2, 0))
        tk.Label(inner_i,
                 text="Síntomas: " + ", ".join(sintomas_sel),
                 font=("Segoe UI", 8, "italic"), bg="#f0f7ff", fg=COLOR_ACCENT,
                 wraplength=310, justify="left").pack(anchor="w", pady=(2, 0))

        # Tarjetas de resultado
        for i, r in enumerate(resultados):
            prob = r["probabilidad"]
            if prob >= 70:
                color_bar, nivel, nivel_bg = COLOR_RED,    "Alta probabilidad",  "#fef2f2"
            elif prob >= 40:
                color_bar, nivel, nivel_bg = COLOR_YELLOW, "Probabilidad media", "#fffbeb"
            else:
                color_bar, nivel, nivel_bg = COLOR_GREEN,  "Probabilidad baja",  "#f0fdf4"

            nivel_ico = "🔴" if prob >= 70 else "🟡" if prob >= 40 else "🟢"

            outer_bg = "#fef9c3" if i == 0 else nivel_bg
            outer = tk.Frame(res_inner, bg=outer_bg)
            outer.pack(fill="x", pady=(0, 5), padx=4)

            if i == 0:
                tk.Label(outer, text="  ⭐ DIAGNÓSTICO PRINCIPAL",
                         font=("Segoe UI", 8, "bold"), bg="#fef9c3", fg="#92400e").pack(anchor="w", padx=10, pady=(4, 0))

            card = tk.Frame(outer, bg=outer_bg)
            card.pack(fill="x", padx=4, pady=(0, 4))
            tk.Frame(card, bg=color_bar, width=5).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=outer_bg)
            inner.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            top = tk.Frame(inner, bg=outer_bg)
            top.pack(fill="x")
            tk.Label(top, text=f"{nivel_ico} {r['enfermedad']}",
                     font=("Segoe UI", 11, "bold"), bg=outer_bg, fg=COLOR_TEXT).pack(side="left")
            tk.Label(top, text=f"{prob}%",
                     font=("Segoe UI", 12, "bold"), bg=outer_bg, fg=color_bar).pack(side="right")

            tk.Label(inner,
                     text=f"{nivel}  •  {r['coincidencias']} de {r['total_sintomas']} síntomas coinciden",
                     font=FONT_SMALL, bg=outer_bg, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x", pady=(2, 4))

            # Barra de progreso
            bar_bg = tk.Frame(inner, bg="#e2e8f0", height=8)
            bar_bg.pack(fill="x")
            bar_bg.update_idletasks()
            ancho_total = bar_bg.winfo_width() or 280
            tk.Frame(bar_bg, bg=color_bar, height=8,
                     width=max(4, int(ancho_total * prob / 100))).place(x=0, y=0)

            if r["sintomas_coinciden"]:
                tk.Label(inner,
                         text="✓ Coincide: " + ", ".join(r["sintomas_coinciden"]),
                         font=("Segoe UI", 8), bg=outer_bg, fg=color_bar,
                         wraplength=290, justify="left", anchor="w").pack(fill="x", pady=(5, 0))

    # ── BOTONES ──────────────────────────────────
    btn_frame = tk.Frame(win, bg=COLOR_BG)
    btn_frame.pack(fill="x", padx=16, pady=(0, 12))

    tk.Button(btn_frame, text="🔍  Generar Diagnóstico",
              command=generar,
              bg=COLOR_ACCENT, fg=COLOR_WHITE,
              font=FONT_BTN, relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left")

    tk.Button(btn_frame, text="↺  Refrescar síntomas",
              command=lambda: cargar_checkboxes(buscar_var.get()),
              bg="#e2e8f0", fg=COLOR_TEXT,
              font=("Segoe UI", 9), relief="flat", padx=12, pady=8, cursor="hand2").pack(side="left", padx=10)

    win.mainloop()
