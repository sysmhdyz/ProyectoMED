import tkinter as tk
from tkinter import messagebox, ttk
from db import pacientes
from motor_inferencia import diagnosticar

# =========================
# VENTANA DIAGNÓSTICO
# =========================
def ventana_diagnostico():
    win = tk.Toplevel()
    win.title("Diagnóstico Médico")
    win.geometry("700x500")

    # ================= PACIENTES =================
    tk.Label(win, text="Selecciona paciente").pack()

    paciente_var = tk.StringVar()
    combo = ttk.Combobox(win, textvariable=paciente_var)

    combo["values"] = [p["nombre"] for p in pacientes]
    combo.pack(pady=10)

    # ================= SÍNTOMAS =================
    tk.Label(win, text="Síntomas (separados por coma)").pack()

    entry_sintomas = tk.Entry(win, width=50)
    entry_sintomas.pack(pady=10)

    # ================= RESULTADOS =================
    resultado = tk.Text(win, height=15, width=70)
    resultado.pack(pady=10)

    # ================= FUNCIONES =================
    def generar_diagnostico():
        paciente = paciente_var.get()
        sintomas = entry_sintomas.get().split(",")

        sintomas = [s.strip() for s in sintomas if s.strip() != ""]

        if not paciente:
            messagebox.showerror("Error", "Selecciona un paciente")
            return

        if not sintomas:
            messagebox.showerror("Error", "Ingresa síntomas")
            return

        resultados = diagnosticar(sintomas)

        resultado.delete("1.0", tk.END)
        resultado.insert(tk.END, f"Paciente: {paciente}\n\n")
        resultado.insert(tk.END, "RESULTADOS POSIBLES:\n\n")

        for r in resultados:
            resultado.insert(
                tk.END,
                f"- {r['enfermedad']} → {r['probabilidad']}%\n"
            )

    # ================= BOTÓN =================
    tk.Button(win, text="Generar diagnóstico", command=generar_diagnostico).pack(pady=10)
    tk.Button(win, text="Cerrar", command=win.destroy).pack(pady=5)

    win.mainloop()