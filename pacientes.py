import tkinter as tk
from tkinter import ttk, messagebox
from db import pacientes

# =========================
# VENTANA PACIENTES
# =========================
def ventana_pacientes():
    win = tk.Toplevel()
    win.title("Gestión de Pacientes")
    win.geometry("650x450")

    # ================= FORMULARIO =================
    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Label(frame, text="Nombre").grid(row=0, column=0)
    entry_nombre = tk.Entry(frame)
    entry_nombre.grid(row=0, column=1)

    tk.Label(frame, text="Edad").grid(row=1, column=0)
    entry_edad = tk.Entry(frame)
    entry_edad.grid(row=1, column=1)

    tk.Label(frame, text="Sexo").grid(row=2, column=0)
    entry_sexo = tk.Entry(frame)
    entry_sexo.grid(row=2, column=1)

    # ================= TABLA =================
    tabla = ttk.Treeview(win, columns=("Nombre", "Edad", "Sexo"), show="headings")
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Edad", text="Edad")
    tabla.heading("Sexo", text="Sexo")
    tabla.pack(pady=20, fill="x")

    # ================= FUNCIONES =================
    def actualizar_tabla():
        for row in tabla.get_children():
            tabla.delete(row)

        for p in pacientes:
            tabla.insert("", "end", values=(p["nombre"], p["edad"], p["sexo"]))

    def agregar():
        nombre = entry_nombre.get()
        edad = entry_edad.get()
        sexo = entry_sexo.get()

        if nombre and edad and sexo:
            pacientes.append({
                "nombre": nombre,
                "edad": edad,
                "sexo": sexo
            })

            actualizar_tabla()

            entry_nombre.delete(0, tk.END)
            entry_edad.delete(0, tk.END)
            entry_sexo.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Completa todos los campos")

    def eliminar():
        seleccionado = tabla.selection()

        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un paciente")
            return

        valores = tabla.item(seleccionado)["values"]

        for p in pacientes:
            if p["nombre"] == valores[0]:
                pacientes.remove(p)
                break

        actualizar_tabla()

    # ================= BOTONES =================
    tk.Button(win, text="Agregar", command=agregar).pack(pady=5)
    tk.Button(win, text="Eliminar", command=eliminar).pack(pady=5)
    tk.Button(win, text="Cerrar", command=win.destroy).pack(pady=10)

    actualizar_tabla()
    win.mainloop()