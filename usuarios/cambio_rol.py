import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLabel, QWidget, QButtonGroup
)
from PyQt6.QtCore import Qt

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


class FilaRol(QFrame):
    """Fila con opción de selección única y nombre del rol, con el mismo diseño de las filas de usuarios"""

    def __init__(self, nombre, marcado=False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            FilaRol {
                background-color: #f4f6f9;
                border-radius: 10px;
                border: 1px solid #e2e6eb;
                border-left: 5px solid #163e7a;
            }
            FilaRol:hover {
                background-color: #eef2f7;
                border: 1px solid #d0d7de;
                border-left: 5px solid #163e7a;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(20)

        # 1. Opción circular (solo una puede estar marcada a la vez)
        self.opcion = QPushButton("")
        self.opcion.setCheckable(True)
        self.opcion.setChecked(marcado)
        self.opcion.setFixedSize(28, 28)
        self.opcion.setCursor(Qt.CursorShape.PointingHandCursor)
        self.opcion.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #b8c2d1;
                border-radius: 14px;
            }
            QPushButton:hover {
                border: 2px solid #163e7a;
            }
            QPushButton:checked {
                background-color: #163e7a;
                border: 2px solid #163e7a;
            }
        """)

        contenedor_opcion = QWidget()
        contenedor_opcion.setFixedWidth(80)
        layout_opcion = QHBoxLayout(contenedor_opcion)
        layout_opcion.setContentsMargins(0, 0, 0, 0)
        layout_opcion.addWidget(self.opcion)
        layout_opcion.addStretch()

        # 2. Nombre del rol
        self.lbl_nombre = QLabel(nombre)
        self.lbl_nombre.setStyleSheet("font-size: 13px; font-weight: bold; color: #163e7a; border: none; background: transparent;")

        layout.addWidget(contenedor_opcion)
        layout.addWidget(self.lbl_nombre, stretch=1)

    def mousePressEvent(self, event):
        # Al presionar en cualquier parte de la fila se selecciona ese rol
        self.opcion.setChecked(True)
        super().mousePressEvent(event)


class VentanaCambioRol(QDialog):
    """Ventana modal para cambiar el rol asignado a un usuario"""

    def __init__(self, datos_usuario, parent=None):
        super().__init__(parent)

        self.id_usuario = datos_usuario.get("id_usuario")
        self.nombre_usuario = datos_usuario.get("usuario", "N/D")
        self.rol_actual_nombre = datos_usuario.get("rol", "")
        self.id_rol_actual = None
        self.roles = {}  # {id_rol: nombre_rol}

        self.setWindowTitle("Cambiar rol")
        self.setModal(True)
        self.setMinimumSize(520, 460)
        self.resize(560, 500)
        self.setStyleSheet("QDialog { background-color: #bfbdbe; }")

        self.cargar_roles()

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Panel principal blanco, igual al de la ventana de usuarios
        self.panel = QFrame()
        self.panel.setObjectName("panelCambioRol")
        self.panel.setStyleSheet("""
            QFrame#panelCambioRol {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        layout_principal.addWidget(self.panel)

        layout_panel = QVBoxLayout(self.panel)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(15)

        lbl_titulo = QLabel("Cambiar rol")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(lbl_titulo)

        lbl_subtitulo = QLabel(f"Usuario: {self.nombre_usuario}   |   Rol actual: {self.rol_actual_nombre}")
        lbl_subtitulo.setStyleSheet("font-size: 13px; color: #777777; border: none; background: transparent;")
        layout_panel.addWidget(lbl_subtitulo)

        # Encabezados de la tabla (con fondo gris claro)
        barra_encabezados = QFrame()
        barra_encabezados.setObjectName("barraEncabezados")
        barra_encabezados.setFixedHeight(38)
        barra_encabezados.setStyleSheet("""
            QFrame#barraEncabezados {
                background-color: #e9edf2;
                border-radius: 10px;
                border: none;
            }
        """)

        headers_layout = QHBoxLayout(barra_encabezados)
        headers_layout.setContentsMargins(15, 0, 15, 0)
        headers_layout.setSpacing(20)

        lbl_h1 = QLabel("Selección")
        lbl_h1.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
        lbl_h1.setFixedWidth(80)

        lbl_h2 = QLabel("Rol Disponible")
        lbl_h2.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")

        headers_layout.addWidget(lbl_h1)
        headers_layout.addWidget(lbl_h2, stretch=1)
        layout_panel.addWidget(barra_encabezados)

        # Filas de roles: solo una opción puede estar marcada a la vez
        self.grupo_roles = QButtonGroup(self)
        self.grupo_roles.setExclusive(True)

        layout_filas = QVBoxLayout()
        layout_filas.setSpacing(8)
        for id_rol, nombre in self.roles.items():
            fila = FilaRol(nombre, marcado=(id_rol == self.id_rol_actual))
            self.grupo_roles.addButton(fila.opcion, id_rol)
            layout_filas.addWidget(fila)
        layout_panel.addLayout(layout_filas)

        layout_panel.addStretch()

        # Mensaje de error (solo se muestra si algo falla)
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

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFixedSize(140, 40)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
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
        """)
        self.btn_guardar.clicked.connect(self.guardar_rol)

        layout_botones.addWidget(self.btn_cancelar)
        layout_botones.addWidget(self.btn_guardar)
        layout_panel.addLayout(layout_botones)

    def cargar_roles(self):
        """Lee los roles disponibles y el rol que tiene el usuario en este momento"""
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)

                cursor.execute("SELECT id_rol, nombre_rol FROM roles ORDER BY id_rol")
                for fila in cursor.fetchall():
                    self.roles[fila["id_rol"]] = fila["nombre_rol"]

                cursor.execute("SELECT id_rol_fk FROM usuarios WHERE id_usuario = %s", (self.id_usuario,))
                resultado = cursor.fetchone()
                if resultado:
                    self.id_rol_actual = resultado["id_rol_fk"]

                cursor.close()
        except Exception as e:
            print(f"Error al cargar los roles: {e}")

    def mostrar_error(self, mensaje):
        self.lbl_estado.setText(mensaje)
        self.lbl_estado.show()

    def guardar_rol(self):
        nuevo_id = self.grupo_roles.checkedId()

        if nuevo_id == -1:
            self.mostrar_error("Selecciona un rol.")
            return

        # Si no cambió nada, simplemente se cierra
        if nuevo_id == self.id_rol_actual:
            self.reject()
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)

                # Debe quedar siempre al menos un administrador
                nombre_actual = str(self.roles.get(self.id_rol_actual, "")).lower()
                if "administrador" in nombre_actual:
                    cursor.execute(
                        "SELECT COUNT(*) AS total FROM usuarios WHERE id_rol_fk = %s",
                        (self.id_rol_actual,)
                    )
                    resultado = cursor.fetchone()
                    if resultado and resultado["total"] <= 1:
                        cursor.close()
                        self.mostrar_error("No se puede cambiar el rol: debe existir al menos un administrador.")
                        return

                cursor.execute(
                    "UPDATE usuarios SET id_rol_fk = %s WHERE id_usuario = %s",
                    (nuevo_id, self.id_usuario)
                )

                # Los privilegios personalizados se reinician para que apliquen los del nuevo rol
                try:
                    cursor.execute(
                        "DELETE FROM privilegios_ventanas WHERE id_usuario_fk = %s",
                        (self.id_usuario,)
                    )
                except Exception:
                    pass  # La tabla aún no existe: no hay nada que reiniciar

                conexion.commit()
                cursor.close()
                self.accept()
                return
        except Exception as e:
            print(f"Error al cambiar el rol: {e}")

        self.mostrar_error("No se pudo cambiar el rol. Intenta de nuevo.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaCambioRol({"id_usuario": 2, "usuario": "Jesus", "rol": "Recursos Humanos"})
    ventana.exec()
    sys.exit(0)