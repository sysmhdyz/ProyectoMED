import tkinter as tk
from tkinter import messagebox
import db  # Asegúrate de que este archivo importe tu db.py modificado

class VentanaGestionEnfermedades:
    def __init__(self, root):
        self.root = root
        self.root.title("Añadir Enfermedad y Síntomas")
        self.root.geometry("450x650")
        
        # --- CAMPOS DE ENFERMEDAD ---
        tk.Label(self.root, text="Nombre de la Enfermedad:", font=("Arial", 10, "bold")).pack(pady=5)
        self.entry_nombre = tk.Entry(self.root, width=40)
        self.entry_nombre.pack(pady=5)
        
        tk.Label(self.root, text="Descripción:", font=("Arial", 10, "bold")).pack(pady=5)
        self.entry_desc = tk.Text(self.root, width=40, height=4)
        self.entry_desc.pack(pady=5)

        # --- SECCIÓN DEL CATÁLOGO DE SÍNTOMAS ---
        tk.Label(self.root, text="Selecciona los síntomas (Catálogo):", font=("Arial", 10, "bold")).pack(pady=10)
        
        frame_lista = tk.Frame(self.root)
        frame_lista.pack(padx=20, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_sintomas = tk.Listbox(
            frame_lista, 
            selectmode=tk.MULTIPLE, 
            yscrollcommand=scrollbar.set,
            font=("Arial", 10)
        )
        self.listbox_sintomas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox_sintomas.yview)

        # Cargamos la lista
        self.cargar_catalogo()

        # --- AGREGAR NUEVO SÍNTOMA AL CATÁLOGO ---
        frame_nuevo = tk.Frame(self.root)
        frame_nuevo.pack(pady=10)
        
        self.entry_nuevo_sintoma = tk.Entry(frame_nuevo, width=25)
        self.entry_nuevo_sintoma.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_nuevo, text="Añadir al Catálogo", command=self.agregar_al_catalogo, bg="#3498db", fg="white").pack(side=tk.LEFT)

        # --- BOTÓN DE GUARDADO FINAL ---
        tk.Button(
            self.root, 
            text="Guardar Enfermedad Completa", 
            command=self.guardar_enfermedad_completa,
            bg="#2ecc71", fg="white", font=("Arial", 11, "bold")
        ).pack(pady=20)

    def cargar_catalogo(self):
        """Limpia el Listbox y carga los síntomas desde el catálogo de la DB."""
        self.listbox_sintomas.delete(0, tk.END)
        self.datos_catalogo = db.get_catalogo_sintomas()
        
        for s in self.datos_catalogo:
            self.listbox_sintomas.insert(tk.END, s['nombre'])

    def agregar_al_catalogo(self):
        """Permite al usuario registrar un síntoma nuevo para el futuro."""
        nuevo = self.entry_nuevo_sintoma.get().strip().capitalize()
        if not nuevo:
            messagebox.showwarning("Error", "Escribe un síntoma primero.")
            return
            
        exito = db.agregar_sintoma_catalogo(nuevo)
        if exito:
            messagebox.showinfo("Éxito", f"'{nuevo}' agregado al catálogo de opciones.")
            self.entry_nuevo_sintoma.delete(0, tk.END)
            self.cargar_catalogo() # Refresca la lista visual inmediatamente
        else:
            messagebox.showerror("Error", "Este síntoma ya existe en el catálogo.")

    def guardar_enfermedad_completa(self):
        """Guarda la enfermedad en la DB y le asigna los síntomas seleccionados."""
        nombre_enf = self.entry_nombre.get().strip()
        desc_enf = self.entry_desc.get("1.0", tk.END).strip()
        indices_seleccionados = self.listbox_sintomas.curselection()

        if not nombre_enf or not desc_enf:
            messagebox.showwarning("Faltan datos", "El nombre y descripción son obligatorios.")
            return
            
        if not indices_seleccionados:
            messagebox.showwarning("Faltan síntomas", "Selecciona al menos un síntoma de la lista.")
            return

        # 1. Guardamos la enfermedad. db.py nos devuelve el ID recién creado.
        enfermedad_id = db.agregar_enfermedad(nombre_enf, desc_enf)

        # 2. Vinculamos cada síntoma seleccionado a esa nueva enfermedad utilizando la función nativa de tu DB.
        for i in indices_seleccionados:
            nombre_sintoma = self.datos_catalogo[i]['nombre']
            db.agregar_sintoma(enfermedad_id, nombre_sintoma)

        # Actualizamos la memoria global de db.py
        db.cargar_todo()

        messagebox.showinfo("¡Guardado!", f"Enfermedad '{nombre_enf}' guardada con éxito con sus síntomas.")
        
        # Limpiar campos para la siguiente
        self.entry_nombre.delete(0, tk.END)
        self.entry_desc.delete("1.0", tk.END)
        self.listbox_sintomas.selection_clear(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaGestionEnfermedades(root)
    root.mainloop()