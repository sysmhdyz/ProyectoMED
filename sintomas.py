import tkinter as tk
from tkinter import ttk, messagebox
import db

class VentanaSintomas:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Síntomas por Enfermedad")
        self.root.geometry("600x500")

        # --- SELECCIÓN DE ENFERMEDAD ---
        tk.Label(self.root, text="1. Selecciona una Enfermedad:", font=("Arial", 11, "bold")).pack(pady=10)
        
        self.combo_enfermedades = ttk.Combobox(self.root, state="readonly", width=50)
        self.combo_enfermedades.pack(pady=5)
        self.combo_enfermedades.bind("<<ComboboxSelected>>", self.al_seleccionar_enfermedad)

        # --- CONTENEDOR PRINCIPAL (2 COLUMNAS) ---
        frame_columnas = tk.Frame(self.root)
        frame_columnas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # COLUMNA IZQUIERDA: Catálogo para agregar
        frame_izq = tk.Frame(frame_columnas)
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(frame_izq, text="2. Selecciona Síntomas (Catálogo):", font=("Arial", 10, "bold")).pack()
        
        scroll_izq = tk.Scrollbar(frame_izq)
        scroll_izq.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox_catalogo = tk.Listbox(frame_izq, selectmode=tk.MULTIPLE, yscrollcommand=scroll_izq.set)
        self.listbox_catalogo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_izq.config(command=self.listbox_catalogo.yview)

        tk.Button(frame_izq, text="Añadir a la Enfermedad ➔", command=self.agregar_sintomas, bg="#3498db", fg="white").pack(pady=10)

        # COLUMNA DERECHA: Síntomas actuales de la enfermedad
        frame_der = tk.Frame(frame_columnas)
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(frame_der, text="Síntomas Actuales:", font=("Arial", 10, "bold")).pack()
        
        scroll_der = tk.Scrollbar(frame_der)
        scroll_der.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox_actuales = tk.Listbox(frame_der, yscrollcommand=scroll_der.set)
        self.listbox_actuales.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_der.config(command=self.listbox_actuales.yview)

        tk.Button(frame_der, text="✖ Eliminar Síntoma", command=self.eliminar_sintoma, bg="#e74c3c", fg="white").pack(pady=10)

        # --- CARGAR DATOS INICIALES ---
        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        """Carga las enfermedades en el combobox y los síntomas en el catálogo."""
        # Cargar Enfermedades
        self.enfermedades_db = db.get_enfermedades()
        nombres_enfermedades = [enf['nombre'] for enf in self.enfermedades_db]
        self.combo_enfermedades['values'] = nombres_enfermedades

        # Cargar Catálogo de Síntomas
        self.catalogo_db = db.get_catalogo_sintomas()
        self.listbox_catalogo.delete(0, tk.END)
        for s in self.catalogo_db:
            self.listbox_catalogo.insert(tk.END, s['nombre'])

    def al_seleccionar_enfermedad(self, event=None):
        """Se ejecuta cuando el usuario elige una enfermedad del Combobox."""
        idx_enf = self.combo_enfermedades.current()
        if idx_enf == -1: return
        
        enfermedad_id = self.enfermedades_db[idx_enf]['id']
        self.actualizar_sintomas_actuales(enfermedad_id)

    def actualizar_sintomas_actuales(self, enfermedad_id):
        """Actualiza la lista de la derecha con los síntomas que ya tiene la enfermedad."""
        self.listbox_actuales.delete(0, tk.END)
        self.sintomas_actuales_db = db.get_sintomas_de_enfermedad(enfermedad_id)
        
        for s in self.sintomas_actuales_db:
            self.listbox_actuales.insert(tk.END, s['nombre'])

    def agregar_sintomas(self):
        """Toma los síntomas seleccionados en el catálogo y los asigna a la enfermedad."""
        idx_enf = self.combo_enfermedades.current()
        if idx_enf == -1:
            messagebox.showwarning("Atención", "Primero selecciona una enfermedad en el paso 1.")
            return

        enfermedad_id = self.enfermedades_db[idx_enf]['id']
        indices_seleccionados = self.listbox_catalogo.curselection()

        if not indices_seleccionados:
            messagebox.showwarning("Atención", "Selecciona al menos un síntoma del catálogo.")
            return

        # Obtenemos los nombres de los síntomas que la enfermedad YA TIENE para no duplicarlos
        nombres_actuales = [s['nombre'] for s in self.sintomas_actuales_db]

        agregados = 0
        for i in indices_seleccionados:
            nombre_sintoma = self.catalogo_db[i]['nombre']
            
            # Evitamos agregar duplicados a la misma enfermedad
            if nombre_sintoma not in nombres_actuales:
                db.agregar_sintoma(enfermedad_id, nombre_sintoma)
                agregados += 1

        db.cargar_todo() # Refrescar memoria de db.py
        self.listbox_catalogo.selection_clear(0, tk.END)
        self.actualizar_sintomas_actuales(enfermedad_id)

        if agregados > 0:
            messagebox.showinfo("Éxito", f"Se agregaron {agregados} síntomas nuevos a la enfermedad.")
        else:
            messagebox.showinfo("Info", "Los síntomas seleccionados ya estaban asignados a esta enfermedad.")

    def eliminar_sintoma(self):
        """Elimina un síntoma específico de la enfermedad seleccionada."""
        idx_enf = self.combo_enfermedades.current()
        idx_sintoma = self.listbox_actuales.curselection()

        if idx_enf == -1 or not idx_sintoma:
            messagebox.showwarning("Atención", "Selecciona un síntoma de la lista 'Síntomas Actuales' para eliminarlo.")
            return

        # Recuperar ID del síntoma que queremos borrar (de la tabla 'sintomas', no del catálogo)
        sintoma_id = self.sintomas_actuales_db[idx_sintoma[0]]['id']
        
        confirmacion = messagebox.askyesno("Confirmar", "¿Seguro que deseas quitar este síntoma de la enfermedad?")
        if confirmacion:
            db.eliminar_sintoma(sintoma_id)
            db.cargar_todo()
            
            enfermedad_id = self.enfermedades_db[idx_enf]['id']
            self.actualizar_sintomas_actuales(enfermedad_id)


if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaSintomas(root)
    root.mainloop()