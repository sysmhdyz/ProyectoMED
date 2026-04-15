import tkinter as tk
from tkinter import ttk, messagebox
from db import enfermedades

# =========================
# VENTANA ENFERMEDADES
# =========================
def ventana_enfermedades():
    win = tk.Toplevel()
    win.title("Gestión de Enfermedades")
    win.geometry("650x450")

    # ================= FORMULARIO =================
    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Label(frame, text="Nombre").grid(row=0, column=0)
    entry_nombre = tk.Entry(frame)
    entry_nombre.grid(row=0, column=1)

    tk.Label(frame, text="Descripción").grid(row=1, column=0)
    entry_desc = tk.Entry(frame)
    entry_desc.grid(row=1, column=1)

    # ================= TABLA =================
    tabla = ttk.Treeview(win, columns=("Nombre", "Descripción"), show="headings")
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Descripción", text="Descripción")
    tabla.pack(pady=20, fill="x")

    # ================= FUNCIONES =================
    def actualizar_tabla():
        for row in tabla.get_children():
            tabla.delete(row)

        for e in enfermedades:
            tabla.insert("", "end", values=(e["nombre"], e["descripcion"]))

    def agregar():
        nombre = entry_nombre.get()
        desc = entry_desc.get()

        if nombre and desc:
            enfermedades.append({
                "nombre": nombre,
                "descripcion": desc
            })

            actualizar_tabla()

            entry_nombre.delete(0, tk.END)
            entry_desc.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Completa todos los campos")

    def eliminar():
        seleccionado = tabla.selection()

        if not seleccionado:
            messagebox.showerror("Error", "Selecciona una enfermedad")
            return

        valores = tabla.item(seleccionado)["values"]

        for e in enfermedades:
            if e["nombre"] == valores[0]:
                enfermedades.remove(e)
                break

        actualizar_tabla()

    # ================= BOTONES =================
    tk.Button(win, text="Agregar enfermedad", command=agregar).pack(pady=5)
    tk.Button(win, text="Eliminar enfermedad", command=eliminar).pack(pady=5)
    tk.Button(win, text="Cerrar", command=win.destroy).pack(pady=10)

    actualizar_tabla()
    win.mainloop()