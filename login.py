import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, 
                            QGraphicsDropShadowEffect, QDialog, QFrame, QSpacerItem, QSizePolicy, QLineEdit)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap

from modales.ventana_error import VentanaError

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
        
        # Usamos un layout vertical maestro para el lado izquierdo sin márgenes
        self.left_master_layout = QVBoxLayout(self.left_container)
        self.left_master_layout.setContentsMargins(0, 0, 0, 0)
        self.left_master_layout.setSpacing(0)

        # Sub-contenedor para el Logo
        self.logo_container = QWidget()
        self.logo_layout = QVBoxLayout(self.logo_container)
        self.logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_layout.setContentsMargins(100, 50, 50, 0)

        # IMPORTACION DEL LOGO
        self.label_imagen = QLabel(self.logo_container)
        directorio = os.path.dirname(__file__)
        pixmap = QPixmap(os.path.join(directorio, 'imagenes', 'logo inces.png'))
        self.label_imagen.setPixmap(pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.label_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_layout.addWidget(self.label_imagen)

        self.left_master_layout.addWidget(self.logo_container, stretch=1)

        # ELEMENTOS GRAFICOS DE LA ESQUINA
        self.adorno_esquina = QSvgWidget(os.path.join(directorio, 'imagenes', 'adorno.svg'))
        self.adorno_esquina.setFixedSize(300, 215)
        self.left_master_layout.addWidget(self.adorno_esquina, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        # Añadimos el bloque izquierdo al diseño principal
        self.layout_principal.addWidget(self.left_container, stretch=1)

        # =================================================================
        # ZONA DERECHA: Zona de logueo
        # =================================================================
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.setContentsMargins(50, 50, 100, 50)

        # 1. Creamos el Frame que actuará como tarjeta blanca
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

        # 2. Sombra difuminada
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor(0, 0, 0, 70))
        self.shadow.setOffset(10, 10)
        self.login_panel.setGraphicsEffect(self.shadow)

        # 3. Layout interno del panel blanco 
        self.panel_layout = QVBoxLayout(self.login_panel)
        self.panel_layout.setContentsMargins(40, 50, 40, 50)
        self.panel_layout.addStretch()

        # 4. ENTRADA DE DATOS (estilos)
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
        
        # Etiqueta de texto (login)
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

        # Entrada de usuario
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_usuario.setStyleSheet(estilo_inputs)
        self.txt_usuario.setFixedHeight(40)
        self.panel_layout.addWidget(self.txt_usuario)

        self.panel_layout.addSpacing(25)

        # Entrada de contraseña
        self.txt_contraseña = QLineEdit()
        self.txt_contraseña.setPlaceholderText("Contraseña")
        self.txt_contraseña.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_contraseña.setStyleSheet(estilo_inputs)
        self.txt_contraseña.setFixedHeight(40)
        self.panel_layout.addWidget(self.txt_contraseña)

        self.panel_layout.addStretch(1)

        # Botón para ingresar
        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setFixedSize(200, 40)
        self.btn_ingresar.clicked.connect(self.validar_usuario)
        self.panel_layout.addWidget(self.btn_ingresar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(15)

        # Botón para registrar 
        self.btn_registrar = QPushButton("Registrar")
        self.btn_registrar.setFixedSize(200, 40)
        self.btn_registrar.clicked.connect(self.abrir_registro)
        self.panel_layout.addWidget(self.btn_registrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addStretch(1)

        # Bucle para estilos de botones
        for btn in [self.btn_ingresar, self.btn_registrar]:
            btn.setStyleSheet(estilo_botones)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Bucle para efectos de sombra
        for widget in [self.txt_usuario, self.txt_contraseña, self.btn_ingresar, self.btn_registrar]:
            efecto_sombra = QGraphicsDropShadowEffect()
            efecto_sombra.setBlurRadius(20)
            efecto_sombra.setXOffset(5)
            efecto_sombra.setYOffset(5)
            efecto_sombra.setColor(QColor(0, 0, 0, 70))
            widget.setGraphicsEffect(efecto_sombra)

        # Añadimos la tarjeta al layout derecho y el contenedor derecho al layout principal
        self.right_layout.addWidget(self.login_panel)
        self.layout_principal.addWidget(self.right_container, stretch=1)

    def validar_usuario(self):
        if self.txt_usuario.text() == "a" and self.txt_contraseña.text() == "a":
            from ventana_principal import VentanaPrincipal

            self.ventana_principal = VentanaPrincipal(ventana_login=self)
            self.ventana_principal.showMaximized() 
            self.hide() 
        else:
            ventana_error = VentanaError(self)
            ventana_error.exec()  # Actualizado a PyQt6 (.exec sin guion bajo)

    def abrir_registro(self):
        from modales.ventana_registro import VentanaRegistro
        
        self.ventana_registro = VentanaRegistro(ventana_login=self)
        self.ventana_registro.showMaximized()
        self.hide()  

    def centrar_ventana(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()  # Actualizado para PyQt6 (reemplaza a QDesktopWidget)
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def limpiar_formulario(self):
        self.txt_usuario.clear()
        self.txt_contraseña.clear()
        self.txt_usuario.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VentanaLogin()
    window.showMaximized()
    sys.exit(app.exec())  # Actualizado a PyQt6 (.exec sin guion bajo)