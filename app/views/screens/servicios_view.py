"""
Vista de Servicios.
Permite al administrador agregar, editar y desactivar los servicios
que ofrece la barberia. Los servicios activos aparecen en el chatbot
de Telegram y en el formulario de citas.
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
AZUL       = "#2980B9"


class ServiciosView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color="#111111")
        self._usuario = usuario
        self._construir()

    def _construir(self):
        # ── Titulo ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Gestion de Servicios",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(pady=(16, 4), padx=16, anchor="w")

        ctk.CTkLabel(
            self,
            text="Agrega o edita los servicios que ofrece la barberia. Solo el administrador puede hacer esto.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_GRAY,
        ).pack(padx=16, anchor="w")

        # ── Formulario para crear o editar un servicio ─────────────────────
        tarjeta = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(
            tarjeta, text="Agregar o editar servicio",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 8))

        # Campo ID — solo lo necesita para editar o desactivar
        ctk.CTkLabel(
            tarjeta, text="ID del servicio (solo para editar o desactivar)",
            text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=16)
        self.entry_id = ctk.CTkEntry(
            tarjeta, placeholder_text="Ej. 1",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40, width=180,
        )
        self.entry_id.pack(anchor="w", padx=16, pady=(2, 10))

        # Campos en dos columnas para aprovechar el espacio
        columnas = ctk.CTkFrame(tarjeta, fg_color="transparent")
        columnas.pack(fill="x", padx=16, pady=(0, 10))
        columnas.columnconfigure(0, weight=1)
        columnas.columnconfigure(1, weight=1)

        # Columna izquierda: nombre y precio
        izq = ctk.CTkFrame(columnas, fg_color="transparent")
        izq.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(izq, text="Nombre del servicio",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_nombre = ctk.CTkEntry(
            izq, placeholder_text="Ej. Corte de cabello",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_nombre.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(izq, text="Precio ($)",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_precio = ctk.CTkEntry(
            izq, placeholder_text="Ej. 25000",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_precio.pack(fill="x", pady=(2, 10))

        # Columna derecha: duracion y descripcion
        der = ctk.CTkFrame(columnas, fg_color="transparent")
        der.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(der, text="Duracion (minutos)",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_duracion = ctk.CTkEntry(
            der, placeholder_text="Ej. 30",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_duracion.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(der, text="Descripcion (opcional)",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_descripcion = ctk.CTkEntry(
            der, placeholder_text="Ej. Incluye lavado y secado",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_descripcion.pack(fill="x", pady=(2, 10))

        # ── Botones de accion ──────────────────────────────────────────────
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

        # Desactivar no elimina el servicio, solo lo oculta del catalogo
        self.btn_desactivar = ctk.CTkButton(
            fila_btns, text="Desactivar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ROJO, hover_color="#B03A2E",
            text_color="white", height=42, corner_radius=8,
        )
        self.btn_desactivar.pack(side="left", padx=(0, 8))

        # Activar sirve para volver a habilitar un servicio desactivado
        self.btn_activar = ctk.CTkButton(
            fila_btns, text="Activar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=AZUL, hover_color="#1F618D",
            text_color="white", height=42, corner_radius=8,
        )
        self.btn_activar.pack(side="left")

        # Mensaje de exito o error debajo de los botones
        self.lbl_resultado = ctk.CTkLabel(
            tarjeta, text="",
            font=ctk.CTkFont(size=12),
            text_color=VERDE,
        )
        self.lbl_resultado.pack(padx=16, pady=(0, 8))

        # ── Tabla con todos los servicios ──────────────────────────────────
        tarjeta2 = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta2.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        ctk.CTkLabel(
            tarjeta2, text="Catalogo de servicios",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            tarjeta2,
            text="Los servicios activos aparecen en el chatbot de Telegram y en el formulario de citas.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_GRAY,
        ).pack(anchor="w", padx=16, pady=(0, 8))

        # Textbox monoespaciado para alinear bien las columnas
        self.tabla = ctk.CTkTextbox(
            tarjeta2, state="disabled",
            fg_color=FIELD_BG, text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=12, family="Courier"),
        )
        self.tabla.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def cargar_servicios(self, servicios):
        """Llena la tabla con la lista de servicios recibida del modelo."""
        self.tabla.configure(state="normal")
        self.tabla.delete("1.0", "end")

        if not servicios:
            self.tabla.insert("end", "No hay servicios registrados.\nUsa el formulario de arriba para agregar el primer servicio.")
        else:
            # Encabezado alineado
            encabezado = f"{'ID':<5} {'NOMBRE':<25} {'PRECIO':>10} {'DURACION':>10} {'ESTADO':<10} {'DESCRIPCION'}\n"
            self.tabla.insert("end", encabezado)
            self.tabla.insert("end", "-" * 80 + "\n")

            for s in servicios:
                estado = "Activo" if s.get("activo") else "Inactivo"
                precio = f"${s.get('precio', 0):,.0f}"
                duracion = f"{s.get('duracion_minutos', 30)} min"
                desc = s.get("descripcion", "") or ""
                linea = (
                    f"{s.get('id',''):<5} "
                    f"{s.get('nombre',''):<25} "
                    f"{precio:>10} "
                    f"{duracion:>10} "
                    f"{estado:<10} "
                    f"{desc}\n"
                )
                self.tabla.insert("end", linea)

        self.tabla.configure(state="disabled")

    def mostrar_resultado(self, mensaje, error=False):
        """Muestra un mensaje de exito en verde o de error en rojo."""
        color = ROJO if error else VERDE
        self.lbl_resultado.configure(text=mensaje, text_color=color)
