import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QGraphicsDropShadowEffect, QFrame, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class VentanaRegistro(QMainWindow):
    def __init__(self, ventana_login=None):
        super().__init__()
        self.ventana_login = ventana_login  # Guardamos la referencia del login para volver a él si es necesario
        self.cerrando_sesion = False

        self.setWindowTitle("Sistema INCES - Registro")
        self.resize(900, 600)

        # --- Contenedor Principal ---
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.widget_central.setStyleSheet("background-color: #bfbdbe;") # Mismo color de fondo del login

        # Layout principal que dejará un pequeño margen en las esquinas de toda la pantalla
        self.layout_principal = QVBoxLayout(self.widget_central)
        self.layout_principal.setContentsMargins(40, 40, 40, 40)  # Margen en las esquinas
        self.layout_principal.setAlignment(Qt.AlignCenter)

        # 1. Tarjeta blanca grande que cubre toda la pantalla dejando el margen
        self.registro_panel = QFrame()
        self.registro_panel.setObjectName("registroPanel")
        
        # QSS con bordes muy redondeados y fondo blanco puro idéntico al login
        self.registro_panel.setStyleSheet("""
            QFrame#registroPanel {
                background-color: #ffffff;
                border-radius: 40px;
            }
        """)

        # 2. Sombra difuminada suave alrededor de la tarjeta
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor(0, 0, 0, 70))
        self.shadow.setOffset(10, 10)
        self.registro_panel.setGraphicsEffect(self.shadow)

        # 3. Layout interno del panel blanco
        self.panel_layout = QVBoxLayout(self.registro_panel)
        self.panel_layout.setAlignment(Qt.AlignCenter)
        self.panel_layout.setContentsMargins(50, 50, 50, 50)

        # Estilos compartidos de inputs y botones
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

        # Título de la ventana
        self.label_titulo = QLabel("Registro de Usuario")
        self.label_titulo.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #000000;
                font-family: 'Arial', sans-serif;
                background: transparent;
                margin-bottom: 20px;
            }
        """)
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.panel_layout.addWidget(self.label_titulo)

        self.panel_layout.addSpacing(15)

        # Campos de entrada de ejemplo para el registro
        self.txt_nuevo_usuario = QLineEdit()
        self.txt_nuevo_usuario.setPlaceholderText("Nuevo Usuario")
        self.txt_nuevo_usuario.setStyleSheet(estilo_inputs)
        self.txt_nuevo_usuario.setFixedSize(350, 40)
        self.panel_layout.addWidget(self.txt_nuevo_usuario, alignment=Qt.AlignCenter)

        self.panel_layout.addSpacing(20)

        self.txt_nueva_contrasena = QLineEdit()
        self.txt_nueva_contrasena.setPlaceholderText("Contraseña")
        self.txt_nueva_contrasena.setEchoMode(QLineEdit.Password)
        self.txt_nueva_contrasena.setStyleSheet(estilo_inputs)
        self.txt_nueva_contrasena.setFixedSize(350, 40)
        self.panel_layout.addWidget(self.txt_nueva_contrasena, alignment=Qt.AlignCenter)

        self.panel_layout.addSpacing(30)

        # Botón para completar el registro
        self.btn_guardar = QPushButton("Registrar")
        self.btn_guardar.setFixedSize(200, 40)
        self.btn_guardar.setStyleSheet(estilo_botones)
        self.btn_guardar.setCursor(Qt.PointingHandCursor)
        self.btn_guardar.clicked.connect(self.procesar_registro)
        self.panel_layout.addWidget(self.btn_guardar, alignment=Qt.AlignCenter)

        self.panel_layout.addSpacing(15)

        # Botón para volver al login
        self.btn_volver = QPushButton("Volver")
        self.btn_volver.setFixedSize(200, 40)
        self.btn_volver.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 20px;
                border: 2px solid #6c757d;
                padding: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
                border: 2px solid #5a6268;
            }
        """)
        self.btn_volver.setCursor(Qt.PointingHandCursor)
        self.btn_volver.clicked.connect(self.regresar_login)
        self.panel_layout.addWidget(self.btn_volver, alignment=Qt.AlignCenter)

        # Efectos de sombra para los elementos internos
        for widget in [self.txt_nuevo_usuario, self.txt_nueva_contrasena, self.btn_guardar, self.btn_volver]:
            efecto_sombra = QGraphicsDropShadowEffect()
            efecto_sombra.setBlurRadius(20)
            efecto_sombra.setXOffset(5)
            efecto_sombra.setYOffset(5)
            efecto_sombra.setColor(QColor(0, 0, 0, 50))
            widget.setGraphicsEffect(efecto_sombra)

        # Añadimos el panel grande al layout principal con márgenes
        self.layout_principal.addWidget(self.registro_panel)

    def procesar_registro(self):
        # Lógica de registro temporal (puedes adaptarla después con tu base de datos o lógica)
        if self.txt_nuevo_usuario.text() != "" and self.txt_nueva_contrasena.text() != "":
            from ventana_principal import VentanaPrincipal
            # Abre la ventana principal y oculta el login original vinculado
            self.ventana_principal = VentanaPrincipal(ventana_login=self.ventana_login)
            self.ventana_principal.showMaximized()
            if self.ventana_login:
                self.ventana_login.hide()
            self.close()
        else:
            print("Complete los campos para registrar")

    def regresar_login(self):
        if self.ventana_login:
            self.ventana_login.show()
        self.close()

    def limpiar_formulario(self):
        self.txt_nuevo_usuario.clear()
        self.txt_nueva_contrasena.clear()
        self.txt_nuevo_usuario.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaRegistro()
    ventana.show()
    sys.exit(app.exec_())