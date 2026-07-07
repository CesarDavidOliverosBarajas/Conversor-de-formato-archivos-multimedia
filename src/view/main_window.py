import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from src.controller.app_controller import AppController


class TkDnD_CTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class MainWindow(TkDnD_CTk):
    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller

        self.title("Oli converter")
        self.geometry("620x750")
        self.minsize(550, 750)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.input_file = None
        self.current_out_path = ""
        self._is_video_source = False

        self.setup_ui()

    def setup_ui(self):
        title_lbl = ctk.CTkLabel(self, text="Conversor Multimedia ", font=ctk.CTkFont(size=24, weight="bold"))
        title_lbl.pack(pady=(30, 5))
        desc_lbl = ctk.CTkLabel(self, text="Transforma Audio, Video e Imágenes totalmente Offline", font=ctk.CTkFont(size=14), text_color="gray")
        desc_lbl.pack(pady=(0, 20))

        # -----------------------------------------------
        # PASO 1: Drag & Drop Area
        # -----------------------------------------------
        self.drop_frame = ctk.CTkFrame(self, height=180, corner_radius=10, fg_color="transparent", border_width=2, border_color="#1f538d")
        self.drop_frame.pack(pady=10, padx=40, fill="x")
        self.drop_frame.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(self.drop_frame, text="1. Arrastra y Suelta tu Archivo Aquí\nO haz clic para seleccionar manualmente", font=ctk.CTkFont(size=15))
        self.drop_label.pack(expand=True)
        self.drop_frame.bind("<Button-1>", self.on_click_select_file)
        self.drop_label.bind("<Button-1>", self.on_click_select_file)

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

        # Modo de Conversión (solo visible para video)
        self.mode_var = ctk.StringVar(value="Video completo")
        self.lbl_mode = ctk.CTkLabel(options_frame, text="Modo:")
        self.mode_seg = ctk.CTkSegmentedButton(
            options_frame, values=["Video completo", "Solo audio"],
            variable=self.mode_var, command=self.on_mode_change
        )
        self.lbl_mode.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.mode_seg.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.lbl_mode.grid_remove()
        self.mode_seg.grid_remove()

        # Nivel de Calidad
        self.quality_var = ctk.StringVar(value="Alta")
        lbl_qlty = ctk.CTkLabel(options_frame, text="Calidad / Compresión:")
        lbl_qlty.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.quality_menu = ctk.CTkOptionMenu(options_frame, variable=self.quality_var, values=["Sin pérdida", "Alta", "Media", "Baja"])
        self.quality_menu.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Carpeta Destino
        self.output_dir_var = ctk.StringVar(value="Origen")
        lbl_out = ctk.CTkLabel(options_frame, text="Carpeta Destino:")
        lbl_out.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        dir_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        dir_frame.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        self.lbl_dir = ctk.CTkLabel(dir_frame, textvariable=self.output_dir_var, text_color="gray", anchor="w")
        self.lbl_dir.pack(side="left", fill="x", expand=True)

        btn_dir = ctk.CTkButton(dir_frame, fg_color="#0C12F2", text="Examinar", width=90, command=self.on_select_output_dir)
        btn_dir.pack(side="right", padx=(5, 0))

        options_frame.columnconfigure(1, weight=1)

        # -----------------------------------------------
        # PASO 3: Acciones
        # -----------------------------------------------
        self.convert_btn = ctk.CTkButton(self, text_color="black", text_color_disabled="black", fg_color="#A0E009", text="INICIAR CONVERSIÓN", font=ctk.CTkFont(size=15, weight="bold"), height=50, command=self.on_convert, state="disabled")
        self.convert_btn.pack(pady=(10, 5), padx=40, fill="x")

        self.transcribe_btn = ctk.CTkButton(self, text_color="white", text_color_disabled="gray", fg_color="#0C12F2", text="TRANSCRIBIR AUDIO A TEXTO", font=ctk.CTkFont(size=14, weight="bold"), height=45, command=self.on_transcribe, state="disabled")
        self.transcribe_btn.pack(pady=(5, 5), padx=40, fill="x")

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
        file_path = file_path.strip("{}")
        self.handle_input_file(file_path)

    def handle_input_file(self, file_path):
        if not os.path.isfile(file_path):
            self.status_label.configure(text="No es un archivo válido.", text_color="red")
            return

        self.input_file = file_path
        filename = os.path.basename(file_path)
        self.drop_label.configure(text=f"Archivo Identificado:\n{filename}", text_color="#1f538d" if ctk.get_appearance_mode() == "Light" else "#2eb8e6")

        self.progress.set(0)
        self.status_label.configure(text="")
        self.current_out_path = ""

        self.output_dir_var.set(os.path.dirname(os.path.abspath(file_path)))
        self.update_format_options(file_path)

    def on_select_output_dir(self):
        folder = filedialog.askdirectory(title="Seleccionar Carpeta de Destino")
        if folder:
            self.output_dir_var.set(folder)

    def update_format_options(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        img_exts = ['.jpg', '.jpeg', '.png', '.webp', '.avif']
        audio_exts = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
        video_exts = ['.mp4', '.mkv', '.avi', '.mov', '.mts', '.mpeg', '.mpg']

        self._is_video_source = ext in video_exts

        if self._is_video_source:
            self.lbl_mode.grid()
            self.mode_seg.grid()
            mode = self.mode_var.get()
        else:
            self.lbl_mode.grid_remove()
            self.mode_seg.grid_remove()
            mode = None

        if ext in img_exts:
            vals = ['jpg', 'png', 'webp', 'avif']
        elif ext in audio_exts:
            vals = ['mp3', 'wav', 'flac', 'aac', 'ogg']
        elif ext in video_exts:
            if mode == "Solo audio":
                vals = ['mp3', 'wav', 'flac', 'aac', 'ogg']
            else:
                vals = ['mp4', 'mkv', 'avi', 'mov', 'mts']
        else:
            self.status_label.configure(text=f"El formato {ext} no es soportado.", text_color="red")
            self.convert_btn.configure(state="disabled")
            self.format_menu.configure(state="disabled")
            self.transcribe_btn.configure(state="disabled")
            return

        target_ext_raw = ext.replace('.', '')
        if target_ext_raw == 'jpeg':
            target_ext_raw = 'jpg'

        vals = [v for v in vals if v != target_ext_raw]

        if vals:
            self.format_menu.configure(state="normal", values=vals)
            self.format_var.set(vals[0])
            self.convert_btn.configure(state="normal", text="INICIAR CONVERSIÓN", fg_color="#A0E009", text_color="black")

            if ext in audio_exts or ext in video_exts:
                self.transcribe_btn.configure(state="normal")
            else:
                self.transcribe_btn.configure(state="disabled")

            self.status_label.configure(text="Listo para convertir", text_color="gray")
        else:
            self.format_var.set("No hay opciones de salida")
            self.convert_btn.configure(state="disabled", fg_color="gray")
            self.transcribe_btn.configure(state="disabled")

    def on_mode_change(self, val):
        if self.input_file:
            self.progress.set(0)
            self.status_label.configure(text="")
            self.update_format_options(self.input_file)

    # ---- EVENTOS DE CONVERSIÓN ----

    def on_convert(self):
        if not self.input_file:
            return

        target_ext = f".{self.format_var.get()}"
        out_filename = os.path.splitext(os.path.basename(self.input_file))[0] + target_ext

        base_dir = self.output_dir_var.get()
        if base_dir == "Origen" or not os.path.isdir(base_dir):
            base_dir = os.path.dirname(os.path.abspath(self.input_file))

        out_path = os.path.join(base_dir, out_filename)
        quality = self.quality_var.get()

        if os.path.exists(out_path):
            ans = messagebox.askyesnocancel(
                title="Advertencia: El archivo ya existe",
                message=f"El archivo:\n'{out_filename}'\nya existe en la carpeta destino.\n\n¿Deseas sobreescribirlo?\n\n• Sí: Elimina el viejo y guarda este\n• No: Te dejaremos escoger otra ruta/nombre\n• Cancelar: Detiene la conversión"
            )
            if ans is None:
                return
            if ans is False:
                new_path = filedialog.asksaveasfilename(
                    title="Guardar archivo como...",
                    initialdir=base_dir,
                    initialfile=out_filename,
                    defaultextension=target_ext,
                    filetypes=[(f"Formato {target_ext}", f"*{target_ext}"), ("Todos", "*.*")]
                )
                if not new_path:
                    return
                out_path = new_path

        self.current_out_path = out_path

        self.status_label.configure(text="Convirtiendo por favor espere...", text_color="orange")
        self.convert_btn.configure(state="disabled", fg_color="gray")
        self.transcribe_btn.configure(state="disabled")
        self.progress.set(0)

        self.controller.start_conversion(
            self.input_file,
            out_path,
            quality,
            self.on_progress_update,
            self.on_complete
        )

    def on_progress_update(self, val):
        self.after(0, self._sync_progress, val)

    def _sync_progress(self, val):
        self.progress.set(val / 100.0)

    def on_complete(self, success, msg):
        self.after(0, self._sync_complete, success, msg)

    def _sync_complete(self, success, msg):
        self.convert_btn.configure(state="normal", fg_color="#A0E009", text_color="black")
        if self.input_file:
            ext = os.path.splitext(self.input_file)[1].lower()
            audio_exts = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
            video_exts = ['.mp4', '.mkv', '.avi', '.mov', '.mts', '.mpeg', '.mpg']
            if ext in audio_exts or ext in video_exts:
                self.transcribe_btn.configure(state="normal")

        if success:
            final_msg = f"¡Éxito! Archivo guardado en:\n{self.current_out_path}"
            self.status_label.configure(text=final_msg, text_color="green")
            self.progress.set(1.0)
        else:
            self.status_label.configure(text=msg, text_color="red")
            self.progress.set(0)

    # ---- EVENTOS DE TRANSCRIPCIÓN ----

    def on_transcribe(self):
        if not self.input_file:
            return

        self.status_label.configure(text="Transcribiendo... esto puede tomar unos minutos.", text_color="orange")
        self.convert_btn.configure(state="disabled", fg_color="gray")
        self.transcribe_btn.configure(state="disabled", text="TRANSCRIBIENDO...")
        self.progress.set(0)

        self.controller.start_transcription(
            self.input_file,
            self.on_transcribe_progress,
            self.on_transcribe_complete
        )

    def on_transcribe_progress(self, val):
        self.after(0, self._sync_transcribe_progress, val)

    def _sync_transcribe_progress(self, val):
        self.progress.set(val / 100.0)

    def on_transcribe_complete(self, success, data):
        self.after(0, self._sync_transcribe_complete, success, data)

    def _sync_transcribe_complete(self, success, data):
        self.convert_btn.configure(state="normal", fg_color="#A0E009", text_color="black")
        self.transcribe_btn.configure(state="normal", text="TRANSCRIBIR AUDIO A TEXTO")

        if not success:
            self.status_label.configure(text=data, text_color="red")
            self.progress.set(0)
            return

        text = data
        if not text.strip():
            self.status_label.configure(text="No se detectó audio con texto en el archivo.", text_color="red")
            self.progress.set(0)
            return

        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        save_path = filedialog.asksaveasfilename(
            title="Guardar transcripción como...",
            initialfile=base_name + "_transcripcion",
            defaultextension=".txt",
            filetypes=[
                ("Documento de Word", "*.docx"),
                ("Archivo de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not save_path:
            self.status_label.configure(text="Transcripción completada pero no se guardó.", text_color="gray")
            self.progress.set(1.0)
            return

        try:
            from src.model.transcriber import Transcriber
            if save_path.endswith('.docx'):
                Transcriber.save_docx(text, save_path)
            else:
                Transcriber.save_txt(text, save_path)

            self.status_label.configure(
                text=f"¡Transcripción guardada en:\n{save_path}", text_color="green"
            )
            self.progress.set(1.0)
        except Exception as e:
            self.status_label.configure(text=f"Error al guardar: {str(e)}", text_color="red")
            self.progress.set(0)
