import tkinter as tk
from tkinter import messagebox, ttk

# =========================
# PALETA Y FUENTES
# =========================
COLOR_BG       = "#f0f4f8"
COLOR_SIDEBAR  = "#1a2535"
COLOR_ACCENT   = "#2c7be5"
COLOR_ACCENT2  = "#17a589"
COLOR_PURPLE   = "#9b59b6"
COLOR_DANGER   = "#e74c3c"
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
    root = tk.Toplevel()
    root.title("Sistema Médico — Dashboard")
    root.geometry("1100x650")
    root.configure(bg=COLOR_BG)
    root.resizable(True, True)

    # ── SIDEBAR ──────────────────────────────────────────
    sidebar = tk.Frame(root, bg=COLOR_SIDEBAR, width=230)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="🏥", font=("Segoe UI", 28),
             bg=COLOR_SIDEBAR, fg=COLOR_WHITE).pack(pady=(28, 0))
    tk.Label(sidebar, text="Sistema Médico",
             bg=COLOR_SIDEBAR, fg=COLOR_WHITE,
             font=("Segoe UI", 13, "bold")).pack()

    tk.Frame(sidebar, bg="#2d3f55", height=1).pack(fill="x", padx=20, pady=14)

    tk.Label(sidebar, text=f"👤  {usuario}",
             bg=COLOR_SIDEBAR, fg=COLOR_WHITE,
             font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=18, pady=(0, 2))
    tk.Label(sidebar, text=f"Rol: {rol.capitalize()}",
             bg=COLOR_SIDEBAR, fg="#8fa3bc",
             font=FONT_SMALL, anchor="w").pack(fill="x", padx=18, pady=(0, 16))

    # ── ÁREA DERECHA ──────────────────────────────────────
    right = tk.Frame(root, bg=COLOR_BG)
    right.pack(side="right", expand=True, fill="both")

    header_frame = tk.Frame(right, bg=COLOR_WHITE, height=56)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)

    header_lbl = tk.Label(header_frame, text="Dashboard",
                          font=("Segoe UI", 14, "bold"),
                          bg=COLOR_WHITE, fg=COLOR_TEXT)
    header_lbl.pack(side="left", padx=24, pady=14)

    canvas = tk.Canvas(right, bg=COLOR_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(right, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=COLOR_BG)

    scroll_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.bind_all("<MouseWheel>",
        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ── HELPERS ──────────────────────────────────────────
    def limpiar():
        for w in scroll_frame.winfo_children():
            w.destroy()

    def set_header(txt):
        header_lbl.config(text=txt)

    # ── COMPONENTES VISUALES ─────────────────────────────
    def _stat_card(parent, titulo, valor, color, col):
        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew", ipadx=16, ipady=14)
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg=color, height=4).place(relx=0, rely=0, relwidth=1)
        tk.Label(card, text=titulo, font=FONT_SMALL,
                 bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(anchor="w", padx=14, pady=(16, 2))
        tk.Label(card, text=valor, font=("Segoe UI", 28, "bold"),
                 bg=COLOR_WHITE, fg=color).pack(anchor="w", padx=14, pady=(0, 14))

    def _tarjeta_vacia(parent, titulo, sub):
        f = tk.Frame(parent, bg=COLOR_WHITE)
        f.pack(fill="x", pady=20, padx=4)
        tk.Label(f, text="📭", font=("Segoe UI", 32), bg=COLOR_WHITE, fg="#cbd5e0").pack(pady=(24, 6))
        tk.Label(f, text=titulo, font=("Segoe UI", 13, "bold"), bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack()
        tk.Label(f, text=sub, font=FONT_SMALL, bg=COLOR_WHITE, fg="#a0aec0").pack(pady=(2, 24))

    def _boton_eliminar(parent, comando):
        tk.Button(parent, text="🗑  Eliminar", command=comando,
                  bg="#fff0f0", fg=COLOR_DANGER,
                  font=("Segoe UI", 8, "bold"),
                  relief="flat", padx=8, pady=3, cursor="hand2"
                  ).pack(anchor="e", pady=(10, 0))

    # ── TARJETA MÉDICO ────────────────────────────────────
    def _tarjeta_medico(parent, m, row, col, refresh_fn):
        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg=COLOR_ACCENT, width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=COLOR_WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        tk.Label(inner, text="🩺", font=("Segoe UI", 20), bg=COLOR_WHITE).pack(anchor="w")
        tk.Label(inner, text=m["nombre"], font=FONT_CARD_T,
                 bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", pady=(4, 0))
        tk.Label(inner, text=m["especialidad"], font=FONT_CARD_S,
                 bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(anchor="w")

        def eliminar():
            if messagebox.askyesno("Eliminar", f"¿Eliminar al Dr. {m['nombre']}?"):
                import db
                db.eliminar_medico(m["nombre"])
                db.cargar_todo()
                refresh_fn()

        _boton_eliminar(inner, eliminar)

    # ── TARJETA ENFERMEDAD ────────────────────────────────
    def _tarjeta_enfermedad(parent, e, row, col, refresh_fn):
        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg=COLOR_ACCENT2, width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=COLOR_WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        tk.Label(inner, text="🦠", font=("Segoe UI", 20), bg=COLOR_WHITE).pack(anchor="w")
        tk.Label(inner, text=e["nombre"], font=FONT_CARD_T,
                 bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", pady=(4, 0))
        tk.Label(inner, text=e["descripcion"], font=FONT_CARD_S,
                 bg=COLOR_WHITE, fg=COLOR_SUBTEXT,
                 wraplength=190, justify="left").pack(anchor="w")

        def eliminar():
            if messagebox.askyesno("Eliminar", f"¿Eliminar '{e['nombre']}'?"):
                import db
                db.eliminar_enfermedad(e["nombre"])
                db.cargar_todo()
                refresh_fn()

        _boton_eliminar(inner, eliminar)

    # ── TARJETA PACIENTE ──────────────────────────────────
    def _tarjeta_paciente(parent, p, row, col, refresh_fn):
        card = tk.Frame(parent, bg=COLOR_WHITE)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Frame(card, bg=COLOR_PURPLE, width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=COLOR_WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        tk.Label(inner, text="🧑", font=("Segoe UI", 20), bg=COLOR_WHITE).pack(anchor="w")
        tk.Label(inner, text=p["nombre"], font=FONT_CARD_T,
                 bg=COLOR_WHITE, fg=COLOR_TEXT).pack(anchor="w", pady=(4, 0))
        info = tk.Frame(inner, bg=COLOR_WHITE)
        info.pack(anchor="w", pady=(4, 0))
        tk.Label(info, text=f"Edad: {p['edad']}",
                 font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(side="left", padx=(0, 10))
        tk.Label(info, text=f"Sexo: {p['sexo']}",
                 font=FONT_CARD_S, bg=COLOR_WHITE, fg=COLOR_SUBTEXT).pack(side="left")

        def eliminar():
            if messagebox.askyesno("Eliminar", f"¿Eliminar al paciente {p['nombre']}?"):
                import db
                db.eliminar_paciente(p["nombre"])
                db.cargar_todo()
                refresh_fn()

        _boton_eliminar(inner, eliminar)

    # ── MODAL MÉDICO ──────────────────────────────────────
    def modal_agregar_medico(refresh_fn):
        modal = tk.Toplevel(root)
        modal.title("Agregar médico")
        modal.geometry("360x250")
        modal.configure(bg=COLOR_WHITE)
        modal.resizable(False, False)
        modal.grab_set()

        tk.Label(modal, text="Nuevo médico",
                 font=("Segoe UI", 13, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT
                 ).pack(pady=(20, 14))

        form = tk.Frame(modal, bg=COLOR_WHITE)
        form.pack(padx=30, fill="x")

        tk.Label(form, text="Nombre", font=FONT_SMALL, bg=COLOR_WHITE,
                 fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_nombre = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_nombre.pack(fill="x", pady=(2, 10), ipady=5)

        tk.Label(form, text="Especialidad", font=FONT_SMALL, bg=COLOR_WHITE,
                 fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_esp = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_esp.pack(fill="x", pady=(2, 16), ipady=5)

        def guardar():
            nombre = e_nombre.get().strip()
            esp = e_esp.get().strip()
            if not nombre or not esp:
                messagebox.showerror("Error", "Completa todos los campos", parent=modal)
                return
            import db
            db.agregar_medico(nombre, esp)
            db.cargar_todo()
            modal.destroy()
            refresh_fn()

        bf = tk.Frame(modal, bg=COLOR_WHITE)
        bf.pack(fill="x", padx=30)
        tk.Button(bf, text="Cancelar", command=modal.destroy,
                  bg="#f7fafc", fg=COLOR_TEXT, font=FONT_BTN,
                  relief="flat", padx=12, pady=5).pack(side="left")
        tk.Button(bf, text="Guardar", command=guardar,
                  bg=COLOR_ACCENT, fg=COLOR_WHITE, font=FONT_BTN,
                  relief="flat", padx=12, pady=5).pack(side="right")

    # ── MODAL ENFERMEDAD ──────────────────────────────────
    def modal_agregar_enfermedad(refresh_fn):
        modal = tk.Toplevel(root)
        modal.title("Agregar enfermedad")
        modal.geometry("360x260")
        modal.configure(bg=COLOR_WHITE)
        modal.resizable(False, False)
        modal.grab_set()

        tk.Label(modal, text="Nueva enfermedad",
                 font=("Segoe UI", 13, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT
                 ).pack(pady=(20, 14))

        form = tk.Frame(modal, bg=COLOR_WHITE)
        form.pack(padx=30, fill="x")

        tk.Label(form, text="Nombre", font=FONT_SMALL, bg=COLOR_WHITE,
                 fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_nombre = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_nombre.pack(fill="x", pady=(2, 10), ipady=5)

        tk.Label(form, text="Descripción", font=FONT_SMALL, bg=COLOR_WHITE,
                 fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_desc = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_desc.pack(fill="x", pady=(2, 16), ipady=5)

        def guardar():
            nombre = e_nombre.get().strip()
            desc = e_desc.get().strip()
            if not nombre or not desc:
                messagebox.showerror("Error", "Completa todos los campos", parent=modal)
                return
            import db
            db.agregar_enfermedad(nombre, desc)
            db.cargar_todo()
            modal.destroy()
            refresh_fn()

        bf = tk.Frame(modal, bg=COLOR_WHITE)
        bf.pack(fill="x", padx=30)
        tk.Button(bf, text="Cancelar", command=modal.destroy,
                  bg="#f7fafc", fg=COLOR_TEXT, font=FONT_BTN,
                  relief="flat", padx=12, pady=5).pack(side="left")
        tk.Button(bf, text="Guardar", command=guardar,
                  bg=COLOR_ACCENT2, fg=COLOR_WHITE, font=FONT_BTN,
                  relief="flat", padx=12, pady=5).pack(side="right")

    # ── MODAL PACIENTE ────────────────────────────────────
    def modal_agregar_paciente(refresh_fn):
        modal = tk.Toplevel(root)
        modal.title("Agregar paciente")
        modal.geometry("360x290")
        modal.configure(bg=COLOR_WHITE)
        modal.resizable(False, False)
        modal.grab_set()

        tk.Label(modal, text="Nuevo paciente",
                 font=("Segoe UI", 13, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT
                 ).pack(pady=(20, 14))

        form = tk.Frame(modal, bg=COLOR_WHITE)
        form.pack(padx=30, fill="x")

        tk.Label(form, text="Nombre", font=FONT_SMALL, bg=COLOR_WHITE,
                 fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_nombre = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_nombre.pack(fill="x", pady=(2, 10), ipady=5)

        tk.Label(form, text="Edad", font=FONT_SMALL, bg=COLOR_WHITE,
                 fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        e_edad = tk.Entry(form, font=FONT_BODY, relief="solid", bd=1)
        e_edad.pack(fill="x", pady=(2, 10), ipady=5)

        tk.Label(form, text="Sexo", font=FONT_SMALL, bg=COLOR_WHITE,
                 fg=COLOR_SUBTEXT, anchor="w").pack(fill="x")
        sexo_var = tk.StringVar(value="Masculino")
        sf = tk.Frame(form, bg=COLOR_WHITE)
        sf.pack(fill="x", pady=(2, 16))
        tk.Radiobutton(sf, text="Masculino", variable=sexo_var,
                       value="Masculino", bg=COLOR_WHITE, font=FONT_BODY).pack(side="left")
        tk.Radiobutton(sf, text="Femenino", variable=sexo_var,
                       value="Femenino", bg=COLOR_WHITE, font=FONT_BODY).pack(side="left", padx=10)

        def guardar():
            nombre = e_nombre.get().strip()
            edad = e_edad.get().strip()
            sexo = sexo_var.get()
            if not nombre or not edad:
                messagebox.showerror("Error", "Completa todos los campos", parent=modal)
                return
            import db
            db.agregar_paciente(nombre, edad, sexo)
            db.cargar_todo()
            modal.destroy()
            refresh_fn()

        bf = tk.Frame(modal, bg=COLOR_WHITE)
        bf.pack(fill="x", padx=30)
        tk.Button(bf, text="Cancelar", command=modal.destroy,
                  bg="#f7fafc", fg=COLOR_TEXT, font=FONT_BTN,
                  relief="flat", padx=12, pady=5).pack(side="left")
        tk.Button(bf, text="Guardar", command=guardar,
                  bg=COLOR_PURPLE, fg=COLOR_WHITE, font=FONT_BTN,
                  relief="flat", padx=12, pady=5).pack(side="right")

    # ── VISTAS ───────────────────────────────────────────
    def vista_inicio():
        limpiar()
        set_header("Dashboard")

        tk.Label(scroll_frame, text=f"Bienvenido, {usuario} 👋",
                 font=("Segoe UI", 20, "bold"), bg=COLOR_BG, fg=COLOR_TEXT
                 ).pack(anchor="w", padx=30, pady=(30, 4))
        tk.Label(scroll_frame,
                 text="Selecciona una opción del menú lateral para comenzar.",
                 font=("Segoe UI", 11), bg=COLOR_BG, fg=COLOR_SUBTEXT
                 ).pack(anchor="w", padx=30, pady=(0, 24))

        import db
        db.cargar_todo()

        stats = tk.Frame(scroll_frame, bg=COLOR_BG)
        stats.pack(fill="x", padx=30, pady=4)
        _stat_card(stats, "🧑 Pacientes",    str(len(db.pacientes)),    COLOR_ACCENT,  0)
        _stat_card(stats, "🩺 Médicos",      str(len(db.medicos)),      COLOR_PURPLE,  1)
        _stat_card(stats, "🦠 Enfermedades", str(len(db.enfermedades)), COLOR_ACCENT2, 2)
        _stat_card(stats, "📋 Diagnósticos", str(len(db.diagnosticos)), "#e67e22",     3)

    def vista_medicos():
        import db
        db.cargar_todo()
        limpiar()
        set_header("🩺  Médicos")

        barra = tk.Frame(scroll_frame, bg=COLOR_BG)
        barra.pack(fill="x", padx=24, pady=(20, 10))
        tk.Label(barra, text="Médicos registrados",
                 font=FONT_SECTION, bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left")
        tk.Button(barra, text="＋  Agregar médico",
                  command=lambda: modal_agregar_medico(vista_medicos),
                  bg=COLOR_ACCENT, fg=COLOR_WHITE, font=FONT_BTN,
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(side="right")

        grid = tk.Frame(scroll_frame, bg=COLOR_BG)
        grid.pack(fill="both", padx=24, pady=4)

        if not db.medicos:
            _tarjeta_vacia(grid, "No hay médicos registrados",
                           "Agrega uno con el botón de arriba")
        else:
            for i, m in enumerate(db.medicos):
                _tarjeta_medico(grid, m, i // 3, i % 3, vista_medicos)

    def vista_enfermedades():
        import db
        db.cargar_todo()
        limpiar()
        set_header("🦠  Enfermedades")

        barra = tk.Frame(scroll_frame, bg=COLOR_BG)
        barra.pack(fill="x", padx=24, pady=(20, 10))
        tk.Label(barra, text="Enfermedades registradas",
                 font=FONT_SECTION, bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left")
        tk.Button(barra, text="＋  Agregar enfermedad",
                  command=lambda: modal_agregar_enfermedad(vista_enfermedades),
                  bg=COLOR_ACCENT2, fg=COLOR_WHITE, font=FONT_BTN,
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(side="right")

        grid = tk.Frame(scroll_frame, bg=COLOR_BG)
        grid.pack(fill="both", padx=24, pady=4)

        if not db.enfermedades:
            _tarjeta_vacia(grid, "No hay enfermedades registradas",
                           "Agrega una con el botón de arriba")
        else:
            for i, e in enumerate(db.enfermedades):
                _tarjeta_enfermedad(grid, e, i // 3, i % 3, vista_enfermedades)

    def vista_pacientes():
        import db
        db.cargar_todo()
        limpiar()
        set_header("🧑  Pacientes")

        barra = tk.Frame(scroll_frame, bg=COLOR_BG)
        barra.pack(fill="x", padx=24, pady=(20, 10))
        tk.Label(barra, text="Pacientes registrados",
                 font=FONT_SECTION, bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left")
        tk.Button(barra, text="＋  Agregar paciente",
                  command=lambda: modal_agregar_paciente(vista_pacientes),
                  bg=COLOR_PURPLE, fg=COLOR_WHITE, font=FONT_BTN,
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(side="right")

        grid = tk.Frame(scroll_frame, bg=COLOR_BG)
        grid.pack(fill="both", padx=24, pady=4)

        if not db.pacientes:
            _tarjeta_vacia(grid, "No hay pacientes registrados",
                           "Agrega uno con el botón de arriba")
        else:
            for i, p in enumerate(db.pacientes):
                _tarjeta_paciente(grid, p, i // 3, i % 3, vista_pacientes)

    def vista_diagnostico():
        limpiar()
        set_header("🧠  Diagnóstico")
        from diagnostico import ventana_diagnostico
        ventana_diagnostico()

    def vista_historial():
        limpiar()
        set_header("📁  Historial")
        from historial import ventana_historial
        ventana_historial()

    # ── BOTONES SIDEBAR ───────────────────────────────────
    current_btn = [None]

    def _nav_btn(texto, comando):
        btn = tk.Button(
            sidebar, text=texto,
            command=lambda: None,
            bg=COLOR_SIDEBAR, fg="#c2ccd8",
            bd=0, font=("Segoe UI", 10),
            activebackground="#243447", activeforeground=COLOR_WHITE,
            anchor="w", padx=18, pady=9,
            relief="flat", cursor="hand2"
        )

        def click(b=btn, cmd=comando):
            if current_btn[0] and current_btn[0] != b:
                current_btn[0].config(bg=COLOR_SIDEBAR, fg="#c2ccd8")
            b.config(bg=COLOR_ACCENT, fg=COLOR_WHITE)
            current_btn[0] = b
            cmd()

        btn.config(command=click)
        btn.bind("<Enter>", lambda e, b=btn: b.config(
            bg="#243447" if b != current_btn[0] else COLOR_ACCENT, fg=COLOR_WHITE))
        btn.bind("<Leave>", lambda e, b=btn: b.config(
            bg=COLOR_ACCENT if b == current_btn[0] else COLOR_SIDEBAR,
            fg=COLOR_WHITE if b == current_btn[0] else "#c2ccd8"))
        btn.pack(fill="x")
        return btn

    tk.Frame(sidebar, bg="#2d3f55", height=1).pack(fill="x", padx=16, pady=8)
    tk.Label(sidebar, text="MENÚ", font=("Segoe UI", 8),
             bg=COLOR_SIDEBAR, fg="#4a6282", anchor="w").pack(fill="x", padx=18)

    if rol == "admin":
        _nav_btn("🦠  Enfermedades", vista_enfermedades)
        _nav_btn("🩺  Médicos",      vista_medicos)

    if rol == "medico":
        _nav_btn("🧑  Pacientes",    vista_pacientes)
        _nav_btn("🧠  Diagnóstico",  vista_diagnostico)
        _nav_btn("📁  Historial",    vista_historial)

    def cerrar_sesion():
        root.destroy()
        if login_root:
            login_root.deiconify()  # muestra el login de nuevo

    tk.Frame(sidebar, bg="#2d3f55", height=1).pack(fill="x", padx=16, pady=8, side="bottom")
    tk.Button(
        sidebar, text="⬅  Cerrar sesión",
        command=cerrar_sesion,
        bg="#c0392b", fg=COLOR_WHITE,
        font=("Segoe UI", 10, "bold"),
        relief="flat", pady=10, cursor="hand2"
    ).pack(fill="x", side="bottom")

    vista_inicio()
    root.mainloop()
