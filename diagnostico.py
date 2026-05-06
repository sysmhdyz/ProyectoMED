import tkinter as tk
from tkinter import messagebox, ttk
import db
from motor_inferencia import diagnosticar

COLOR_BG      = "#f0f4f8"
COLOR_WHITE   = "#ffffff"
COLOR_ACCENT  = "#2c7be5"
COLOR_TEXT    = "#2d3748"
COLOR_SUBTEXT = "#718096"
COLOR_GREEN   = "#17a589"
COLOR_YELLOW  = "#e67e22"
COLOR_RED     = "#e74c3c"

def ventana_diagnostico():
    win = tk.Toplevel()
    win.title("Diagnóstico Médico")
    win.geometry("820x600")
    win.configure(bg=COLOR_BG)
    win.resizable(True, True)

    # ── TÍTULO ────────────────────────────────────────────
    header = tk.Frame(win, bg=COLOR_WHITE, height=52)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="🧠  Diagnóstico Médico",
             font=("Segoe UI", 14, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT
             ).pack(side="left", padx=20, pady=12)

    # ── LAYOUT PRINCIPAL ─────────────────────────────────
    body = tk.Frame(win, bg=COLOR_BG)
    body.pack(fill="both", expand=True, padx=16, pady=12)

    left  = tk.Frame(body, bg=COLOR_BG)
    right = tk.Frame(body, bg=COLOR_BG)
    left.pack(side="left", fill="both", expand=True, padx=(0, 8))
    right.pack(side="right", fill="both", expand=True, padx=(8, 0))

    # ── PANEL IZQUIERDO: selección ─────────────────────
    # Paciente
    pac_frame = tk.Frame(left, bg=COLOR_WHITE)
    pac_frame.pack(fill="x", pady=(0, 10))
    tk.Label(pac_frame, text="Paciente", font=("Segoe UI", 9),
             bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w").pack(fill="x", padx=14, pady=(10, 2))

    db.cargar_todo()
    paciente_var = tk.StringVar()
    combo = ttk.Combobox(pac_frame, textvariable=paciente_var, state="readonly",
                         font=("Segoe UI", 10))
    combo["values"] = [p["nombre"] for p in db.pacientes]
    combo.pack(fill="x", padx=14, pady=(0, 12), ipady=4)

    # Síntomas disponibles (checkboxes agrupados por enfermedad)
    sint_frame_outer = tk.Frame(left, bg=COLOR_WHITE)
    sint_frame_outer.pack(fill="both", expand=True)

    tk.Label(sint_frame_outer, text="Síntomas del paciente",
             font=("Segoe UI", 10, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT, anchor="w"
             ).pack(fill="x", padx=14, pady=(10, 4))
    tk.Label(sint_frame_outer, text="Marca los síntomas que presenta el paciente",
             font=("Segoe UI", 8), bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w"
             ).pack(fill="x", padx=14, pady=(0, 8))

    # Canvas con scroll para los checkboxes
    canvas = tk.Canvas(sint_frame_outer, bg=COLOR_WHITE, highlightthickness=0)
    sb = ttk.Scrollbar(sint_frame_outer, orient="vertical", command=canvas.yview)
    check_frame = tk.Frame(canvas, bg=COLOR_WHITE)
    check_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=check_frame, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True, padx=14, pady=(0, 14))
    sb.pack(side="right", fill="y", pady=(0, 14))
    canvas.bind_all("<MouseWheel>",
        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # Variables de los checkboxes
    check_vars = {}   # sintoma_id -> BooleanVar

    def cargar_checkboxes():
        for w in check_frame.winfo_children():
            w.destroy()
        check_vars.clear()

        db.cargar_todo()
        enfermedades = db.get_enfermedades()

        if not enfermedades:
            tk.Label(check_frame, text="No hay enfermedades ni síntomas registrados.",
                     font=("Segoe UI", 9), bg=COLOR_WHITE, fg=COLOR_SUBTEXT
                     ).pack(anchor="w", padx=4, pady=8)
            return

        for enf in enfermedades:
            sint_list = db.get_sintomas_de_enfermedad(enf["id"])
            if not sint_list:
                continue

            # Encabezado de enfermedad
            tk.Label(check_frame, text=f"  {enf['nombre']}",
                     font=("Segoe UI", 9, "bold"), bg="#f8f9fa", fg=COLOR_ACCENT,
                     anchor="w", relief="flat"
                     ).pack(fill="x", pady=(6, 2))

            for s in sint_list:
                var = tk.BooleanVar()
                check_vars[s["id"]] = (var, s["nombre"])
                tk.Checkbutton(
                    check_frame, text=f"    {s['nombre']}",
                    variable=var, bg=COLOR_WHITE,
                    font=("Segoe UI", 9), fg=COLOR_TEXT,
                    activebackground=COLOR_WHITE, anchor="w"
                ).pack(fill="x", pady=1)

    cargar_checkboxes()

    # ── PANEL DERECHO: resultados ──────────────────────
    res_frame = tk.Frame(right, bg=COLOR_WHITE)
    res_frame.pack(fill="both", expand=True)

    tk.Label(res_frame, text="Resultados del diagnóstico",
             font=("Segoe UI", 10, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT, anchor="w"
             ).pack(fill="x", padx=14, pady=(10, 4))

    res_canvas = tk.Canvas(res_frame, bg=COLOR_WHITE, highlightthickness=0)
    res_sb = ttk.Scrollbar(res_frame, orient="vertical", command=res_canvas.yview)
    res_inner = tk.Frame(res_canvas, bg=COLOR_WHITE)
    res_inner.bind("<Configure>",
        lambda e: res_canvas.configure(scrollregion=res_canvas.bbox("all")))
    res_canvas.create_window((0, 0), window=res_inner, anchor="nw")
    res_canvas.configure(yscrollcommand=res_sb.set)
    res_canvas.pack(side="left", fill="both", expand=True, padx=14, pady=(0, 14))
    res_sb.pack(side="right", fill="y", pady=(0, 14))

    # Placeholder inicial
    placeholder = tk.Label(res_inner,
        text="Los resultados aparecerán\naquí después del diagnóstico.",
        font=("Segoe UI", 10), bg=COLOR_WHITE, fg="#cbd5e0", justify="center")
    placeholder.pack(expand=True, pady=60)

    # ── FUNCIÓN DIAGNÓSTICO ───────────────────────────
    def generar():
        paciente = paciente_var.get()
        if not paciente:
            messagebox.showerror("Error", "Selecciona un paciente", parent=win)
            return

        # Recolectar síntomas marcados
        sintomas_sel = [nombre for (var, nombre) in check_vars.values() if var.get()]

        if not sintomas_sel:
            messagebox.showerror("Error", "Marca al menos un síntoma", parent=win)
            return

        resultados = diagnosticar(sintomas_sel)

        # Limpiar resultados anteriores
        for w in res_inner.winfo_children():
            w.destroy()

        if not resultados:
            tk.Label(res_inner,
                     text="⚠️  Sin coincidencias\n\nNinguna enfermedad registrada\ncoincide con los síntomas seleccionados.",
                     font=("Segoe UI", 10), bg=COLOR_WHITE, fg=COLOR_SUBTEXT, justify="center"
                     ).pack(pady=40)
            return

        tk.Label(res_inner, text=f"Paciente: {paciente}",
                 font=("Segoe UI", 10, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT, anchor="w"
                 ).pack(fill="x", pady=(4, 2))
        tk.Label(res_inner, text=f"Síntomas evaluados: {len(sintomas_sel)}",
                 font=("Segoe UI", 9), bg=COLOR_WHITE, fg=COLOR_SUBTEXT, anchor="w"
                 ).pack(fill="x", pady=(0, 10))

        # Guardar el resultado principal en BD
        mejor = resultados[0]
        db.agregar_diagnostico(paciente, mejor["enfermedad"], mejor["probabilidad"])

        # Mostrar cada resultado como tarjeta
        for r in resultados:
            prob = r["probabilidad"]

            if prob >= 70:
                color_barra = COLOR_RED
                nivel = "Alta probabilidad"
            elif prob >= 40:
                color_barra = COLOR_YELLOW
                nivel = "Probabilidad media"
            else:
                color_barra = COLOR_GREEN
                nivel = "Probabilidad baja"

            card = tk.Frame(res_inner, bg="#f8f9fa", relief="flat")
            card.pack(fill="x", pady=4)

            # Barra de color lateral
            tk.Frame(card, bg=color_barra, width=5).pack(side="left", fill="y")

            info = tk.Frame(card, bg="#f8f9fa")
            info.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            top_row = tk.Frame(info, bg="#f8f9fa")
            top_row.pack(fill="x")
            tk.Label(top_row, text=r["enfermedad"],
                     font=("Segoe UI", 11, "bold"), bg="#f8f9fa", fg=COLOR_TEXT
                     ).pack(side="left")
            tk.Label(top_row, text=f"{prob}%",
                     font=("Segoe UI", 11, "bold"), bg="#f8f9fa", fg=color_barra
                     ).pack(side="right")

            tk.Label(info, text=f"{nivel}  •  {r['coincidencias']} de {r['total_sintomas']} síntomas coinciden",
                     font=("Segoe UI", 8), bg="#f8f9fa", fg=COLOR_SUBTEXT, anchor="w"
                     ).pack(fill="x", pady=(2, 4))

            # Barra de progreso visual
            barra_bg = tk.Frame(info, bg="#e2e8f0", height=6)
            barra_bg.pack(fill="x")
            barra_bg.update_idletasks()
            ancho = int(barra_bg.winfo_width() * prob / 100) or int(200 * prob / 100)
            tk.Frame(barra_bg, bg=color_barra, height=6, width=ancho).place(x=0, y=0, rely=0)

            # Síntomas que coincidieron
            if r["sintomas_coinciden"]:
                tk.Label(info,
                         text="Coincide con: " + ", ".join(r["sintomas_coinciden"]),
                         font=("Segoe UI", 8), bg="#f8f9fa", fg=COLOR_SUBTEXT,
                         wraplength=260, justify="left", anchor="w"
                         ).pack(fill="x", pady=(4, 0))

    # ── BOTÓN ────────────────────────────────────────────
    btn_frame = tk.Frame(win, bg=COLOR_BG)
    btn_frame.pack(fill="x", padx=16, pady=(0, 12))

    tk.Button(btn_frame, text="🔍  Generar diagnóstico",
              command=generar,
              bg=COLOR_ACCENT, fg=COLOR_WHITE,
              font=("Segoe UI", 11, "bold"),
              relief="flat", padx=20, pady=8, cursor="hand2"
              ).pack(side="left")

    tk.Button(btn_frame, text="↺  Refrescar síntomas",
              command=cargar_checkboxes,
              bg="#e2e8f0", fg=COLOR_TEXT,
              font=("Segoe UI", 9),
              relief="flat", padx=12, pady=8, cursor="hand2"
              ).pack(side="left", padx=10)

    win.mainloop()
