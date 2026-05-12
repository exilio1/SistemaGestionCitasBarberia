"""
Vista de Empleados.
Permite crear, ver y desactivar empleados (barberos).
Solo el administrador puede acceder a esta pantalla.
"""

import customtkinter as ctk

# Colores de la aplicacion
GOLD       = "#C9A020"
GOLD_HOVER = "#A8841A"
BG_CARD    = "#1C1C1C"
FIELD_BG   = "#252525"
TEXT_GRAY  = "#888888"
TEXT_WHITE = "#F0F0F0"
VERDE      = "#27AE60"
ROJO       = "#E74C3C"


class EmpleadosView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color="#111111")
        self._usuario = usuario
        self._construir()

    def _construir(self):
        # ── Titulo ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Gestión de Empleados",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(pady=(16, 4), padx=16, anchor="w")

        ctk.CTkLabel(
            self,
            text="Administra los barberos del negocio. Solo el administrador puede hacer esto.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_GRAY,
        ).pack(padx=16, anchor="w")

        # ── Formulario para crear un nuevo empleado ────────────────────────
        tarjeta = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(
            tarjeta, text="Agregar nuevo empleado",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            tarjeta, text="ID para editar o desactivar",
            text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=16)
        self.entry_id = ctk.CTkEntry(
            tarjeta, placeholder_text="Ej. 1",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40, width=180,
        )
        self.entry_id.pack(anchor="w", padx=16, pady=(2, 10))

        # Campos del formulario en dos columnas para aprovechar el espacio
        columnas = ctk.CTkFrame(tarjeta, fg_color="transparent")
        columnas.pack(fill="x", padx=16, pady=(0, 10))
        columnas.columnconfigure(0, weight=1)
        columnas.columnconfigure(1, weight=1)

        # Columna izquierda: nombre y telefono
        izq = ctk.CTkFrame(columnas, fg_color="transparent")
        izq.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(izq, text="Nombre completo",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_nombre = ctk.CTkEntry(
            izq, placeholder_text="Ej. Carlos Ramirez",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_nombre.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(izq, text="Teléfono",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_telefono = ctk.CTkEntry(
            izq, placeholder_text="Ej. 3001234567",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_telefono.pack(fill="x", pady=(2, 10))

        # Columna derecha: especialidad y porcentaje de ganancia
        der = ctk.CTkFrame(columnas, fg_color="transparent")
        der.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(der, text="Especialidad",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_especialidad = ctk.CTkEntry(
            der, placeholder_text="Ej. Corte y barba",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_especialidad.pack(fill="x", pady=(2, 10))

        # El porcentaje de ganancia define cuanto del pago le corresponde al barbero
        ctk.CTkLabel(der, text="% Ganancia (default 60%)",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_porcentaje = ctk.CTkEntry(
            der, placeholder_text="Ej. 60",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_porcentaje.pack(fill="x", pady=(2, 10))

        # Botones de accion: agregar, editar y desactivar
        fila_btns = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila_btns.pack(anchor="w", padx=16, pady=(0, 14))

        self.btn_crear = ctk.CTkButton(
            fila_btns, text="Agregar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=VERDE, hover_color="#1E8449",
            text_color="white", height=42, corner_radius=8,
        )
        self.btn_crear.pack(side="left", padx=(0, 8))

        self.btn_editar = ctk.CTkButton(
            fila_btns, text="Editar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#111111", height=42, corner_radius=8,
        )
        self.btn_editar.pack(side="left", padx=(0, 8))

        # Desactivar en lugar de eliminar para preservar el historial de citas
        self.btn_eliminar = ctk.CTkButton(
            fila_btns, text="Desactivar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ROJO, hover_color="#B03A2E",
            text_color="white", height=42, corner_radius=8,
        )
        self.btn_eliminar.pack(side="left")

        # Label para mensajes de exito o error
        self.lbl_resultado = ctk.CTkLabel(
            tarjeta, text="",
            font=ctk.CTkFont(size=12),
            text_color=VERDE,
        )
        self.lbl_resultado.pack(padx=16, pady=(0, 8))

        # ── Tabla con los empleados activos ───────────────────────────────
        tarjeta2 = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta2.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        ctk.CTkLabel(
            tarjeta2, text="Empleados activos",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # Textbox monoespaciado para alinear bien las columnas
        self.tabla = ctk.CTkTextbox(
            tarjeta2, state="disabled",
            fg_color=FIELD_BG, text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=12, family="Courier"),
        )
        self.tabla.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def cargar_empleados(self, empleados):
        """Llena la tabla con la lista de empleados recibida del modelo."""
        self.tabla.configure(state="normal")
        self.tabla.delete("1.0", "end")

        if not empleados:
            self.tabla.insert("end", "No hay empleados registrados.")
        else:
            # Encabezado con columnas alineadas
            encabezado = f"{'ID':<5} {'NOMBRE':<22} {'TELÉFONO':<15} {'ESPECIALIDAD':<22} {'%':>5}\n"
            self.tabla.insert("end", encabezado)
            self.tabla.insert("end", "-" * 72 + "\n")

            for e in empleados:
                linea = (
                    f"{e.get('id',''):<5} "
                    f"{e.get('nombre',''):<22} "
                    f"{e.get('telefono',''):<15} "
                    f"{e.get('especialidad',''):<22} "
                    f"{e.get('porcentaje_ganancia', 60):>4.0f}%\n"
                )
                self.tabla.insert("end", linea)

        self.tabla.configure(state="disabled")

    def mostrar_resultado(self, mensaje, error=False):
        """Muestra un mensaje de exito en verde o de error en rojo."""
        color = ROJO if error else VERDE
        self.lbl_resultado.configure(text=mensaje, text_color=color)
