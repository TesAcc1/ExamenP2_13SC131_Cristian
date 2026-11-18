import customtkinter as ctk

# Configuración inicial de apariencia
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class Calculadora(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración y centrado de la ventana principal
        self.title("Calculadora")
        self.resizable(False, False)
        ancho_v, alto_v = 340, 535
        self.update_idletasks()
        factor = self._get_window_scaling()
        pos_x = int((self.winfo_screenwidth() - ancho_v) * factor / 2)
        pos_y = int((self.winfo_screenheight() - alto_v) * factor / 2)
        self.geometry(f"{ancho_v}x{alto_v}+{pos_x}+{pos_y}")

        # Variables de estado de la calculadora
        self.primer_numero = self.operador = self._timer_o = None
        self.reiniciar_pantalla = self.modo_oscuro = self._presionando_o = False
        self.encendida = True

        # Paleta de materiales (Modo Claro / Modo Oscuro)
        self.color_chasis = ("#E6E2D8", "#2C2E33")
        self.color_bisel_ext = ("#BFB9AC", "#1E2024")
        self.borde_bisel_ext = ("#968F80", "#3E4148")
        self.color_lcd_on = ("#8E9E7B", "#2E4730")
        self.color_lcd_off = ("#788569", "#111811")
        self.borde_lcd = ("#525E47", "#162417")
        self.texto_lcd = ("#111A0E", "#A6FFA6")
        self.texto_hist = ("#323E2A", "#68A868")
        self.color_led_on, self.borde_led_on, self.hover_led_on = ("#2E9E47", "#27853C"), ("#1E6E31", "#185426"), ("#25853B", "#1F6E31")
        self.color_led_off, self.borde_led_off, self.hover_led_off = ("#237A38", "#1C632D"), ("#175727", "#134721"), ("#1D692F", "#175225")

        self.configure(fg_color=self.color_chasis)

        # Panel superior y celda solar
        self.cabezal = ctk.CTkFrame(self, fg_color="transparent")
        self.cabezal.pack(fill="x", padx=16, pady=(12, 6))
        self.celda_solar = ctk.CTkButton(
            self.cabezal, text="│  │  │  │", width=84, height=20, font=("Consolas", 10, "bold"),
            fg_color=("#241A16", "#1B1412"), border_color=("#756F64", "#4A4D55"), border_width=2,
            corner_radius=8, text_color_disabled=("#9C8276", "#998278"), hover=False, state="disabled"
        )
        self.celda_solar.pack(side="right")

        # Pantalla principal e historial con marco de doble bisel
        self.marco_exterior_display = ctk.CTkFrame(
            self, fg_color=self.color_bisel_ext, border_color=self.borde_bisel_ext, border_width=2, corner_radius=9
        )
        self.marco_exterior_display.pack(fill="x", padx=16, pady=(0, 2))
        self.marco_display = ctk.CTkFrame(
            self.marco_exterior_display, fg_color=self.color_lcd_on, border_color=self.borde_lcd, border_width=2, corner_radius=6
        )
        self.marco_display.pack(fill="x", padx=4, pady=4)

        self.lbl_historial = ctk.CTkLabel(self.marco_display, text="", font=("Consolas", 13, "bold"), text_color=self.texto_hist, anchor="e")
        self.lbl_historial.pack(fill="x", padx=10, pady=(6, 0))
        self.lbl_pantalla = ctk.CTkLabel(self.marco_display, text="0", font=("Consolas", 27, "bold"), text_color=self.texto_lcd, anchor="e")
        self.lbl_pantalla.pack(fill="x", padx=10, pady=(0, 6))

        # Botón de encendido tipo botón-LED y línea divisoria
        self.barra_off = ctk.CTkFrame(self, fg_color="transparent")
        self.barra_off.pack(fill="x", padx=18, pady=(4, 4))
        self.btn_off = ctk.CTkButton(
            self.barra_off, text="ON", width=46, height=20, font=("Segoe UI", 10, "bold"),
            fg_color=self.color_led_on, border_color=self.borde_led_on, hover_color=self.hover_led_on,
            text_color="#FFFFFF", border_width=2, corner_radius=9, command=self.alternar_energia
        )
        self.btn_off.pack(side="right")

        self.ranura_chasis = ctk.CTkFrame(self, height=2, fg_color=("#CBC5B6", "#1C1D20"))
        self.ranura_chasis.pack(fill="x", padx=18, pady=(2, 6))

        # Contenedor de la cuadrícula de botones
        self.panel_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_botones.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        for i in range(5):
            if i < 4:
                self.panel_botones.columnconfigure(i, weight=1, pad=4)
            self.panel_botones.rowconfigure(i, weight=1, pad=4)

        self.crear_botones()
        self.bind("<KeyPress>", self.tecla_presionada)
        self.bind("<KeyRelease>", self.tecla_liberada)
        self.animar_encendido()

    # Control de eventos del teclado físico
    def tecla_presionada(self, event):
        c, k = event.char, event.keysym
        if k in ["M", "m"] and (event.state & 0x0001):
            return self.cambiar_tema()
        if k.lower() == "o":
            if not self._presionando_o:
                self._presionando_o = True
                self._timer_o = self.after(550, self._activar_o_sostenida)
            return

        mapa_op = {"+": "+", "-": "−", "*": "×", "x": "×", "X": "×", "/": "÷", "d": "÷", "D": "÷"}
        if c.isdigit():
            self.click_numero(int(c))
        elif c in mapa_op:
            self.click_operador(mapa_op[c])
        elif c == ".":
            self.click_punto()
        elif k in ["Return", "KP_Enter"] or c == "=":
            self.calcular()
        elif k == "BackSpace":
            self.retroceso()
        elif k == "Delete":
            self.borrar_entrada()
        elif k == "Escape" or c in ["c", "C"]:
            self.borrar_todo()

    def tecla_liberada(self, event):
        if event.keysym.lower() == "o":
            self._presionando_o = False
            if self._timer_o:
                self.after_cancel(self._timer_o)
                self._timer_o = None

    def _activar_o_sostenida(self):
        self._timer_o = None
        self.alternar_energia()

    # Animación de inicialización y formato numérico
    def animar_encendido(self):
        self.lbl_pantalla.configure(text="CARGANDO")
        self.after(400, lambda: self.lbl_pantalla.configure(text="0") if self.lbl_pantalla.cget("text") == "CARGANDO" else None)

    def formatear_con_comas(self, cadena):
        if "e" in cadena or cadena in ["INDEFINIDO", "CARGANDO", ""]:
            return cadena
        signo = "-" if cadena.startswith("-") else ""
        limpio = cadena.lstrip("-")
        if "." in limpio:
            entero, dec = limpio.split(".", 1)
            return f"{signo}{int(entero or 0):,}.{dec}"
        return f"{signo}{int(limpio):,}" if limpio else "0"

    def formatear_numero(self, valor):
        if valor == 0:
            return "0"
        if abs(valor) >= 1e100:
            return "INDEFINIDO"
        if abs(valor) >= 1e12 or (0 < abs(valor) < 1e-8):
            base, exp = f"{valor:.11e}".split("e")
            return f"{base.rstrip('0').rstrip('.')}e{int(exp)}"
        if valor.is_integer():
            return self.formatear_con_comas(str(int(valor)))
        texto = f"{valor:.10f}".rstrip("0").rstrip(".")
        if len(texto) > 12:
            dec = max(0, 12 - len(str(int(valor))) - 1)
            texto = f"{valor:.{dec}f}".rstrip("0").rstrip(".")
        return self.formatear_con_comas(texto)

    # Encendido y apagado de la pantalla
    def alternar_energia(self):
        self.encendida = not self.encendida
        if not self.encendida:
            self.primer_numero = self.operador = None
            self.lbl_historial.configure(text="")
            self.lbl_pantalla.configure(text="")
            self.marco_display.configure(fg_color=self.color_lcd_off)
            self.btn_off.configure(text="OFF", fg_color=self.color_led_off, border_color=self.borde_led_off, hover_color=self.hover_led_off, text_color=("#D8EEDD", "#B0D4B6"))
        else:
            self.marco_display.configure(fg_color=self.color_lcd_on)
            self.btn_off.configure(text="ON", fg_color=self.color_led_on, border_color=self.borde_led_on, hover_color=self.hover_led_on, text_color="#FFFFFF")
            self.animar_encendido()

    # Captura de dígitos y punto decimal
    def click_numero(self, digito):
        if not self.encendida or self.lbl_pantalla.cget("text") == "CARGANDO":
            return
        actual = self.lbl_pantalla.cget("text").replace(",", "")
        if self.reiniciar_pantalla or actual in ["0", "INDEFINIDO"]:
            if self.operador is None or actual == "INDEFINIDO":
                self.lbl_historial.configure(text="")
            nuevo, self.reiniciar_pantalla = str(digito), False
        elif len(actual.replace(".", "").replace("-", "")) < 12:
            nuevo = actual + str(digito)
        else:
            return
        self.lbl_pantalla.configure(text=self.formatear_con_comas(nuevo))

    def click_punto(self):
        if not self.encendida or self.lbl_pantalla.cget("text") == "CARGANDO":
            return
        actual = self.lbl_pantalla.cget("text").replace(",", "")
        if self.reiniciar_pantalla or actual in ["0", "INDEFINIDO"]:
            if self.operador is None or actual == "INDEFINIDO":
                self.lbl_historial.configure(text="")
            nuevo, self.reiniciar_pantalla = "0.", False
        elif "." not in actual and "e" not in actual and len(actual.replace("-", "")) < 12:
            nuevo = actual + "."
        else:
            return
        self.lbl_pantalla.configure(text=self.formatear_con_comas(nuevo))

    # Selección de operadores y cálculo de resultados
    def click_operador(self, op):
        if not self.encendida or self.lbl_pantalla.cget("text") in ["INDEFINIDO", "CARGANDO"]:
            return
        if self.primer_numero is not None and not self.reiniciar_pantalla:
            self.calcular()
        try:
            self.primer_numero = float(self.lbl_pantalla.cget("text").replace(",", ""))
        except ValueError:
            return
        self.operador, self.reiniciar_pantalla = op, True
        self.lbl_historial.configure(text=f"{self.formatear_numero(self.primer_numero)} {op}")

    def calcular(self):
        if not self.encendida or self.operador is None or self.primer_numero is None:
            return
        try:
            segundo = float(self.lbl_pantalla.cget("text").replace(",", ""))
        except ValueError:
            return

        expresion = f"{self.formatear_numero(self.primer_numero)} {self.operador} {self.formatear_numero(segundo)} ="
        if self.operador == "÷" and segundo == 0:
            self.lbl_historial.configure(text=f"{self.formatear_numero(self.primer_numero)} ÷ 0 =")
            self.lbl_pantalla.configure(text="INDEFINIDO")
            self.primer_numero, self.operador, self.reiniciar_pantalla = None, None, True
            return

        ops = {"+": self.primer_numero + segundo, "−": self.primer_numero - segundo,
               "×": self.primer_numero * segundo, "÷": self.primer_numero / segundo if segundo else 0}
        res = ops[self.operador]
        texto_res = self.formatear_numero(res)
        self.lbl_historial.configure(text=expresion)
        self.lbl_pantalla.configure(text=texto_res)
        self.primer_numero = res if texto_res != "INDEFINIDO" else None
        self.operador, self.reiniciar_pantalla = None, True

    # Funciones de limpieza y cambio de apariencia
    def borrar_todo(self):
        if not self.encendida:
            return self.alternar_energia()
        self.primer_numero, self.operador, self.reiniciar_pantalla = None, None, False
        self.lbl_historial.configure(text="")
        self.lbl_pantalla.configure(text="0")

    def borrar_entrada(self):
        if self.encendida and self.lbl_pantalla.cget("text") != "CARGANDO":
            self.lbl_pantalla.configure(text="0")

    def retroceso(self):
        if not self.encendida or self.lbl_pantalla.cget("text") == "CARGANDO":
            return
        actual = self.lbl_pantalla.cget("text").replace(",", "")
        if actual == "INDEFINIDO" or self.reiniciar_pantalla or "e" in actual:
            return self.lbl_pantalla.configure(text="0")
        nuevo = actual[:-1]
        self.lbl_pantalla.configure(text=self.formatear_con_comas("0" if nuevo in ["", "-"] else nuevo))

    def cambiar_tema(self):
        self.modo_oscuro = not self.modo_oscuro
        ctk.set_appearance_mode("dark" if self.modo_oscuro else "light")
        self.btn_tema.configure(text="☀️" if self.modo_oscuro else "🌙")

    # Construcción de la cuadrícula de botones con doble bisel
    def crear_botones(self):
        estilos = {
            "num": (("#FAF8F3", "#383A40"), ("#ABA69A", "#4F535D"), ("#E8E4DA", "#2E3035"), ("#18191B", "#FFFFFF"), ("Segoe UI", 24, "bold")),
            "op":  (("#375469", "#294152"), ("#203340", "#3F5E75"), ("#2B4354", "#203442"), "white", ("Segoe UI", 24, "bold")),
            "ctl": (("#D5D0C5", "#42454D"), ("#A09B90", "#585D68"), ("#C5C0B5", "#35383E"), ("#18191B", "#FFFFFF"), ("Segoe UI", 17, "bold"))
        }
        botones = [
            ("C", self.borrar_todo, "ctl"), ("CE", self.borrar_entrada, "ctl"), ("⌫", self.retroceso, "ctl"), ("÷", lambda: self.click_operador("÷"), "op"),
            ("7", lambda: self.click_numero(7), "num"), ("8", lambda: self.click_numero(8), "num"), ("9", lambda: self.click_numero(9), "num"), ("×", lambda: self.click_operador("×"), "op"),
            ("4", lambda: self.click_numero(4), "num"), ("5", lambda: self.click_numero(5), "num"), ("6", lambda: self.click_numero(6), "num"), ("−", lambda: self.click_operador("−"), "op"),
            ("1", lambda: self.click_numero(1), "num"), ("2", lambda: self.click_numero(2), "num"), ("3", lambda: self.click_numero(3), "num"), ("+", lambda: self.click_operador("+"), "op"),
            ("🌙", self.cambiar_tema, "ctl"), ("0", lambda: self.click_numero(0), "num"), (".", self.click_punto, "num"), ("=", self.calcular, "op")
        ]

        for idx, (texto, cmd, tipo) in enumerate(botones):
            fg, borde, hover, t_col, fuente = estilos[tipo]
            socket = ctk.CTkFrame(self.panel_botones, fg_color=self.color_bisel_ext, border_color=self.borde_bisel_ext, border_width=2, corner_radius=9)
            socket.grid(row=idx // 4, column=idx % 4, sticky="nsew", padx=2, pady=2)
            btn = ctk.CTkButton(socket, text=texto, font=fuente, fg_color=fg, border_color=borde, hover_color=hover, border_width=2, corner_radius=6, text_color=t_col, command=cmd)
            btn.pack(fill="both", expand=True, padx=4, pady=4)

            if texto == "🌙":
                self.btn_tema = btn
            elif texto == "5":
                muesca = ctk.CTkFrame(socket, width=14, height=3, corner_radius=0, fg_color=t_col)
                muesca.place(relx=0.5, rely=0.81, anchor="center")
                muesca.bind("<Button-1>", lambda e: self.click_numero(5))


if __name__ == "__main__":
    app = Calculadora()
    app.mainloop()