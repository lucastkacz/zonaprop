import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import re


class LimpiadorCSVUnificado:
    def __init__(self, root):
        self.root = root
        self.root.title("Limpiador CSV Unificado")
        self.root.geometry("600x750")

        self.df = None
        self.file_path = None

        # Marco principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Marco para selección de archivo
        file_frame = ttk.LabelFrame(
            main_frame, text="Seleccionar Archivo CSV", padding="10"
        )
        file_frame.pack(fill=tk.X, pady=5)

        self.file_path_var = tk.StringVar()
        ttk.Entry(
            file_frame, textvariable=self.file_path_var, width=50, state="readonly"
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Examinar", command=self.browse_file).pack(
            side=tk.RIGHT, padx=5
        )

        # Marco para opciones de procesamiento
        options_frame = ttk.LabelFrame(
            main_frame, text="Opciones de Procesamiento", padding="10"
        )
        options_frame.pack(fill=tk.X, pady=5)

        # Checkbox para eliminar duplicados
        self.eliminar_duplicados_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Eliminar duplicados basados en URL",
            variable=self.eliminar_duplicados_var,
        ).pack(anchor=tk.W, pady=2)

        # Checkbox para limpiar precios
        self.limpiar_precios_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Limpiar columnas de precio y expensas",
            variable=self.limpiar_precios_var,
        ).pack(anchor=tk.W, pady=2)

        # No mostramos opciones para mantener primera/última aparición
        # Siempre mantendremos la primera aparición (como en el comportamiento original)

        # Checkbox para filtrar outliers en expensas
        self.filtrar_expensas_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Filtrar valores atípicos en expensas (método IQR)",
            variable=self.filtrar_expensas_var,
        ).pack(anchor=tk.W, pady=2)

        # Checkbox para filtrar publicaciones
        self.filtrar_publicado_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Conservar solo publicaciones de 'hoy'",
            variable=self.filtrar_publicado_var,
        ).pack(anchor=tk.W, pady=2)

        # Checkbox para normalizar antigüedad
        self.normalizar_antiguedad_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Convertir 'A estrenar' a '0' en antigüedad",
            variable=self.normalizar_antiguedad_var,
        ).pack(anchor=tk.W, pady=2)

        # Checkbox para completar metros cuadrados
        self.completar_m2_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Completar datos faltantes de m² total/cubiertos",
            variable=self.completar_m2_var,
        ).pack(anchor=tk.W, pady=2)

        # Checkbox para filtrar metros cuadrados inconsistentes
        self.filtrar_m2_inconsistentes_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Filtrar filas donde m² total < m² cubiertos",
            variable=self.filtrar_m2_inconsistentes_var,
        ).pack(anchor=tk.W, pady=2)

        # Log de operaciones
        log_frame = ttk.LabelFrame(main_frame, text="Log de Operaciones", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = tk.Text(log_frame, height=10, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Scrollbar para el log
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Botones de acción
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            buttons_frame,
            text="Procesar y Guardar",
            command=self.procesar_y_guardar,
            state="disabled",
        ).pack(side=tk.LEFT, padx=5)
        self.proceso_btn = buttons_frame.winfo_children()[
            0
        ]  # Guardar referencia al botón

        ttk.Button(buttons_frame, text="Salir", command=root.destroy).pack(
            side=tk.RIGHT, padx=5
        )

        # Inicializar el log
        self.log("Programa iniciado. Por favor, seleccione un archivo CSV.")

    def log(self, mensaje):
        """Añadir mensaje al log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{mensaje}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def browse_file(self):
        """Abrir diálogo para seleccionar archivo CSV"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            self.file_path_var.set(file_path)
            self.log(f"Archivo seleccionado: {os.path.basename(file_path)}")
            self.cargar_csv(file_path)

    def cargar_csv(self, file_path):
        """Cargar archivo CSV"""
        try:
            self.log("Cargando archivo CSV...")

            # Intentar diferentes encodings comunes
            encodings = ["utf-8", "latin1", "ISO-8859-1"]
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(file_path, encoding=encoding)
                    self.log(f"Archivo cargado con encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue

            if self.df is None:
                messagebox.showerror(
                    "Error",
                    "No se pudo leer el archivo CSV con ninguna codificación conocida.",
                )
                self.log("ERROR: No se pudo leer el archivo.")
                return

            # Verificar si existe la columna 'url'
            if "url" not in self.df.columns:
                # Buscar columnas similares a 'url'
                posibles_columnas = []
                for col in self.df.columns:
                    if (
                        "url" in col.lower()
                        or "link" in col.lower()
                        or "enlace" in col.lower()
                    ):
                        posibles_columnas.append(col)

                if posibles_columnas:
                    col_sugerida = posibles_columnas[0]
                    respuesta = messagebox.askyesno(
                        "Columna no encontrada",
                        f"No se encontró la columna 'url'. ¿Desea usar '{col_sugerida}' en su lugar?",
                    )
                    if respuesta:
                        self.df.rename(columns={col_sugerida: "url"}, inplace=True)
                        self.log(f"Columna '{col_sugerida}' renombrada a 'url'")
                    else:
                        self.log(
                            "ADVERTENCIA: No se encontró columna 'url'. No se eliminarán duplicados."
                        )
                else:
                    self.log(
                        "ADVERTENCIA: No se encontró columna 'url'. No se eliminarán duplicados."
                    )

            # Verificar si existen las columnas 'precio' y 'expensas'
            columnas_numeros = ["precio", "expensas"]
            for columna in columnas_numeros:
                if columna not in self.df.columns:
                    # Buscar columnas similares
                    posibles_columnas = []
                    for col in self.df.columns:
                        col_lower = col.lower()
                        if (
                            columna == "precio"
                            and ("precio" in col_lower or "price" in col_lower)
                        ) or (
                            columna == "expensas"
                            and ("expensa" in col_lower or "expense" in col_lower)
                        ):
                            posibles_columnas.append(col)

                    if posibles_columnas:
                        col_sugerida = posibles_columnas[0]
                        respuesta = messagebox.askyesno(
                            "Columna no encontrada",
                            f"No se encontró la columna '{columna}'. ¿Desea usar '{col_sugerida}' en su lugar?",
                        )
                        if respuesta:
                            self.df.rename(
                                columns={col_sugerida: columna}, inplace=True
                            )
                            self.log(
                                f"Columna '{col_sugerida}' renombrada a '{columna}'"
                            )
                        else:
                            self.log(
                                f"ADVERTENCIA: No se encontró columna '{columna}'. No se limpiará."
                            )
                    else:
                        self.log(
                            f"ADVERTENCIA: No se encontró columna '{columna}'. No se limpiará."
                        )

            # Verificar columnas 'publicado' y 'antigüedad'
            otras_columnas = ["publicado", "antigüedad"]
            for columna in otras_columnas:
                if columna not in self.df.columns:
                    # Buscar columnas similares
                    posibles_columnas = []
                    for col in self.df.columns:
                        col_lower = col.lower()
                        if (
                            columna == "publicado"
                            and (
                                "publicado" in col_lower
                                or "publicacion" in col_lower
                                or "fecha" in col_lower
                            )
                        ) or (
                            columna == "antigüedad"
                            and (
                                "antiguedad" in col_lower
                                or "antiguedad" in col_lower
                                or "anios" in col_lower
                                or "años" in col_lower
                            )
                        ):
                            posibles_columnas.append(col)

                    if posibles_columnas:
                        col_sugerida = posibles_columnas[0]
                        respuesta = messagebox.askyesno(
                            "Columna no encontrada",
                            f"No se encontró la columna '{columna}'. ¿Desea usar '{col_sugerida}' en su lugar?",
                        )
                        if respuesta:
                            self.df.rename(
                                columns={col_sugerida: columna}, inplace=True
                            )
                            self.log(
                                f"Columna '{col_sugerida}' renombrada a '{columna}'"
                            )
                        else:
                            self.log(
                                f"ADVERTENCIA: No se encontró columna '{columna}'. No se procesará."
                            )
                    else:
                        self.log(
                            f"ADVERTENCIA: No se encontró columna '{columna}'. No se procesará."
                        )

            # Habilitar el botón de procesar
            self.proceso_btn.config(state="normal")

            # Resumen de datos
            self.log(
                f"Datos cargados: {len(self.df)} filas, {len(self.df.columns)} columnas"
            )

            # Mostrar columnas disponibles
            self.log(
                f"Columnas disponibles: {', '.join(self.df.columns.tolist()[:5])}..."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo CSV: {str(e)}")
            self.log(f"ERROR: {str(e)}")

    def limpiar_precios_expensas(self):
        """Limpiar datos numéricos en las columnas de precio y expensas"""
        if self.df is None:
            return

        self.log("Limpiando columnas de precio y expensas...")

        # Verificar y limpiar columna de precio
        if "precio" in self.df.columns:
            # Convertir a string primero para manejar valores numéricos y nulos
            self.df["precio"] = self.df["precio"].astype(str)

            # Eliminar todos los caracteres no numéricos excepto puntos
            self.df["precio"] = self.df["precio"].apply(
                lambda x: re.sub(r"[^\d\.]", "", x) if x != "nan" else ""
            )

            # Eliminar los puntos que son separadores de miles
            self.df["precio"] = self.df["precio"].apply(
                lambda x: x.replace(".", "") if x != "" else x
            )

            # Convertir a float
            self.df["precio"] = pd.to_numeric(self.df["precio"], errors="coerce")

            # Filtrar valores extremadamente bajos (como 1, que probablemente son marcadores)
            self.df.loc[self.df["precio"] < 100, "precio"] = None

            self.log(
                f"Columna 'precio' limpiada. Valores no nulos: {self.df['precio'].count()}"
            )
        else:
            self.log("No se encontró la columna 'precio'")

        # Verificar y limpiar columna de expensas
        if "expensas" in self.df.columns:
            # Convertir a string primero para manejar valores numéricos y nulos
            self.df["expensas"] = self.df["expensas"].astype(str)

            # Eliminar todos los caracteres no numéricos excepto puntos
            self.df["expensas"] = self.df["expensas"].apply(
                lambda x: re.sub(r"[^\d\.]", "", x) if x != "nan" else ""
            )

            # Eliminar los puntos que son separadores de miles
            self.df["expensas"] = self.df["expensas"].apply(
                lambda x: x.replace(".", "") if x != "" else x
            )

            # Convertir a float
            self.df["expensas"] = pd.to_numeric(self.df["expensas"], errors="coerce")

            # Filtrar valores extremadamente bajos (como 1, que probablemente son marcadores)
            self.df.loc[self.df["expensas"] < 1000, "expensas"] = None

            self.log(
                f"Columna 'expensas' limpiada. Valores no nulos: {self.df['expensas'].count()}"
            )
        else:
            self.log("No se encontró la columna 'expensas'")

    def filtrar_expensas_outliers(self):
        """Filtrar outliers en la columna de expensas utilizando el método IQR"""
        if self.df is None or "expensas" not in self.df.columns:
            self.log(
                "No se puede filtrar outliers: no hay datos o falta columna 'expensas'"
            )
            return 0

        self.log("Filtrando valores atípicos en la columna 'expensas'...")

        # Verificar que hay suficientes datos no nulos
        if self.df["expensas"].count() < 10:
            self.log("Insuficientes datos no nulos para filtrar outliers en 'expensas'")
            return 0

        # Calcular estadísticas
        Q1 = self.df["expensas"].quantile(0.25)
        Q3 = self.df["expensas"].quantile(0.75)
        IQR = Q3 - Q1

        # Definir límites para outliers (con factor 1.5 para IQR, que es el estándar)
        limite_inferior = max(0, Q1 - 1.5 * IQR)
        limite_superior = Q3 + 1.5 * IQR

        # Contar valores fuera de rango
        valores_fuera_rango = self.df[
            (self.df["expensas"] < limite_inferior)
            | (self.df["expensas"] > limite_superior)
        ].shape[0]

        # Establecer valores fuera de rango como None (NA)
        self.df.loc[
            (self.df["expensas"] < limite_inferior)
            | (self.df["expensas"] > limite_superior),
            "expensas",
        ] = None

        self.log(
            f"Filtrado de outliers en 'expensas': {valores_fuera_rango} valores fuera de rango"
        )
        self.log(
            f"Rango aceptable para 'expensas': {limite_inferior:.2f} - {limite_superior:.2f}"
        )

        return valores_fuera_rango

    def filtrar_publicaciones_hoy(self):
        """Filtrar para mantener solo las publicaciones de 'hoy'"""
        if self.df is None or "publicado" not in self.df.columns:
            self.log(
                "No se puede filtrar publicaciones: no hay datos o falta columna 'publicado'"
            )
            return 0

        self.log("Filtrando publicaciones para mantener solo las de 'hoy'...")

        # Contar filas antes
        filas_antes = len(self.df)

        # Filtrar para mantener solo filas con 'hoy' en la columna 'publicado'
        self.df = self.df[
            self.df["publicado"].str.contains("hoy", case=False, na=False)
        ]

        # Contar filas después
        filas_despues = len(self.df)
        filas_eliminadas = filas_antes - filas_despues

        self.log(
            f"Se eliminaron {filas_eliminadas} filas que no contenían 'hoy' en 'publicado'"
        )
        self.log(f"Quedan {filas_despues} filas con publicaciones de 'hoy'")

        return filas_eliminadas

    def normalizar_antiguedad(self):
        """Normalizar la columna de antigüedad, reemplazando 'A estrenar' por '0'"""
        if self.df is None or "antigüedad" not in self.df.columns:
            self.log(
                "No se puede normalizar antigüedad: no hay datos o falta columna 'antigüedad'"
            )
            return 0

        self.log(
            "Normalizando columna 'antigüedad', reemplazando 'A estrenar' por '0'..."
        )

        # Contar ocurrencias antes
        ocurrencias = (
            self.df["antigüedad"].str.contains("estrenar", case=False, na=False).sum()
        )

        # Reemplazar 'A estrenar' por '0'
        self.df["antigüedad"] = self.df["antigüedad"].apply(
            lambda x: "0" if isinstance(x, str) and "estrenar" in x.lower() else x
        )

        # Intentar convertir a numérico
        self.df["antigüedad"] = pd.to_numeric(self.df["antigüedad"], errors="coerce")

        self.log(
            f"Se reemplazaron {ocurrencias} valores de 'A estrenar' por '0' en 'antigüedad'"
        )

        return ocurrencias

    def completar_metros_cuadrados(self):
        """Completar datos faltantes en columnas de metros cuadrados"""
        # Verificar nombres de columnas posibles
        nombres_totales = [
            "tot. m²",
            "tot.m²",
            "total m²",
            "total m2",
            "m² totales",
            "m2 totales",
            "m² total",
            "m2 total",
        ]
        nombres_cubiertos = [
            "cub. m²",
            "cub.m²",
            "cubiertos m²",
            "cubiertos m2",
            "m² cubiertos",
            "m2 cubiertos",
            "m² cubierto",
            "m2 cubierto",
        ]

        # Identificar columnas
        col_total = None
        col_cubiertos = None

        for col in self.df.columns:
            col_lower = col.lower()
            if any(nombre.lower() in col_lower for nombre in nombres_totales):
                col_total = col
            if any(nombre.lower() in col_lower for nombre in nombres_cubiertos):
                col_cubiertos = col

        if not col_total or not col_cubiertos:
            self.log(
                "No se encontraron las columnas de metros cuadrados totales o cubiertos"
            )
            return 0, 0

        self.log(
            f"Completando datos faltantes entre '{col_total}' y '{col_cubiertos}'..."
        )

        # Convertir a numérico primero y asegurar que son comparables
        self.df[col_total] = pd.to_numeric(self.df[col_total], errors="coerce")
        self.df[col_cubiertos] = pd.to_numeric(self.df[col_cubiertos], errors="coerce")

        # Identificar filas donde falta un valor pero existe el otro
        total_faltante = self.df[col_total].isna() & self.df[col_cubiertos].notna()
        cubiertos_faltante = self.df[col_cubiertos].isna() & self.df[col_total].notna()

        # Contar cuántos valores se completarán
        total_a_completar = total_faltante.sum()
        cubiertos_a_completar = cubiertos_faltante.sum()

        # Completar valores faltantes
        self.df.loc[total_faltante, col_total] = self.df.loc[
            total_faltante, col_cubiertos
        ]
        self.df.loc[cubiertos_faltante, col_cubiertos] = self.df.loc[
            cubiertos_faltante, col_total
        ]

        self.log(
            f"Se completaron {total_a_completar} valores faltantes en '{col_total}'"
        )
        self.log(
            f"Se completaron {cubiertos_a_completar} valores faltantes en '{col_cubiertos}'"
        )

        return total_a_completar, cubiertos_a_completar

    def filtrar_metros_inconsistentes(self):
        """Filtrar filas donde m² total < m² cubiertos (inconsistentes)"""
        # Verificar nombres de columnas posibles
        nombres_totales = [
            "tot. m²",
            "tot.m²",
            "total m²",
            "total m2",
            "m² totales",
            "m2 totales",
            "m² total",
            "m2 total",
        ]
        nombres_cubiertos = [
            "cub. m²",
            "cub.m²",
            "cubiertos m²",
            "cubiertos m2",
            "m² cubiertos",
            "m2 cubiertos",
            "m² cubierto",
            "m2 cubierto",
        ]

        # Identificar columnas
        col_total = None
        col_cubiertos = None

        for col in self.df.columns:
            col_lower = col.lower()
            if any(nombre.lower() in col_lower for nombre in nombres_totales):
                col_total = col
            if any(nombre.lower() in col_lower for nombre in nombres_cubiertos):
                col_cubiertos = col

        if not col_total or not col_cubiertos:
            self.log(
                "No se encontraron las columnas de metros cuadrados totales o cubiertos"
            )
            return 0

        self.log(
            f"Filtrando filas donde '{col_total}' < '{col_cubiertos}' (inconsistentes)..."
        )

        # Asegurarse que sean valores numéricos
        self.df[col_total] = pd.to_numeric(self.df[col_total], errors="coerce")
        self.df[col_cubiertos] = pd.to_numeric(self.df[col_cubiertos], errors="coerce")

        # Contar filas antes
        filas_antes = len(self.df)

        # Filtrar filas inconsistentes
        inconsistentes = (
            (self.df[col_total] < self.df[col_cubiertos])
            & self.df[col_total].notna()
            & self.df[col_cubiertos].notna()
        )
        cantidad_inconsistentes = inconsistentes.sum()

        if cantidad_inconsistentes > 0:
            self.df = self.df[~inconsistentes]

        self.log(
            f"Se eliminaron {cantidad_inconsistentes} filas con m² totales < m² cubiertos"
        )

        return cantidad_inconsistentes

    def eliminar_duplicados(self):
        """Eliminar duplicados basados en la URL"""
        if self.df is None or "url" not in self.df.columns:
            self.log(
                "No se puede eliminar duplicados: no hay datos o falta columna 'url'"
            )
            return

        self.log("Eliminando duplicados basados en la columna 'url'...")

        # Contar filas antes
        filas_antes = len(self.df)

        # Verificar cuántos duplicados hay en la columna URL
        duplicados = self.df.duplicated(subset=["url"]).sum()

        if duplicados == 0:
            self.log("No se encontraron URLs duplicadas")
            return

        # Siempre mantenemos la primera aparición (comportamiento predeterminado)
        keep = "first"

        # Eliminar duplicados
        self.df = self.df.drop_duplicates(subset=["url"], keep=keep)

        # Calcular filas eliminadas
        filas_eliminadas = filas_antes - len(self.df)

        self.log(
            f"Se eliminaron {filas_eliminadas} filas duplicadas (se mantuvo la primera aparición)"
        )

    def procesar_y_guardar(self):
        """Procesar datos y guardar el resultado"""
        if self.df is None:
            messagebox.showwarning("Advertencia", "No hay datos para procesar.")
            return

        try:
            # Hacer una copia del DataFrame original
            df_original = self.df.copy()

            # Inicializar variables para el resumen
            expensas_atipicas = 0
            filas_eliminadas_publicacion = 0
            antiguedades_normalizadas = 0
            total_m2_completados = 0
            cubiertos_m2_completados = 0
            filas_m2_inconsistentes = 0

            # Ejecutar procesos según opciones seleccionadas
            if self.eliminar_duplicados_var.get() and "url" in self.df.columns:
                self.eliminar_duplicados()

            if self.limpiar_precios_var.get():
                self.limpiar_precios_expensas()

            if self.filtrar_expensas_var.get() and "expensas" in self.df.columns:
                expensas_atipicas = self.filtrar_expensas_outliers()

            if self.filtrar_publicado_var.get() and "publicado" in self.df.columns:
                filas_eliminadas_publicacion = self.filtrar_publicaciones_hoy()

            if self.normalizar_antiguedad_var.get() and "antigüedad" in self.df.columns:
                antiguedades_normalizadas = self.normalizar_antiguedad()

            if self.completar_m2_var.get():
                total_m2_completados, cubiertos_m2_completados = (
                    self.completar_metros_cuadrados()
                )

            if self.filtrar_m2_inconsistentes_var.get():
                filas_m2_inconsistentes = self.filtrar_metros_inconsistentes()

            # Pedir ubicación para guardar el archivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                initialdir=os.path.dirname(self.file_path) if self.file_path else None,
                initialfile=(
                    f"limpio_{os.path.basename(self.file_path)}"
                    if self.file_path
                    else "datos_limpios.csv"
                ),
            )

            if file_path:
                # Guardar el DataFrame procesado
                self.df.to_csv(file_path, index=False)
                self.log(f"Archivo guardado como: {os.path.basename(file_path)}")

                # Mostrar resumen final
                filas_originales = len(df_original)
                filas_finales = len(self.df)
                reduccion = filas_originales - filas_finales

                resumen = f"Resumen del proceso:\n"
                resumen += f"- Filas originales: {filas_originales}\n"
                resumen += f"- Filas finales: {filas_finales}\n"
                resumen += f"- Reducción total: {reduccion} filas ({reduccion/filas_originales*100:.1f}%)\n\n"

                # Detalles de las operaciones realizadas
                if self.eliminar_duplicados_var.get() and "url" in df_original.columns:
                    duplicados = df_original.duplicated(subset=["url"]).sum()
                    resumen += f"- URLs duplicadas eliminadas: {duplicados}\n"

                if (
                    self.filtrar_expensas_var.get()
                    and "expensas" in df_original.columns
                ):
                    resumen += f"- Valores atípicos en expensas identificados: {expensas_atipicas}\n"

                if (
                    self.filtrar_publicado_var.get()
                    and "publicado" in df_original.columns
                ):
                    resumen += f"- Publicaciones no recientes eliminadas: {filas_eliminadas_publicacion}\n"

                if (
                    self.normalizar_antiguedad_var.get()
                    and "antigüedad" in df_original.columns
                ):
                    resumen += f"- Propiedades 'A estrenar' normalizadas: {antiguedades_normalizadas}\n"

                if self.completar_m2_var.get():
                    resumen += f"- Metros cuadrados totales completados: {total_m2_completados}\n"
                    resumen += f"- Metros cuadrados cubiertos completados: {cubiertos_m2_completados}\n"

                if self.filtrar_m2_inconsistentes_var.get():
                    resumen += f"- Filas con m² inconsistentes eliminadas: {filas_m2_inconsistentes}\n"

                messagebox.showinfo("Proceso Completado", resumen)
                self.log(resumen)

        except Exception as e:
            messagebox.showerror("Error", f"Error durante el procesamiento: {str(e)}")
            self.log(f"ERROR: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LimpiadorCSVUnificado(root)
    root.mainloop()
