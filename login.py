import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QGraphicsDropShadowEffect,
                            QDialog, QGraphicsDropShadowEffect, QFrame, QSpacerItem, QSizePolicy, QLineEdit)
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap

class VentanaLogin(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema INCES")
        self.resize(900,600)

        # --- Contenedor Principal ---
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.widget_central.setStyleSheet("background-color: #bfbdbe;")

        # Layout Horizontal Principal: Dividirá la pantalla en Izquierda y Derecha
        self.layout_principal = QHBoxLayout(self.widget_central)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        # =================================================================
        # ZONA IZQUIERDA: Aquí irá el Logo y Texto Institucional más adelante
        # =================================================================
        self.left_container = QWidget()
        
        # Usamos un layout vertical maestro para el lado izquierdo sin márgenes
        self.left_master_layout = QVBoxLayout(self.left_container)
        self.left_master_layout.setContentsMargins(0, 0, 0, 0)
        self.left_master_layout.setSpacing(0)

        # Sub-contenedor para el Logo (este sí tendrá márgenes para centrarlo e independizarlo)
        self.logo_container = QWidget()
        self.logo_layout = QVBoxLayout(self.logo_container)
        self.logo_layout.setAlignment(Qt.AlignCenter)
        # Le damos un margen superior y derecho para empujar y equilibrar el logo visualmente
        self.logo_layout.setContentsMargins(100, 50, 50, 0)

        # IMPORTACION DEL LOGO
        self.label_imagen = QLabel(self.logo_container)
        directorio = os.path.dirname(__file__)
        pixmap = QPixmap(os.path.join(directorio, 'imagenes', 'logo inces.png'))
        self.label_imagen.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label_imagen.setAlignment(Qt.AlignCenter)
        self.logo_layout.addWidget(self.label_imagen)

        # Añadimos el contenedor del logo al layout maestro izquierdo
        self.left_master_layout.addWidget(self.logo_container, stretch=1)

        # ELEMENTOS GRAFICOS DE LA ESQUINA (Fuera del contenedor del logo)
        self.adorno_esquina = QSvgWidget(os.path.join(directorio, 'imagenes', 'adorno.svg'))
        self.adorno_esquina.setFixedSize(300, 215)
        
        # Lo acoplamos al fondo a la izquierda y abajo, ignorando los márgenes del logo
        self.left_master_layout.addWidget(self.adorno_esquina, alignment=Qt.AlignLeft | Qt.AlignBottom)

        # Añadimos el bloque izquierdo al diseño principal
        self.layout_principal.addWidget(self.left_container, stretch=1)

        # =================================================================
        # ZONA DERECHA: zona de logueo
        # =================================================================
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setAlignment(Qt.AlignCenter)
        # para que la tarjeta blanca mantenga su distancia del borde de la pantalla.
        self.right_layout.setContentsMargins(50, 50, 100, 50)

        # 1. Creamos el Frame que actuará como tarjeta blanca
        self.login_panel = QFrame()
        self.login_panel.setObjectName("loginPanel")
        self.login_panel.setFixedWidth(380)
        self.login_panel.setFixedHeight(460)

        # QSS con bordes muy redondeados y fondo blanco puro
        self.login_panel.setStyleSheet("""
            QFrame#loginPanel {
                background-color: #ffffff;
                border-radius: 40px;  /* Curvatura pronunciada */
            }
        """)

        # 2. Sombra difuminada muy suave hacia abajo y la derecha (Efecto Drop Shadow)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor(0, 0, 0, 70)) # Sombra negra sutil
        self.shadow.setOffset(10, 10) # Desplazamiento en X e Y
        self.login_panel.setGraphicsEffect(self.shadow)

        # 3. Layout interno del panel blanco 
        self.panel_layout = QVBoxLayout(self.login_panel)
        self.panel_layout.setContentsMargins(40, 50, 40, 50)
        self.panel_layout.addStretch() # Mantiene el interior limpio por ahora

        # Añadimos la zona derecha al layout principal
        self.layout_principal.addWidget(self.right_container, stretch=1)

        self.panel_layout.addStretch(1)

        # 4. ENTRADA DE DATOS (estilos)
        estilo_inputs = """
            QLineEdit {
                background-color: #e0dede;  /* Color gris claro del fondo del input */
                border: none;               /* Quitamos el borde por defecto */
                border-radius: 20px;        /* Mitad de la altura para efecto cápsula */
                padding-left: 25px;         /* Margen interno izquierdo para el texto */
                padding-right: 25px;
                color: black;               /* Color del texto escrito */
                font-size: 16px;            /* Tamaño de la letra */
                font-weight: bold;
            }
            """
        
        estilo_botones = """
            QPushButton {
                background-color: #0833a2; /* Color de fondo */
                color: white;               /* Color del texto */
                border-radius: 20px;        /* El radio define la curvatura */
                border: 2px solid #0833a2;  /* Borde opcional */
                padding: 5px;               /*Separacion entre el texto y el borde del boton*/
                font-size: 16px;            /* Tamaño de la letra */
                font-weight: bold;
            }
    
            QPushButton:hover {
                background-color: #3150ff; /* Cambio de color al pasar el ratón */
                border: 2px solid #3150ff
            }
                """ #agregar estilo al boton
        
        # Etiqueta de texto (login)
        self.label_login = QLabel("Login")
        self.label_login.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #000000;
                font-family: 'Arial', sans-serif;
                background: transparent; /* Evita que tome fondos grises de layouts traseros */
                margin-bottom: 10px;     /* Despegamos un poco el título de los inputs */
            }
        """)
        self.label_login.setAlignment(Qt.AlignCenter)
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
        self.txt_contraseña.setEchoMode(QLineEdit.Password)
        self.txt_contraseña.setStyleSheet(estilo_inputs)
        self.txt_contraseña.setFixedHeight(40)
        self.panel_layout.addWidget(self.txt_contraseña)

        self.panel_layout.addStretch(1)

        # boton para ingresar
        self.btn_ingresar = QPushButton("Ingresar") #titulo del boton
        self.btn_ingresar.setFixedSize(200, 40) #tamaño del boton
        self.btn_ingresar.clicked.connect(self.validar_usuario) #acccion del boton
        self.panel_layout.addWidget(self.btn_ingresar, alignment=Qt.AlignCenter) #centrado del boton

        self.panel_layout.addSpacing(15)

        # boton para registrar 
        self.btn_registrar = QPushButton("Registrar") #titulo del boton
        self.btn_registrar.setFixedSize(200, 40) #tamaño del boton
        #self.btn_registrar.clicked.connect(None) #acccion del boton
        self.panel_layout.addWidget(self.btn_registrar, alignment=Qt.AlignCenter) #centrado del boton

        self.panel_layout.addStretch(1)

        # Bucle para estilos de botones
        for btn_efectos in [self.btn_ingresar, self.btn_registrar]:
            btn_efectos.setStyleSheet(estilo_botones)
            btn_efectos.setCursor(Qt.PointingHandCursor)

        # Bucle para efectos de sombra
        for widget in [self.txt_usuario, self.txt_contraseña, self.btn_ingresar, self.btn_registrar]:
            # Creamos un objeto de sombra NUEVO en cada iteración del bucle
            efecto_sombra = QGraphicsDropShadowEffect()
            efecto_sombra.setBlurRadius(20)
            efecto_sombra.setXOffset(5)
            efecto_sombra.setYOffset(5)
            efecto_sombra.setColor(QColor(0, 0, 0, 70))
            widget.setGraphicsEffect(efecto_sombra)

        # Añadimos la tarjeta al layout derecho
        self.right_layout.addWidget(self.login_panel)
        self.layout_principal.addWidget(self.right_container, stretch=1)


    def validar_usuario(self):
        if self.txt_usuario.text() == "a" and self.txt_contraseña.text() == "a":
            from ventana_principal import VentanaPrincipal

            # Pasamos 'self' (el login actual) para conservarlo oculto en memoria sin afectar recursos
            self.ventana_principal = VentanaPrincipal(ventana_login=self)
            self.ventana_principal.showMaximized() 
            
            # Ocultamos el login en lugar de destruirlo
            self.hide() 

        else:
            print("Credenciales incorrectas")

    def centrar_ventana(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VentanaLogin()
    window.showMaximized()
    sys.exit(app.exec_())