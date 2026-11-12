import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget,
                            QPushButton, QGraphicsDropShadowEffect, QFrame, QLineEdit, QComboBox, QMessageBox, QListView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from modales.ventana_error import VentanaError

# Importación del gestor de base de datos global desde la raíz
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


class VentanaRegistro(QMainWindow):
    def __init__(self, ventana_login=None):
        super().__init__()
        self.ventana_login = ventana_login  # Guardamos la referencia del login para volver a él
        self.cerrando_sesion = False

        self.setWindowTitle("Sistema INCES - Registro")
        self.resize(900, 600)

        # --- Contenedor Principal ---
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.widget_central.setStyleSheet("background-color: #bfbdbe;")

        self.layout_principal = QVBoxLayout(self.widget_central)
        self.layout_principal.setContentsMargins(40, 40, 40, 40)
        self.layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Tarjeta blanca grande central
        self.registro_panel = QFrame()
        self.registro_panel.setObjectName("registroPanel")
        self.registro_panel.setStyleSheet("""
            QFrame#registroPanel {
                background-color: #ffffff;
                border-radius: 40px;
            }
        """)

        # 2. Sombra difuminada suave
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor(0, 0, 0, 70))
        self.shadow.setOffset(10, 10)
        self.registro_panel.setGraphicsEffect(self.shadow)

        # 3. Layout interno del panel blanco
        self.panel_layout = QVBoxLayout(self.registro_panel)
        self.panel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_layout.setContentsMargins(50, 30, 50, 30)

        estilo_inputs = """
            QLineEdit {
                background-color: #e0dede;
                border: none;
                border-radius: 20px;
                padding-left: 25px;
                padding-right: 25px;
                color: black;
                font-size: 15px;
                font-weight: bold;
            }
        """

        estilo_botones = """
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
        """

        # Título de la ventana
        self.label_titulo = QLabel("Registro de Usuario")
        self.label_titulo.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #000000;
                font-family: 'Arial', sans-serif;
                background: transparent;
                margin-bottom: 10px;
            }
        """)
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_layout.addWidget(self.label_titulo)

        self.panel_layout.addSpacing(10)

        # Campo Cédula del Trabajador
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Cédula")
        self.txt_cedula.setStyleSheet(estilo_inputs)
        self.txt_cedula.setFixedSize(350, 40)
        self.panel_layout.addWidget(self.txt_cedula, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(15)

        # Campo Nuevo Usuario
        self.txt_nuevo_usuario = QLineEdit()
        self.txt_nuevo_usuario.setPlaceholderText("Nombre de Usuario")
        self.txt_nuevo_usuario.setStyleSheet(estilo_inputs)
        self.txt_nuevo_usuario.setFixedSize(350, 40)
        self.panel_layout.addWidget(self.txt_nuevo_usuario, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(15)

        # Campo Contraseña
        self.txt_nueva_contrasena = QLineEdit()
        self.txt_nueva_contrasena.setPlaceholderText("Contraseña")
        self.txt_nueva_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_nueva_contrasena.setStyleSheet(estilo_inputs)
        self.txt_nueva_contrasena.setFixedSize(350, 40)
        self.panel_layout.addWidget(self.txt_nueva_contrasena, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(15)

        # Selector de Rol (ComboBox) seguro (sin rol Administrador)
        self.combo_rol = QComboBox()
        self.combo_rol.setView(QListView())
        self.combo_rol.setFixedSize(350, 40)
        self.cargar_roles()
        self.actualizar_estilo_combo()
        self.combo_rol.currentIndexChanged.connect(self.actualizar_estilo_combo)
        self.panel_layout.addWidget(self.combo_rol, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(25)

        # Botón Registrar
        self.btn_guardar = QPushButton("Registrarse")
        self.btn_guardar.setFixedSize(200, 40)
        self.btn_guardar.setStyleSheet(estilo_botones)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.clicked.connect(self.procesar_registro)
        self.panel_layout.addWidget(self.btn_guardar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(12)

        # Botón Volver
        self.btn_volver = QPushButton("Volver")
        self.btn_volver.setFixedSize(200, 40)
        self.btn_volver.setStyleSheet(estilo_botones)
        self.btn_volver.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_volver.clicked.connect(self.regresar_login)
        self.panel_layout.addWidget(self.btn_volver, alignment=Qt.AlignmentFlag.AlignCenter)

        # Efectos de sombra para los componentes internos
        for widget in [self.txt_cedula, self.txt_nuevo_usuario, self.txt_nueva_contrasena, self.combo_rol, self.btn_guardar, self.btn_volver]:
            efecto_sombra = QGraphicsDropShadowEffect()
            efecto_sombra.setBlurRadius(20)
            efecto_sombra.setXOffset(5)
            efecto_sombra.setYOffset(5)
            efecto_sombra.setColor(QColor(0, 0, 0, 50))
            widget.setGraphicsEffect(efecto_sombra)

        self.layout_principal.addWidget(self.registro_panel)

    def cargar_roles(self):
        """Carga los roles permitidos desde la BD, excluyendo por seguridad cualquier rol de Administrador"""
        self.combo_rol.clear()
        self.combo_rol.addItem("Seleccione su rol", None)
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                # Filtro de seguridad: Excluimos cualquier rol que contenga la palabra 'admin'
                cursor.execute("SELECT id_rol, nombre_rol FROM roles WHERE LOWER(nombre_rol) NOT LIKE '%admin%'")
                roles = cursor.fetchall()
                
                for r in roles:
                    self.combo_rol.addItem(r["nombre_rol"], r["id_rol"])
                cursor.close()
        except Exception as e:
            print(f"Error al cargar roles seguros desde la BD: {e}")
            # Respaldo estático seguro por si ocurre algún fallo
            self.combo_rol.addItem("Recursos humanos", 1)
            self.combo_rol.addItem("Secretario/a", 2)

    def actualizar_estilo_combo(self):
        """Método dinámico para estilizar el texto del ComboBox"""
        if self.combo_rol.currentIndex() == 0:
            self.combo_rol.setStyleSheet("""
                QComboBox {
                    background-color: #e0dede;
                    border: none;
                    border-radius: 20px;
                    padding-left: 25px;
                    padding-right: 25px;
                    color: #777777;
                    font-size: 15px;
                    font-weight: bold;
                }
                QComboBox::drop-down { border: 0px; }
            """)
        else:
            self.combo_rol.setStyleSheet("""
                QComboBox {
                    background-color: #e0dede;
                    border: none;
                    border-radius: 20px;
                    padding-left: 25px;
                    padding-right: 25px;
                    color: black;
                    font-size: 15px;
                    font-weight: bold;
                }
                QComboBox::drop-down { border: 0px; }
            """)

    def procesar_registro(self):
        cedula = self.txt_cedula.text().strip()
        usuario = self.txt_nuevo_usuario.text().strip()
        contrasena = self.txt_nueva_contrasena.text().strip()
        id_rol = self.combo_rol.currentData()

        if not cedula or not usuario or not contrasena or self.combo_rol.currentIndex() == 0:
            ventana_error = VentanaError(self)
            ventana_error.exec()
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)

                # 1. Verificar si la cédula existe en la tabla trabajadores[cite: 6]
                cursor.execute("SELECT * FROM trabajadores WHERE cedula_trabajador = %s", (cedula,))
                trabajador = cursor.fetchone()

                if not trabajador:
                    QMessageBox.warning(self, "Acceso Denegado", "La cédula ingresada no pertenece a ningún trabajador registrado en el sistema.")
                    cursor.close()
                    return

                # 2. Verificar duplicados de usuario o cédula
                cursor.execute("SELECT * FROM usuarios WHERE cedula_trabajador_fk = %s OR nombre_usuario = %s", (cedula, usuario))
                existente = cursor.fetchone()

                if existente:
                    QMessageBox.warning(self, "Registro Existente", "Ya existe una cuenta de usuario asociada a esta cédula o este nombre de usuario.")
                    cursor.close()
                    return

                # 3. Registrar el nuevo usuario en la base de datos
                sql = """
                    INSERT INTO usuarios (nombre_usuario, contraseña, cedula_trabajador_fk, id_rol_fk)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (usuario, contrasena, cedula, id_rol))
                conexion.commit()
                cursor.close()

                QMessageBox.information(self, "Éxito", "¡Usuario registrado correctamente!")
                if self.ventana_login:
                    self.ventana_login.show()
                self.close()
            else:
                ventana_error = VentanaError(self)
                ventana_error.exec()
        except Exception as e:
            print(f"Error al procesar el registro en la BD: {e}")
            ventana_error = VentanaError(self)
            ventana_error.exec()

    def regresar_login(self):
        if self.ventana_login:
            self.ventana_login.show()
        self.close()

    def limpiar_formulario(self):
        self.txt_cedula.clear()
        self.txt_nuevo_usuario.clear()
        self.txt_nueva_contrasena.clear()
        self.combo_rol.setCurrentIndex(0)
        self.actualizar_estilo_combo()
        self.txt_cedula.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaRegistro()
    ventana.showMaximized()
    sys.exit(app.exec())