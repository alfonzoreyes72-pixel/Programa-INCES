import sys
import os

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QFrame, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


def paleta_clara():
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor("#bfbdbe"))
    p.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))
    p.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor("#f4f6f9"))
    p.setColor(QPalette.ColorRole.Text, QColor("#333333"))
    p.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.ButtonText, QColor("#333333"))
    p.setColor(QPalette.ColorRole.Highlight, QColor("#e6f0ff"))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#0833a2"))
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#999999"))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor("#333333"))
    return p


# Misma estética de inputs que la ventana de registro de trabajadores
ESTILO_VENTANA = """
    QDialog {
        background-color: #bfbdbe;
    }
    QLabel {
        font-size: 13px;
        font-weight: bold;
        color: #2c2c2c;
        background: transparent;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 13px;
        color: #333333;
    }
    QLineEdit:focus {
        border: 2px solid #0833a2;
    }
    QLineEdit:read-only {
        background-color: #f0f0f0;
        color: #666666;
    }
    QCheckBox {
        font-size: 12px;
        color: #555555;
        background: transparent;
    }
"""


class VentanaCredenciales(QDialog):
    """Ventana modal para actualizar el nombre de usuario y la contraseña de un usuario"""

    def __init__(self, datos_usuario, parent=None, modo_prueba=False):
        super().__init__(parent)

        self.id_usuario = datos_usuario.get("id_usuario")
        self.usuario_original = str(datos_usuario.get("usuario", ""))
        self.trabajador = str(datos_usuario.get("trabajador_vinculado", "N/D"))
        # En modo prueba la ventana funciona completa pero NO escribe en la base de datos
        self.modo_prueba = modo_prueba

        titulo = "Actualizar credenciales"
        self.setWindowTitle(titulo + (" (modo prueba)" if modo_prueba else ""))
        self.setFixedSize(500, 520)
        self.setPalette(paleta_clara())
        self.setStyleSheet(ESTILO_VENTANA)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; background: transparent;")
        layout_principal.addWidget(lbl_titulo)

        card_contenedor = QFrame()
        card_contenedor.setObjectName("cardContenedor")
        card_contenedor.setStyleSheet("QFrame#cardContenedor { background-color: #ffffff; border-radius: 15px; }")
        layout_card = QVBoxLayout(card_contenedor)
        layout_card.setContentsMargins(20, 20, 20, 20)
        layout_card.setSpacing(15)

        lbl_ayuda = QLabel("Deja la contraseña en blanco si solo quieres cambiar el nombre de usuario.")
        lbl_ayuda.setWordWrap(True)
        lbl_ayuda.setStyleSheet("font-size: 12px; font-weight: normal; color: #777777; background: transparent;")
        layout_card.addWidget(lbl_ayuda)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.txt_trabajador = QLineEdit(self.trabajador)
        self.txt_trabajador.setReadOnly(True)
        self.txt_trabajador.setFixedHeight(36)

        self.txt_usuario = QLineEdit(self.usuario_original)
        self.txt_usuario.setPlaceholderText("Nombre de usuario")
        self.txt_usuario.setMaxLength(20)
        self.txt_usuario.setFixedHeight(36)

        self.txt_clave = QLineEdit()
        self.txt_clave.setPlaceholderText("Nueva contraseña")
        self.txt_clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_clave.setMaxLength(60)
        self.txt_clave.setFixedHeight(36)

        self.txt_confirmar = QLineEdit()
        self.txt_confirmar.setPlaceholderText("Repite la nueva contraseña")
        self.txt_confirmar.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_confirmar.setMaxLength(60)
        self.txt_confirmar.setFixedHeight(36)

        form_layout.addRow("Trabajador vinculado:", self.txt_trabajador)
        form_layout.addRow("Nombre de usuario:", self.txt_usuario)
        form_layout.addRow("Nueva contraseña:", self.txt_clave)
        form_layout.addRow("Confirmar contraseña:", self.txt_confirmar)
        layout_card.addLayout(form_layout)

        self.chk_mostrar = QCheckBox("Mostrar contraseñas")
        self.chk_mostrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_mostrar.toggled.connect(self.alternar_visibilidad)
        layout_card.addWidget(self.chk_mostrar)

        layout_card.addStretch()
        layout_principal.addWidget(card_contenedor)

        layout_botones = QHBoxLayout()
        layout_botones.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(100, 36)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton { background-color: #e0dede; color: #333333; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #d0d0d0; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(self.btn_cancelar)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFixedSize(100, 36)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton { background-color: #163e7a; color: white; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #235299; }
        """)
        self.btn_guardar.clicked.connect(self.guardar_credenciales)
        layout_botones.addWidget(self.btn_guardar)

        layout_principal.addLayout(layout_botones)

    def alternar_visibilidad(self, mostrar):
        modo = QLineEdit.EchoMode.Normal if mostrar else QLineEdit.EchoMode.Password
        self.txt_clave.setEchoMode(modo)
        self.txt_confirmar.setEchoMode(modo)

    def guardar_credenciales(self):
        usuario = self.txt_usuario.text().strip()
        # El login recorta los espacios de la contraseña, por eso aquí también
        clave = self.txt_clave.text().strip()
        confirmacion = self.txt_confirmar.text().strip()

        if not usuario:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingrese el nombre de usuario.")
            return
        if len(usuario) < 3:
            QMessageBox.warning(self, "Usuario inválido", "El nombre de usuario debe tener al menos 3 caracteres.")
            return
        if " " in usuario:
            QMessageBox.warning(self, "Usuario inválido", "El nombre de usuario no puede contener espacios.")
            return

        cambia_clave = bool(clave or confirmacion)
        if cambia_clave:
            if len(clave) < 4:
                QMessageBox.warning(self, "Contraseña inválida", "La contraseña debe tener al menos 4 caracteres.")
                return
            if clave != confirmacion:
                QMessageBox.warning(self, "Contraseñas distintas", "Las contraseñas no coinciden.")
                return

        # Si no cambió nada, simplemente se cierra
        if usuario == self.usuario_original and not cambia_clave:
            self.reject()
            return

        # Modo prueba: se valida todo pero no se escribe en la base de datos
        if self.modo_prueba:
            QMessageBox.information(
                self, "Modo de prueba",
                "Las validaciones son correctas.\n\nModo de prueba: los cambios NO se guardaron en la base de datos."
            )
            self.accept()
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                QMessageBox.critical(self, "Error de Conexión", "No se pudo conectar con la base de datos MySQL.")
                return

            cursor = conexion.cursor(dictionary=True)

            # El nombre de usuario no puede repetirse
            cursor.execute(
                "SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s AND id_usuario <> %s",
                (usuario, self.id_usuario)
            )
            if cursor.fetchone():
                cursor.close()
                QMessageBox.warning(self, "Usuario existente", "Ya existe otro usuario con ese nombre. Elige uno distinto.")
                return

            if cambia_clave:
                cursor.execute(
                    "UPDATE usuarios SET nombre_usuario = %s, `contraseña` = %s WHERE id_usuario = %s",
                    (usuario, clave, self.id_usuario)
                )
            else:
                cursor.execute(
                    "UPDATE usuarios SET nombre_usuario = %s WHERE id_usuario = %s",
                    (usuario, self.id_usuario)
                )

            if cursor.rowcount == 0:
                cursor.close()
                QMessageBox.warning(self, "Usuario no encontrado", "Este usuario ya no existe en la base de datos.")
                return

            conexion.commit()
            cursor.close()
            QMessageBox.information(self, "Éxito", "Credenciales actualizadas correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar:\n{e}")


if __name__ == "__main__":
    # Al ejecutar este archivo solo se abre con datos de prueba y en modo prueba:
    # se puede probar toda la ventana sin escribir nada en la base de datos real.
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(paleta_clara())
    datos_prueba = {
        "id_usuario": 0,
        "usuario": "usuario_prueba",
        "trabajador_vinculado": "María Pérez (datos de prueba)",
    }
    ventana = VentanaCredenciales(datos_prueba, modo_prueba=True)
    ventana.exec()
    sys.exit(0)