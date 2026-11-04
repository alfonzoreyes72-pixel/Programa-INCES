import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                            QGraphicsDropShadowEffect, QStackedWidget)
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt

from inicio.ventana_inicio import VentanaInicio
from perfil.ventana_perfil import VentanaPerfil
from usuarios.ventana_usuarios import VentanaUsuarios
from trabajadores.ventana_trabajadores import VentanaTrabajadores
from asistencias.ventana_asistencias import VentanaAsistencias
from votacion.ventana_votacion import VentanaVotacion
from operativas.ventana_operativas import VentanaOperativas
from reportes.ventana_reportes import VentanaReportes

class VentanaPrincipal(QMainWindow):
    def __init__(self, ventana_login=None):
        super().__init__()
        self.ventana_login = ventana_login  # Guardamos la referencia del login oculto
        self.cerrando_sesion = False        # Bandera para saber si se cerró sesión o se usó la "X"
        self.menu_expandido = True          # Estado inicial del menú lateral
        
        self.setWindowTitle("Sistema - Ventana Completa")
        
        # Widget central de la ventana
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal (divide la pantalla en menú lateral y área de contenido)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==================== MENÚ LATERAL IZQUIERDO ====================
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet("background-color: #163e7a;")
        self.sidebar.setFixedWidth(260)  # Ancho fijo para el menú lateral
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(12)
        
        # --- ENCABEZADO DEL SIDEBAR (Botón hamburguesa + Logo institucional) ---
        header_menu_layout = QHBoxLayout()
        header_menu_layout.setSpacing(10)
        
        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setFixedSize(40, 40)
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3b6ba3;
            }
        """)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        header_menu_layout.addWidget(self.btn_toggle)
        
        self.label_logo_sidebar = QLabel()
        directorio = os.path.dirname(__file__)
        ruta_logo = os.path.join(directorio, 'imagenes', 'INCES Sede Monagas.svg')
        if not os.path.exists(ruta_logo):
            ruta_logo = os.path.join(directorio, 'imagenes', 'logo inces.png')
            
        pixmap = QPixmap(ruta_logo)
        self.label_logo_sidebar.setPixmap(pixmap.scaled(140, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_menu_layout.addWidget(self.label_logo_sidebar)
        
        sidebar_layout.addLayout(header_menu_layout)
        sidebar_layout.addSpacing(10)
        
        # Estilo común para los botones del menú lateral (con soporte de tamaño de icono)
        estilo_boton = """
            QPushButton {
                background-color: transparent;
                color: white;
                text-align: left;
                padding: 10px;
                border: none;
                font-size: 14px;
                font-weight: bold;
                icon-size: 22px;
            }
            QPushButton:hover {
                background-color: #3b6ba3;
                border-radius: 18px;
            }
            QPushButton:checked {
                background-color: #235299;  /* Color fijo cuando está seleccionado */
                border-radius: 18px;
            }
        """

        # Creación individual de los botones del menú lateral con sus respectivas rutas autocalculables
        self.btn_inicio = QPushButton("  Inicio")
        self.btn_inicio.setStyleSheet(estilo_boton)
        self.btn_inicio.setIcon(QIcon(os.path.join(directorio, 'imagenes', 'icono-inicio.svg')))
        self.btn_inicio.setCheckable(True)
        self.btn_inicio.setChecked(True)
        sidebar_layout.addWidget(self.btn_inicio)
        self.btn_inicio.clicked.connect(lambda: self.cambiar_pagina(0, self.btn_inicio))
        
        self.btn_perfil = QPushButton("  Perfil")
        self.btn_perfil.setStyleSheet(estilo_boton)
        self.btn_perfil.setIcon(QIcon(os.path.join(directorio, 'imagenes', 'icono-perfil.svg')))
        self.btn_perfil.setCheckable(True)
        sidebar_layout.addWidget(self.btn_perfil)
        self.btn_perfil.clicked.connect(lambda: self.cambiar_pagina(1, self.btn_perfil))
        
        self.btn_usuarios = QPushButton("  Usuarios")
        self.btn_usuarios.setStyleSheet(estilo_boton)
        self.btn_usuarios.setIcon(QIcon(os.path.join(directorio, 'imagenes', 'icono-usuarios.svg')))
        self.btn_usuarios.setCheckable(True)
        sidebar_layout.addWidget(self.btn_usuarios)
        self.btn_usuarios.clicked.connect(lambda: self.cambiar_pagina(2, self.btn_usuarios))
        
        self.btn_trabajadores = QPushButton("  Trabajadores")
        self.btn_trabajadores.setStyleSheet(estilo_boton)
        self.btn_trabajadores.setIcon(QIcon(os.path.join(directorio, 'imagenes', 'icono-trabajadores.svg')))
        self.btn_trabajadores.setCheckable(True)
        sidebar_layout.addWidget(self.btn_trabajadores)
        self.btn_trabajadores.clicked.connect(lambda: self.cambiar_pagina(3, self.btn_trabajadores))

        self.btn_votacion = QPushButton("  Centros de Votación")
        self.btn_votacion.setStyleSheet(estilo_boton)
        self.btn_votacion.setIcon(QIcon(os.path.join(directorio, 'imagenes', 'icono-votacion.svg')))
        self.btn_votacion.setCheckable(True)
        sidebar_layout.addWidget(self.btn_votacion)
        self.btn_votacion.clicked.connect(lambda: self.cambiar_pagina(4, self.btn_votacion))
        
        self.btn_asistencias = QPushButton("  Asistencias")
        self.btn_asistencias.setStyleSheet(estilo_boton)
        self.btn_asistencias.setIcon(QIcon(os.path.join(directorio, 'imagenes', 'icono-asistencias.svg')))
        self.btn_asistencias.setCheckable(True)
        sidebar_layout.addWidget(self.btn_asistencias)
        self.btn_asistencias.clicked.connect(lambda: self.cambiar_pagina(5, self.btn_asistencias))
        
        self.btn_operativas = QPushButton("  Novedades Operativas")
        self.btn_operativas.setStyleSheet(estilo_boton)
        self.btn_operativas.setIcon(QIcon(os.path.join(directorio, 'imagenes', 'icono-operativas.svg')))
        self.btn_operativas.setCheckable(True)
        sidebar_layout.addWidget(self.btn_operativas)
        self.btn_operativas.clicked.connect(lambda: self.cambiar_pagina(6, self.btn_operativas))
        
        self.btn_reportes = QPushButton("  Reportes")
        self.btn_reportes.setStyleSheet(estilo_boton)
        self.btn_reportes.setIcon(QIcon(os.path.join(directorio, 'imagenes', 'icono-reportes.svg')))
        self.btn_reportes.setCheckable(True)
        sidebar_layout.addWidget(self.btn_reportes)
        self.btn_reportes.clicked.connect(lambda: self.cambiar_pagina(7, self.btn_reportes))
        
        # Espaciador flexible para empujar el botón de salida hacia el fondo
        sidebar_layout.addStretch()
        
        # Botón de Cerrar sesión
        self.btn_cerrar = QPushButton("  Cerrar sesión")
        self.btn_cerrar.setIcon(QIcon(os.path.join(directorio, 'imagenes', 'icono-cerrar-sesion.svg')))
        self.btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #163e7a;
                border-radius: 18px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                icon-size: 22px; /* Asegura el tamaño del icono */
            }
            QPushButton:hover {
                background-color: #d9d9d9;
            }
        """)
        
        efecto_sombra = QGraphicsDropShadowEffect(self)
        efecto_sombra.setBlurRadius(20)
        efecto_sombra.setXOffset(5)
        efecto_sombra.setYOffset(5)
        efecto_sombra.setColor(QColor(0, 0, 0, 70))
        self.btn_cerrar.setGraphicsEffect(efecto_sombra)

        self.btn_cerrar.clicked.connect(self.cerrar_sesion)
        sidebar_layout.addWidget(self.btn_cerrar)
        
        # ==================== ÁREA PRINCIPAL (DERECHA) ====================
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #bfbdbe;")

        self.pagina_inicio = VentanaInicio()
        self.pagina_perfil = VentanaPerfil()
        self.pagina_usuarios = VentanaUsuarios()
        self.pagina_trabajadores = VentanaTrabajadores()
        self.pagina_votacion = VentanaVotacion()
        self.pagina_asistencias = VentanaAsistencias()
        self.pagina_operativas = VentanaOperativas()
        self.pagina_reportes = VentanaReportes()

        self.stacked_widget.addWidget(self.pagina_inicio)
        self.stacked_widget.addWidget(self.pagina_perfil)
        self.stacked_widget.addWidget(self.pagina_usuarios)
        self.stacked_widget.addWidget(self.pagina_trabajadores)
        self.stacked_widget.addWidget(self.pagina_votacion)
        self.stacked_widget.addWidget(self.pagina_asistencias)
        self.stacked_widget.addWidget(self.pagina_operativas)
        self.stacked_widget.addWidget(self.pagina_reportes)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)

    # ==================== MÉTODOS ====================
    def toggle_sidebar(self):
        """Método para contraer o expandir el menú lateral de forma responsiva"""
        if self.menu_expandido:
            # Contraer menú
            self.sidebar.setFixedWidth(75)
            self.label_logo_sidebar.hide()
            
            self.btn_inicio.setText("")
            self.btn_perfil.setText("")
            self.btn_usuarios.setText("")
            self.btn_trabajadores.setText("")
            self.btn_votacion.setText("")
            self.btn_asistencias.setText("")
            self.btn_operativas.setText("")
            self.btn_reportes.setText("")
            self.btn_cerrar.setText("")  # Oculta el texto, manteniendo el icono visible
            self.menu_expandido = False
        else:
            # Expandir menú
            self.sidebar.setFixedWidth(260)
            self.label_logo_sidebar.show()
            
            self.btn_inicio.setText("  Inicio")
            self.btn_perfil.setText("  Perfil")
            self.btn_usuarios.setText("  Usuarios")
            self.btn_trabajadores.setText("  Trabajadores")
            self.btn_votacion.setText("  Centros de Votación")
            self.btn_asistencias.setText("  Asistencias")
            self.btn_operativas.setText("  Novedades Operativas")
            self.btn_reportes.setText("  Reportes")
            self.btn_cerrar.setText("  Cerrar sesión")  # Restaura el texto completo
            self.menu_expandido = True
            
    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()

    def cambiar_pagina(self, indice, boton_activo):
        self.stacked_widget.setCurrentIndex(indice)
        botones = [
            self.btn_inicio, 
            self.btn_perfil, 
            self.btn_usuarios, 
            self.btn_trabajadores, 
            self.btn_votacion, 
            self.btn_asistencias, 
            self.btn_operativas, 
            self.btn_reportes
        ]
        for btn in botones:
            if btn == boton_activo:
                btn.setChecked(True)
            else:
                btn.setChecked(False)

    def closeEvent(self, event):
        if self.cerrando_sesion:
            if self.ventana_login:
                self.ventana_login.limpiar_formulario()
                self.ventana_login.show()
            event.accept()
        else:
            event.accept()
            QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.showMaximized() 
    sys.exit(app.exec_())