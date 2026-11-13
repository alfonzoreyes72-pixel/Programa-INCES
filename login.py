import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QGraphicsDropShadowEffect,
                            QDialog, QFrame, QLineEdit)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap

from modales.ventana_error import VentanaError

# Importación del gestor de base de datos global desde la raíz
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


class VentanaLogin(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema INCES")
        self.resize(900, 600)

        # --- Contenedor Principal ---
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.widget_central.setStyleSheet("background-color: #bfbdbe;")

        # Layout Horizontal Principal: Dividirá la pantalla en Izquierda y Derecha
        self.layout_principal = QHBoxLayout(self.widget_central)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        # =================================================================
        # ZONA IZQUIERDA: Logo y adorno institucional
        # =================================================================
        self.left_container = QWidget()
        
        self.left_master_layout = QVBoxLayout(self.left_container)
        self.left_master_layout.setContentsMargins(0, 0, 0, 0)
        self.left_master_layout.setSpacing(0)

        self.logo_container = QWidget()
        self.logo_layout = QVBoxLayout(self.logo_container)
        self.logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_layout.setContentsMargins(100, 50, 50, 0)

        self.label_imagen = QLabel(self.logo_container)
        directorio = os.path.dirname(__file__)
        pixmap = QPixmap(os.path.join(directorio, 'imagenes', 'logo inces.png'))
        self.label_imagen.setPixmap(pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.label_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_layout.addWidget(self.label_imagen)

        self.left_master_layout.addWidget(self.logo_container, stretch=1)

        self.adorno_esquina = QSvgWidget(os.path.join(directorio, 'imagenes', 'adorno.svg'))
        self.adorno_esquina.setFixedSize(300, 215)
        self.left_master_layout.addWidget(self.adorno_esquina, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        self.layout_principal.addWidget(self.left_container, stretch=1)

        # =================================================================
        # ZONA DERECHA: Zona de logueo
        # =================================================================
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.setContentsMargins(50, 50, 100, 50)

        self.login_panel = QFrame()
        self.login_panel.setObjectName("loginPanel")
        self.login_panel.setFixedWidth(380)
        self.login_panel.setFixedHeight(460)

        self.login_panel.setStyleSheet("""
            QFrame#loginPanel {
                background-color: #ffffff;
                border-radius: 40px;
            }
        """)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor(0, 0, 0, 70))
        self.shadow.setOffset(10, 10)
        self.login_panel.setGraphicsEffect(self.shadow)

        self.panel_layout = QVBoxLayout(self.login_panel)
        self.panel_layout.setContentsMargins(40, 50, 40, 50)
        self.panel_layout.addStretch()

        estilo_inputs = """
            QLineEdit {
                background-color: #e0dede;
                border: none;
                border-radius: 20px;
                padding-left: 25px;
                padding-right: 25px;
                color: black;
                font-size: 16px;
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
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3150ff;
                border: 2px solid #3150ff;
            }
        """
        
        self.label_login = QLabel("Login")
        self.label_login.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #000000;
                font-family: 'Arial', sans-serif;
                background: transparent;
                margin-bottom: 10px;
            }
        """)
        self.label_login.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_layout.addWidget(self.label_login)

        self.panel_layout.addSpacing(15)

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_usuario.setStyleSheet(estilo_inputs)
        self.txt_usuario.setFixedHeight(40)
        self.panel_layout.addWidget(self.txt_usuario)

        self.panel_layout.addSpacing(25)

        self.txt_contraseña = QLineEdit()
        self.txt_contraseña.setPlaceholderText("Contraseña")
        self.txt_contraseña.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_contraseña.setStyleSheet(estilo_inputs)
        self.txt_contraseña.setFixedHeight(40)
        self.panel_layout.addWidget(self.txt_contraseña)

        self.panel_layout.addStretch(1)

        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setFixedSize(200, 40)
        self.btn_ingresar.clicked.connect(self.validar_usuario)
        self.panel_layout.addWidget(self.btn_ingresar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(15)

        self.btn_registrar = QPushButton("Registrar")
        self.btn_registrar.setFixedSize(200, 40)
        self.btn_registrar.clicked.connect(self.abrir_registro)
        self.panel_layout.addWidget(self.btn_registrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addStretch(1)

        for btn in [self.btn_ingresar, self.btn_registrar]:
            btn.setStyleSheet(estilo_botones)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        for widget in [self.txt_usuario, self.txt_contraseña, self.btn_ingresar, self.btn_registrar]:
            efecto_sombra = QGraphicsDropShadowEffect()
            efecto_sombra.setBlurRadius(20)
            efecto_sombra.setXOffset(5)
            efecto_sombra.setYOffset(5)
            efecto_sombra.setColor(QColor(0, 0, 0, 70))
            widget.setGraphicsEffect(efecto_sombra)

        self.right_layout.addWidget(self.login_panel)
        self.layout_principal.addWidget(self.right_container, stretch=1)

    def validar_usuario(self):
        usuario = self.txt_usuario.text().strip()
        contrasena = self.txt_contraseña.text().strip()

        if not usuario or not contrasena:
            ventana_error = VentanaError(self)
            ventana_error.exec()
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                # Consulta uniendo con roles para obtener el nombre del rol
                sql = """
                    SELECT u.*, r.nombre_rol 
                    FROM usuarios u 
                    JOIN roles r ON u.id_rol_fk = r.id_rol 
                    WHERE u.nombre_usuario = %s AND u.contraseña = %s
                """
                cursor.execute(sql, (usuario, contrasena))
                resultado = cursor.fetchone()
                cursor.close()

                if resultado:
                    from ventana_principal import VentanaPrincipal
                    rol_usuario = resultado.get('nombre_rol', 'Administrador')
                    self.ventana_principal = VentanaPrincipal(rol=rol_usuario, ventana_login=self)
                    self.ventana_principal.showMaximized() 
                    self.hide() 
                else:
                    ventana_error = VentanaError(self)
                    ventana_error.exec()
            else:
                ventana_error = VentanaError(self)
                ventana_error.exec()
        except Exception as e:
            print(f"Error al validar usuario en la base de datos: {e}")
            ventana_error = VentanaError(self)
            ventana_error.exec()

    def abrir_registro(self):
        from modales.ventana_registro import VentanaRegistro
        self.ventana_registro = VentanaRegistro(ventana_login=self)
        self.ventana_registro.showMaximized()
        self.hide()

    def limpiar_formulario(self):
        self.txt_usuario.clear()
        self.txt_contraseña.clear()
        self.txt_usuario.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VentanaLogin()
    window.showMaximized()
    sys.exit(app.exec())