import tkinter as tk
from tkinter import messagebox
from db import usuarios
from dashboard import abrir_dashboard

# =========================
# VENTANA LOGIN
# =========================
def ventana_login():
    global entry_user, entry_pass, login_win

    login_win = tk.Tk()
    login_win.title("Login - Sistema Médico")
    login_win.geometry("300x250")

    tk.Label(login_win, text="Usuario").pack(pady=5)
    entry_user = tk.Entry(login_win)
    entry_user.pack()

    tk.Label(login_win, text="Contraseña").pack(pady=5)
    entry_pass = tk.Entry(login_win, show="*")
    entry_pass.pack()

    tk.Button(login_win, text="Iniciar sesión", command=validar_login).pack(pady=20)

    login_win.mainloop()

# =========================
# VALIDACIÓN
# =========================
def validar_login():
    user = entry_user.get()
    password = entry_pass.get()

    for u in usuarios:
        if u["usuario"] == user and u["password"] == password:
            login_win.destroy()
            abrir_dashboard(user, u["rol"])
            return

    messagebox.showerror("Error", "Usuario o contraseña incorrectos")