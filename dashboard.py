import tkinter as tk

# =========================
# DASHBOARD PRINCIPAL
# =========================
def abrir_dashboard(usuario, rol):
    dashboard = tk.Tk()
    dashboard.title("Dashboard - Sistema Médico")
    dashboard.geometry("500x400")

    # ================= HEADER =================
    tk.Label(
        dashboard,
        text="SISTEMA MÉDICO",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    tk.Label(dashboard, text=f"Usuario: {usuario}").pack()
    tk.Label(dashboard, text=f"Rol: {rol}").pack(pady=5)

    tk.Label(
        dashboard,
        text="MENÚ PRINCIPAL",
        font=("Arial", 12, "bold")
    ).pack(pady=10)

    # ================= IMPORTS (dentro para evitar errores circulares) =================
    def abrir_pacientes():
        from pacientes import ventana_pacientes
        ventana_pacientes()

    def abrir_medicos():
        from medicos import ventana_medicos
        ventana_medicos()

    def abrir_enfermedades():
        from enfermedades import ventana_enfermedades
        ventana_enfermedades()

    # ================= MENÚ ADMIN =================
    if rol == "admin":
        tk.Button(dashboard, text="Usuarios (pendiente)").pack(pady=5)
        tk.Button(dashboard, text="Enfermedades", command=abrir_enfermedades).pack(pady=5)
        tk.Button(dashboard, text="Médicos", command=abrir_medicos).pack(pady=5)

    # ================= MENÚ MÉDICO =================
    if rol == "medico":
        tk.Button(dashboard, text="Pacientes", command=abrir_pacientes).pack(pady=5)
        tk.Button(dashboard, text="Diagnóstico (pendiente)").pack(pady=5)
        tk.Button(dashboard, text="Historial (pendiente)").pack(pady=5)

    # ================= SALIR =================
    tk.Button(dashboard, text="Cerrar sesión", command=dashboard.destroy).pack(pady=20)

    dashboard.mainloop()