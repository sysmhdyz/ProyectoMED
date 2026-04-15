import tkinter as tk
from tkinter import ttk, messagebox
from db import sintomas

# =========================
# VENTANA SÍNTOMAS
# =========================
def ventana_sintomas():
    win = tk.Toplevel()
    win.title("Gestión de Síntomas")
    win.geometry("650x450")

    # ================= FORMULARIO =================
    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Label(frame, text="Síntoma").grid(row=0, column=0)
    entry_sintoma = tk.Entry(frame)
    entry_sintoma.grid(row=0, column=1)

    tk.Label(frame, text="Descripción").grid(row=1, column=0)
    entry_desc = tk.Entry(frame)
    entry_desc.grid(row=1, column=1)

    # ================= TABLA =================
    tabla = ttk.Treeview(win, columns=("Síntoma", "Descripción"), show="headings")
    tabla.heading("Síntoma", text="Síntoma")
    tabla.heading("Descripción", text="Descripción")
    tabla.pack(pady=20, fill="x")

    # ================= FUNCIONES =================
    def actualizar_tabla():
        for row in tabla.get_children():
            tabla.delete(row)

        for s in sintomas:
            tabla.insert("", "end", values=(s["nombre"], s["descripcion"]))

    def agregar():
        nombre = entry_sintoma.get()
        desc = entry_desc.get()

        if nombre and desc:
            sintomas.append({
                "nombre": nombre,
                "descripcion": desc
            })

            actualizar_tabla()

            entry_sintoma.delete(0, tk.END)
            entry_desc.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Completa todos los campos")

    def eliminar():
        seleccionado = tabla.selection()

        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un síntoma")
            return

        valores = tabla.item(seleccionado)["values"]

        for s in sintomas:
            if s["nombre"] == valores[0]:
                sintomas.remove(s)
                break

        actualizar_tabla()

    # ================= BOTONES =================
    tk.Button(win, text="Agregar síntoma", command=agregar).pack(pady=5)
    tk.Button(win, text="Eliminar síntoma", command=eliminar).pack(pady=5)
    tk.Button(win, text="Cerrar", command=win.destroy).pack(pady=10)

    actualizar_tabla()
    win.mainloop()