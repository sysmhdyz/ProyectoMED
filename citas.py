import tkinter as tk
from tkinter import ttk, messagebox
import db
from datetime import datetime, date

# ── PALETA ───────────────────────────────────────────
COLOR_BG      = "#f0f4f8"
COLOR_WHITE   = "#ffffff"
COLOR_ACCENT  = "#2c7be5"
COLOR_TEXT    = "#2d3748"
COLOR_SUBTEXT = "#718096"
COLOR_GREEN   = "#17a589"
COLOR_YELLOW  = "#f39c12"
COLOR_RED     = "#e74c3c"
COLOR_PURPLE  = "#8e44ad"

FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_BODY  = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI", 10, "bold")
FONT_BOLD  = ("Segoe UI", 10, "bold")

HORAS = [f"{h:02d}:{m:02d}" for h in range(7, 21) for m in (0, 30)]

TIPO_COLORS = {
    "general":     "#2c7be5",
    "urgencia":    "#e74c3c",
    "estudio":     "#f39c12",
    "preventivo":  "#17a589",
    "especialidad":"#8e44ad",
}
TIPO_ICONS = {
    "general":     "📋",
    "urgencia":    "🚨",
    "estudio":     "🔬",
    "preventivo":  "💉",
    "especialidad":"🩺",
}


# ═══════════════════════════════════════════════════
# HELPER: GRÁFICA DE BARRAS EN CANVAS PURO
# ═══════════════════════════════════════════════════
def _dibujar_barras(canvas, datos: dict, colores: list):
    canvas.delete("all")
    canvas.update_idletasks()
    W = canvas.winfo_width()  or 680
    H = canvas.winfo_height() or 300
    if W < 100: W = 680
    if H < 100: H = 300

    ML, MR, MT, MB = 54, 24, 24, 56
    area_w = W - ML - MR
    area_h = H - MT - MB

    if not datos:
        canvas.create_text(W//2, H//2, text="Sin datos suficientes",
                           font=("Segoe UI", 11), fill=COLOR_SUBTEXT)
        return

    max_val = max(datos.values()) or 1
    keys    = list(datos.keys())
    n       = len(keys)
    spacing = area_w / n
    bar_w   = max(14, int(spacing * 0.55))

    # Ejes
    canvas.create_line(ML, MT, ML, H - MB, fill="#cbd5e0", width=2)
    canvas.create_line(ML, H - MB, W - MR, H - MB, fill="#cbd5e0", width=2)

    # Guías horizontales
    pasos = 4
    for i in range(1, pasos + 1):
        y   = MT + area_h * (1 - i / pasos)
        val = round(max_val * i / pasos)
        canvas.create_line(ML, y, W - MR, y, fill="#e2e8f0", dash=(4, 3))
        canvas.create_text(ML - 6, y, text=str(val),
                           font=("Segoe UI", 8), fill=COLOR_SUBTEXT, anchor="e")

    for idx, key in enumerate(keys):
        val   = datos[key]
        color = colores[idx % len(colores)]
        xc    = ML + idx * spacing + spacing / 2
        bh    = int((val / max_val) * area_h)
        x0, x1 = xc - bar_w / 2, xc + bar_w / 2
        y0, y1 = H - MB - bh, H - MB

        # Sombra
        canvas.create_rectangle(x0+3, y0+3, x1+3, y1, fill="#d4dbe6", outline="")
        # Barra (gradiente simulado con dos rectángulos)
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="", width=0)
        # Highlight
        canvas.create_rectangle(x0, y0, x0 + bar_w * 0.35, y1,
                                 fill=_lighten(color), outline="", width=0)
        # Valor
        canvas.create_text(xc, y0 - 9, text=str(val),
                           font=("Segoe UI", 9, "bold"), fill=color)
        # Etiqueta
        lbl = key if len(key) <= 15 else key[:14] + "…"
        canvas.create_text(xc, H - MB + 14, text=lbl,
                           font=("Segoe UI", 8), fill=COLOR_TEXT, angle=0)


def _lighten(hex_color):
    """Devuelve una versión más clara del color para el highlight."""
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = min(255, r + 50)
        g = min(255, g + 50)
        b = min(255, b + 50)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


# ═══════════════════════════════════════════════════
# MODAL: EDITAR ESTADO DE UNA CITA
# ═══════════════════════════════════════════════════
def modal_editar_cita(parent, cita_data, on_save):
    modal = tk.Toplevel(parent)
    modal.title("Editar Cita")
    modal.geometry("420x320")
    modal.configure(bg=COLOR_WHITE)
    modal.resizable(False, False)
    modal.grab_set()

    tk.Frame(modal, bg=COLOR_ACCENT, height=4).pack(fill="x")
    tk.Label(modal, text="✏️  Editar Estado de Cita",
             font=FONT_BOLD, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(pady=(14, 4))

    # Info de la cita
    info_bg = tk.Frame(modal, bg="#f0f7ff")
    info_bg.pack(fill="x", padx=24, pady=(4, 12))
    tk.Label(info_bg, text=f"👤 {cita_data['paciente']}   📅 {cita_data['fecha']}  🕐 {cita_data['hora']}",
             font=FONT_SMALL, bg="#f0f7ff", fg=COLOR_TEXT).pack(padx=10, pady=6)
    if cita_data.get("motivo"):
        tk.Label(info_bg, text=f"📋 {cita_data['motivo']}",
                 font=("Segoe UI", 8), bg="#f0f7ff", fg=COLOR_SUBTEXT).pack(padx=10, pady=(0, 6))

    form = tk.Frame(modal, bg=COLOR_WHITE)
    form.pack(padx=24, fill="both", expand=True)

    # Asistencia
    tk.Label(form, text="Estado de asistencia", font=FONT_SMALL,
             bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
    asist_var = tk.StringVar(value=cita_data.get("asistio", "Pendiente"))
    frame_radio = tk.Frame(form, bg=COLOR_WHITE)
    frame_radio.pack(fill="x", pady=(4, 10))
    for val, color in [("Asistió", COLOR_GREEN), ("No asistió", COLOR_RED), ("Pendiente", COLOR_YELLOW)]:
        tk.Radiobutton(frame_radio, text=val, variable=asist_var, value=val,
                       bg=COLOR_WHITE, fg=color, font=FONT_BODY,
                       activebackground=COLOR_WHITE,
                       selectcolor=COLOR_WHITE).pack(side="left", padx=8)

    # Notas
    tk.Label(form, text="Notas / Observaciones", font=FONT_SMALL,
             bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
    entry_notas = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
    entry_notas.insert(0, cita_data.get("notas", ""))
    entry_notas.pack(fill="x", ipady=5, pady=(2, 12))

    def guardar():
        db.actualizar_cita(cita_data["id"], asist_var.get(), entry_notas.get().strip())
        db.cargar_todo()
        modal.destroy()
        on_save()

    btns = tk.Frame(modal, bg=COLOR_WHITE)
    btns.pack(fill="x", padx=24, pady=(0, 16))
    tk.Button(btns, text="Cancelar", command=modal.destroy,
              bg="#f7fafc", fg=COLOR_TEXT, font=FONT_BTN,
              relief="flat", padx=12, pady=5).pack(side="left")
    tk.Button(btns, text="💾 Guardar cambios", command=guardar,
              bg=COLOR_GREEN, fg=COLOR_WHITE, font=FONT_BTN,
              relief="flat", padx=12, pady=5).pack(side="right")


# ═══════════════════════════════════════════════════
# MODAL: GESTIONAR MOTIVOS DE CITA
# ═══════════════════════════════════════════════════
def modal_gestionar_motivos(parent, on_close=None):
    db.cargar_todo()
    modal = tk.Toplevel(parent)
    modal.title("Gestionar Motivos de Cita")
    modal.geometry("500x520")
    modal.configure(bg=COLOR_BG)
    modal.grab_set()

    tk.Frame(modal, bg=COLOR_PURPLE, height=4).pack(fill="x")
    tk.Label(modal, text="📋  Catálogo de Motivos de Cita",
             font=FONT_BOLD, bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=(12, 4))

    # Formulario agregar
    add_frame = tk.Frame(modal, bg=COLOR_WHITE)
    add_frame.pack(fill="x", padx=16, pady=(4, 8))
    tk.Frame(add_frame, bg=COLOR_ACCENT, height=3).pack(fill="x")

    row_form = tk.Frame(add_frame, bg=COLOR_WHITE)
    row_form.pack(fill="x", padx=12, pady=8)

    tk.Label(row_form, text="Nombre:", font=FONT_SMALL,
             bg=COLOR_WHITE, fg=COLOR_SUBTEXT).grid(row=0, column=0, sticky="w", padx=(0, 6))
    entry_nom = tk.Entry(row_form, font=FONT_BODY, relief="solid", bd=1, width=22)
    entry_nom.grid(row=0, column=1, ipady=4, padx=(0, 10))

    tk.Label(row_form, text="Tipo:", font=FONT_SMALL,
             bg=COLOR_WHITE, fg=COLOR_SUBTEXT).grid(row=0, column=2, sticky="w", padx=(0, 6))
    tipo_var = tk.StringVar(value="general")
    combo_tipo = ttk.Combobox(row_form, textvariable=tipo_var,
                               values=["general","urgencia","estudio","preventivo","especialidad"],
                               state="readonly", font=FONT_BODY, width=12)
    combo_tipo.grid(row=0, column=3, ipady=4)

    def agregar_motivo():
        nom = entry_nom.get().strip()
        if not nom:
            messagebox.showerror("Error", "Escribe un nombre para el motivo.", parent=modal)
            return
        ok = db.agregar_motivo_cita(nom, tipo_var.get())
        if ok:
            db.cargar_todo()
            entry_nom.delete(0, tk.END)
            actualizar_lista()
        else:
            messagebox.showerror("Error", "Ese motivo ya existe.", parent=modal)

    tk.Button(add_frame, text="➕ Agregar motivo", command=agregar_motivo,
              bg=COLOR_ACCENT, fg=COLOR_WHITE, font=FONT_BTN,
              relief="flat", padx=10, pady=4, cursor="hand2").pack(pady=(0, 10))

    # Lista existente
    tk.Label(modal, text="Motivos registrados", font=FONT_BOLD,
             bg=COLOR_BG, fg=COLOR_TEXT, anchor="w").pack(fill="x", padx=16)

    frame_lista = tk.Frame(modal, bg=COLOR_BG)
    frame_lista.pack(fill="both", expand=True, padx=16, pady=8)

    sb = ttk.Scrollbar(frame_lista, orient="vertical")
    sb.pack(side="right", fill="y")

    cols = ("Tipo", "Nombre")
    tree = ttk.Treeview(frame_lista, columns=cols, show="headings",
                         yscrollcommand=sb.set, height=12)
    tree.heading("Tipo",   text="Tipo")
    tree.heading("Nombre", text="Nombre")
    tree.column("Tipo",   width=110, anchor="center")
    tree.column("Nombre", width=310, anchor="w")
    tree.pack(side="left", fill="both", expand=True)
    sb.config(command=tree.yview)

    # Tags de color por tipo
    for tipo, color in TIPO_COLORS.items():
        tree.tag_configure(tipo, foreground=color)

    def actualizar_lista():
        for r in tree.get_children():
            tree.delete(r)
        for m in db.motivos_cita:
            ico = TIPO_ICONS.get(m["tipo"], "📋")
            tree.insert("", "end", iid=str(m["id"]),
                        values=(f"{ico} {m['tipo']}", m["nombre"]),
                        tags=(m["tipo"],))

    def eliminar_motivo():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "Selecciona un motivo.", parent=modal)
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este motivo?", parent=modal):
            db.eliminar_motivo_cita(int(sel[0]))
            db.cargar_todo()
            actualizar_lista()

    tk.Button(modal, text="🗑 Eliminar seleccionado", command=eliminar_motivo,
              bg="#fff0f0", fg=COLOR_RED, font=FONT_SMALL,
              relief="flat", padx=10, pady=4, cursor="hand2").pack(pady=(0, 4))

    def al_cerrar():
        if on_close:
            on_close()
        modal.destroy()

    tk.Button(modal, text="Cerrar", command=al_cerrar,
              bg="#e2e8f0", fg=COLOR_TEXT, font=FONT_BTN,
              relief="flat", padx=16, pady=5, cursor="hand2").pack(pady=(0, 12))

    actualizar_lista()


# ═══════════════════════════════════════════════════
# VENTANA PRINCIPAL DE CITAS
# ═══════════════════════════════════════════════════
def ventana_citas():
    win = tk.Toplevel()
    win.title("Gestión de Citas Médicas")
    win.geometry("1130x680")
    win.configure(bg=COLOR_BG)
    win.resizable(True, True)

    db.cargar_todo()

    # ── HEADER ────────────────────────────────────
    header = tk.Frame(win, bg=COLOR_WHITE, height=56)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="📅  Gestión de Citas Médicas",
             font=FONT_TITLE, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(side="left", padx=24, pady=14)

    btn_frame_hdr = tk.Frame(header, bg=COLOR_WHITE)
    btn_frame_hdr.pack(side="right", padx=16, pady=10)
    tk.Button(btn_frame_hdr, text="📊 Ver Histórico",
              command=lambda: ventana_historico(win),
              bg=COLOR_PURPLE, fg=COLOR_WHITE, font=FONT_BTN,
              relief="flat", padx=12, pady=5, cursor="hand2").pack(side="right", padx=(6, 0))
    tk.Button(btn_frame_hdr, text="⚙ Motivos",
              command=lambda: modal_gestionar_motivos(win, on_close=_refrescar_motivos),
              bg="#64748b", fg=COLOR_WHITE, font=FONT_BTN,
              relief="flat", padx=12, pady=5, cursor="hand2").pack(side="right")

    # ── BODY ──────────────────────────────────────
    body = tk.Frame(win, bg=COLOR_BG)
    body.pack(fill="both", expand=True, padx=16, pady=12)

    left  = tk.Frame(body, bg=COLOR_BG, width=350)
    right = tk.Frame(body, bg=COLOR_BG)
    left.pack(side="left", fill="y", padx=(0, 10))
    left.pack_propagate(False)
    right.pack(side="right", fill="both", expand=True)

    # ══════════════════════════
    # PANEL IZQUIERDO
    # ══════════════════════════
    form_card = tk.Frame(left, bg=COLOR_WHITE)
    form_card.pack(fill="x", pady=(0, 10))
    tk.Frame(form_card, bg=COLOR_ACCENT, height=3).pack(fill="x")
    tk.Label(form_card, text="Nueva Cita", font=FONT_BOLD,
             bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", padx=16, pady=(12, 4))

    def lbl(parent, texto):
        tk.Label(parent, text=texto, font=FONT_SMALL,
                 bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x", padx=16, pady=(5, 1))

    # Paciente
    lbl(form_card, "Paciente")
    paciente_var = tk.StringVar()
    combo_pac = ttk.Combobox(form_card, textvariable=paciente_var,
                              state="readonly", font=FONT_BODY)
    combo_pac["values"] = [p["nombre"] for p in db.pacientes]
    combo_pac.pack(fill="x", padx=16, ipady=4, pady=(0, 2))

    # Médico
    lbl(form_card, "Médico")
    medico_var = tk.StringVar()
    combo_med = ttk.Combobox(form_card, textvariable=medico_var,
                              state="readonly", font=FONT_BODY)
    combo_med["values"] = [m["nombre"] for m in db.medicos]
    combo_med.pack(fill="x", padx=16, ipady=4, pady=(0, 2))

    # Motivo de cita (catálogo + enfermedades + libre)
    lbl(form_card, "Motivo de la cita")
    motivo_var = tk.StringVar()
    combo_motivo = ttk.Combobox(form_card, textvariable=motivo_var, font=FONT_BODY)
    combo_motivo.pack(fill="x", padx=16, ipady=4, pady=(0, 2))

    def _refrescar_motivos():
        db.cargar_todo()
        _actualizar_valores_motivo()

    def _actualizar_valores_motivo():
        opciones = []
        # Motivos del catálogo con ícono de tipo
        for m in db.motivos_cita:
            ico = TIPO_ICONS.get(m["tipo"], "📋")
            opciones.append(f"{ico} {m['nombre']}")
        # Separador visual
        opciones.append("─── Enfermedades registradas ───")
        for e in db.enfermedades:
            opciones.append(f"🦠 {e['nombre']}")
        combo_motivo["values"] = opciones

    _actualizar_valores_motivo()

    # Fecha
    lbl(form_card, "Fecha (YYYY-MM-DD)")
    entry_fecha = tk.Entry(form_card, font=FONT_BODY, relief="solid", bd=1)
    entry_fecha.insert(0, date.today().strftime("%Y-%m-%d"))
    entry_fecha.pack(fill="x", padx=16, ipady=5, pady=(0, 2))

    # Hora
    lbl(form_card, "Hora")
    hora_var = tk.StringVar(value="09:00")
    combo_hora = ttk.Combobox(form_card, textvariable=hora_var,
                               values=HORAS, state="readonly", font=FONT_BODY)
    combo_hora.pack(fill="x", padx=16, ipady=4, pady=(0, 2))

    # Notas
    lbl(form_card, "Notas (opcional)")
    entry_notas = tk.Entry(form_card, font=FONT_BODY, relief="solid", bd=1)
    entry_notas.pack(fill="x", padx=16, ipady=5, pady=(0, 10))

    def guardar_cita():
        pac   = paciente_var.get().strip()
        med   = medico_var.get().strip()
        motiv = motivo_var.get().strip()
        fec   = entry_fecha.get().strip()
        hora  = hora_var.get().strip()
        nota  = entry_notas.get().strip()

        # Quitar prefijo de ícono si viene del combo
        if motiv.startswith(("📋","🚨","🔬","💉","🩺","🦠")):
            motiv = motiv[2:].strip()

        if motiv == "─── Enfermedades registradas ───":
            messagebox.showerror("Error", "Selecciona un motivo válido.", parent=win)
            return

        if not pac or not med or not fec or not hora:
            messagebox.showerror("Error", "Paciente, médico, fecha y hora son obligatorios.", parent=win)
            return
        try:
            datetime.strptime(fec, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Usa YYYY-MM-DD.", parent=win)
            return

        ok = db.agregar_cita(pac, med, motiv, fec, hora, nota)
        if ok:
            db.cargar_todo()
            actualizar_tabla()
            entry_notas.delete(0, tk.END)
            messagebox.showinfo("✅ Éxito", f"Cita agendada:\n{pac}  —  {fec} {hora}", parent=win)
        else:
            messagebox.showerror(
                "⚠️ Duplicado",
                f"Ya existe una cita para '{pac}'\nel {fec} a las {hora}.\nElige otra hora o fecha.",
                parent=win
            )

    tk.Button(form_card, text="➕ Agendar Cita", command=guardar_cita,
              bg=COLOR_ACCENT, fg=COLOR_WHITE, font=FONT_BTN,
              relief="flat", padx=10, pady=7, cursor="hand2").pack(fill="x", padx=16, pady=(0, 14))

    # ── Panel editar asistencia ───────────────────
    edit_card = tk.Frame(left, bg=COLOR_WHITE)
    edit_card.pack(fill="x")
    tk.Frame(edit_card, bg=COLOR_GREEN, height=3).pack(fill="x")
    tk.Label(edit_card, text="Editar Estado de Cita", font=FONT_BOLD,
             bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", padx=16, pady=(10, 2))
    tk.Label(edit_card, text="Selecciona una fila en la tabla →",
             font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(anchor="w", padx=16)

    selected_id = [None]

    def abrir_editor():
        if selected_id[0] is None:
            messagebox.showerror("Error", "Selecciona una cita en la tabla primero.", parent=win)
            return
        cita_data = db.get_cita_by_id(selected_id[0])
        if cita_data:
            modal_editar_cita(win, cita_data, on_save=actualizar_tabla)

    tk.Button(edit_card, text="✏️ Editar cita seleccionada", command=abrir_editor,
              bg=COLOR_GREEN, fg=COLOR_WHITE, font=FONT_BTN,
              relief="flat", padx=10, pady=6, cursor="hand2").pack(fill="x", padx=16, pady=(8, 14))

    # ══════════════════════════
    # PANEL DERECHO – TABLA
    # ══════════════════════════
    barra = tk.Frame(right, bg=COLOR_BG)
    barra.pack(fill="x", pady=(0, 8))
    tk.Label(barra, text="Citas registradas", font=("Segoe UI", 11, "bold"),
             bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left")

    # Filtro
    filtro_var = tk.StringVar()
    filtro_entry = tk.Entry(barra, textvariable=filtro_var, font=FONT_BODY,
                            relief="solid", bd=1, width=18)
    filtro_entry.pack(side="right", padx=(0, 8))
    tk.Label(barra, text="🔍 Filtrar:", font=FONT_SMALL,
             bg=COLOR_BG, fg=COLOR_SUBTEXT).pack(side="right", padx=(0, 4))
    filtro_var.trace_add("write", lambda *_: actualizar_tabla())

    # Tabla
    cols = ("ID", "Paciente", "Médico", "Motivo", "Fecha", "Hora", "Estado", "Notas")
    style = ttk.Style()
    style.configure("Citas.Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#f0f4f8")
    style.configure("Citas.Treeview", font=FONT_SMALL, rowheight=28)

    frame_tabla = tk.Frame(right, bg=COLOR_BG)
    frame_tabla.pack(fill="both", expand=True)

    sb_y = ttk.Scrollbar(frame_tabla, orient="vertical")
    sb_y.pack(side="right", fill="y")
    sb_x = ttk.Scrollbar(frame_tabla, orient="horizontal")
    sb_x.pack(side="bottom", fill="x")

    tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings",
                          yscrollcommand=sb_y.set, xscrollcommand=sb_x.set,
                          style="Citas.Treeview")
    widths = {"ID":36, "Paciente":140, "Médico":130, "Motivo":160,
              "Fecha":88, "Hora":56, "Estado":90, "Notas":150}
    for c in cols:
        tabla.heading(c, text=c)
        tabla.column(c, width=widths[c],
                     anchor="center" if c in ("ID","Fecha","Hora","Estado") else "w")
    tabla.pack(side="left", fill="both", expand=True)
    sb_y.config(command=tabla.yview)
    sb_x.config(command=tabla.xview)

    tabla.tag_configure("asistio",   background="#eafaf1", foreground="#065f46")
    tabla.tag_configure("noasistio", background="#fdf2f2", foreground="#991b1b")
    tabla.tag_configure("pendiente", background="#fef9e7", foreground="#92400e")

    def actualizar_tabla():
        for r in tabla.get_children():
            tabla.delete(r)
        f = filtro_var.get().lower()
        for c in db.citas:
            texto = (c["paciente"] + c["medico"] + c["fecha"] +
                     c.get("motivo","") + c.get("asistio","")).lower()
            if f and f not in texto:
                continue
            asist = c.get("asistio", "Pendiente")
            tag   = "asistio" if asist == "Asistió" else "noasistio" if asist == "No asistió" else "pendiente"
            tabla.insert("", "end", iid=str(c["id"]),
                         values=(c["id"], c["paciente"], c["medico"],
                                 c.get("motivo",""), c["fecha"], c["hora"],
                                 asist, c.get("notas","")),
                         tags=(tag,))

    def on_select(event):
        sel = tabla.selection()
        if sel:
            selected_id[0] = int(sel[0])

    tabla.bind("<<TreeviewSelect>>", on_select)

    def eliminar_cita_sel():
        if selected_id[0] is None:
            messagebox.showerror("Error", "Selecciona una cita primero.", parent=win)
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar esta cita?", parent=win):
            db.eliminar_cita(selected_id[0])
            selected_id[0] = None
            db.cargar_todo()
            actualizar_tabla()

    tk.Button(right, text="🗑 Eliminar cita seleccionada",
              command=eliminar_cita_sel,
              bg="#fff0f0", fg=COLOR_RED, font=FONT_SMALL,
              relief="flat", padx=10, pady=4, cursor="hand2").pack(anchor="e", pady=(6, 0))

    actualizar_tabla()
    win.mainloop()


# ═══════════════════════════════════════════════════
# VENTANA HISTÓRICO CON GRÁFICAS DE BARRAS
# ═══════════════════════════════════════════════════
def ventana_historico(parent=None):
    db.cargar_todo()
    citas = db.citas

    win = tk.Toplevel(parent)
    win.title("📊 Histórico de Citas")
    win.geometry("900x640")
    win.configure(bg=COLOR_BG)
    win.resizable(True, True)

    header = tk.Frame(win, bg=COLOR_WHITE, height=52)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="📊  Histórico de Citas Médicas",
             font=FONT_TITLE, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(side="left", padx=24, pady=12)

    if not citas:
        tk.Label(win, text="📭\n\nNo hay citas registradas aún.",
                 font=("Segoe UI", 14), bg=COLOR_BG, fg=COLOR_SUBTEXT,
                 justify="center").pack(expand=True)
        return

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=16, pady=12)

    tab1 = tk.Frame(notebook, bg=COLOR_BG)
    tab2 = tk.Frame(notebook, bg=COLOR_BG)
    tab3 = tk.Frame(notebook, bg=COLOR_BG)
    notebook.add(tab1, text="  Asistencia  ")
    notebook.add(tab2, text="  Por Motivo  ")
    notebook.add(tab3, text="  Por Médico  ")

    def _tab_grafica(parent_tab, datos, titulo, colores):
        wrap = tk.Frame(parent_tab, bg=COLOR_WHITE)
        wrap.pack(fill="both", expand=True, padx=20, pady=16)
        tk.Label(wrap, text=titulo, font=("Segoe UI", 12, "bold"),
                 bg=COLOR_WHITE, fg=COLOR_TEXT).pack(pady=(12, 4))
        cvs = tk.Canvas(wrap, bg=COLOR_WHITE, highlightthickness=0, height=300)
        cvs.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        wrap.update_idletasks()
        _dibujar_barras(cvs, datos, colores)
        cvs.bind("<Configure>", lambda e: _dibujar_barras(cvs, datos, colores))

    # TAB 1 – Asistencia
    asist = {"Asistió": 0, "No asistió": 0, "Pendiente": 0}
    for c in citas:
        a = c.get("asistio", "Pendiente")
        if a in asist:
            asist[a] += 1

    _tab_grafica(tab1, asist, "Estado de Asistencia a Citas",
                 [COLOR_GREEN, COLOR_RED, COLOR_YELLOW])

    # Resumen numérico
    res_frame = tk.Frame(tab1, bg=COLOR_BG)
    res_frame.pack(fill="x", padx=20, pady=(0, 10))
    for lbl, val, col in [
        ("Total citas",  len(citas),          COLOR_ACCENT),
        ("Asistió",      asist["Asistió"],     COLOR_GREEN),
        ("No asistió",   asist["No asistió"],  COLOR_RED),
        ("Pendiente",    asist["Pendiente"],   COLOR_YELLOW),
    ]:
        cc = tk.Frame(res_frame, bg=COLOR_WHITE)
        cc.pack(side="left", expand=True, fill="x", padx=5, ipady=6)
        tk.Frame(cc, bg=col, height=3).pack(fill="x")
        tk.Label(cc, text=str(val), font=("Segoe UI", 20, "bold"),
                 bg=COLOR_WHITE, fg=col).pack()
        tk.Label(cc, text=lbl, font=FONT_SMALL,
                 bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(pady=(0, 6))

    # TAB 2 – Por motivo
    mot_count = {}
    for c in citas:
        m = c.get("motivo", "Sin especificar") or "Sin especificar"
        mot_count[m] = mot_count.get(m, 0) + 1
    mot_sorted = dict(sorted(mot_count.items(), key=lambda x: x[1], reverse=True)[:10])

    COLS_MOT = ["#2c7be5","#17a589","#e67e22","#8e44ad","#e74c3c",
                "#1abc9c","#3498db","#f39c12","#d35400","#7f8c8d"]
    _tab_grafica(tab2, mot_sorted, "Citas por Motivo (Top 10)", COLS_MOT)

    # TAB 3 – Por médico
    med_count = {}
    for c in citas:
        med_count[c["medico"]] = med_count.get(c["medico"], 0) + 1

    COLS_MED = ["#9b59b6","#2ecc71","#e74c3c","#3498db","#f1c40f",
                "#1abc9c","#e67e22","#2980b9","#8e44ad","#27ae60"]
    _tab_grafica(tab3, med_count, "Citas por Médico", COLS_MED)

    win.mainloop()
