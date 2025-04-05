import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui


class AutoClickerBrowser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Clicker para Navegador")
        self.root.geometry("420x460")
        self.root.resizable(False, False)

        # Configurar la ventana para que siempre esté en primer plano
        self.root.attributes("-topmost", True)

        # Variables
        self.click_position = None
        self.click_interval = tk.StringVar(value="1.0")  # Predeterminado a 1 segundo
        self.click_count = tk.StringVar(value="10")
        self.running = False
        self.paused = False
        self.click_thread = None
        self.tracking_position = False
        self.track_coords_id = None

        # Configurar estilo uniforme
        self.configure_style()

        # Crear la interfaz gráfica
        self.setup_gui()

        # Configurar eventos de teclado
        self.root.bind("<Control-Alt-p>", lambda e: self.toggle_pause())
        self.root.bind("<Control-Alt-s>", lambda e: self.stop_clicking())

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def configure_style(self):
        # Configurar estilo uniforme para todos los elementos
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 11))
        style.configure("TCheckbutton", font=("Arial", 11))
        style.configure("TEntry", font=("Arial", 11))
        style.configure("TLabelframe.Label", font=("Arial", 11))

    def setup_gui(self):
        # Marco para configuración de posición
        position_frame = ttk.LabelFrame(self.root, text="Posición del Clic")
        position_frame.pack(fill="x", padx=10, pady=5)

        position_label = ttk.Label(
            position_frame, text="Posición Actual: No Establecida"
        )
        position_label.pack(side="left", padx=10, pady=10)
        self.position_label = position_label

        position_button = ttk.Button(
            position_frame,
            text="Establecer Posición",
            command=self.start_position_tracking,
        )
        position_button.pack(side="right", padx=10, pady=10)

        # Coordenadas en vivo
        live_coords_frame = ttk.Frame(self.root)
        live_coords_frame.pack(fill="x", padx=10, pady=0)

        live_coords_label = ttk.Label(
            live_coords_frame, text="Coordenadas actuales: ---"
        )
        live_coords_label.pack(side="left", pady=5)
        self.live_coords_label = live_coords_label

        # Instrucciones simplificadas
        instructions_frame = ttk.Frame(self.root)
        instructions_frame.pack(fill="x", padx=10, pady=0)

        instructions_label = ttk.Label(
            instructions_frame,
            text="Presione ENTER para confirmar la posición",
            justify="left",
        )
        instructions_label.pack(fill="x", pady=5, anchor="w")
        self.instructions_label = instructions_label

        # Marco para ajustes de clics
        settings_frame = ttk.LabelFrame(self.root, text="Configuración de Clics")
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Configuración de intervalo
        interval_label = ttk.Label(settings_frame, text="Intervalo (segundos):")
        interval_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        interval_entry = ttk.Entry(
            settings_frame, textvariable=self.click_interval, width=10
        )
        interval_entry.grid(row=0, column=1, padx=10, pady=10)

        # Configuración de cantidad
        count_label = ttk.Label(settings_frame, text="Número de Clics:")
        count_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        count_entry = ttk.Entry(settings_frame, textvariable=self.click_count, width=10)
        count_entry.grid(row=1, column=1, padx=10, pady=10)

        # Casilla de clics infinitos
        self.infinite_var = tk.BooleanVar(value=False)
        infinite_check = ttk.Checkbutton(
            settings_frame,
            text="Clics Infinitos",
            variable=self.infinite_var,
            command=self.toggle_infinite,
        )
        infinite_check.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Etiqueta informativa sobre Ctrl+W
        info_label = ttk.Label(
            settings_frame,
            text="Después de cada clic se presionará Ctrl+W",
            foreground="blue",
        )
        info_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Botones de control
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=15)

        # Usar botones ttk para mantener consistencia visual
        start_button = ttk.Button(
            control_frame, text="Iniciar", command=self.start_clicking, width=10
        )
        start_button.pack(side="left", padx=15, pady=10, expand=True)

        pause_button = ttk.Button(
            control_frame, text="Pausar", command=self.toggle_pause, width=10
        )
        pause_button.pack(side="left", padx=15, pady=10, expand=True)

        stop_button = ttk.Button(
            control_frame, text="Detener", command=self.stop_clicking, width=10
        )
        stop_button.pack(side="left", padx=15, pady=10, expand=True)

        # Casilla de verificación para mantener la ventana siempre visible
        topmost_frame = ttk.Frame(self.root)
        topmost_frame.pack(fill="x", padx=10, pady=0)

        self.topmost_var = tk.BooleanVar(value=True)
        topmost_check = ttk.Checkbutton(
            topmost_frame,
            text="Mantener ventana siempre visible",
            variable=self.topmost_var,
            command=self.toggle_topmost,
        )
        topmost_check.pack(side="left", padx=10, pady=0)

        # Espacio adicional para asegurar que los botones sean visibles
        spacer = ttk.Frame(self.root, height=10)
        spacer.pack(fill="x", side="bottom")

        # Barra de estado
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)

        status_label = ttk.Label(status_frame, text="Estado: Listo")
        status_label.pack(side="left")
        self.status_label = status_label

    def toggle_topmost(self):
        """Activar o desactivar la ventana siempre en primer plano"""
        is_topmost = self.topmost_var.get()
        self.root.attributes("-topmost", is_topmost)

    def start_position_tracking(self):
        self.tracking_position = True
        self.update_status("Mueva el ratón a la posición deseada")

        # Mostrar instrucciones destacadas
        self.instructions_label.config(
            text="Presione ENTER para confirmar la posición", foreground="blue"
        )

        # Comenzar a actualizar las coordenadas del ratón en tiempo real
        self.track_mouse_position()

        # Configurar eventos temporales para capturar la posición (solo ENTER)
        self.root.bind("<Return>", lambda e: self.confirm_current_position())

        # Cambiar el aspecto del botón para indicar que está activo
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.winfo_children():
                for child in widget.winfo_children():
                    if (
                        isinstance(child, ttk.Button)
                        and child["text"] == "Establecer Posición"
                    ):
                        child.configure(text="Seleccionando...")

    def confirm_current_position(self):
        if not self.tracking_position:
            return

        current_pos = pyautogui.position()
        self.click_position = current_pos
        self.position_label.config(
            text=f"Posición Actual: {current_pos.x}, {current_pos.y}"
        )
        self.update_status("Posición establecida")
        self.stop_position_tracking()

    def stop_position_tracking(self):
        self.tracking_position = False
        if self.track_coords_id:
            self.root.after_cancel(self.track_coords_id)
            self.track_coords_id = None

        # Eliminar los enlaces temporales
        self.root.unbind("<Return>")

        # Restablecer el texto de instrucciones
        self.instructions_label.config(
            text="Presione ENTER para confirmar la posición", foreground="black"
        )

        # Restablecer el texto del botón
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.winfo_children():
                for child in widget.winfo_children():
                    if (
                        isinstance(child, ttk.Button)
                        and child["text"] == "Seleccionando..."
                    ):
                        child.configure(text="Establecer Posición")

    def track_mouse_position(self):
        if not self.tracking_position:
            self.live_coords_label.config(text="Coordenadas actuales: ---")
            return

        try:
            current_pos = pyautogui.position()
            self.live_coords_label.config(
                text=f"Coordenadas actuales: {current_pos.x}, {current_pos.y}"
            )
        except:
            pass

        # Programar la próxima actualización
        self.track_coords_id = self.root.after(50, self.track_mouse_position)

    def toggle_infinite(self):
        if self.infinite_var.get():
            self.click_count.set("∞")
        else:
            self.click_count.set("10")

    def start_clicking(self):
        if self.running:
            messagebox.showinfo("En Ejecución", "¡El auto clicker ya está funcionando!")
            return

        if not self.click_position:
            messagebox.showerror("Error", "¡Por favor establece una posición primero!")
            return

        try:
            interval = float(self.click_interval.get().replace(",", "."))
            if interval <= 0:
                raise ValueError("El intervalo debe ser positivo")

            if not self.infinite_var.get():
                if self.click_count.get() == "∞":
                    count = -1
                else:
                    count = int(self.click_count.get())
                    if count <= 0:
                        raise ValueError("La cantidad debe ser positiva")
            else:
                count = -1  # -1 indica clics infinitos
        except ValueError as e:
            messagebox.showerror("Entrada Inválida", str(e))
            return

        self.running = True
        self.paused = False
        self.update_status("Ejecutando...")

        # Iniciar clics en un hilo separado
        self.click_thread = threading.Thread(
            target=self.clicking_loop, args=(interval, count)
        )
        self.click_thread.daemon = True
        self.click_thread.start()

    def clicking_loop(self, interval, count):
        clicks_performed = 0

        while self.running and (count == -1 or clicks_performed < count):
            if not self.paused:
                # Realizar el clic
                try:
                    # Hacer clic en la posición establecida
                    pyautogui.click(self.click_position.x, self.click_position.y)

                    # Pequeña pausa para asegurar que el clic se registre
                    time.sleep(0.3)

                    # Presionar Ctrl+W para cerrar la pestaña
                    pyautogui.hotkey("ctrl", "w")

                    clicks_performed += 1

                    # Actualizar estado con conteo
                    if count == -1:
                        self.update_status(f"Ejecutando... Clics: {clicks_performed}")
                    else:
                        self.update_status(
                            f"Ejecutando... Clics: {clicks_performed}/{count}"
                        )
                except Exception as e:
                    self.update_status(f"Error al hacer clic: {str(e)}")
                    self.running = False
                    break

            # Esperar el intervalo especificado
            time_elapsed = 0
            while time_elapsed < interval and self.running:
                if self.paused:
                    self.update_status("Pausado")
                time.sleep(0.1)
                time_elapsed += 0.1

        if self.running:  # Si salimos porque se alcanzó el conteo
            self.running = False
            self.update_status(f"Completados {clicks_performed} clics")

    def toggle_pause(self):
        if not self.running:
            return

        self.paused = not self.paused
        if self.paused:
            self.update_status("Pausado")
        else:
            self.update_status("Reanudado")

    def stop_clicking(self):
        self.running = False
        self.paused = False
        self.update_status("Detenido")

    def update_status(self, message):
        # Actualizar etiqueta de estado (seguro para hilos)
        self.root.after(0, lambda: self.status_label.config(text=f"Estado: {message}"))

    def on_close(self):
        self.running = False
        self.tracking_position = False

        if self.track_coords_id:
            self.root.after_cancel(self.track_coords_id)

        self.root.destroy()


if __name__ == "__main__":
    # Evitar que pyautogui genere excepciones cuando el ratón llega al borde de la pantalla
    pyautogui.FAILSAFE = False

    try:
        app = AutoClickerBrowser()
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error: {str(e)}")
