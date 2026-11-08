import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QLabel, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

class FilaTrabajador(QFrame):
    """Componente interactivo para cada fila de trabajador en la lista"""
    cliqueado = pyqtSignal(dict)

    def __init__(self, datos_trabajador, parent=None):
        super().__init__(parent)
        self.datos = datos_trabajador
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        
        self.setStyleSheet("""
            FilaTrabajador {
                background-color: transparent;
                border-radius: 10px;
                border-bottom: 1px solid #eaeaea;
            }
            FilaTrabajador:hover {
                background-color: #e8ebf0;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)

        self.lbl_nombre = QLabel(self.datos["nombre"])
        self.lbl_nombre.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; border: none; background: transparent;")
        
        self.lbl_cedula = QLabel(self.datos["cedula"])
        self.lbl_cedula.setStyleSheet("font-size: 14px; font-weight: bold; color: #555555; border: none; background: transparent;")

        layout.addWidget(self.lbl_nombre)
        layout.addStretch()
        layout.addWidget(self.lbl_cedula)

    def mousePressEvent(self, event):
        self.cliqueado.emit(self.datos)
        super().mousePressEvent(event)


class VentanaTrabajadores(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout principal horizontal
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        # Contenedor izquierdo (Tarjetas superiores + Listado)
        self.contenedor_izq = QWidget()
        layout_izq = QVBoxLayout(self.contenedor_izq)
        layout_izq.setContentsMargins(0, 0, 0, 0)
        layout_izq.setSpacing(15)

        # =================================================================
        # 1. TRES TARJETAS DE WIDGETS SUPERIORES
        # =================================================================
        layout_tarjetas = QHBoxLayout()
        layout_tarjetas.setSpacing(15)

        self.card_total = self.crear_tarjeta_metrica("Total Trabajadores", "1,003", "#163e7a")
        self.card_fijo = self.crear_tarjeta_metrica("Contrato Fijo", "2,160", "#235299")
        self.card_temporal = self.crear_tarjeta_metrica("Contrato Temporal", "1,691", "#3b6ba3")

        layout_tarjetas.addWidget(self.card_total)
        layout_tarjetas.addWidget(self.card_fijo)
        layout_tarjetas.addWidget(self.card_temporal)
        layout_izq.addLayout(layout_tarjetas)

        # =================================================================
        # 2. PANEL PRINCIPAL DEL LISTADO
        # =================================================================
        self.panel_listado = QFrame()
        self.panel_listado.setObjectName("panelListado")
        self.panel_listado.setStyleSheet("""
            QFrame#panelListado {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        
        self.panel_listado.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout_panel = QVBoxLayout(self.panel_listado)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(15)

        # Título "Listado de trabajadores" (Actualizado al tono oscuro sutil #2c2c2c)
        self.lbl_titulo_lista = QLabel("Listado de trabajadores")
        self.lbl_titulo_lista.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(self.lbl_titulo_lista)

        # Controles debajo del título
        controles_layout = QHBoxLayout()
        controles_layout.setSpacing(10)

        self.btn_agregar = QPushButton("+ Agregar")
        self.btn_agregar.setFixedSize(105, 36)
        self.btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #163e7a;
                color: white;
                border-radius: 18px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #235299; }
        """)
        controles_layout.addWidget(self.btn_agregar)

        self.btn_modificar = QPushButton("Modificar")
        self.btn_modificar.setFixedSize(105, 36)
        self.btn_modificar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_modificar.setStyleSheet("""
            QPushButton {
                background-color: #163e7a;
                color: white;
                border-radius: 18px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #235299; }
        """)
        controles_layout.addWidget(self.btn_modificar)

        controles_layout.addStretch()

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("🔍 Buscar trabajador...")
        self.txt_buscar.setFixedSize(220, 36)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #f4f6f9;
                border: 1px solid #dcdcdc;
                border-radius: 18px;
                padding-left: 15px;
                padding-right: 15px;
                color: black;
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit:focus { border: 2px solid #0833a2; }
        """)
        controles_layout.addWidget(self.txt_buscar)

        layout_panel.addLayout(controles_layout)

        # Scroll Area para el listado personalizado
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.contenedor_filas = QWidget()
        self.contenedor_filas.setStyleSheet("background: transparent; border: none;")
        self.layout_filas = QVBoxLayout(self.contenedor_filas)
        self.layout_filas.setContentsMargins(0, 0, 0, 0)
        self.layout_filas.setSpacing(5)
        self.layout_filas.addStretch()

        self.scroll_area.setWidget(self.contenedor_filas)
        layout_panel.addWidget(self.scroll_area)

        layout_izq.addWidget(self.panel_listado)
        layout_principal.addWidget(self.contenedor_izq, stretch=3)

        # =================================================================
        # 3. TARJETA BLANCA LATERAL DE DETALLES CON SCROLL INTERNO
        # =================================================================
        self.panel_detalles = QFrame()
        self.panel_detalles.setObjectName("panelDetalles")
        self.panel_detalles.setFixedWidth(300)
        self.panel_detalles.setStyleSheet("""
            QFrame#panelDetalles {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        
        layout_detalles = QVBoxLayout(self.panel_detalles)
        layout_detalles.setContentsMargins(20, 20, 20, 20)
        layout_detalles.setSpacing(12)

        # Cabecera con botón de cerrar
        header_detalles = QHBoxLayout()
        header_detalles.addStretch()
        self.btn_cerrar_detalle = QPushButton("✕")
        self.btn_cerrar_detalle.setFixedSize(28, 28)
        self.btn_cerrar_detalle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cerrar_detalle.setStyleSheet("""
            QPushButton {
                background-color: #f4f6f9;
                color: #555555;
                border-radius: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #e0dede; color: black; }
        """)
        self.btn_cerrar_detalle.clicked.connect(self.ocultar_detalles)
        header_detalles.addWidget(self.btn_cerrar_detalle)
        layout_detalles.addLayout(header_detalles)

        # Círculo Avatar Estilo WhatsApp (Centrado, fijo arriba)
        self.lbl_avatar = QLabel("A")
        self.lbl_avatar.setFixedSize(75, 75)
        self.lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_avatar.setStyleSheet("""
            QLabel {
                background-color: #163e7a;
                color: white;
                font-size: 30px;
                font-weight: bold;
                border-radius: 37px;
            }
        """)
        
        avatar_layout = QHBoxLayout()
        avatar_layout.addStretch()
        avatar_layout.addWidget(self.lbl_avatar)
        avatar_layout.addStretch()
        layout_detalles.addLayout(avatar_layout)

        # Nombre del Trabajador Centrado (Fijo arriba)
        self.lbl_nombre_detalle = QLabel("Nombre del Trabajador")
        self.lbl_nombre_detalle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nombre_detalle.setWordWrap(True)
        self.lbl_nombre_detalle.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_nombre_detalle.setStyleSheet("font-size: 16px; font-weight: bold; color: #163e7a; border: none; background: transparent;")
        layout_detalles.addWidget(self.lbl_nombre_detalle)

        # Línea de separación sutil
        separador = QFrame()
        separador.setFixedHeight(1)
        separador.setStyleSheet("background-color: #f0f0f0; border: none;")
        layout_detalles.addWidget(separador)

        # --- QSCROLLAREA INTERNO PARA LOS DETALLES EXTENSOS ---
        self.scroll_detalles = QScrollArea()
        self.scroll_detalles.setWidgetResizable(True)
        self.scroll_detalles.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f4f6f9;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Contenedor interno del scroll de detalles
        self.contenido_scroll_detalles = QWidget()
        self.contenido_scroll_detalles.setStyleSheet("background: transparent; border: none;")
        layout_scroll_detalles = QVBoxLayout(self.contenido_scroll_detalles)
        layout_scroll_detalles.setContentsMargins(0, 0, 5, 0)
        layout_scroll_detalles.setSpacing(10)

        # Información detallada adicional (Habilitada para seleccionarse y copiarse con el mouse)
        self.lbl_detalles_contenido = QLabel()
        self.lbl_detalles_contenido.setWordWrap(True)
        self.lbl_detalles_contenido.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_detalles_contenido.setStyleSheet("font-size: 13px; color: #444444; border: none; background: transparent; line-height: 140%;")
        layout_scroll_detalles.addWidget(self.lbl_detalles_contenido)
        layout_scroll_detalles.addStretch()

        self.scroll_detalles.setWidget(self.contenido_scroll_detalles)
        layout_detalles.addWidget(self.scroll_detalles)
        
        layout_principal.addWidget(self.panel_detalles)
        self.panel_detalles.hide()

        self.cargar_trabajadores_ejemplo()

    def crear_tarjeta_metrica(self, titulo, valor, color_borde):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 15px;
                border-left: 6px solid {color_borde};
                border-top: none;
                border-right: none;
                border-bottom: none;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; border: none; background: transparent;")
        
        lbl_val = QLabel(valor)
        lbl_val.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color_borde}; border: none; background: transparent;")
        
        layout.addWidget(lbl_tit)
        layout.addWidget(lbl_val)
        return card

    def cargar_trabajadores_ejemplo(self):
        trabajadores = [
            {"nombre": "Carlos Arciniegas", "cedula": "18.783.456", "departamento": "Tecnología", "contrato": "Fijo"},
            {"nombre": "Angel Malavé", "cedula": "32.745.323", "departamento": "Recursos Humanos", "contrato": "Temporal"},
            {"nombre": "Fernando AA", "cedula": "24.985.569", "departamento": "Administración", "contrato": "Fijo"},
            {"nombre": "Alanis ElNOQ", "cedula": "29.112.334", "departamento": "Formación", "contrato": "Fijo"},
            {"nombre": "Carla A.", "cedula": "31.116.632", "departamento": "Sistemas", "contrato": "Temporal"},
            {"nombre": "Jesús López", "cedula": "27.559.871", "departamento": "Operaciones", "contrato": "Fijo"}
        ]

        for t in trabajadores:
            fila = FilaTrabajador(t)
            fila.cliqueado.connect(self.mostrar_detalles_trabajador)
            self.layout_filas.insertWidget(self.layout_filas.count() - 1, fila)

    def mostrar_detalles_trabajador(self, datos):
        nombre = datos['nombre']
        inicial = nombre[0].upper() if nombre else "?"
        
        self.lbl_avatar.setText(inicial)
        self.lbl_nombre_detalle.setText(nombre)

        texto = f"""
        <b>Cédula:</b> {datos['cedula']}<br><br>
        <b>Departamento:</b> {datos['departamento']}<br><br>
        <b>Tipo Contrato:</b> {datos['contrato']}<br><br>
        <b>Correo:</b> trabajador@inces.gob.ve<br><br>
        <b>Teléfono:</b> 0414-1234567<br><br>
        <b>Fecha de Ingreso:</b> 15/03/2022<br><br>
        <b>Ubicación:</b> Sede Principal Monagas
        """
        self.lbl_detalles_contenido.setText(texto)
        self.panel_detalles.show()

    def ocultar_detalles(self):
        self.panel_detalles.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaTrabajadores()
    ventana.resize(1050, 650)
    ventana.show()
    sys.exit(app.exec())