import tkinter as tk
from tkinter import messagebox
from dashboard import abrir_dashboard
from db import usuarios

# =========================
# LOGIN PROFESIONAL
# =========================
def ventana_login():
    global entry_user, entry_pass, root

    root = tk.Tk()
    root.title("Sistema Médico")
    root.geometry("400x350")
    root.configure(bg="#f4f6f9")

    root.eval('tk::PlaceWindow . center')

    # ================= CARD =================
    card = tk.Frame(root, bg="white", bd=2, relief="ridge")
    card.place(relx=0.5, rely=0.5, anchor="center", width=300, height=250)

    # ================= TÍTULO =================
    tk.Label(
        card,
        text="🏥 Sistema Médico",
        font=("Arial", 14, "bold"),
        bg="white",
        fg="#2c7be5"
    ).pack(pady=10)

    # ================= USUARIO =================
    tk.Label(card, text="Usuario", bg="white", font=("Arial", 10)).pack(pady=5)
    entry_user = tk.Entry(card, font=("Arial", 10), bd=2, relief="groove")
    entry_user.pack(pady=5)

    # ================= PASSWORD =================
    tk.Label(card, text="Contraseña", bg="white", font=("Arial", 10)).pack(pady=5)
    entry_pass = tk.Entry(card, show="*", font=("Arial", 10), bd=2, relief="groove")
    entry_pass.pack(pady=5)

    # ================= BOTÓN =================
    tk.Button(
        card,
        text="Iniciar sesión",
        command=validar_login,
        bg="#2c7be5",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=10,
        pady=5
    ).pack(pady=15)

    root.mainloop()

# =========================
# VALIDACIÓN
# =========================
def validar_login():
    user = entry_user.get().strip()
    password = entry_pass.get().strip()

    if not user or not password:
        messagebox.showerror("Error", "Completa todos los campos")
        return

    for u in usuarios:
        if u["usuario"] == user and u["password"] == password:
            root.withdraw()
            abrir_dashboard(user, u["rol"], login_root=root)
            return

    messagebox.showerror("Error", "Usuario o contraseña incorrectos")
