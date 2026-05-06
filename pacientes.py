import tkinter as tk
from tkinter import ttk, messagebox
import db  # IMPORTANTE: Importamos el módulo db completo, no solo la lista

# =========================
# PALETA Y FUENTES (Para coincidir con el Dashboard)
# =========================
COLOR_BG       = "#f0f4f8"
COLOR_WHITE    = "#ffffff"
COLOR_ACCENT   = "#2c7be5"
COLOR_DANGER   = "#e74c3c"
COLOR_TEXT     = "#2d3748"
FONT_BODY      = ("Segoe UI", 10)
FONT_BTN       = ("Segoe UI", 10, "bold")
FONT_TITLE     = ("Segoe UI", 14, "bold")

# =========================
# VENTANA PACIENTES
# =========================
def ventana_pacientes():
    win = tk.Toplevel()
    win.title("Gestión de Pacientes")
    win.geometry("750x550")
    win.configure(bg=COLOR_BG)
    win.grab_set() # Evita que el usuario clickee el dashboard mientras esta ventana está abierta

    # ================= TÍTULO =================
    tk.Label(win, text="🧑 Gestión de Pacientes", font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=(20, 10))

    # ================= FORMULARIO =================
    frame = tk.Frame(win, bg=COLOR_WHITE, relief="solid", bd=1)
    frame.pack(pady=10, padx=20, fill="x", ipadx=10, ipady=10)

    # Organizado en una sola fila para que se vea moderno
    tk.Label(frame, text="Nombre:", font=FONT_BODY, bg=COLOR_WHITE, fg=COLOR_TEXT).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="e")
    entry_nombre = tk.Entry(frame, font=FONT_BODY, width=25, relief="solid", bd=1)
    entry_nombre.grid(row=0, column=1, padx=5, pady=10)

    tk.Label(frame, text="Edad:", font=FONT_BODY, bg=COLOR_WHITE, fg=COLOR_TEXT).grid(row=0, column=2, padx=(15, 5), pady=10, sticky="e")
    entry_edad = tk.Entry(frame, font=FONT_BODY, width=8, relief="solid", bd=1)
    entry_edad.grid(row=0, column=3, padx=5, pady=10)

    tk.Label(frame, text="Sexo:", font=FONT_BODY, bg=COLOR_WHITE, fg=COLOR_TEXT).grid(row=0, column=4, padx=(15, 5), pady=10, sticky="e")
    # Uso de Combobox para elegir opciones predefinidas
    combo_sexo = ttk.Combobox(frame, values=["Masculino", "Femenino", "Otro"], font=FONT_BODY, width=12, state="readonly")
    combo_sexo.grid(row=0, column=5, padx=5, pady=10)

    # ================= BOTONES SUPERIORES =================
    frame_btns = tk.Frame(win, bg=COLOR_BG)
    frame_btns.pack(fill="x", padx=20, pady=5)

    # ================= TABLA =================
    frame_tabla = tk.Frame(win, bg=COLOR_BG)
    frame_tabla.pack(pady=(5, 15), padx=20, fill="both", expand=True)

    scroll = ttk.Scrollbar(frame_tabla, orient="vertical")
    scroll.pack(side="right", fill="y")

    # Estilizando la tabla
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    style.configure("Treeview", font=FONT_BODY, rowheight=28)

    tabla = ttk.Treeview(frame_tabla, columns=("Nombre", "Edad", "Sexo"), show="headings", yscrollcommand=scroll.set)
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Edad", text="Edad")
    tabla.heading("Sexo", text="Sexo")
    
    tabla.column("Nombre", width=350)
    tabla.column("Edad", width=100, anchor="center")
    tabla.column("Sexo", width=150, anchor="center")
    
    tabla.pack(side="left", fill="both", expand=True)
    scroll.config(command=tabla.yview)

    # ================= FUNCIONES =================
    def actualizar_tabla():
        for row in tabla.get_children():
            tabla.delete(row)

        db.cargar_todo() # Sincroniza la información fresca desde la DB SQLite
        for p in db.pacientes:
            tabla.insert("", "end", values=(p["nombre"], p["edad"], p["sexo"]))

    def agregar():
        nombre = entry_nombre.get().strip()
        edad = entry_edad.get().strip()
        sexo = combo_sexo.get().strip()

        if nombre and edad and sexo:
            try:
                # Se guarda en SQLite usando la función de tu db.py
                db.agregar_paciente(nombre, edad, sexo)
                actualizar_tabla()

                # Limpiar formulario
                entry_nombre.delete(0, tk.END)
                entry_edad.delete(0, tk.END)
                combo_sexo.set('')
            except Exception as e:
                messagebox.showerror("Error DB", f"No se pudo guardar: {e}", parent=win)
        else:
            messagebox.showerror("Error", "Completa todos los campos", parent=win)

    def eliminar():
        seleccionado = tabla.selection()

        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un paciente de la tabla", parent=win)
            return

        valores = tabla.item(seleccionado)["values"]
        nombre_paciente = valores[0]

        confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar al paciente {nombre_paciente}?", parent=win)
        if confirmar:
            # Se elimina de SQLite usando la función de tu db.py
            db.eliminar_paciente(nombre_paciente)
            actualizar_tabla()

    # Ubicando botones con diseño moderno
    tk.Button(frame_btns, text="＋ Agregar Paciente", command=agregar, bg=COLOR_ACCENT, fg=COLOR_WHITE, font=FONT_BTN, relief="flat", padx=15, pady=4, cursor="hand2").pack(side="left", padx=(0, 10))
    tk.Button(frame_btns, text="🗑 Eliminar", command=eliminar, bg=COLOR_DANGER, fg=COLOR_WHITE, font=FONT_BTN, relief="flat", padx=15, pady=4, cursor="hand2").pack(side="left")
    tk.Button(win, text="Cerrar", command=win.destroy, bg="#cbd5e0", fg=COLOR_TEXT, font=FONT_BTN, relief="flat", padx=20, pady=5, cursor="hand2").pack(pady=10)

    # Cargar los datos iniciales
    actualizar_tabla()