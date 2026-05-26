import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

class BlockDeNotas:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Block de Notas")
        self.ventana.geometry("800x600")
        self.ventana.configure(bg="black")

        self.archivo_actual = None
        self.modificado = False
        self.tamano_fuente = 12

        self.fuente_familia = "Courier New"
        if not self._fuente_disponible("Courier New"):
            self.fuente_familia = "Liberation Mono"
        if not self._fuente_disponible(self.fuente_familia):
            self.fuente_familia = "monospace"

        self.texto = scrolledtext.ScrolledText(
            self.ventana,
            bg="black",
            fg="white",
            insertbackground="white",
            font=(self.fuente_familia, self.tamano_fuente),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            padx=8,
            pady=8,
            undo=True,
        )
        self.texto.pack(fill=tk.BOTH, expand=True)
        self.texto.bind("<<Modified>>", self._marcar_modificado)

        self.barra_menu = tk.Menu(self.ventana, bg="#2d2d2d", fg="white")
        self.ventana.config(menu=self.barra_menu)

        menu_archivo = tk.Menu(self.barra_menu, tearoff=0, bg="#2d2d2d", fg="white")
        menu_archivo.add_command(label="Nuevo", command=self.nuevo, accelerator="Ctrl+N")
        menu_archivo.add_command(label="Abrir...", command=self.abrir, accelerator="Ctrl+O")
        menu_archivo.add_command(label="Guardar", command=self.guardar, accelerator="Ctrl+S")
        menu_archivo.add_command(label="Guardar como...", command=self.guardar_como, accelerator="Ctrl+Shift+S")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Cerrar", command=self.cerrar, accelerator="Ctrl+W")
        self.barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

        self.ventana.bind("<Control-n>", lambda e: self.nuevo())
        self.ventana.bind("<Control-N>", lambda e: self.nuevo())
        self.ventana.bind("<Control-o>", lambda e: self.abrir())
        self.ventana.bind("<Control-O>", lambda e: self.abrir())
        self.ventana.bind("<Control-s>", lambda e: self.guardar())
        self.ventana.bind("<Control-S>", lambda e: self.guardar())
        self.ventana.bind("<Control-Shift-S>", lambda e: self.guardar_como())
        self.ventana.bind("<Control-w>", lambda e: self.cerrar())
        self.ventana.bind("<Control-W>", lambda e: self.cerrar())
        self.ventana.bind("<Control-plus>", lambda e: self._zoom_in())
        self.ventana.bind("<Control-Shift-equal>", lambda e: self._zoom_in())
        self.ventana.bind("<Control-KP_Add>", lambda e: self._zoom_in())
        self.ventana.bind("<Control-minus>", lambda e: self._zoom_out())
        self.ventana.bind("<Control-KP_Subtract>", lambda e: self._zoom_out())
        self.ventana.bind("<Control-0>", lambda e: self._zoom_reset())
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)

    def _fuente_disponible(self, nombre):
        from tkinter import font
        fuentes = [f.lower() for f in font.families()]
        return nombre.lower() in fuentes

    def _marcar_modificado(self, _=None):
        if self.texto.edit_modified():
            self.modificado = True
            self.texto.edit_modified(False)

    def _preguntar_guardar(self):
        if not self.modificado:
            return True
        resp = messagebox.askyesnocancel(
            "Block de Notas",
            "Desea guardar los cambios?",
        )
        if resp is None:
            return False
        if resp:
            return self.guardar()
        return True

    def _actualizar_titulo(self):
        titulo = "Block de Notas"
        if self.archivo_actual:
            titulo = f"{os.path.basename(self.archivo_actual)} - Block de Notas"
        if self.modificado:
            titulo = f"* {titulo}"
        self.ventana.title(titulo)

    def _aplicar_fuente(self):
        self.texto.config(font=(self.fuente_familia, self.tamano_fuente))

    def _zoom_in(self):
        self.tamano_fuente = min(self.tamano_fuente + 2, 72)
        self._aplicar_fuente()

    def _zoom_out(self):
        self.tamano_fuente = max(self.tamano_fuente - 2, 6)
        self._aplicar_fuente()

    def _zoom_reset(self):
        self.tamano_fuente = 12
        self._aplicar_fuente()

    def nuevo(self):
        if not self._preguntar_guardar():
            return
        self.texto.delete("1.0", tk.END)
        self.archivo_actual = None
        self.modificado = False
        self._actualizar_titulo()

    def abrir(self, _=None):
        if not self._preguntar_guardar():
            return
        ruta = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
        except UnicodeDecodeError:
            try:
                with open(ruta, "r", encoding="latin-1") as f:
                    contenido = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
                return
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
            return

        self.texto.delete("1.0", tk.END)
        self.texto.insert("1.0", contenido)
        self.archivo_actual = ruta
        self.modificado = False
        self._actualizar_titulo()

    def guardar(self, _=None):
        if self.archivo_actual:
            try:
                contenido = self.texto.get("1.0", tk.END).rstrip("\n")
                with open(self.archivo_actual, "w", encoding="utf-8") as f:
                    f.write(contenido)
                self.modificado = False
                self._actualizar_titulo()
                return True
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
                return False
        return self.guardar_como()

    def guardar_como(self, _=None):
        ruta = filedialog.asksaveasfilename(
            title="Guardar como",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return False
        self.archivo_actual = ruta
        return self.guardar()

    def cerrar(self, _=None):
        if not self._preguntar_guardar():
            return
        self.ventana.destroy()

    def ejecutar(self):
        self._actualizar_titulo()
        self.ventana.mainloop()


if __name__ == "__main__":
    app = BlockDeNotas()
    app.ejecutar()
