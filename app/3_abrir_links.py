import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, TclError
import pandas as pd
import webbrowser
import time
import threading


class LinkOpenerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Abridor de Enlaces CSV")
        self.root.geometry("650x480")
        self.root.resizable(True, True)

        # Configurar la ventana para que siempre esté en primer plano
        self.root.attributes("-topmost", True)

        # Variables
        self.csv_file_path = tk.StringVar()
        self.column_var = tk.StringVar()
        self.start_row = tk.StringVar(value="1")
        self.num_links = tk.StringVar(value="10")
        self.delay = tk.StringVar(value="1.0")
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Listo para comenzar")
        self.df = None
        self.columns = []
        self.total_rows = 0
        self.opening_in_progress = False

        # Crear interfaz
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sección para seleccionar archivo CSV
        ttk.Label(main_frame, text="Archivo CSV con enlaces:", font=("Arial", 11)).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        main_frame.columnconfigure(0, weight=1)

        ttk.Entry(input_frame, textvariable=self.csv_file_path, width=50).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(input_frame, text="Examinar...", command=self.select_csv_file).pack(
            side=tk.RIGHT, padx=(10, 0)
        )

        # Frame para la información del archivo
        file_info_frame = ttk.LabelFrame(main_frame, text="Información del Archivo")
        file_info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Etiquetas para mostrar información del archivo
        self.file_info_label = ttk.Label(
            file_info_frame, text="No se ha cargado ningún archivo", font=("Arial", 10)
        )
        self.file_info_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # Selección de columna
        column_frame = ttk.Frame(file_info_frame)
        column_frame.grid(row=1, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(column_frame, text="Columna con enlaces:", font=("Arial", 10)).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        self.column_combo = ttk.Combobox(
            column_frame, textvariable=self.column_var, state="disabled"
        )
        self.column_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Configuración de apertura
        config_frame = ttk.LabelFrame(main_frame, text="Configuración de Apertura")
        config_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Fila de inicio
        start_row_frame = ttk.Frame(config_frame)
        start_row_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        ttk.Label(
            start_row_frame, text="Empezar desde la fila:", font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        self.start_row_entry = ttk.Entry(
            start_row_frame, textvariable=self.start_row, width=10, state="disabled"
        )
        self.start_row_entry.pack(side=tk.LEFT)

        # Cantidad de enlaces
        num_links_frame = ttk.Frame(config_frame)
        num_links_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        ttk.Label(
            num_links_frame, text="Cantidad de enlaces a abrir:", font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        self.num_links_entry = ttk.Entry(
            num_links_frame, textvariable=self.num_links, width=10, state="disabled"
        )
        self.num_links_entry.pack(side=tk.LEFT)

        # Delay entre enlaces
        delay_frame = ttk.Frame(config_frame)
        delay_frame.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

        ttk.Label(delay_frame, text="Segundos entre enlaces:", font=("Arial", 10)).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Entry(delay_frame, textvariable=self.delay, width=10).pack(side=tk.LEFT)

        # Resumen
        summary_frame = ttk.LabelFrame(main_frame, text="Resumen")
        summary_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.summary_label = ttk.Label(
            summary_frame,
            text="Configure las opciones para empezar",
            font=("Arial", 10),
        )
        self.summary_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # Barra de progreso
        self.progress = ttk.Progressbar(
            main_frame, variable=self.progress_var, maximum=100
        )
        self.progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Botones de control
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.start_button = ttk.Button(
            button_frame,
            text="Abrir Enlaces",
            command=self.start_opening_links,
            style="Accent.TButton",
            state="disabled",
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(
            button_frame,
            text="Detener",
            command=self.stop_opening_links,
            state="disabled",
        )
        self.stop_button.pack(side=tk.LEFT)

        # Información de estado
        ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 9)).grid(
            row=7, column=0, sticky=tk.W
        )

        # Estilo para botón de acento
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))

        # Vincular eventos de cambio
        self.start_row.trace_add("write", self.update_summary)
        self.num_links.trace_add("write", self.update_summary)
        self.delay.trace_add("write", self.update_summary)
        self.column_var.trace_add("write", self.update_summary)

    def select_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        )

        if not file_path:
            return

        self.csv_file_path.set(file_path)
        self.load_csv_file(file_path)

    def load_csv_file(self, file_path):
        try:
            # Leer el archivo CSV
            self.df = pd.read_csv(file_path, encoding="utf-8")
            self.columns = list(self.df.columns)
            self.total_rows = len(self.df)

            # Actualizar la interfaz con la información del archivo
            self.file_info_label.config(
                text=f"Archivo cargado: {os.path.basename(file_path)}\nTotal de filas: {self.total_rows}"
            )

            # Actualizar el combo de columnas
            self.column_combo["values"] = self.columns
            if self.columns:
                self.column_combo.current(0)
            self.column_combo["state"] = "readonly"

            # Habilitar y configurar campos de entrada
            self.start_row_entry["state"] = "normal"
            self.num_links_entry["state"] = "normal"

            # Establecer valores predeterminados
            self.start_row.set("1")
            self.num_links.set(str(self.total_rows))  # Por defecto usar todas las filas

            # Habilitar el botón de inicio
            self.start_button["state"] = "normal"

            # Actualizar el resumen
            self.update_summary()

            self.status_var.set(f"Archivo CSV cargado con {self.total_rows} filas")

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo cargar el archivo CSV:\n{str(e)}"
            )
            self.status_var.set("Error al cargar el archivo CSV")

    def get_int_value(self, string_var, default_value, min_value, max_value):
        """Obtiene un valor entero seguro desde un StringVar"""
        try:
            value = int(string_var.get())
            return max(min_value, min(value, max_value))
        except (ValueError, TclError):
            return default_value

    def get_float_value(self, string_var, default_value, min_value):
        """Obtiene un valor flotante seguro desde un StringVar"""
        try:
            value = float(string_var.get())
            return max(min_value, value)
        except (ValueError, TclError):
            return default_value

    def update_summary(self, *args):
        if self.df is None or not self.column_var.get() in self.columns:
            return

        # Obtener valores de forma segura
        start = self.get_int_value(self.start_row, 1, 1, self.total_rows)
        count = self.get_int_value(
            self.num_links, self.total_rows, 1, self.total_rows - start + 1
        )
        delay = self.get_float_value(self.delay, 2.0, 0.1)

        # Calcular fin
        end = start + count - 1

        # Actualizar los campos si han cambiado
        if str(start) != self.start_row.get():
            self.start_row.set(str(start))
        if str(count) != self.num_links.get():
            self.num_links.set(str(count))
        if (
            str(delay) != self.delay.get()
            and abs(delay - float(self.delay.get() or 0)) > 0.01
        ):
            self.delay.set(str(delay))

        # Actualizar resumen
        summary = (
            f"Se abrirán {count} enlaces desde la fila {start} hasta la fila {end}.\n"
        )
        summary += f"Con {delay} segundos de espera entre cada enlace."

        self.summary_label.config(text=summary)

    def start_opening_links(self):
        if self.opening_in_progress:
            return

        # Obtener los valores configurados de forma segura
        column_name = self.column_var.get()
        start_row = self.get_int_value(self.start_row, 1, 1, self.total_rows)
        num_links = self.get_int_value(
            self.num_links, min(10, self.total_rows), 1, self.total_rows - start_row + 1
        )
        delay = self.get_float_value(self.delay, 2.0, 0.1)

        if not column_name:
            messagebox.showerror(
                "Error", "Por favor, seleccione una columna con enlaces"
            )
            return

        # Confirmar la operación
        end_row = start_row + num_links - 1

        confirm_msg = f"Se abrirán {num_links} enlaces desde la fila {start_row} hasta la fila {end_row}.\n"
        confirm_msg += f"Con {delay} segundos de espera entre cada enlace.\n\n"
        confirm_msg += "¿Desea continuar?"

        if not messagebox.askyesno("Confirmar", confirm_msg):
            return

        # Iniciar el proceso en un hilo separado
        self.opening_in_progress = True
        self.progress_var.set(0)
        self.start_button["state"] = "disabled"
        self.stop_button["state"] = "normal"

        # Crear e iniciar el hilo
        self.opener_thread = threading.Thread(
            target=self.open_links_thread,
            args=(column_name, start_row - 1, num_links, delay),
        )
        self.opener_thread.daemon = True
        self.opener_thread.start()

    def open_links_thread(self, column_name, start_index, num_links, delay):
        try:
            end_index = min(start_index + num_links, self.total_rows)
            links_opened = 0

            self.status_var.set(f"Abriendo enlaces {start_index+1} a {end_index}")

            # Abrir enlaces uno por uno
            for i in range(start_index, end_index):
                if not self.opening_in_progress:
                    break

                # Obtener el enlace
                link = str(self.df.iloc[i][column_name])

                # Verificar si el enlace es válido
                if pd.isna(link) or not link.strip():
                    self.status_var.set(f"Saltando fila {i+1}: enlace no válido")
                    continue

                # Asegurar que el enlace tenga prefijo http:// o https://
                if not link.startswith(("http://", "https://")):
                    link = "https://" + link

                # Abrir el enlace
                self.status_var.set(f"Abriendo enlace {i+1}: {link}")
                try:
                    webbrowser.open_new_tab(link)
                    links_opened += 1

                    # Actualizar progreso
                    progress_pct = (links_opened / num_links) * 100
                    self.progress_var.set(progress_pct)

                    # Esperar entre enlaces
                    for _ in range(int(delay * 10)):
                        if not self.opening_in_progress:
                            break
                        time.sleep(0.1)

                except Exception as e:
                    self.status_var.set(f"Error al abrir el enlace {i+1}: {str(e)}")

            if links_opened == num_links:
                self.status_var.set(
                    f"¡Proceso completado! Se abrieron {links_opened} enlaces"
                )
            else:
                self.status_var.set(
                    f"Proceso finalizado: se abrieron {links_opened} de {num_links} enlaces"
                )

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        finally:
            self.opening_in_progress = False
            self.root.after(0, self.reset_buttons)

    def reset_buttons(self):
        self.start_button["state"] = "normal"
        self.stop_button["state"] = "disabled"

    def stop_opening_links(self):
        if self.opening_in_progress:
            self.opening_in_progress = False
            self.status_var.set("Deteniendo el proceso...")


if __name__ == "__main__":
    root = tk.Tk()
    app = LinkOpenerApp(root)
    root.mainloop()
