import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget,
                            QPushButton, QGraphicsDropShadowEffect, QFrame, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

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
        self.layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        self.panel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_layout.addWidget(self.label_titulo)

        self.panel_layout.addSpacing(15)

        # Campos de entrada de ejemplo para el registro
        self.txt_nuevo_usuario = QLineEdit()
        self.txt_nuevo_usuario.setPlaceholderText("Nuevo Usuario")
        self.txt_nuevo_usuario.setStyleSheet(estilo_inputs)
        self.txt_nuevo_usuario.setFixedSize(350, 40)
        self.panel_layout.addWidget(self.txt_nuevo_usuario, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(20)

        self.txt_nueva_contrasena = QLineEdit()
        self.txt_nueva_contrasena.setPlaceholderText("Contraseña")
        self.txt_nueva_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_nueva_contrasena.setStyleSheet(estilo_inputs)
        self.txt_nueva_contrasena.setFixedSize(350, 40)
        self.panel_layout.addWidget(self.txt_nueva_contrasena, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(20)

        # Selector desplegable (ComboBox) con efecto de marcador de posición dinámico
        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["Seleccione su rol", "Recursos humanos", "Secretario/a"])
        self.combo_rol.setFixedSize(350, 40)
        self.actualizar_estilo_combo()
        self.combo_rol.currentIndexChanged.connect(self.actualizar_estilo_combo)
        self.panel_layout.addWidget(self.combo_rol, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(30)

        # Botón para completar el registro
        self.btn_guardar = QPushButton("Registrar")
        self.btn_guardar.setFixedSize(200, 40)
        self.btn_guardar.setStyleSheet(estilo_botones)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.clicked.connect(self.procesar_registro)
        self.panel_layout.addWidget(self.btn_guardar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.panel_layout.addSpacing(15)

        # Botón para volver al login
        self.btn_volver = QPushButton("Volver")
        self.btn_volver.setFixedSize(200, 40)
        self.btn_volver.setStyleSheet(estilo_botones)
        self.btn_volver.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_volver.clicked.connect(self.regresar_login)
        self.panel_layout.addWidget(self.btn_volver, alignment=Qt.AlignmentFlag.AlignCenter)

        # Efectos de sombra para los elementos internos
        for widget in [self.txt_nuevo_usuario, self.txt_nueva_contrasena, self.combo_rol, self.btn_guardar, self.btn_volver]:
            efecto_sombra = QGraphicsDropShadowEffect()
            efecto_sombra.setBlurRadius(20)
            efecto_sombra.setXOffset(5)
            efecto_sombra.setYOffset(5)
            efecto_sombra.setColor(QColor(0, 0, 0, 50))
            widget.setGraphicsEffect(efecto_sombra)

        # Añadimos el panel grande al layout principal con márgenes
        self.layout_principal.addWidget(self.registro_panel)

    def actualizar_estilo_combo(self):
        """Método dinámico para mostrar el texto en gris claro con negritas o texto negro normal según la selección"""
        if self.combo_rol.currentIndex() == 0:
            self.combo_rol.setStyleSheet("""
                QComboBox {
                    background-color: #e0dede;
                    border: none;
                    border-radius: 20px;
                    padding-left: 25px;
                    padding-right: 25px;
                    color: #777777;       /* Color gris para que vaya a juego */
                    font-size: 16px;
                    font-weight: bold;    /* ¡Letras en negritas como pediste! */
                }
                QComboBox::drop-down {
                    border: 0px;
                }
            """)
        else:
            self.combo_rol.setStyleSheet("""
                QComboBox {
                    background-color: #e0dede;
                    border: none;
                    border-radius: 20px;
                    padding-left: 25px;
                    padding-right: 25px;
                    color: black;         /* Color negro al seleccionar un rol real */
                    font-size: 16px;
                    font-weight: bold;    /* Negrita */
                }
                QComboBox::drop-down {
                    border: 0px;
                }
            """)

    def procesar_registro(self):
        if self.txt_nuevo_usuario.text() != "" and self.txt_nueva_contrasena.text() != "":
            # Al completar el registro con éxito, volvemos al login
            if self.ventana_login:
                self.ventana_login.show()
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
        self.combo_rol.setCurrentIndex(0)
        self.actualizar_estilo_combo()
        self.txt_nuevo_usuario.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaRegistro()
    ventana.showMaximized()
    sys.exit(app.exec())  # Actualizado a PyQt6 (.exec sin guion bajo)