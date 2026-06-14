"""
TP Integrador — Codificación de Datos
Algoritmos: Huffman y Shannon-Fano
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

import algoritmos as alg
import metricas   as met


# ══════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════════════════
class CompresorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Compresor de Datos — Huffman & Shannon-Fano")
        self.root.geometry("860x700")
        self.root.resizable(True, True)
        self.root.configure(bg="#1e2329")

        # Estado compartido entre pasos
        self.text        = None
        self.freqs       = None
        self.h_root      = None
        self.h_codes     = None
        self.s_codes     = None
        self.h_encoded   = None
        self.s_encoded   = None
        self.plot_data   = None

        self._build_ui()

    # ──────────────────────────────────────
    #  CONSTRUCCIÓN DE LA UI
    # ──────────────────────────────────────
    def _build_ui(self):
        # ── Barra de menú ──
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Abrir archivo .TXT",        command=self.cargar_txt)
        file_menu.add_command(label="Abrir imagen B/N (Pillow)", command=self.cargar_imagen)
        file_menu.add_separator()
        file_menu.add_command(label="Generar imagen de prueba",  command=self.generar_imagen_prueba)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        chart_menu = tk.Menu(menubar, tearoff=0)
        chart_menu.add_command(label="Ver Gráficos Comparativos", command=self.ver_graficos)
        menubar.add_cascade(label="Gráficos", menu=chart_menu)
        self.root.config(menu=menubar)

        # ── Encabezado ──
        header = tk.Frame(self.root, bg="#2c3e50", pady=10)
        header.pack(fill="x")
        tk.Label(header, text="COMPRESOR DE DATOS",
                 font=("Consolas", 16, "bold"), bg="#2c3e50", fg="#3498db").pack()
        tk.Label(header, text="Huffman  ·  Shannon-Fano  |  Comunicación de Datos — UTN",
                 font=("Consolas", 9), bg="#2c3e50", fg="#7f8c8d").pack()

        # ── Panel entrada ──
        frame_in = tk.LabelFrame(self.root, text=" Texto / Datos de Entrada ",
                                  bg="#1e2329", fg="#bdc3c7",
                                  font=("Consolas", 9, "bold"), bd=1)
        frame_in.pack(fill="both", padx=12, pady=(10, 4))

        # Botones de carga
        btn_row = tk.Frame(frame_in, bg="#1e2329")
        btn_row.pack(fill="x", padx=6, pady=4)
        self._btn(btn_row, "📄 Cargar .TXT",   self.cargar_txt).pack(side="left", padx=4)
        self._btn(btn_row, "🖼️ Cargar Imagen", self.cargar_imagen).pack(side="left", padx=4)
        self._btn(btn_row, "🗑️ Limpiar",       self.limpiar).pack(side="left", padx=4)

        # Área de texto
        self.txt_input = tk.Text(frame_in, height=7, bg="#0d1117", fg="#c9d1d9",
                                  insertbackground="white", font=("Consolas", 10),
                                  wrap="word", bd=0, relief="flat")
        self.txt_input.pack(fill="both", padx=6, pady=(0, 6))

        # ── Botón principal ──
        self._btn(self.root, "▶  PROCESAR Y CODIFICAR", self.procesar,
                  bg="#2980b9", fg="white",
                  font=("Consolas", 11, "bold")).pack(pady=8, ipadx=20, ipady=4)

        # ── Notebook con pestañas de resultados ──
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",            background="#1e2329", borderwidth=0)
        style.configure("TNotebook.Tab",        background="#2c3e50", foreground="#bdc3c7",
                        padding=[10, 4], font=("Consolas", 9))
        style.map("TNotebook.Tab",              background=[("selected", "#2980b9")])
        style.configure("TFrame",               background="#1e2329")

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # Pestaña 1 — Métricas
        tab_met = ttk.Frame(nb)
        nb.add(tab_met, text="  📊 Métricas  ")
        self.txt_metricas = self._text_area(tab_met)
        self.txt_metricas.pack(fill="both", expand=True, padx=6, pady=6)

        # Pestaña 2 — Tabla Huffman
        tab_huff = ttk.Frame(nb)
        nb.add(tab_huff, text="  🌳 Tabla Huffman  ")
        self.txt_tabla_h = self._text_area(tab_huff)
        self.txt_tabla_h.pack(fill="both", expand=True, padx=6, pady=6)

        # Pestaña 3 — Tabla Shannon-Fano
        tab_sf = ttk.Frame(nb)
        nb.add(tab_sf, text="  🌿 Tabla Shannon-Fano  ")
        self.txt_tabla_s = self._text_area(tab_sf)
        self.txt_tabla_s.pack(fill="both", expand=True, padx=6, pady=6)

        # Pestaña 4 — Decodificación
        tab_dec = ttk.Frame(nb)
        nb.add(tab_dec, text="  ✅ Decodificación  ")
        self.txt_decode = self._text_area(tab_dec)
        self.txt_decode.pack(fill="both", expand=True, padx=6, pady=6)

        # ── Barra de estado ──
        self.status_var = tk.StringVar(value="Listo. Ingresá texto o cargá un archivo.")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              bg="#2c3e50", fg="#95a5a6",
                              font=("Consolas", 8), anchor="w", padx=8)
        status_bar.pack(fill="x", side="bottom")

    # ──────────────────────────────────────
    #  WIDGETS AUXILIARES
    # ──────────────────────────────────────
    def _btn(self, parent, text, cmd, bg="#2c3e50", fg="#ecf0f1",
             font=("Consolas", 9)):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg, activebackground="#34495e",
                         activeforeground="white", font=font,
                         relief="flat", cursor="hand2", bd=0,
                         padx=10, pady=4)

    def _text_area(self, parent):
        t = tk.Text(parent, bg="#0d1117", fg="#c9d1d9",
                    font=("Consolas", 9), wrap="word",
                    insertbackground="white", bd=0, relief="flat",
                    state="normal")
        sb = tk.Scrollbar(parent, command=t.yview)
        t.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        return t

    def _write(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", text)

    def _status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    # ──────────────────────────────────────
    #  CARGA DE DATOS
    # ──────────────────────────────────────
    def cargar_txt(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.txt_input.delete("1.0", "end")
            self.txt_input.insert("end", content)
            self._status(f"Archivo cargado: {os.path.basename(path)} ({len(content)} caracteres)")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

    def cargar_imagen(self):
        """Carga una imagen B/N con Pillow y la convierte a secuencia de píxeles '0'/'1'."""
        try:
            from PIL import Image
        except ImportError:
            messagebox.showerror("Error",
                "Pillow no está instalado.\n"
                "Ejecutá: pip install pillow")
            return

        path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.bmp *.jpg *.jpeg *.pbm *.tiff"),
                       ("Todos", "*.*")])
        if not path:
            return
        try:
            img = Image.open(path).convert("1")   # modo 1-bit B/N
            pixels = list(img.getdata())
            bits = "".join("1" if p > 0 else "0" for p in pixels)

            self.txt_input.delete("1.0", "end")
            self.txt_input.insert("end", bits)
            w, h = img.size
            self._status(
                f"Imagen cargada: {os.path.basename(path)} "
                f"({w}×{h} px → {len(bits)} bits/píxeles)")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def generar_imagen_prueba(self):
        """Genera un archivo PNG de prueba en blanco y negro."""
        try:
            from PIL import Image
            img = Image.new("1", (20, 20), 0)
            pixels = img.load()
            # Dibuja un rectángulo y una cruz
            for x in range(20):
                for y in range(20):
                    if x == 0 or x == 19 or y == 0 or y == 19:
                        pixels[x, y] = 1
                    if x == y or x + y == 19:
                        pixels[x, y] = 1
            img.save("prueba_bn.png")
            messagebox.showinfo("Listo",
                "Se creó 'prueba_bn.png' en la carpeta actual.\n"
                "Usá Archivo → Cargar Imagen para abrirla.")
        except ImportError:
            messagebox.showerror("Error", "Pillow no está instalado.\nEjecutá: pip install pillow")

    def limpiar(self):
        self.txt_input.delete("1.0", "end")
        for w in [self.txt_metricas, self.txt_tabla_h, self.txt_tabla_s, self.txt_decode]:
            self._write(w, "")
        self.text = self.freqs = self.h_root = self.h_codes = None
        self.s_codes = self.h_encoded = self.s_encoded = self.plot_data = None
        self._status("Listo.")

    # ──────────────────────────────────────
    #  PROCESAMIENTO PRINCIPAL
    # ──────────────────────────────────────
    def procesar(self):
        raw = self.txt_input.get("1.0", "end").strip()
        if not raw:
            messagebox.showwarning("Aviso", "No hay datos para procesar.")
            return

        self.text = raw
        self._status("Procesando…")

        # ── 1. Frecuencias ──────────────────
        from collections import Counter
        self.freqs = Counter(self.text)
        total = len(self.text)

        # ── 2. Huffman ──────────────────────
        self.h_root, _ = alg.build_huffman(self.text)
        self.h_codes    = alg.get_huffman_codes(self.h_root)
        self.h_encoded  = alg.huffman_encode(self.text, self.h_codes)

        h_orig, h_comp, h_rate, h_avg, h_ent, h_eff = met.calculate_metrics(
            self.text, self.h_codes, self.freqs)

        # ── 3. Shannon-Fano ─────────────────
        sorted_freqs = sorted(self.freqs.items(), key=lambda x: x[1], reverse=True)
        self.s_codes   = alg.shannon_fano(sorted_freqs)
        self.s_encoded = alg.sf_encode(self.text, self.s_codes)

        s_orig, s_comp, s_rate, s_avg, s_ent, s_eff = met.calculate_metrics(
            self.text, self.s_codes, self.freqs)

        # ── 4. Decodificación y verificación ─
        h_decoded = alg.huffman_decode(self.h_encoded, self.h_root)
        s_decoded = alg.sf_decode(self.s_encoded, self.s_codes)
        h_ok = (h_decoded == self.text)
        s_ok = (s_decoded == self.text)

        # ── 5. Guardar plot_data ─────────────
        self.plot_data = {
            "h_rate": h_rate, "s_rate": s_rate,
            "h_eff":  h_eff,  "s_eff":  s_eff,
            "h_avg":  h_avg,  "s_avg":  s_avg,
            "h_ent":  h_ent,  "s_ent":  s_ent,
        }

        # ── Pestaña Métricas ─────────────────
        sep  = "─" * 52
        out  = f"{'RESUMEN DE MÉTRICAS':^52}\n{sep}\n"
        out += f"  Símbolos distintos : {len(self.freqs)}\n"
        out += f"  Total de caracteres: {total}\n"
        out += f"  Bits originales    : {h_orig}  (asumiendo 8 bits/símbolo)\n"
        out += f"\n{'':>4}{'Huffman':>18}{'Shannon-Fano':>18}\n"
        out += f"  {sep}\n"
        rows_m = [
            ("Bits comprimidos",  f"{h_comp}",         f"{s_comp}"),
            ("Tasa compresión",   f"{h_rate:.2f} %",   f"{s_rate:.2f} %"),
            ("Longitud media (L)",f"{h_avg:.4f} bits", f"{s_avg:.4f} bits"),
            ("Entropía (H)",      f"{h_ent:.4f} bits", f"{s_ent:.4f} bits"),
            ("Eficiencia",        f"{h_eff:.2f} %",    f"{s_eff:.2f} %"),
        ]
        for label, hv, sv in rows_m:
            out += f"  {label:<22}{hv:>14}{sv:>14}\n"
        out += f"\n{sep}\n"
        out += f"  Muestra codif. Huffman (primeros 80 bits):\n  {self.h_encoded[:80]}...\n"
        out += f"\n  Muestra codif. Shannon (primeros 80 bits):\n  {self.s_encoded[:80]}...\n"
        self._write(self.txt_metricas, out)

        # ── Pestaña Tabla Huffman ─────────────
        self._write(self.txt_tabla_h, self._fmt_tabla("Huffman", self.h_codes, self.freqs, total))

        # ── Pestaña Tabla Shannon-Fano ────────
        self._write(self.txt_tabla_s, self._fmt_tabla("Shannon-Fano", self.s_codes, self.freqs, total))

        # ── Pestaña Decodificación ────────────
        dec_out  = f"{'VERIFICACIÓN DE DECODIFICACIÓN':^52}\n{'─'*52}\n\n"
        dec_out += f"  Huffman      → {'✅ CORRECTO' if h_ok else '❌ ERROR'}\n"
        dec_out += f"  Shannon-Fano → {'✅ CORRECTO' if s_ok else '❌ ERROR'}\n\n"
        dec_out += f"{'─'*52}\n"
        dec_out += f"  Texto original    ({total} chars):\n  {self.text[:120]}{'...' if total > 120 else ''}\n\n"
        dec_out += f"  Huffman decoded   ({len(h_decoded)} chars):\n  {h_decoded[:120]}{'...' if len(h_decoded) > 120 else ''}\n\n"
        dec_out += f"  Shannon decoded   ({len(s_decoded)} chars):\n  {s_decoded[:120]}{'...' if len(s_decoded) > 120 else ''}\n"
        self._write(self.txt_decode, dec_out)

        self._status(
            f"✅  Procesado — {total} símbolos · "
            f"Huffman: {h_rate:.1f}% · Shannon-Fano: {s_rate:.1f}%"
        )

    # ──────────────────────────────────────
    #  FORMATEADOR DE TABLA
    # ──────────────────────────────────────
    def _fmt_tabla(self, name, codes, freqs, total):
        sep = "─" * 64
        out = f"{'TABLA DE CÓDIGOS — ' + name.upper():^64}\n{sep}\n"
        out += f"  {'Símbolo':<12} {'Frec':>6} {'Prob':>10} {'Código':<20} {'Long':>5}\n"
        out += f"  {sep}\n"
        for char, freq in sorted(freqs.items(), key=lambda x: x[1], reverse=True):
            code    = codes.get(char, "")
            prob    = freq / total
            display = repr(char)
            out += f"  {display:<12} {freq:>6} {prob:>10.4f} {code:<20} {len(code):>5}\n"
        out += f"  {sep}\n"
        return out

    # ──────────────────────────────────────
    #  GRÁFICOS
    # ──────────────────────────────────────
    def ver_graficos(self):
        if not self.plot_data:
            messagebox.showinfo("Aviso", "Procesá datos primero (botón ▶ PROCESAR).")
            return
        met.show_charts(self.freqs, self.h_codes, self.s_codes, self.plot_data)


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = CompresorApp(root)
    root.mainloop()
