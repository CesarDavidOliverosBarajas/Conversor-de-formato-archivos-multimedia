import os
import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from src.controller.app_controller import AppController

# Clase puente para inyectar Drag & Drop nativo dentro de CustomTkinter
class TkDnD_CTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class MainWindow(TkDnD_CTk):
    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller
        
        self.title("Oli converter")
        self.geometry("620x700")
        self.minsize(550, 700)
        
        # Tema UI (Opcional, pero te asegura el aspecto moderno oscuro/claro)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Variables de estado
        self.input_file = None
        
        self.setup_ui()

    def setup_ui(self):
        """Diseño jerárquico de CTk en Pantalla."""
        # Titulo y descripciones
        title_lbl = ctk.CTkLabel(self, text="Conversor Multimedia ", font=ctk.CTkFont(size=24, weight="bold"))
        title_lbl.pack(pady=(30, 5))
        desc_lbl = ctk.CTkLabel(self, text="Transforma Audio, Video e Imágenes totalmente Offline", font=ctk.CTkFont(size=14), text_color="gray")
        desc_lbl.pack(pady=(0, 20))

        # -----------------------------------------------
        # PASO 1: Drag & Drop Area
        # -----------------------------------------------
        self.drop_frame = ctk.CTkFrame(self, height=180, corner_radius=10, fg_color="transparent", border_width=2, border_color="#1f538d")
        self.drop_frame.pack(pady=10, padx=40, fill="x")
        self.drop_frame.pack_propagate(False) # Mantener altura
        
        self.drop_label = ctk.CTkLabel(self.drop_frame, text="1. Arrastra y Suelta tu Archivo Aquí\nO haz clic para seleccionar manualmente", font=ctk.CTkFont(size=15))
        self.drop_label.pack(expand=True)
        self.drop_frame.bind("<Button-1>", self.on_click_select_file)
        self.drop_label.bind("<Button-1>", self.on_click_select_file)
        
        # Bind Drag and Drop nativo al Frame Principal
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop)
        
        # -----------------------------------------------
        # PASO 2: Selección de Parámetros
        # -----------------------------------------------
        options_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=1, border_color="#A0E009", corner_radius=10)
        options_frame.pack(pady=20, padx=40, fill="x", ipadx=10, ipady=10)
        
        # Formato de Salida
        self.format_var = ctk.StringVar(value="Esperando Archivo...")
        lbl_fmt = ctk.CTkLabel(options_frame, text="2. Formato de Salida:")
        lbl_fmt.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.format_menu = ctk.CTkOptionMenu(options_frame, variable=self.format_var, values=["..."], state="disabled")
        self.format_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Nivel de Calidad
        self.quality_var = ctk.StringVar(value="Alta")
        lbl_qlty = ctk.CTkLabel(options_frame, text="Calidad / Compresión:")
        lbl_qlty.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.quality_menu = ctk.CTkOptionMenu(options_frame, variable=self.quality_var, values=["Sin pérdida", "Alta", "Media", "Baja"])
        self.quality_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Carpeta Destino
        self.output_dir_var = ctk.StringVar(value="Origen")
        lbl_out = ctk.CTkLabel(options_frame, text="Carpeta Destino:")
        lbl_out.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        dir_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        dir_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        self.lbl_dir = ctk.CTkLabel(dir_frame, textvariable=self.output_dir_var, text_color="gray", anchor="w")
        self.lbl_dir.pack(side="left", fill="x", expand=True)
        
        btn_dir = ctk.CTkButton(dir_frame, fg_color="#0C12F2", text="Examinar", width=90, command=self.on_select_output_dir)
        btn_dir.pack(side="right", padx=(5,0))
        
        options_frame.columnconfigure(1, weight=1) # El menú se expande estéticamente

        # -----------------------------------------------
        # PASO 3: Conversión y Progreso
        # -----------------------------------------------
        self.convert_btn = ctk.CTkButton(self, text_color="black", text_color_disabled="black", fg_color="#A0E009", text="INICIAR CONVERSIÓN", font=ctk.CTkFont(size=15, weight="bold"), height=50, command=self.on_convert, state="disabled")
        self.convert_btn.pack(pady=(10, 5), padx=40, fill="x")
        
        self.progress = ctk.CTkProgressBar(self, height=10)
        self.progress.set(0)
        self.progress.pack(pady=10, padx=40, fill="x")
        
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=13), wraplength=500)
        self.status_label.pack(pady=(10, 20))

    # ---- MÉTODOS DE BINDEO ----

    def on_click_select_file(self, event=None):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.handle_input_file(file_path)

    def on_drop(self, event):
        file_path = event.data
        # En sistemas Windows DnD a veces entrega "{Ruta con Espacios}", se remueven llaves.
        file_path = file_path.strip("{}")
        self.handle_input_file(file_path)

    def handle_input_file(self, file_path):
        if not os.path.isfile(file_path):
            self.status_label.configure(text="No es un archivo válido.", text_color="red")
            return
            
        self.input_file = file_path
        filename = os.path.basename(file_path)
        self.drop_label.configure(text=f"Archivo Identificado:\n{filename}", text_color="#1f538d" if ctk.get_appearance_mode() == "Light" else "#2eb8e6")
        
        # TEST/FIX: Limpiar estados residuales apenas cargan un nuevo archivo para evitar arrastrar logic bugs visuales 
        self.progress.set(0)
        self.status_label.configure(text="")
        if hasattr(self, 'current_out_path'):
            self.current_out_path = ""
        
        # Guardar en la misma ruta por defecto
        self.output_dir_var.set(os.path.dirname(os.path.abspath(file_path)))
        
        # Validar y cargar Opciones
        self.update_format_options(file_path)

    def on_select_output_dir(self):
        folder = filedialog.askdirectory(title="Seleccionar Carpeta de Destino")
        if folder:
            self.output_dir_var.set(folder)

    def update_format_options(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        img_exts = ['.jpg', '.jpeg', '.png', '.webp', '.avif']
        audio_exts = ['.mp3', '.wav', '.flac', '.aac']
        video_exts = ['.mp4', '.mkv', '.avi', '.mov', '.mts']
        
        if ext in img_exts:
            vals = ['jpg', 'png', 'webp', 'avif']
        elif ext in audio_exts:
            vals = ['mp3', 'wav', 'flac', 'aac']
        elif ext in video_exts:
            vals = ['mp4', 'mkv', 'avi', 'mov', 'mts']
        else:
            self.status_label.configure(text=f"El formato {ext} no es soportado.", text_color="red")
            self.convert_btn.configure(state="disabled")
            self.format_menu.configure(state="disabled")
            return
            
        # Filtramos la extension original (ej. no dejar que convierta de jpg a jpg)
        target_ext_raw = ext.replace('.', '')
        # Arreglo para que evite fallos si target_ext_raw es equivalente
        if target_ext_raw == 'jpeg': target_ext_raw = 'jpg'
        
        vals = [v for v in vals if v != target_ext_raw]
        
        if vals:
            self.format_menu.configure(state="normal", values=vals)
            self.format_var.set(vals[0])
            self.convert_btn.configure(state="normal", text="INICIAR CONVERSIÓN", fg_color="#A0E009", text_color="black")
            self.status_label.configure(text="Listo para convertir", text_color="gray")
        else:
            self.format_var.set("No hay opciones de salida")
            self.convert_btn.configure(state="disabled", fg_color="gray")

    # ---- EVENTOS DE CONTROLADOR ----

    def on_convert(self):
        if not self.input_file:
            return
            
        target_ext = f".{self.format_var.get()}"
        out_filename = os.path.splitext(os.path.basename(self.input_file))[0] + target_ext
        
        # En caso de no existir o fallar, intentar la ruta del archivo input como seguro
        base_dir = self.output_dir_var.get()
        if base_dir == "Origen" or not os.path.isdir(base_dir):
             base_dir = os.path.dirname(os.path.abspath(self.input_file))
             
        out_path = os.path.join(base_dir, out_filename)
        quality = self.quality_var.get()
        
        # Bloque de validación inteligente si existe el archivo
        if os.path.exists(out_path):
            from tkinter import messagebox
            ans = messagebox.askyesnocancel(
                title="Advertencia: El archivo ya existe", 
                message=f"El archivo:\n'{out_filename}'\nya existe en la carpeta destino.\n\n¿Deseas sobreescribirlo?\n\n• Sí: Elimina el viejo y guarda este\n• No: Te dejaremos escoger otra ruta/nombre\n• Cancelar: Detiene la conversión"
            )
            if ans is None:
                return # Detiene si cancela o presiona la X
            if ans is False:
                # El usuario eligió NO sobreescribir. Se llama a la ventana nativa File Explorer/Finder
                new_path = filedialog.asksaveasfilename(
                    title="Guardar archivo como...",
                    initialdir=base_dir,
                    initialfile=out_filename,
                    defaultextension=target_ext,
                    filetypes=[(f"Formato {target_ext}", f"*{target_ext}"), ("Todos", "*.*")]
                )
                if not new_path:
                    return # Detiene si cierra la ventana del Finder
                out_path = new_path

        self.current_out_path = out_path # Guardar en memoria para informar al usuario después
        
        # Bloquear GUI temporalmente
        self.status_label.configure(text="Convirtiendo por favor espere...", text_color="orange")
        self.convert_btn.configure(state="disabled", fg_color="gray")
        self.progress.set(0)
        
        # Se solicita al controlador la conversión en Background
        self.controller.start_conversion(
            self.input_file, 
            out_path, 
            quality, 
            # Inyeccion de Callbacks
            self.on_progress_update, 
            self.on_complete
        )

    # Nota: Los callbacks de hilos secundarios deben integrarse al hilo Main usando `.after()` de Tkinter
    def on_progress_update(self, val):
        self.after(0, self._sync_progress, val)
        
    def _sync_progress(self, val):
        self.progress.set(val / 100.0)

    def on_complete(self, success, msg):
        self.after(0, self._sync_complete, success, msg)
        
    def _sync_complete(self, success, msg):
        self.convert_btn.configure(state="normal", fg_color="#A0E009", text_color="black")
        
        if success:
            final_msg = f"¡Éxito! Archivo guardado en:\n{self.current_out_path}"
            self.status_label.configure(text=final_msg, text_color="green")
            self.progress.set(1.0)
        else:
            # Mostrar todo el error completo para debuggear claro
            self.status_label.configure(text=msg, text_color="red")
            self.progress.set(0)
