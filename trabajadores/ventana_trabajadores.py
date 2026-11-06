import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QHeaderView, QScrollArea
)
from PyQt6.QtCore import Qt


class VentanaTrabajadores(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout principal de la vista
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(0)

        # =================================================================
        # 1. QSCROLLAREA (Para mover la barra al borde exterior de la tarjeta)
        # =================================================================
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            /* Estilo opcional para hacer la barra lateral más estética y delgada */
            QScrollBar:vertical {
                background: #f4f6f9;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Contenedor que irá dentro del ScrollArea
        contenedor_scroll = QWidget()
        contenedor_scroll.setStyleSheet("background-color: transparent;")
        layout_contenedor = QVBoxLayout(contenedor_scroll)
        layout_contenedor.setContentsMargins(0, 0, 0, 0)

        # =================================================================
        # 2. TARJETA PRINCIPAL (Fondo Blanco Sin Sombra)
        # =================================================================
        self.panel_principal = QFrame()
        self.panel_principal.setObjectName("panelTrabajadores")
        self.panel_principal.setStyleSheet("""
            QFrame#panelTrabajadores {
                background-color: #ffffff;
                border-radius: 20px;
            }
        """)

        # Layout interno del panel principal
        layout_panel = QVBoxLayout(self.panel_principal)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(15)

        # =================================================================
        # 3. FRANJA SUPERIOR DE CONTROLES (Buscador y Botones)
        # =================================================================
        self.franja_superior = QFrame()
        self.franja_superior.setObjectName("franjaSuperior")
        self.franja_superior.setStyleSheet("""
            QFrame#franjaSuperior {
                background-color: #f4f6f9;
                border-radius: 15px;
            }
        """)
        
        layout_franja = QHBoxLayout(self.franja_superior)
        layout_franja.setContentsMargins(15, 12, 15, 12)
        layout_franja.setSpacing(12)

        # Barra de búsqueda
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar trabajador por cédula o nombre...")
        self.txt_buscar.setFixedHeight(38)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 19px;
                padding-left: 20px;
                padding-right: 20px;
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #0833a2;
            }
        """)
        layout_franja.addWidget(self.txt_buscar, stretch=1)

        # Botón Buscar
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setFixedSize(110, 38)
        self.btn_buscar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar.setStyleSheet("""
            QPushButton {
                background-color: #0833a2;
                color: white;
                border-radius: 19px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3150ff;
            }
        """)
        layout_franja.addWidget(self.btn_buscar)

        # Botón Agregar Trabajador
        self.btn_agregar = QPushButton("+ Agregar")
        self.btn_agregar.setFixedSize(120, 38)
        self.btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 19px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout_franja.addWidget(self.btn_agregar)

        layout_panel.addWidget(self.franja_superior)

        # =================================================================
        # 4. TABLA DE TRABAJADORES
        # =================================================================
        self.tabla_trabajadores = QTableWidget()
        
        columnas = ["Cédula", "Nombre", "Departamento", "Teléfono", "Fecha de Ingreso"]
        self.tabla_trabajadores.setColumnCount(len(columnas))
        self.tabla_trabajadores.setHorizontalHeaderLabels(columnas)
        
        self.tabla_trabajadores.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_trabajadores.verticalHeader().setVisible(False)
        self.tabla_trabajadores.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_trabajadores.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Desactivamos el scroll interno de la tabla para que el scroll exterior maneje todo el panel
        self.tabla_trabajadores.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabla_trabajadores.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tabla_trabajadores.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0dede;
                border-radius: 12px;
                gridline-color: #f0f0f0;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #163e7a;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border: none;
            }
            QHeaderView::section:first {
                border-top-left-radius: 12px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 12px;
            }
            QTableWidget::item {
                padding: 10px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #e6f0ff;
                color: #0833a2;
            }
        """)

        # Simulamos una altura fija inicial o dejamos que crezca, pero con el scroll area se adaptará
        self.tabla_trabajadores.setRowCount(0)
        layout_panel.addWidget(self.tabla_trabajadores)

        # Empaquetamos todo en el scroll area
        layout_contenedor.addWidget(self.panel_principal)
        self.scroll_area.setWidget(contenedor_scroll)
        layout_principal.addWidget(self.scroll_area)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaTrabajadores()
    ventana.show()
    sys.exit(app.exec())