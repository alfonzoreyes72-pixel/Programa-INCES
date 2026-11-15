import sys
import os
from html import escape
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


MENSAJE_CUENTA_INHABILITADA = "Tu cuenta ha sido inhabilitada temporalmente por el administrador."

ESTILO_BOTON_CANCELAR = """
    QPushButton {
        background-color: #e0dede;
        color: #333333;
        border-radius: 20px;
        border: 2px solid #e0dede;
        padding: 5px;
        font-size: 15px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #d0cdcd;
        border: 2px solid #d0cdcd;
    }
"""

ESTILO_BOTON_AZUL = """
    QPushButton {
        background-color: #0833a2;
        color: white;
        border-radius: 20px;
        border: 2px solid #0833a2;
        padding: 5px;
        font-size: 15px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #3150ff;
        border: 2px solid #3150ff;
    }
    QPushButton:disabled {
        background-color: #c3cde6;
        border: 2px solid #c3cde6;
    }
"""

ESTILO_BOTON_ROJO = """
    QPushButton {
        background-color: #d32f2f;
        color: white;
        border-radius: 20px;
        border: 2px solid #d32f2f;
        padding: 5px;
        font-size: 15px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #e53935;
        border: 2px solid #e53935;
    }
    QPushButton:disabled {
        background-color: #e8c4c4;
        border: 2px solid #e8c4c4;
    }
"""


def asegurar_columna_bloqueado():
    """La tabla usuarios no tiene la columna 'bloqueado'; se agrega una sola vez si falta."""
    try:
        db = GestorBD()
        conexion = db.obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SHOW COLUMNS FROM usuarios LIKE 'bloqueado'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE usuarios ADD COLUMN bloqueado TINYINT(1) NOT NULL DEFAULT 0")
                conexion.commit()
            cursor.close()
    except Exception as e:
        print(f"Error al verificar la columna bloqueado: {e}")


class AvisoCuentaInhabilitada(QDialog):
    """Aviso modal que se muestra al usuario cuando su cuenta fue inhabilitada"""

    def __init__(self, parent=None, titulo="Cuenta inhabilitada", mensaje=MENSAJE_CUENTA_INHABILITADA):
        super().__init__(parent)

        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setFixedSize(480, 300)
        self.setStyleSheet("QDialog { background-color: #bfbdbe; }")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        panel = QFrame()
        panel.setObjectName("panelAviso")
        panel.setStyleSheet("""
            QFrame#panelAviso {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        layout_principal.addWidget(panel)

        layout_panel = QVBoxLayout(panel)
        layout_panel.setContentsMargins(25, 25, 25, 25)
        layout_panel.setSpacing(15)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(lbl_titulo)

        caja_mensaje = QFrame()
        caja_mensaje.setObjectName("cajaMensaje")
        caja_mensaje.setStyleSheet("""
            QFrame#cajaMensaje {
                background-color: #fdecec;
                border-radius: 10px;
                border: 1px solid #f5c6c6;
                border-left: 5px solid #d32f2f;
            }
        """)
        layout_mensaje = QVBoxLayout(caja_mensaje)
        layout_mensaje.setContentsMargins(15, 12, 15, 12)

        lbl_mensaje = QLabel(mensaje)
        lbl_mensaje.setWordWrap(True)
        lbl_mensaje.setStyleSheet("font-size: 14px; font-weight: bold; color: #7a1c1c; border: none; background: transparent;")
        layout_mensaje.addWidget(lbl_mensaje)
        layout_panel.addWidget(caja_mensaje)

        layout_panel.addStretch()

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setFixedSize(160, 40)
        btn_aceptar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aceptar.setStyleSheet(ESTILO_BOTON_AZUL)
        btn_aceptar.clicked.connect(self.accept)
        layout_panel.addWidget(btn_aceptar, alignment=Qt.AlignmentFlag.AlignCenter)


class VentanaAcceso(QDialog):
    """Ventana modal para bloquear el acceso de un usuario o devolvérselo si ya estaba bloqueado"""

    def __init__(self, datos_usuario, parent=None, id_usuario_actual=None):
        super().__init__(parent)

        self.id_usuario = datos_usuario.get("id_usuario")
        self.nombre_usuario = datos_usuario.get("usuario", "N/D")
        self.trabajador = datos_usuario.get("trabajador_vinculado", "N/D")
        self.cedula = datos_usuario.get("cedula", "N/D")
        self.rol = datos_usuario.get("rol", "N/D")
        self.id_usuario_actual = id_usuario_actual

        # Si ya estaba bloqueado, la ventana sirve para devolverle el acceso
        self.va_a_bloquear = not bool(datos_usuario.get("bloqueado"))
        color = "#d32f2f" if self.va_a_bloquear else "#163e7a"
        titulo = "Bloquear acceso" if self.va_a_bloquear else "Devolver acceso"

        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setMinimumSize(540, 580)
        self.resize(580, 620)
        self.setStyleSheet("QDialog { background-color: #bfbdbe; }")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Panel principal blanco, igual al de la ventana de usuarios
        self.panel = QFrame()
        self.panel.setObjectName("panelAcceso")
        self.panel.setStyleSheet("""
            QFrame#panelAcceso {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        layout_principal.addWidget(self.panel)

        layout_panel = QVBoxLayout(self.panel)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(15)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(lbl_titulo)

        # Pregunta principal con el nombre del usuario resaltado
        nombre_html = f"<span style='color:{color};'>{escape(str(self.nombre_usuario))}</span>"
        if self.va_a_bloquear:
            texto_pregunta = f"¿Estás seguro de querer bloquear el acceso a {nombre_html}?"
        else:
            texto_pregunta = f"¿Quieres devolverle el acceso a {nombre_html}?"

        lbl_pregunta = QLabel(texto_pregunta)
        lbl_pregunta.setTextFormat(Qt.TextFormat.RichText)
        lbl_pregunta.setWordWrap(True)
        lbl_pregunta.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(lbl_pregunta)

        # Tarjeta con los datos del usuario
        tarjeta_datos = QFrame()
        tarjeta_datos.setObjectName("tarjetaDatos")
        tarjeta_datos.setStyleSheet(f"""
            QFrame#tarjetaDatos {{
                background-color: #f4f6f9;
                border-radius: 10px;
                border: 1px solid #e2e6eb;
                border-left: 5px solid {color};
            }}
        """)
        layout_datos = QVBoxLayout(tarjeta_datos)
        layout_datos.setContentsMargins(15, 12, 15, 12)
        layout_datos.setSpacing(6)

        for etiqueta, valor in [
            ("Usuario", self.nombre_usuario),
            ("Trabajador vinculado", self.trabajador),
            ("Cédula", self.cedula),
            ("Rol asignado", self.rol),
        ]:
            lbl = QLabel(f"<span style='color:#777777;'>{etiqueta}:</span>  <b style='color:#163e7a;'>{escape(str(valor))}</b>")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            lbl.setStyleSheet("font-size: 13px; border: none; background: transparent;")
            layout_datos.addWidget(lbl)
        layout_panel.addWidget(tarjeta_datos)

        # Advertencias o información según la acción
        if self.va_a_bloquear:
            fondo, borde, color_titulo, color_texto = "#fdecec", "#f5c6c6", "#b71c1c", "#7a1c1c"
            titulo_caja = "⚠ Antes de continuar, ten en cuenta:"
            puntos = [
                "El usuario no podrá iniciar sesión hasta que el administrador le devuelva el acceso.",
                "Si tiene la sesión iniciada, se cerrará automáticamente en pocos segundos.",
                "Sus datos, su rol y sus privilegios se conservan sin cambios.",
                "Puedes devolverle el acceso en cualquier momento desde esta misma opción.",
            ]
        else:
            fondo, borde, color_titulo, color_texto = "#eaf1fb", "#c9daf0", "#163e7a", "#163e7a"
            titulo_caja = "ℹ Al devolver el acceso:"
            puntos = [
                "El usuario podrá iniciar sesión nuevamente en el sistema.",
                "Conservará su rol y sus privilegios anteriores.",
                "Podrás volver a bloquearle el acceso cuando lo necesites.",
            ]

        caja_info = QFrame()
        caja_info.setObjectName("cajaInfo")
        caja_info.setStyleSheet(f"""
            QFrame#cajaInfo {{
                background-color: {fondo};
                border-radius: 10px;
                border: 1px solid {borde};
            }}
        """)
        layout_info = QVBoxLayout(caja_info)
        layout_info.setContentsMargins(15, 12, 15, 12)
        layout_info.setSpacing(6)

        lbl_caja_titulo = QLabel(titulo_caja)
        lbl_caja_titulo.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color_titulo}; border: none; background: transparent;")
        layout_info.addWidget(lbl_caja_titulo)

        for texto in puntos:
            lbl = QLabel(f"•  {texto}")
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"font-size: 12px; color: {color_texto}; border: none; background: transparent;")
            layout_info.addWidget(lbl)
        layout_panel.addWidget(caja_info)

        layout_panel.addStretch()

        # Mensaje de estado (bloqueos de seguridad o errores)
        self.lbl_estado = QLabel("")
        self.lbl_estado.setWordWrap(True)
        self.lbl_estado.setStyleSheet("font-size: 12px; font-weight: bold; color: #d32f2f; border: none; background: transparent;")
        self.lbl_estado.hide()
        layout_panel.addWidget(self.lbl_estado)

        # Botones inferiores
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(12)
        layout_botones.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(140, 40)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet(ESTILO_BOTON_CANCELAR)
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_confirmar = QPushButton(titulo)
        self.btn_confirmar.setFixedSize(200, 40)
        self.btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirmar.setStyleSheet(ESTILO_BOTON_ROJO if self.va_a_bloquear else ESTILO_BOTON_AZUL)
        self.btn_confirmar.clicked.connect(self.confirmar)

        layout_botones.addWidget(self.btn_cancelar)
        layout_botones.addWidget(self.btn_confirmar)
        layout_panel.addLayout(layout_botones)

        # Verificaciones de seguridad iniciales
        motivo = self.obtener_motivo_bloqueo()
        if motivo:
            self.btn_confirmar.setEnabled(False)
            self.mostrar_mensaje(motivo)

    def obtener_motivo_bloqueo(self):
        """Devuelve un texto si la acción NO se puede realizar, o None si es seguro continuar"""
        if self.va_a_bloquear and self.id_usuario_actual is not None and self.id_usuario == self.id_usuario_actual:
            return "No puedes bloquear tu propia cuenta mientras tienes la sesión iniciada."

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                return "No se pudo verificar el usuario en la base de datos."

            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.nombre_rol,
                       (SELECT COUNT(*) FROM usuarios u2
                        WHERE u2.id_rol_fk = u.id_rol_fk AND COALESCE(u2.bloqueado, 0) = 0) AS activos_rol
                FROM usuarios u
                LEFT JOIN roles r ON u.id_rol_fk = r.id_rol
                WHERE u.id_usuario = %s
            """, (self.id_usuario,))
            resultado = cursor.fetchone()
            cursor.close()

            if not resultado:
                return "Este usuario ya no existe en la base de datos."

            if self.va_a_bloquear:
                nombre_rol = str(resultado.get("nombre_rol") or "").lower()
                if "administrador" in nombre_rol and resultado["activos_rol"] <= 1:
                    return "No se puede bloquear: es el único administrador activo del sistema."
        except Exception as e:
            print(f"Error al verificar el usuario: {e}")
            return "No se pudo verificar el usuario en la base de datos."

        return None

    def mostrar_mensaje(self, texto):
        self.lbl_estado.setText(texto)
        self.lbl_estado.show()

    def confirmar(self):
        # Se vuelve a verificar justo antes de aplicar el cambio
        motivo = self.obtener_motivo_bloqueo()
        if motivo:
            self.btn_confirmar.setEnabled(False)
            self.mostrar_mensaje(motivo)
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "UPDATE usuarios SET bloqueado = %s WHERE id_usuario = %s",
                    (1 if self.va_a_bloquear else 0, self.id_usuario)
                )
                conexion.commit()
                cursor.close()
                self.accept()
                return
        except Exception as e:
            print(f"Error al actualizar el acceso del usuario: {e}")

        self.mostrar_mensaje("No se pudo actualizar el acceso del usuario. Intenta de nuevo.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    datos_prueba = {
        "id_usuario": 1,
        "usuario": "usuario_prueba",
        "trabajador_vinculado": "Carlos Gomez",
        "cedula": "26543210",
        "rol": "Administrador",
        "bloqueado": 0,
    }
    ventana = VentanaAcceso(datos_prueba)
    ventana.exec()
    sys.exit(0)