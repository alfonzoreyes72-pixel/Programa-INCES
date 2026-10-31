import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                            QGraphicsDropShadowEffect,QStackedWidget)
from PyQt5.QtGui import QColor
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
        
        self.setWindowTitle("Sistema - Ventana Completa")
        
        # Widget central de la ventana
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal (divide la pantalla en menú lateral y área de contenido)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==================== MENÚ LATERAL IZQUIERDO ====================
        sidebar = QWidget()
        sidebar.setStyleSheet("background-color: #163e7a;")
        sidebar.setFixedWidth(260)  # Ancho fijo para el menú lateral
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)
        sidebar_layout.setSpacing(12)
        
        # Estilo común para los botones del menú lateral
        estilo_boton = """
            QPushButton {
                background-color: transparent;
                color: white;
                text-align: left;
                padding: 10px;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #235299;
                border-radius: 18px;
            }
            QPushButton:checked {
                background-color: #235299;  /* Color fijo cuando está seleccionado */
                border-radius: 18px;
            }
        """

        # Creación individual de los 7 botones del menú lateral
        self.btn_inicio = QPushButton("  Inicio")
        self.btn_inicio.setStyleSheet(estilo_boton)
        self.btn_inicio.setCheckable(True)       # Permitir que se quede marcado
        self.btn_inicio.setChecked(True)         # Arranca marcado por defecto en el inicio
        sidebar_layout.addWidget(self.btn_inicio)
        self.btn_inicio.clicked.connect(lambda: self.cambiar_pagina(0, self.btn_inicio))
        
        self.btn_perfil = QPushButton("  Perfil")
        self.btn_perfil.setStyleSheet(estilo_boton)
        self.btn_perfil.setCheckable(True)
        sidebar_layout.addWidget(self.btn_perfil)
        self.btn_perfil.clicked.connect(lambda: self.cambiar_pagina(1, self.btn_perfil))
        
        self.btn_usuarios = QPushButton("  Usuarios")
        self.btn_usuarios.setStyleSheet(estilo_boton)
        self.btn_usuarios.setCheckable(True)
        sidebar_layout.addWidget(self.btn_usuarios)
        self.btn_usuarios.clicked.connect(lambda: self.cambiar_pagina(2, self.btn_usuarios))
        
        self.btn_trabajadores = QPushButton("  Trabajadores")
        self.btn_trabajadores.setStyleSheet(estilo_boton)
        self.btn_trabajadores.setCheckable(True)
        sidebar_layout.addWidget(self.btn_trabajadores)
        self.btn_trabajadores.clicked.connect(lambda: self.cambiar_pagina(3, self.btn_trabajadores))

        self.btn_votacion = QPushButton("  Centros de Votación")
        self.btn_votacion.setStyleSheet(estilo_boton)
        self.btn_votacion.setCheckable(True)
        sidebar_layout.addWidget(self.btn_votacion)
        self.btn_votacion.clicked.connect(lambda: self.cambiar_pagina(4, self.btn_votacion))
        
        self.btn_asistencias = QPushButton("  Asistencias")
        self.btn_asistencias.setStyleSheet(estilo_boton)
        self.btn_asistencias.setCheckable(True)
        sidebar_layout.addWidget(self.btn_asistencias)
        self.btn_asistencias.clicked.connect(lambda: self.cambiar_pagina(5, self.btn_asistencias))
        
        self.btn_operativas = QPushButton("  Novedades Operativas")
        self.btn_operativas.setStyleSheet(estilo_boton)
        self.btn_operativas.setCheckable(True)
        sidebar_layout.addWidget(self.btn_operativas)
        self.btn_operativas.clicked.connect(lambda: self.cambiar_pagina(6, self.btn_operativas))
        
        self.btn_reportes = QPushButton("  Reportes")
        self.btn_reportes.setStyleSheet(estilo_boton)
        self.btn_reportes.setCheckable(True)
        sidebar_layout.addWidget(self.btn_reportes)
        self.btn_reportes.clicked.connect(lambda: self.cambiar_pagina(7, self.btn_reportes))
        
        # Espaciador flexible para empujar el botón de salida hacia el fondo
        sidebar_layout.addStretch()
        
        # Botón de Cerrar sesión[cite: 1]
        btn_cerrar = QPushButton("Cerrar sesión")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #163e7a;
                border-radius: 18px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d9d9d9;
            }
        """)
    # --- APLICAMOS LA SOMBRA AL BOTON DE CERRAR ---
        efecto_sombra = QGraphicsDropShadowEffect(self)
        efecto_sombra.setBlurRadius(20)
        efecto_sombra.setXOffset(5)
        efecto_sombra.setYOffset(5)
        efecto_sombra.setColor(QColor(0, 0, 0, 70))
        btn_cerrar.setGraphicsEffect(efecto_sombra)

        btn_cerrar.clicked.connect(self.cerrar_sesion)
        sidebar_layout.addWidget(btn_cerrar)
        
        # ==================== ÁREA PRINCIPAL (DERECHA) ====================
        # Creamos el gestor de páginas (Stacked Widget)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #bfbdbe")

        # Instanciamos cada vista modular
        self.pagina_inicio = VentanaInicio()
        self.pagina_perfil = VentanaPerfil()
        self.pagina_usuarios = VentanaUsuarios()
        self.pagina_trabajadores = VentanaTrabajadores()
        self.pagina_votacion = VentanaVotacion()
        self.pagina_asistencias = VentanaAsistencias()
        self.pagina_operativas = VentanaOperativas()
        self.pagina_reportes = VentanaReportes()

        # Las añadimos al carrusel
        self.stacked_widget.addWidget(self.pagina_inicio)    # Índice 0 (Se muestra por defecto al abrir)
        self.stacked_widget.addWidget(self.pagina_perfil)  # Índice 1
        self.stacked_widget.addWidget(self.pagina_usuarios)  # Índice 2
        self.stacked_widget.addWidget(self.pagina_trabajadores)  # Índice 3
        self.stacked_widget.addWidget(self.pagina_votacion)  # Índice 4
        self.stacked_widget.addWidget(self.pagina_asistencias)  # Índice 5
        self.stacked_widget.addWidget(self.pagina_operativas)  # Índice 6
        self.stacked_widget.addWidget(self.pagina_reportes)  # Índice 7

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

    # ==================== MÉTODOS ====================
    def cerrar_sesion(self):
        # Activamos la bandera indicando que el cierre se originó por el botón "Salir"
        self.cerrando_sesion = True
        self.close()

    def cambiar_pagina(self, indice, boton_activo):
        # 1. Cambiamos la vista en el stacked widget
        self.stacked_widget.setCurrentIndex(indice)
        
        # 2. Lista con todos los botones del menú lateral para controlarlos
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
        # 3. Recorremos los botones: marcamos solo el activo y desmarcamos el resto
        for btn in botones:
            if btn == boton_activo:
                btn.setChecked(True)
            else:
                btn.setChecked(False)

    def closeEvent(self, event):
        # Controlamos si se cerró por sesión o si le dieron a la "X" normal
        if self.cerrando_sesion:
            if self.ventana_login:
                self.ventana_login.limpiar_formulario() # <--- ¡Limpiamos los datos por seguridad!
                self.ventana_login.show()               # Volvemos a mostrar el login oculto
            event.accept()
        else:
            # Si le dieron a la "X", cerramos toda la aplicación por completo
            event.accept()
            QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    
    # Abre la ventana maximizada (pantalla completa)
    ventana.showMaximized() 
    
    sys.exit(app.exec_())