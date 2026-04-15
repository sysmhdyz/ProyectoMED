import tkinter as tk
from tkinter import ttk
from db import historial

# =========================
# VENTANA HISTORIAL
# =========================
def ventana_historial():
    win = tk.Toplevel()
    win.title("Historial Médico")
    win.geometry("700x450")

    # ================= TABLA =================
    tabla = ttk.Treeview(
        win,
        columns=("Paciente", "Enfermedad", "Probabilidad"),
        show="headings"
    )

    tabla.heading("Paciente", text="Paciente")
    tabla.heading("Enfermedad", text="Enfermedad")
    tabla.heading("Probabilidad", text="Probabilidad")

    tabla.pack(pady=20, fill="x")

    # ================= CARGAR DATOS =================
    def cargar():
        for row in tabla.get_children():
            tabla.delete(row)

        for h in historial:
            tabla.insert(
                "",
                "end",
                values=(h["paciente"], h["enfermedad"], h["probabilidad"])
            )

    # ================= BOTÓN =================
    tk.Button(win, text="Actualizar historial", command=cargar).pack(pady=10)
    tk.Button(win, text="Cerrar", command=win.destroy).pack(pady=5)

    cargar()
    win.mainloop()