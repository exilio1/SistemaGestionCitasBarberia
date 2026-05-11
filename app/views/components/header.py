"""
Componente Header — Cabecera superior del dashboard.
Muestra el nombre del modulo activo, notificaciones y datos del usuario.
"""

import customtkinter as ctk
from datetime import datetime

# ── Colores ───────────────────────────────────────────────────────────────────
BG        = "#161616"   # fondo oscuro de la barra
BORDER    = "#222222"   # borde sutil
GOLD      = "#C9A020"   # color dorado para el avatar del usuario
TEXT_W    = "#F0F0F0"   # texto blanco principal
TEXT_G    = "#777777"   # texto gris secundario (fecha, rol)
CARD      = "#1F1F1F"   # no se usa en este archivo pero lo dejo por consistencia


class Header(ctk.CTkFrame):
    """Barra superior con fecha, notificaciones y perfil del usuario."""

    def __init__(self, parent, usuario: dict):
        super().__init__(
            parent,
            fg_color=BG,
            corner_radius=12,
            border_width=1, border_color=BORDER,
            height=56,   # altura fija de 56px
        )
        # Evito que el frame se encoja aunque el contenido sea pequeno
        self.pack_propagate(False)
        self._construir(usuario)

    def _construir(self, usuario):
        # ── Lado izquierdo: titulo de la aplicacion ───────────────────────
        izq = ctk.CTkFrame(self, fg_color="transparent")
        izq.pack(side="left", padx=16, pady=0)

        ctk.CTkLabel(
            izq, text="Barbers Studio",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_W,
        ).pack(side="left")

        ctk.CTkLabel(
            izq, text=" — Sistema de Gestión",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_G,
        ).pack(side="left")

        # ── Lado derecho: fecha actual + perfil del usuario ────────────────
        der = ctk.CTkFrame(self, fg_color="transparent")
        der.pack(side="right", padx=16)

        # Calculo la fecha de hoy en formato legible (ej: 28 ABR 2026)
        hoy_str = datetime.now().strftime("%d %b %Y").upper()
        ctk.CTkLabel(
            der, text=hoy_str,
            font=ctk.CTkFont(size=11),
            text_color=TEXT_G,
        ).pack(side="left", padx=(0, 16))

        # Separador vertical decorativo entre la fecha y el perfil
        ctk.CTkFrame(der, fg_color=BORDER, width=1, height=24).pack(
            side="left", padx=(0, 16)
        )

        # Nombre y rol del usuario alineados a la derecha
        info = ctk.CTkFrame(der, fg_color="transparent")
        info.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            info,
            text=usuario.get("nombre", "")[:20],  # limito a 20 caracteres
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_W, anchor="e",
        ).pack(anchor="e")

        ctk.CTkLabel(
            info,
            text=usuario.get("rol", "").capitalize(),
            font=ctk.CTkFont(size=10),
            text_color=TEXT_G, anchor="e",
        ).pack(anchor="e")

        # Circulo dorado con la inicial del nombre — actua como avatar
        inicial = usuario.get("nombre", "U")[0].upper()
        circulo = ctk.CTkFrame(
            der, fg_color=GOLD, corner_radius=18, width=36, height=36
        )
        circulo.pack(side="left")
        circulo.pack_propagate(False)
        ctk.CTkLabel(
            circulo, text=inicial,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0D0D0D",
        ).pack(expand=True)
