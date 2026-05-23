"""
Popup de Autenticación de Doble Factor (2FA / TOTP).

Modo 'setup':
    Primera vez que el usuario entra al sistema.
    Muestra el código QR para escanear con Google Authenticator.
    El usuario escanea, ingresa el código de 6 dígitos para confirmar
    que quedó bien configurado y recién entonces se hace el login.

Modo 'verificar':
    Logins siguientes. Solo pide el código de 6 dígitos
    que muestra Google Authenticator en ese momento.
"""

import io
import qrcode
import customtkinter as ctk
from PIL import Image

GOLD       = "#C9A020"
GOLD_HOVER = "#A8841A"
BG         = "#1A1A1A"
FIELD_BG   = "#252525"
TEXT_WHITE = "#F0F0F0"
TEXT_GRAY  = "#777777"
ROJO       = "#E74C3C"


class Popup2FA(ctk.CTkToplevel):
    """
    Parámetros
    ----------
    parent       : ventana padre
    modo         : 'setup' | 'verificar'
    on_verificar : función(codigo: str) → bool
                   El controlador la define; devuelve True si el código es correcto.
    uri          : solo en modo setup — el URI otpauth:// para generar el QR
    on_cancelar  : función opcional si el usuario cierra sin verificar
    """

    def __init__(self, parent, modo: str, on_verificar,
                 uri: str = "", on_cancelar=None):
        super().__init__(parent)
        self._modo         = modo
        self._on_verificar = on_verificar
        self._on_cancelar  = on_cancelar
        self._uri          = uri

        self.title("Verificación de seguridad — Barbers Studio")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.grab_set()
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._cancelar)

        if modo == "setup":
            self.geometry("420x560")
            self._construir_setup()
        else:
            self.geometry("380x300")
            self._construir_verificar()

        self._centrar()

    def _centrar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    # ── Modo SETUP ────────────────────────────────────────────────────────────

    def _construir_setup(self):
        PAD = {"padx": 32}

        ctk.CTkLabel(
            self, text="Configurar Google Authenticator",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(pady=(24, 4), **PAD)

        ctk.CTkLabel(
            self,
            text="1. Abre Google Authenticator en tu celular\n"
                 "2. Toca el botón + y elige «Escanear código QR»\n"
                 "3. Apunta la cámara a este código",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_GRAY,
            justify="left",
        ).pack(pady=(0, 12), **PAD)

        # ── Generar y mostrar el QR ───────────────────────────────────────
        qr_img  = self._generar_qr(self._uri)
        ctk_img = ctk.CTkImage(light_image=qr_img, dark_image=qr_img, size=(200, 200))
        ctk.CTkLabel(self, image=ctk_img, text="").pack(pady=(0, 12))

        ctk.CTkLabel(
            self,
            text="4. Después de escanear, escribe el código de 6 dígitos\n"
                 "   que aparece en la app para confirmar la configuración",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_GRAY,
            justify="left",
        ).pack(**PAD)

        self._entry = ctk.CTkEntry(
            self,
            placeholder_text="Código de 6 dígitos",
            fg_color=FIELD_BG, border_width=1, border_color="#333333",
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=20),
            height=48, justify="center",
        )
        self._entry.pack(fill="x", padx=32, pady=(10, 4))
        self._entry.bind("<Return>", lambda e: self._verificar())

        self._lbl_error = ctk.CTkLabel(
            self, text="", text_color=ROJO, font=ctk.CTkFont(size=11)
        )
        self._lbl_error.pack(pady=(0, 6))

        ctk.CTkButton(
            self, text="CONFIRMAR Y ACTIVAR 2FA",
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#0D0D0D", font=ctk.CTkFont(size=13, weight="bold"),
            height=44, corner_radius=8,
            command=self._verificar,
        ).pack(fill="x", padx=32, pady=(0, 20))

    # ── Modo VERIFICAR ────────────────────────────────────────────────────────

    def _construir_verificar(self):
        PAD = {"padx": 32}

        ctk.CTkLabel(
            self, text="Verificación en dos pasos",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(pady=(28, 4), **PAD)

        ctk.CTkLabel(
            self,
            text="Abre Google Authenticator e ingresa\n"
                 "el código de 6 dígitos para continuar.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_GRAY,
            justify="center",
        ).pack(pady=(4, 16), **PAD)

        self._entry = ctk.CTkEntry(
            self,
            placeholder_text="_ _ _ _ _ _",
            fg_color=FIELD_BG, border_width=1, border_color="#333333",
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=28, weight="bold"),
            height=56, justify="center",
        )
        self._entry.pack(fill="x", padx=32, pady=(0, 4))
        self._entry.bind("<Return>", lambda e: self._verificar())
        self._entry.focus()

        self._lbl_error = ctk.CTkLabel(
            self, text="", text_color=ROJO, font=ctk.CTkFont(size=11)
        )
        self._lbl_error.pack(pady=(0, 8))

        ctk.CTkButton(
            self, text="VERIFICAR",
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#0D0D0D", font=ctk.CTkFont(size=13, weight="bold"),
            height=44, corner_radius=8,
            command=self._verificar,
        ).pack(fill="x", padx=32, pady=(0, 10))

        ctk.CTkButton(
            self, text="Cancelar",
            fg_color="transparent", hover_color="#252525",
            text_color=TEXT_GRAY, font=ctk.CTkFont(size=12),
            height=32, corner_radius=8,
            command=self._cancelar,
        ).pack(fill="x", padx=32)

    # ── Lógica común ─────────────────────────────────────────────────────────

    def _verificar(self):
        codigo = self._entry.get().strip().replace(" ", "")
        if len(codigo) != 6 or not codigo.isdigit():
            self._lbl_error.configure(text="El código debe tener exactamente 6 dígitos.")
            return
        if self._on_verificar(codigo):
            self.destroy()
        else:
            self._lbl_error.configure(text="Código incorrecto. Inténtalo de nuevo.")
            self._entry.delete(0, "end")

    def _cancelar(self):
        if self._on_cancelar:
            self._on_cancelar()
        self.destroy()

    @staticmethod
    def _generar_qr(uri: str) -> Image.Image:
        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Image.open(buf).convert("RGB")
