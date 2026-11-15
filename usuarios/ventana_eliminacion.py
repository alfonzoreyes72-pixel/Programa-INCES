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


ESTILO_ELIMINAR_ETAPA_1 = """
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
        color: #ffffff;
    }
"""

ESTILO_ELIMINAR_ETAPA_2 = """
    QPushButton {
        background-color: #8b0000;
        color: white;
        border-radius: 20px;
        border: 2px solid #8b0000;
        padding: 5px;
        font-size: 15px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #a30000;
        border: 2px solid #a30000;
    }
"""


class VentanaEliminacion(QDialog):
    """Ventana modal para eliminar un usuario con doble verificación"""

    def __init__(self, datos_usuario, parent=None, id_usuario_actual=None):
        super().__init__(parent)

        self.id_usuario = datos_usuario.get("id_usuario")
        self.nombre_usuario = datos_usuario.get("usuario", "N/D")
        self.trabajador = datos_usuario.get("trabajador_vinculado", "N/D")
        self.cedula = datos_usuario.get("cedula", "N/D")
        self.rol = datos_usuario.get("rol", "N/D")
        self.id_usuario_actual = id_usuario_actual
        self.etapa = 1  # 1 = primer clic pendiente, 2 = esperando la confirmación final

        self.setWindowTitle("Eliminar usuario")
        self.setModal(True)
        self.setMinimumSize(540, 560)
        self.resize(580, 600)
        self.setStyleSheet("QDialog { background-color: #bfbdbe; }")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Panel principal blanco, igual al de la ventana de usuarios
        self.panel = QFrame()
        self.panel.setObjectName("panelEliminacion")
        self.panel.setStyleSheet("""
            QFrame#panelEliminacion {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        layout_principal.addWidget(self.panel)

        layout_panel = QVBoxLayout(self.panel)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(15)

        lbl_titulo = QLabel("Eliminar usuario")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(lbl_titulo)

        # Pregunta principal con el nombre del usuario resaltado
        lbl_pregunta = QLabel(
            f"¿Estás seguro de querer eliminar a "
            f"<span style='color:#d32f2f;'>{escape(str(self.nombre_usuario))}</span>?"
        )
        lbl_pregunta.setTextFormat(Qt.TextFormat.RichText)
        lbl_pregunta.setWordWrap(True)
        lbl_pregunta.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(lbl_pregunta)

        # Tarjeta con los datos del usuario que se va a eliminar
        tarjeta_datos = QFrame()
        tarjeta_datos.setObjectName("tarjetaDatos")
        tarjeta_datos.setStyleSheet("""
            QFrame#tarjetaDatos {
                background-color: #f4f6f9;
                border-radius: 10px;
                border: 1px solid #e2e6eb;
                border-left: 5px solid #d32f2f;
            }
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

        # Advertencias
        caja_advertencias = QFrame()
        caja_advertencias.setObjectName("cajaAdvertencias")
        caja_advertencias.setStyleSheet("""
            QFrame#cajaAdvertencias {
                background-color: #fdecec;
                border-radius: 10px;
                border: 1px solid #f5c6c6;
            }
        """)
        layout_adv = QVBoxLayout(caja_advertencias)
        layout_adv.setContentsMargins(15, 12, 15, 12)
        layout_adv.setSpacing(6)

        lbl_adv_titulo = QLabel("⚠ Antes de continuar, ten en cuenta:")
        lbl_adv_titulo.setStyleSheet("font-size: 13px; font-weight: bold; color: #b71c1c; border: none; background: transparent;")
        layout_adv.addWidget(lbl_adv_titulo)

        advertencias = [
            "Esta acción es permanente y no se puede deshacer.",
            "El usuario perderá el acceso al sistema y no podrá volver a iniciar sesión.",
            "Se eliminarán también los privilegios asignados a este usuario.",
            "El trabajador vinculado no se elimina: su registro y sus asistencias se conservan.",
        ]
        for texto in advertencias:
            lbl = QLabel(f"•  {texto}")
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 12px; color: #7a1c1c; border: none; background: transparent;")
            layout_adv.addWidget(lbl)
        layout_panel.addWidget(caja_advertencias)

        # Primera verificación: paloma de confirmación
        fila_confirmacion = QFrame()
        fila_confirmacion.setObjectName("filaConfirmacion")
        fila_confirmacion.setFixedHeight(52)
        fila_confirmacion.setStyleSheet("""
            QFrame#filaConfirmacion {
                background-color: #f4f6f9;
                border-radius: 10px;
                border: 1px solid #e2e6eb;
            }
        """)
        layout_conf = QHBoxLayout(fila_confirmacion)
        layout_conf.setContentsMargins(15, 0, 15, 0)
        layout_conf.setSpacing(15)

        self.paloma = QPushButton("✓")
        self.paloma.setCheckable(True)
        self.paloma.setFixedSize(28, 28)
        self.paloma.setCursor(Qt.CursorShape.PointingHandCursor)
        self.paloma.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #ffffff;
                border: 2px solid #b8c2d1;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #d32f2f;
            }
            QPushButton:checked {
                background-color: #d32f2f;
                border: 2px solid #d32f2f;
                color: #ffffff;
            }
            QPushButton:disabled {
                border: 2px solid #d0d7de;
            }
        """)
        self.paloma.toggled.connect(self.al_cambiar_confirmacion)

        self.lbl_confirmacion = QLabel("Entiendo que esta acción no se puede deshacer")
        self.lbl_confirmacion.setStyleSheet("font-size: 13px; font-weight: bold; color: #333333; border: none; background: transparent;")

        layout_conf.addWidget(self.paloma)
        layout_conf.addWidget(self.lbl_confirmacion, stretch=1)
        layout_panel.addWidget(fila_confirmacion)

        layout_panel.addStretch()

        # Mensaje de estado (bloqueos, segunda verificación o errores)
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
        self.btn_cancelar.setStyleSheet("""
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
        """)
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_eliminar = QPushButton("Eliminar usuario")
        self.btn_eliminar.setFixedSize(260, 40)
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.setStyleSheet(ESTILO_ELIMINAR_ETAPA_1)
        self.btn_eliminar.setEnabled(False)
        self.btn_eliminar.clicked.connect(self.al_presionar_eliminar)

        layout_botones.addWidget(self.btn_cancelar)
        layout_botones.addWidget(self.btn_eliminar)
        layout_panel.addLayout(layout_botones)

        # Bloqueos de seguridad: si aplica alguno, no se permite continuar
        self.motivo_bloqueo = self.obtener_motivo_bloqueo()
        if self.motivo_bloqueo:
            self.paloma.setEnabled(False)
            self.lbl_confirmacion.setStyleSheet("font-size: 13px; font-weight: bold; color: #aaaaaa; border: none; background: transparent;")
            self.mostrar_mensaje(self.motivo_bloqueo)

    def obtener_motivo_bloqueo(self):
        """Devuelve un texto si el usuario NO se puede eliminar, o None si es seguro continuar"""
        if self.id_usuario_actual is not None and self.id_usuario == self.id_usuario_actual:
            return "No puedes eliminar tu propia cuenta mientras tienes la sesión iniciada."

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                return "No se pudo verificar el usuario en la base de datos."

            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.nombre_rol,
                       (SELECT COUNT(*) FROM usuarios u2 WHERE u2.id_rol_fk = u.id_rol_fk) AS total_rol
                FROM usuarios u
                LEFT JOIN roles r ON u.id_rol_fk = r.id_rol
                WHERE u.id_usuario = %s
            """, (self.id_usuario,))
            resultado = cursor.fetchone()
            cursor.close()

            if not resultado:
                return "Este usuario ya no existe en la base de datos."

            nombre_rol = str(resultado.get("nombre_rol") or "").lower()
            if "administrador" in nombre_rol and resultado["total_rol"] <= 1:
                return "No se puede eliminar: es el único administrador del sistema."
        except Exception as e:
            print(f"Error al verificar el usuario antes de eliminarlo: {e}")
            return "No se pudo verificar el usuario en la base de datos."

        return None

    def mostrar_mensaje(self, texto, color="#d32f2f"):
        self.lbl_estado.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {color}; border: none; background: transparent;")
        self.lbl_estado.setText(texto)
        self.lbl_estado.show()

    def al_cambiar_confirmacion(self, marcado):
        """Primera verificación: la paloma habilita el botón. Si se desmarca, se reinicia el proceso."""
        self.etapa = 1
        self.lbl_estado.hide()
        self.btn_eliminar.setText("Eliminar usuario")
        self.btn_eliminar.setStyleSheet(ESTILO_ELIMINAR_ETAPA_1)
        self.btn_eliminar.setEnabled(marcado and not self.motivo_bloqueo)

    def al_presionar_eliminar(self):
        """Segunda verificación: el primer clic pide confirmar, el segundo elimina."""
        if self.etapa == 1:
            self.etapa = 2
            self.btn_eliminar.setText("Sí, eliminar definitivamente")
            self.btn_eliminar.setStyleSheet(ESTILO_ELIMINAR_ETAPA_2)
            self.mostrar_mensaje(
                f"Última verificación: presiona de nuevo para eliminar definitivamente a {self.nombre_usuario}."
            )
        else:
            self.eliminar_usuario()

    def eliminar_usuario(self):
        # Se vuelve a verificar justo antes de borrar, por si algo cambió mientras la ventana estaba abierta
        motivo = self.obtener_motivo_bloqueo()
        if motivo:
            self.motivo_bloqueo = motivo
            self.btn_eliminar.setEnabled(False)
            self.mostrar_mensaje(motivo)
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (self.id_usuario,))
                conexion.commit()
                cursor.close()
                self.accept()
                return
        except Exception as e:
            print(f"Error al eliminar el usuario: {e}")

        self.mostrar_mensaje("No se pudo eliminar el usuario. Intenta de nuevo.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaEliminacion({
        "id_usuario": 2,
        "usuario": "Jesus",
        "trabajador_vinculado": "Jesús López",
        "cedula": 32753323,
        "rol": "Recursos Humanos",
    })
    ventana.exec()
    sys.exit(0)