import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import glob


class CSVMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unificador de CSV - Unión Completa")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Variables
        self.csv_dir = tk.StringVar()
        self.output_file = tk.StringVar()
        self.csv_files = []
        self.selected_files = {}  # Diccionario para rastrear archivos seleccionados
        self.file_paths = {}  # Diccionario para mantener las rutas completas

        # Create UI
        self.create_widgets()

    def select_all_files(self):
        """Seleccionar todos los archivos en el treeview"""
        for item in self.csv_tree.get_children():
            self.selected_files[item] = True
            values = list(self.csv_tree.item(item, "values"))
            values[0] = "✓"
            self.csv_tree.item(item, values=values)

    def deselect_all_files(self):
        """Deseleccionar todos los archivos en el treeview"""
        for item in self.csv_tree.get_children():
            self.selected_files[item] = False
            values = list(self.csv_tree.item(item, "values"))
            values[0] = ""
            self.csv_tree.item(item, values=values)

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sección de directorio de entrada
        input_frame = ttk.LabelFrame(
            main_frame, text="Directorio de Entrada", padding="10"
        )
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Carpeta con CSVs:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Entry(input_frame, textvariable=self.csv_dir, width=50).grid(
            row=0, column=1, sticky=tk.W + tk.E, padx=5, pady=5
        )
        ttk.Button(input_frame, text="Examinar...", command=self.browse_directory).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Sección de archivos CSV
        csv_frame = ttk.LabelFrame(
            main_frame, text="Archivos CSV Encontrados", padding="10"
        )
        csv_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Crear un treeview para mostrar los archivos CSV con checkbox
        self.csv_tree = ttk.Treeview(
            csv_frame, columns=("selected", "filename"), show="headings"
        )
        self.csv_tree.heading("selected", text="Seleccionar")
        self.csv_tree.heading("filename", text="Nombre del archivo")

        # Ajustar el ancho de las columnas
        self.csv_tree.column("selected", width=80, anchor=tk.CENTER)
        self.csv_tree.column("filename", width=300)

        self.csv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Añadir evento de clic para manejar los checkboxes
        self.csv_tree.bind("<ButtonRelease-1>", self.handle_checkbox_click)

        # Añadir barra de desplazamiento al treeview
        scrollbar = ttk.Scrollbar(
            csv_frame, orient=tk.VERTICAL, command=self.csv_tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.csv_tree.configure(yscrollcommand=scrollbar.set)

        # Contador de archivos CSV
        self.count_label = ttk.Label(csv_frame, text="Se encontraron 0 archivos CSV")
        self.count_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=5, pady=5)

        # Sección de configuración de salida
        output_frame = ttk.LabelFrame(
            main_frame, text="Configuración de Salida", padding="10"
        )
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text="Archivo de salida:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Entry(output_frame, textvariable=self.output_file, width=50).grid(
            row=0, column=1, sticky=tk.W + tk.E, padx=5, pady=5
        )
        ttk.Button(
            output_frame, text="Examinar...", command=self.browse_output_file
        ).grid(row=0, column=2, padx=5, pady=5)

        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame, text="Unir archivos CSV", command=self.merge_csv_files
        ).pack(side=tk.RIGHT, padx=5)
        ttk.Button(
            button_frame, text="Escanear carpeta", command=self.scan_directory
        ).pack(side=tk.RIGHT, padx=5)

        # Botones para selección
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            selection_frame, text="Seleccionar todos", command=self.select_all_files
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            selection_frame, text="Deseleccionar todos", command=self.deselect_all_files
        ).pack(side=tk.LEFT, padx=5)

    def browse_directory(self):
        directory = filedialog.askdirectory(
            title="Seleccionar carpeta con archivos CSV"
        )
        if directory:
            self.csv_dir.set(directory)
            self.scan_directory()

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Guardar CSV unificado como",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            defaultextension=".csv",
        )
        if file_path:
            self.output_file.set(file_path)

    def scan_directory(self):
        directory = self.csv_dir.get()
        if not directory:
            messagebox.showerror("Error", "Por favor, selecciona primero una carpeta")
            return

        # Eliminar archivos previamente listados
        for item in self.csv_tree.get_children():
            self.csv_tree.delete(item)

        # Limpiar selecciones anteriores
        self.selected_files = {}
        self.file_paths = {}  # Diccionario para mantener las rutas completas

        # Encontrar todos los archivos CSV en el directorio
        self.csv_files = glob.glob(os.path.join(directory, "*.csv"))

        # Mostrar los archivos encontrados con checkboxes seleccionados por defecto
        for file_path in self.csv_files:
            filename = os.path.basename(file_path)
            item_id = self.csv_tree.insert("", tk.END, values=("✓", filename))
            self.selected_files[item_id] = True  # Todos seleccionados por defecto
            self.file_paths[item_id] = file_path  # Guardar la ruta completa

        # Actualizar el contador de archivos
        self.count_label.config(
            text=f"Se encontraron {len(self.csv_files)} archivos CSV"
        )

    def handle_checkbox_click(self, event):
        """Manejar clics en los checkboxes del treeview"""
        # Determinar si el clic fue en la columna de checkbox
        region = self.csv_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.csv_tree.identify_column(event.x)
            if column == "#1":  # Primera columna (checkbox)
                item = self.csv_tree.identify_row(event.y)
                if item:
                    # Cambiar el estado del checkbox
                    current_state = self.selected_files.get(item, True)
                    new_state = not current_state
                    self.selected_files[item] = new_state

                    # Actualizar el valor en el treeview
                    values = list(self.csv_tree.item(item, "values"))
                    values[0] = "✓" if new_state else ""
                    self.csv_tree.item(item, values=values)

    def merge_csv_files(self):
        if not self.csv_files:
            messagebox.showerror(
                "Error",
                "No se encontraron archivos CSV. Por favor, escanea una carpeta con archivos CSV.",
            )
            return

        if not self.output_file.get():
            messagebox.showerror(
                "Error",
                "Por favor, selecciona una ubicación para el archivo de salida.",
            )
            return

        # Obtener solo los archivos seleccionados
        selected_csv_files = []
        for item in self.csv_tree.get_children():
            if self.selected_files.get(item, False):
                # Obtener la ruta completa desde el diccionario
                file_path = self.file_paths.get(item)
                if file_path:
                    selected_csv_files.append(file_path)

        if not selected_csv_files:
            messagebox.showerror(
                "Error", "No hay archivos CSV seleccionados para unir."
            )
            return

        try:
            # Mostrar indicador de progreso
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Unión en progreso")
            progress_window.geometry("300x100")
            progress_window.transient(self.root)
            progress_window.grab_set()

            ttk.Label(progress_window, text="Uniendo archivos CSV...").pack(pady=10)
            progress = ttk.Progressbar(
                progress_window, orient="horizontal", length=200, mode="indeterminate"
            )
            progress.pack(pady=10)
            progress.start()

            # Actualizar UI
            self.root.update_idletasks()

            # Realizar la unión completa solo con los archivos seleccionados
            result_df = self.full_join_csv_files(selected_csv_files)

            # Guardar el resultado
            result_df.to_csv(self.output_file.get(), index=False)

            # Cerrar ventana de progreso
            progress_window.destroy()

            messagebox.showinfo(
                "Éxito",
                f"Se unieron con éxito {len(selected_csv_files)} archivos CSV en {self.output_file.get()}",
            )

        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error durante la unión: {str(e)}"
            )

    def full_join_csv_files(self, files_to_process):
        """Realiza una unión completa de los archivos CSV seleccionados, manteniendo todas las columnas de todos los archivos."""
        if not files_to_process:
            return pd.DataFrame()

        # Comenzar con un dataframe vacío
        result_df = pd.DataFrame()

        # Procesar cada archivo CSV seleccionado
        for file_path in files_to_process:
            try:
                # Leer el CSV actual
                current_df = pd.read_csv(file_path, encoding="utf-8", low_memory=False)

                # Para el primer archivo, simplemente usarlo como punto de partida
                if result_df.empty:
                    result_df = current_df
                else:
                    # Obtener todos los nombres de columna únicos
                    all_columns = list(
                        set(result_df.columns).union(set(current_df.columns))
                    )

                    # Asegurarse de que todas las columnas existan en ambos dataframes (rellenar con None los valores faltantes)
                    for col in all_columns:
                        if col not in result_df.columns:
                            result_df[col] = None
                        if col not in current_df.columns:
                            current_df[col] = None

                    # Concatenar los dataframes
                    result_df = pd.concat([result_df, current_df], ignore_index=True)

            except Exception as e:
                print(f"Error al procesar el archivo {file_path}: {str(e)}")

        return result_df


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVMergerApp(root)
    root.mainloop()
