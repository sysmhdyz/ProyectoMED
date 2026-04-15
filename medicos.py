import tkinter as tk
from tkinter import ttk, messagebox
from db import medicos

# =========================
# VENTANA MÉDICOS
# =========================
def ventana_medicos():
    win = tk.Toplevel()
    win.title("Gestión de Médicos")
    win.geometry("650x450")

    # ================= FORMULARIO =================
    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Label(frame, text="Nombre").grid(row=0, column=0)
    entry_nombre = tk.Entry(frame)
    entry_nombre.grid(row=0, column=1)

    tk.Label(frame, text="Especialidad").grid(row=1, column=0)
    entry_esp = tk.Entry(frame)
    entry_esp.grid(row=1, column=1)

    # ================= TABLA =================
    tabla = ttk.Treeview(win, columns=("Nombre", "Especialidad"), show="headings")
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Especialidad", text="Especialidad")
    tabla.pack(pady=20, fill="x")

    # ================= FUNCIONES =================
    def actualizar_tabla():
        for row in tabla.get_children():
            tabla.delete(row)

        for m in medicos:
            tabla.insert("", "end", values=(m["nombre"], m["especialidad"]))

    def agregar():
        nombre = entry_nombre.get()
        esp = entry_esp.get()

        if nombre and esp:
            medicos.append({
                "nombre": nombre,
                "especialidad": esp
            })

            actualizar_tabla()

            entry_nombre.delete(0, tk.END)
            entry_esp.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Completa todos los campos")

    def eliminar():
        seleccionado = tabla.selection()

        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un médico")
            return

        valores = tabla.item(seleccionado)["values"]

        for m in medicos:
            if m["nombre"] == valores[0]:
                medicos.remove(m)
                break

        actualizar_tabla()

    # ================= BOTONES =================
    tk.Button(win, text="Agregar médico", command=agregar).pack(pady=5)
    tk.Button(win, text="Eliminar médico", command=eliminar).pack(pady=5)
    tk.Button(win, text="Cerrar", command=win.destroy).pack(pady=10)

    actualizar_tabla()
    win.mainloop()