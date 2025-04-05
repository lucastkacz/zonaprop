import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import glob


class CSVCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Combinador de archivos CSV")
        self.root.geometry("650x580")
        self.root.resizable(True, True)

        # Variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.csv_files = []
        self.csv_checkboxes = {}
        self.property_count = 0
        self.development_count = 0

        # Crear interfaz
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sección para seleccionar carpeta de entrada
        ttk.Label(
            main_frame, text="Carpeta con archivos CSV:", font=("Arial", 10)
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        main_frame.columnconfigure(0, weight=1)

        ttk.Entry(input_frame, textvariable=self.input_folder, width=50).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(
            input_frame, text="Examinar...", command=self.select_input_folder
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # Sección para mostrar archivos CSV encontrados
        ttk.Label(
            main_frame, text="Archivos CSV encontrados:", font=("Arial", 10)
        ).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        # Frame para la tabla de archivos
        files_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        files_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(3, weight=1)

        # Crear un canvas con scrollbar para la tabla de archivos
        canvas = tk.Canvas(files_frame, height=180)
        scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=canvas.yview)
        self.files_table_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configurar el frame dentro del canvas
        canvas_window = canvas.create_window(
            (0, 0), window=self.files_table_frame, anchor="nw"
        )

        # Asegurar que el canvas y el frame interno se ajusten correctamente
        self.files_table_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width)
        )

        # Botones para seleccionar/deseleccionar todos
        select_frame = ttk.Frame(main_frame)
        select_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(
            select_frame, text="Seleccionar Todos", command=self.select_all_files
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            select_frame, text="Deseleccionar Todos", command=self.deselect_all_files
        ).pack(side=tk.LEFT)

        # Sección para mostrar conteo de tipos
        self.counts_frame = ttk.LabelFrame(main_frame, text="Distribución de Tipos")
        self.counts_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Etiquetas para mostrar conteo (se llenarán al cargar los archivos)
        self.property_label = ttk.Label(
            self.counts_frame, text="PROPERTY: 0", font=("Arial", 10)
        )
        self.property_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.development_label = ttk.Label(
            self.counts_frame, text="DEVELOPMENT: 0", font=("Arial", 10)
        )
        self.development_label.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Sección para seleccionar carpeta de salida
        ttk.Label(
            main_frame, text="Carpeta para archivos CSV de salida:", font=("Arial", 10)
        ).grid(row=6, column=0, sticky=tk.W, pady=(0, 5))

        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Entry(output_frame, textvariable=self.output_folder, width=50).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(
            output_frame, text="Examinar...", command=self.select_output_folder
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # Información sobre archivos que se generarán
        output_info_frame = ttk.Frame(main_frame)
        output_info_frame.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(
            output_info_frame, text="Se generarán dos archivos:", font=("Arial", 9)
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(
            output_info_frame,
            text="- Propiedades.csv (para registros de tipo PROPERTY)",
            font=("Arial", 9),
        ).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(
            output_info_frame,
            text="- Desarrollos.csv (para registros de tipo DEVELOPMENT)",
            font=("Arial", 9),
        ).grid(row=2, column=0, sticky=tk.W)

        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            main_frame, variable=self.progress_var, maximum=100
        )
        self.progress.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Botón para ejecutar
        ttk.Button(
            main_frame,
            text="Combinar y separar archivos CSV",
            command=self.combine_and_split_csv_files,
            style="Accent.TButton",
        ).grid(row=10, column=0, pady=(0, 10))

        # Información de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para comenzar")
        ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 9)).grid(
            row=11, column=0, sticky=tk.W
        )

        # Estilo para botón de acento
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))

    def select_input_folder(self):
        folder_path = filedialog.askdirectory(
            title="Seleccionar carpeta con archivos CSV"
        )
        if folder_path:
            self.input_folder.set(folder_path)
            self.find_csv_files(folder_path)

    def find_csv_files(self, folder_path):
        # Limpiar tabla de archivos anterior
        for widget in self.files_table_frame.winfo_children():
            widget.destroy()

        self.csv_files = []
        self.csv_checkboxes = {}
        self.property_count = 0
        self.development_count = 0

        # Método más robusto para encontrar archivos CSV
        csv_files = []

        # Buscar usando múltiples patrones para capturar variaciones en extensiones
        csv_patterns = ["*.csv", "*.CSV"]
        for pattern in csv_patterns:
            csv_files.extend(glob.glob(os.path.join(folder_path, pattern)))

        # Adicionalmente, verificar manualmente cada archivo en la carpeta
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) and file.lower().endswith(".csv"):
                if file_path not in csv_files:  # Evitar duplicados
                    csv_files.append(file_path)

        # Eliminar duplicados (por si acaso) y ordenar
        csv_files = list(set(csv_files))
        csv_files.sort()

        if not csv_files:
            ttk.Label(
                self.files_table_frame,
                text="No se encontraron archivos CSV en la carpeta seleccionada",
                font=("Arial", 10),
                foreground="red",
            ).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
            self.status_var.set("No se encontraron archivos CSV")
            return

        # Crear encabezados de la tabla - más compactos
        ttk.Label(self.files_table_frame, text="Sel.", font=("Arial", 9, "bold")).grid(
            row=0, column=0, padx=5, pady=3, sticky=tk.W
        )
        ttk.Label(
            self.files_table_frame, text="Nombre del archivo", font=("Arial", 9, "bold")
        ).grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)

        # Crear filas para cada archivo CSV y escanear los tipos de propiedades
        self.root.config(cursor="watch")  # Cambiar cursor a espera
        self.root.update()

        try:
            # Recorrer todos los archivos CSV
            for i, file_path in enumerate(csv_files):
                file_name = os.path.basename(file_path)

                # Variable para checkbox
                var = tk.BooleanVar(value=True)
                self.csv_checkboxes[file_path] = var

                # Checkbox
                ttk.Checkbutton(self.files_table_frame, variable=var).grid(
                    row=i + 1, column=0, padx=5, pady=1
                )

                # Nombre del archivo
                ttk.Label(self.files_table_frame, text=file_name).grid(
                    row=i + 1, column=1, padx=5, pady=1, sticky=tk.W
                )

                self.csv_files.append(file_path)

                # Escanear el archivo para contar tipos de propiedades
                try:
                    df = pd.read_csv(file_path, encoding="utf-8")

                    # Contar tipos
                    if "Tipo Propiedad" in df.columns:
                        property_count = len(df[df["Tipo Propiedad"] == "PROPERTY"])
                        development_count = len(
                            df[df["Tipo Propiedad"] == "DEVELOPMENT"]
                        )

                        self.property_count += property_count
                        self.development_count += development_count
                except Exception as e:
                    print(f"Error al escanear {file_name}: {str(e)}")

            # Actualizar etiquetas de conteo
            self.property_label.config(text=f"PROPERTY: {self.property_count}")
            self.development_label.config(text=f"DEVELOPMENT: {self.development_count}")

        finally:
            self.root.config(cursor="")  # Restaurar cursor

        self.status_var.set(f"Se encontraron {len(csv_files)} archivos CSV")

    def select_all_files(self):
        for var in self.csv_checkboxes.values():
            var.set(True)

    def deselect_all_files(self):
        for var in self.csv_checkboxes.values():
            var.set(False)

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(
            title="Seleccionar carpeta para guardar archivos CSV"
        )
        if folder_path:
            self.output_folder.set(folder_path)

    def combine_and_split_csv_files(self):
        input_folder = self.input_folder.get()
        output_folder = self.output_folder.get()

        if not input_folder or not output_folder:
            messagebox.showerror(
                "Error",
                "Por favor, seleccione una carpeta de entrada y una carpeta de salida.",
            )
            return

        # Obtener archivos seleccionados
        selected_files = [
            file for file, var in self.csv_checkboxes.items() if var.get()
        ]

        if not selected_files:
            messagebox.showerror(
                "Error", "No hay archivos seleccionados para combinar."
            )
            return

        try:
            self.status_var.set(f"Combinando {len(selected_files)} archivos CSV...")
            self.root.update_idletasks()

            # Leer y combinar archivos CSV
            all_data = []
            total_files = len(selected_files)

            for i, file in enumerate(selected_files):
                # Actualizar progreso
                self.progress_var.set(
                    (i / total_files) * 50
                )  # Primera mitad del progreso
                self.root.update_idletasks()

                # Leer archivo CSV
                df = pd.read_csv(file, encoding="utf-8")
                all_data.append(df)

            # Combinar todos los DataFrames
            combined_df = pd.concat(all_data, ignore_index=True)

            # Separar por tipo de propiedad
            property_df = combined_df[
                combined_df["Tipo Propiedad"] == "PROPERTY"
            ].copy()
            development_df = combined_df[
                combined_df["Tipo Propiedad"] == "DEVELOPMENT"
            ].copy()

            # Renumerar las columnas '#' para cada DataFrame
            if not property_df.empty:
                property_df["#"] = range(1, len(property_df) + 1)

            if not development_df.empty:
                development_df["#"] = range(1, len(development_df) + 1)

            # Definir rutas para archivos de salida
            property_output = os.path.join(output_folder, "Propiedades.csv")
            development_output = os.path.join(output_folder, "Desarrollos.csv")

            # Guardar los DataFrames en archivos CSV separados
            self.progress_var.set(75)  # 75% del progreso
            self.root.update_idletasks()

            property_count = len(property_df)
            development_count = len(development_df)

            if property_count > 0:
                property_df.to_csv(property_output, index=False, encoding="utf-8")

            if development_count > 0:
                development_df.to_csv(development_output, index=False, encoding="utf-8")

            self.progress_var.set(100)
            self.status_var.set(f"Combinación y separación completada")

            # Mensaje de éxito
            result_message = "Proceso completado con éxito.\n\n"

            if property_count > 0:
                result_message += f"Propiedades.csv: {property_count} registros\n"
            else:
                result_message += "No se encontraron registros de tipo PROPERTY\n"

            if development_count > 0:
                result_message += f"Desarrollos.csv: {development_count} registros\n"
            else:
                result_message += "No se encontraron registros de tipo DEVELOPMENT\n"

            result_message += f"\nLos archivos se han guardado en:\n{output_folder}"

            messagebox.showinfo("Éxito", result_message)

        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al procesar los archivos CSV:\n{str(e)}"
            )
            self.status_var.set("Error en el procesamiento")


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVCombinerApp(root)
    root.mainloop()
