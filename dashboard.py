import tkinter as tk
from tkinter import messagebox, ttk
import db

# =========================
# PALETA Y FUENTES
# =========================
COLOR_BG       = "#f0f4f8"
COLOR_SIDEBAR  = "#1a2535"
COLOR_ACCENT   = "#2c7be5"
COLOR_ACCENT2  = "#17a589"
COLOR_DANGER   = "#e74c3c"
COLOR_WARNING  = "#f39c12"
COLOR_WHITE    = "#ffffff"
COLOR_TEXT     = "#2d3748"
COLOR_SUBTEXT  = "#718096"

FONT_SECTION = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_BTN     = ("Segoe UI", 10, "bold")
FONT_CARD_T  = ("Segoe UI", 11, "bold")
FONT_CARD_S  = ("Segoe UI", 9)

# =========================
# DASHBOARD PRINCIPAL
# =========================
def abrir_dashboard(usuario, rol, login_root=None):
    if login_root:
        login_root.withdraw()

    root = tk.Toplevel()
    root.title("Sistema Médico — Dashboard")
    root.geometry("1150x700")
    root.configure(bg=COLOR_BG)
    root.resizable(True, True)

    # ── SIDEBAR ──────────────────────────────────────────
    sidebar = tk.Frame(root, bg=COLOR_SIDEBAR, width=230)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="🏥", font=("Segoe UI", 28), bg=COLOR_SIDEBAR, fg=COLOR_WHITE).pack(pady=(28, 0))
    tk.Label(sidebar, text="Sistema Médico", bg=COLOR_SIDEBAR, fg=COLOR_WHITE, font=("Segoe UI", 13, "bold")).pack()
    tk.Frame(sidebar, bg="#2d3f55", height=1).pack(fill="x", padx=20, pady=14)
    tk.Label(sidebar, text=f"👤  {usuario}", bg=COLOR_SIDEBAR, fg=COLOR_WHITE, font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=18, pady=(0, 2))
    tk.Label(sidebar, text=f"Rol: {rol.capitalize()}", bg=COLOR_SIDEBAR, fg="#8fa3bc", font=FONT_SMALL, anchor="w").pack(fill="x", padx=18, pady=(0, 16))

    # ── ÁREA DERECHA ──────────────────────────────────────
    right = tk.Frame(root, bg=COLOR_BG)
    right.pack(side="right", expand=True, fill="both")

    header_frame = tk.Frame(right, bg=COLOR_WHITE, height=56)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)

    header_lbl = tk.Label(header_frame, text="Dashboard", font=("Segoe UI", 14, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT)
    header_lbl.pack(side="left", padx=24, pady=14)

    canvas = tk.Canvas(right, bg=COLOR_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(right, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=COLOR_BG)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ── HELPERS ──────────────────────────────────────────
    def limpiar():
        for w in scroll_frame.winfo_children():
            w.destroy()

    def set_header(txt):
        header_lbl.config(text=txt)

    # ── TARJETAS ──────────────────────────────────────────
    def _stat_card(parent, titulo, valor, color, col):
        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew", ipadx=16, ipady=14)
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg=color, height=4).place(relx=0, rely=0, relwidth=1)
        tk.Label(card, text=titulo, font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(anchor="w", padx=14, pady=(16, 2))
        tk.Label(card, text=valor, font=("Segoe UI", 28, "bold"), bg=COLOR_WHITE, fg=color).pack(anchor="w", padx=14, pady=(0, 14))

    def _tarjeta_vacia(parent, titulo, sub):
        f = tk.Frame(parent, bg=COLOR_WHITE)
        f.pack(fill="x", pady=20, padx=4)
        tk.Label(f, text="📭", font=("Segoe UI", 32), bg=COLOR_WHITE, fg="#cbd5e0").pack(pady=(24, 6))
        tk.Label(f, text=titulo, font=("Segoe UI", 13, "bold"), bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack()
        tk.Label(f, text=sub, font=FONT_SMALL, bg=COLOR_WHITE, fg="#a0aec0").pack(pady=(2, 24))

    def _tarjeta_medico(parent, m, row, col, refresh_fn):
        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg=COLOR_ACCENT, width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=COLOR_WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        tk.Label(inner, text="🩺", font=("Segoe UI", 20), bg=COLOR_WHITE).pack(anchor="w")
        tk.Label(inner, text=m["nombre"], font=FONT_CARD_T, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", pady=(4, 0))
        tk.Label(inner, text=m["especialidad"], font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(anchor="w")

        def eliminar():
            if messagebox.askyesno("Eliminar", f"¿Eliminar al Dr. {m['nombre']}?"):
                db.eliminar_medico(m['nombre'])
                db.cargar_todo()
                refresh_fn()

        tk.Button(inner, text="🗑 Eliminar", command=eliminar, bg="#fff0f0", fg=COLOR_DANGER,
                  font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=3, cursor="hand2").pack(anchor="e", pady=(10, 0))

    def _tarjeta_enfermedad(parent, e, row, col, refresh_fn):
        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg=COLOR_ACCENT2, width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=COLOR_WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        tk.Label(inner, text="🦠", font=("Segoe UI", 20), bg=COLOR_WHITE).pack(anchor="w")
        tk.Label(inner, text=e["nombre"], font=FONT_CARD_T, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", pady=(4, 0))
        tk.Label(inner, text=e["descripcion"], font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, wraplength=190, justify="left").pack(anchor="w")

        try:
            sintomas_db = db.get_sintomas_de_enfermedad(e["id"])
            texto_sintomas = "Síntomas: " + ", ".join([s["nombre"] for s in sintomas_db]) if sintomas_db else "Sin síntomas registrados"
        except Exception:
            texto_sintomas = "Error al cargar síntomas"

        tk.Label(inner, text=texto_sintomas, font=("Segoe UI", 8, "italic"), bg=COLOR_WHITE,
                 fg=COLOR_ACCENT, wraplength=190, justify="left").pack(anchor="w", pady=(5, 0))

        def eliminar():
            if messagebox.askyesno("Eliminar", f"¿Eliminar '{e['nombre']}'?"):
                db.eliminar_enfermedad(e['nombre'])
                db.cargar_todo()
                refresh_fn()

        tk.Button(inner, text="🗑 Eliminar", command=eliminar, bg="#fff0f0", fg=COLOR_DANGER,
                  font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=3, cursor="hand2").pack(anchor="e", pady=(10, 0))

    def _tarjeta_paciente(parent, p, row, col, refresh_fn):
        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg="#3498db", width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=COLOR_WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        tk.Label(inner, text="🧑", font=("Segoe UI", 20), bg=COLOR_WHITE).pack(anchor="w")
        tk.Label(inner, text=p["nombre"], font=FONT_CARD_T, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", pady=(4, 0))
        tk.Label(inner, text=f"Edad: {p['edad']} | Sexo: {p['sexo']}", font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(anchor="w")

        def eliminar():
            if messagebox.askyesno("Eliminar", f"¿Eliminar a {p['nombre']}?"):
                db.eliminar_paciente(p['nombre'])
                db.cargar_todo()
                refresh_fn()

        tk.Button(inner, text="🗑 Eliminar", command=eliminar, bg="#fff0f0", fg=COLOR_DANGER,
                  font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=3, cursor="hand2").pack(anchor="e", pady=(10, 0))

    def _tarjeta_registro(parent, item, icon, color, row, col):
        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=COLOR_WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        tk.Label(inner, text=icon, font=("Segoe UI", 20), bg=COLOR_WHITE).pack(anchor="w")
        tk.Label(inner, text=f"Paciente: {item['paciente']}", font=FONT_CARD_T, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", pady=(4, 0))
        tk.Label(inner, text=f"Enfermedad: {item['enfermedad']}", font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_ACCENT).pack(anchor="w")
        tk.Label(inner, text=f"Probabilidad: {item['probabilidad']}%", font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(anchor="w")
        tk.Label(inner, text=f"Fecha: {item['fecha']}", font=("Segoe UI", 8, "italic"), bg=COLOR_WHITE, fg="#a0aec0").pack(anchor="w", pady=(8, 0))

    def _tarjeta_cita(parent, c, row, col, refresh_fn):
        asist = c.get("asistio", "Pendiente")
        color_map = {"Asistió": "#17a589", "No asistió": COLOR_DANGER, "Pendiente": COLOR_WARNING}
        color = color_map.get(asist, COLOR_WARNING)

        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=COLOR_WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        tk.Label(inner, text="📅", font=("Segoe UI", 20), bg=COLOR_WHITE).pack(anchor="w")
        tk.Label(inner, text=c["paciente"], font=FONT_CARD_T, bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", pady=(4, 0))
        tk.Label(inner, text=f"Dr. {c['medico']}", font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(anchor="w")
        tk.Label(inner, text=f"📆 {c['fecha']}  🕐 {c['hora']}", font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_ACCENT).pack(anchor="w")
        if c.get("enfermedad"):
            tk.Label(inner, text=f"🦠 {c['enfermedad']}", font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(anchor="w")

        estado_bg = {"Asistió": "#eafaf1", "No asistió": "#fdf2f2", "Pendiente": "#fef9e7"}
        bg = estado_bg.get(asist, "#fef9e7")
        tk.Label(inner, text=asist, font=("Segoe UI", 8, "bold"), bg=bg, fg=color,
                 padx=6, pady=2, relief="flat").pack(anchor="w", pady=(6, 0))

        def eliminar():
            if messagebox.askyesno("Eliminar", f"¿Eliminar cita de {c['paciente']} el {c['fecha']}?"):
                db.eliminar_cita(c["id"])
                db.cargar_todo()
                refresh_fn()

        tk.Button(inner, text="🗑 Eliminar", command=eliminar, bg="#fff0f0", fg=COLOR_DANGER,
                  font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=3, cursor="hand2").pack(anchor="e", pady=(8, 0))

    # ── MODALES ──────────────────────────────────────────
    def _crear_modal_base(titulo, altura):
        modal = tk.Toplevel(root)
        modal.title(titulo)
        modal.geometry(f"380x{altura}")
        modal.configure(bg=COLOR_WHITE)
        modal.resizable(False, False)
        modal.grab_set()
        tk.Label(modal, text=titulo, font=("Segoe UI", 13, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT).pack(pady=(15, 10))
        form = tk.Frame(modal, bg=COLOR_WHITE)
        form.pack(padx=30, fill="both", expand=True)
        return modal, form

    def _boton_guardar(modal, form, comando):
        bf = tk.Frame(modal, bg=COLOR_WHITE)
        bf.pack(fill="x", padx=30, pady=(0, 20))
        tk.Button(bf, text="Cancelar", command=modal.destroy, bg="#f7fafc", fg=COLOR_TEXT, font=FONT_BTN, relief="flat", padx=12, pady=5).pack(side="left")
        tk.Button(bf, text="Guardar", command=comando, bg=COLOR_ACCENT2, fg=COLOR_WHITE, font=FONT_BTN, relief="flat", padx=12, pady=5).pack(side="right")

    def modal_agregar_paciente(refresh_fn):
        modal, form = _crear_modal_base("Nuevo Paciente", 320)
        tk.Label(form, text="Nombre", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_nombre = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_nombre.pack(fill="x", pady=(2, 10), ipady=5)
        tk.Label(form, text="Edad", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_edad = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_edad.pack(fill="x", pady=(2, 10), ipady=5)
        tk.Label(form, text="Sexo", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        c_sexo = ttk.Combobox(form, values=["Masculino", "Femenino", "Otro"], state="readonly", font=FONT_BODY)
        c_sexo.pack(fill="x", pady=(2, 10), ipady=5)

        def guardar():
            nombre, edad, sexo = e_nombre.get().strip(), e_edad.get().strip(), c_sexo.get()
            if not nombre or not edad or not sexo:
                messagebox.showerror("Error", "Completa todos los campos", parent=modal)
                return
            db.agregar_paciente(nombre, edad, sexo)
            db.cargar_todo()
            modal.destroy()
            refresh_fn()
        _boton_guardar(modal, form, guardar)

    def modal_agregar_diagnostico(refresh_fn):
        modal, form = _crear_modal_base("Nuevo Diagnóstico", 320)
        tk.Label(form, text="Paciente", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        c_paciente = ttk.Combobox(form, values=[p['nombre'] for p in db.pacientes], state="readonly", font=FONT_BODY)
        c_paciente.pack(fill="x", pady=(2, 10), ipady=5)
        tk.Label(form, text="Enfermedad", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        c_enf = ttk.Combobox(form, values=[e['nombre'] for e in db.enfermedades], state="readonly", font=FONT_BODY)
        c_enf.pack(fill="x", pady=(2, 10), ipady=5)
        tk.Label(form, text="Probabilidad (%)", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_prob = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_prob.pack(fill="x", pady=(2, 10), ipady=5)

        def guardar():
            paciente, enf, prob = c_paciente.get(), c_enf.get(), e_prob.get().strip()
            if not paciente or not enf or not prob:
                messagebox.showerror("Error", "Completa todos los campos", parent=modal)
                return
            try:
                db.agregar_diagnostico(paciente, enf, float(prob))
                db.cargar_todo()
                modal.destroy()
                refresh_fn()
            except ValueError:
                messagebox.showerror("Error", "La probabilidad debe ser un número", parent=modal)
        _boton_guardar(modal, form, guardar)

    def modal_agregar_medico(refresh_fn):
        modal, form = _crear_modal_base("Nuevo Médico", 250)
        tk.Label(form, text="Nombre", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_nombre = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_nombre.pack(fill="x", pady=(2, 10), ipady=5)
        tk.Label(form, text="Especialidad", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_esp = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_esp.pack(fill="x", pady=(2, 10), ipady=5)

        def guardar():
            nombre, esp = e_nombre.get().strip(), e_esp.get().strip()
            if not nombre or not esp: return
            db.agregar_medico(nombre, esp)
            db.cargar_todo()
            modal.destroy()
            refresh_fn()
        _boton_guardar(modal, form, guardar)

    def modal_agregar_enfermedad(refresh_fn):
        modal, form = _crear_modal_base("Nueva Enfermedad", 480)
        tk.Label(form, text="Nombre", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_nombre = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_nombre.pack(fill="x", pady=(2, 10), ipady=5)
        tk.Label(form, text="Descripción", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_desc = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_desc.pack(fill="x", pady=(2, 10), ipady=5)
        tk.Label(form, text="Síntomas (Selecciona varios)", font=FONT_SMALL, bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        frame_lista = tk.Frame(form, bg=COLOR_WHITE, relief="solid", bd=1)
        frame_lista.pack(fill="both", expand=True, pady=(2, 15))
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        lista_sintomas = tk.Listbox(frame_lista, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, font=FONT_BODY, bd=0, highlightthickness=0, height=6)
        lista_sintomas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=lista_sintomas.yview)
        try:
            catalogo = db.get_catalogo_sintomas()
            for s in catalogo:
                lista_sintomas.insert(tk.END, s['nombre'])
        except Exception as e:
            catalogo = []

        def guardar():
            nombre, desc = e_nombre.get().strip(), e_desc.get().strip()
            seleccionados = lista_sintomas.curselection()
            if not nombre or not desc or not seleccionados:
                messagebox.showerror("Error", "Completa nombre, descripción y selecciona al menos un síntoma", parent=modal)
                return
            enfermedad_id = db.agregar_enfermedad(nombre, desc)
            for i in seleccionados:
                db.agregar_sintoma(enfermedad_id, catalogo[i]['nombre'])
            db.cargar_todo()
            modal.destroy()
            refresh_fn()
        _boton_guardar(modal, form, guardar)

    # ── VISTAS ────────────────────────────────────────────
    def _crear_vista_base(titulo, btn_texto, btn_cmd, datos, fn_tarjeta, refresh_fn):
        limpiar()
        set_header(titulo)
        barra = tk.Frame(scroll_frame, bg=COLOR_BG)
        barra.pack(fill="x", padx=24, pady=(20, 10))
        tk.Label(barra, text=f"{titulo} registrados", font=FONT_SECTION, bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left")
        if btn_texto:
            tk.Button(barra, text=f"＋ {btn_texto}", command=lambda: btn_cmd(refresh_fn),
                      bg=COLOR_ACCENT, fg=COLOR_WHITE, font=FONT_BTN, relief="flat", padx=14, pady=6, cursor="hand2").pack(side="right")
        grid = tk.Frame(scroll_frame, bg=COLOR_BG)
        grid.pack(fill="both", padx=24, pady=4)
        if not datos:
            _tarjeta_vacia(grid, "No hay registros aquí", "Usa el botón superior para empezar" if btn_texto else "")
        else:
            for i, item in enumerate(datos):
                if fn_tarjeta == _tarjeta_registro:
                    icon, color = ("🧠", COLOR_WARNING) if "Diagnóstico" in titulo else ("📁", "#8e44ad")
                    fn_tarjeta(grid, item, icon, color, i // 3, i % 3)
                else:
                    fn_tarjeta(grid, item, i // 3, i % 3, refresh_fn)

    def vista_inicio():
        limpiar()
        set_header("Dashboard")
        db.cargar_todo()
        tk.Label(scroll_frame, text=f"Bienvenido, {usuario} 👋", font=("Segoe UI", 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w", padx=30, pady=(30, 4))
        stats = tk.Frame(scroll_frame, bg=COLOR_BG)
        stats.pack(fill="x", padx=30, pady=(20, 4))
        _stat_card(stats, "🧑 Pacientes",    str(len(db.pacientes)),    COLOR_ACCENT,   0)
        _stat_card(stats, "🩺 Médicos",      str(len(db.medicos)),      "#9b59b6",      1)
        _stat_card(stats, "🦠 Enfermedades", str(len(db.enfermedades)), COLOR_ACCENT2,  2)
        _stat_card(stats, "📋 Diagnósticos", str(len(db.diagnosticos)), COLOR_WARNING,  3)
        if rol == "medico":
            _stat_card(stats, "📅 Citas",    str(len(db.citas)),        "#8e44ad",      4)

    def vista_medicos():      _crear_vista_base("🩺 Médicos",       "Agregar médico",    modal_agregar_medico,       db.medicos,      _tarjeta_medico,      vista_medicos)
    def vista_enfermedades(): _crear_vista_base("🦠 Enfermedades",  "Agregar enfermedad",modal_agregar_enfermedad,   db.enfermedades, _tarjeta_enfermedad,  vista_enfermedades)
    def vista_pacientes():    _crear_vista_base("🧑 Pacientes",     "Agregar paciente",  modal_agregar_paciente,     db.pacientes,    _tarjeta_paciente,    vista_pacientes)
    def vista_diagnostico():  _crear_vista_base("🧠 Diagnósticos",  "Nuevo Diagnóstico", modal_agregar_diagnostico,  db.diagnosticos, _tarjeta_registro,    vista_diagnostico)
    def vista_historial():    _crear_vista_base("📁 Historial",     "Agregar Registro",  modal_agregar_diagnostico,  db.historial,    _tarjeta_registro,    vista_historial)

    def vista_citas():
        db.cargar_todo()
        _crear_vista_base("📅 Citas", None, None, db.citas, _tarjeta_cita, vista_citas)
        # Botón para abrir gestión completa de citas
        from citas import ventana_citas, ventana_historico
        barra_extra = tk.Frame(scroll_frame, bg=COLOR_BG)
        barra_extra.pack(fill="x", padx=24, pady=(0, 8))
        tk.Button(barra_extra, text="➕ Gestionar Citas", command=ventana_citas,
                  bg=COLOR_ACCENT, fg=COLOR_WHITE, font=FONT_BTN,
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(side="left")
        tk.Button(barra_extra, text="📊 Ver Histórico", command=lambda: ventana_historico(root),
                  bg="#8e44ad", fg=COLOR_WHITE, font=FONT_BTN,
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(side="left", padx=10)

    def vista_diagnostico_medico():
        from diagnostico import ventana_diagnostico
        ventana_diagnostico()

    # ── BOTONES SIDEBAR ───────────────────────────────────
    current_btn = [None]
    def _nav_btn(texto, comando):
        btn = tk.Button(sidebar, text=texto, bg=COLOR_SIDEBAR, fg="#c2ccd8", bd=0,
                        font=("Segoe UI", 10), activebackground="#243447", activeforeground=COLOR_WHITE,
                        anchor="w", padx=18, pady=9, relief="flat", cursor="hand2")
        def click(b=btn, cmd=comando):
            if current_btn[0] and current_btn[0] != b:
                current_btn[0].config(bg=COLOR_SIDEBAR, fg="#c2ccd8")
            b.config(bg=COLOR_ACCENT, fg=COLOR_WHITE)
            current_btn[0] = b
            cmd()
        btn.config(command=click)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#243447" if b != current_btn[0] else COLOR_ACCENT, fg=COLOR_WHITE))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLOR_ACCENT if b == current_btn[0] else COLOR_SIDEBAR, fg=COLOR_WHITE if b == current_btn[0] else "#c2ccd8"))
        btn.pack(fill="x")
        return btn

    tk.Frame(sidebar, bg="#2d3f55", height=1).pack(fill="x", padx=16, pady=8)
    tk.Label(sidebar, text="MENÚ", font=("Segoe UI", 8), bg=COLOR_SIDEBAR, fg="#4a6282", anchor="w").pack(fill="x", padx=18)

    if rol == "admin":
        _nav_btn("🦠 Enfermedades", vista_enfermedades)
        _nav_btn("🩺 Médicos",      vista_medicos)

    if rol == "medico":
        _nav_btn("🧑 Pacientes",      vista_pacientes)
        _nav_btn("🧠 Diagnóstico",    vista_diagnostico_medico)
        _nav_btn("📁 Historial",      vista_historial)
        _nav_btn("📅 Citas",          vista_citas)

    # ── CERRAR SESIÓN ─────────────────────────────────────
    def cerrar_sesion():
        root.destroy()
        if login_root:
            login_root.deiconify()

    tk.Frame(sidebar, bg="#2d3f55", height=1).pack(fill="x", padx=16, pady=8, side="bottom")
    tk.Button(sidebar, text="⬅ Cerrar sesión", command=cerrar_sesion,
              bg="#c0392b", fg=COLOR_WHITE, font=("Segoe UI", 10, "bold"),
              relief="flat", pady=10, cursor="hand2").pack(fill="x", side="bottom")

    vista_inicio()
    root.mainloop()

if __name__ == "__main__":
    abrir_dashboard("Prueba", "medico")
