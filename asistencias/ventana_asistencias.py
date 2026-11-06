import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QHeaderView, QScrollArea,
    QDateEdit, QLabel, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QTime


class VentanaAsistencias(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout principal de la vista
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(0)

        # =================================================================
        # 1. QSCROLLAREA
        # =================================================================
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
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

        # Contenedor principal dentro del ScrollArea
        contenedor_scroll = QWidget()
        contenedor_scroll.setStyleSheet("background-color: transparent;")
        layout_contenedor = QVBoxLayout(contenedor_scroll)
        layout_contenedor.setContentsMargins(0, 0, 0, 0)

        # =================================================================
        # 2. TARJETA PRINCIPAL (Fondo Blanco Sin Sombra)
        # =================================================================
        self.panel_principal = QFrame()
        self.panel_principal.setObjectName("panelAsistencias")
        self.panel_principal.setStyleSheet("""
            QFrame#panelAsistencias {
                background-color: #ffffff;
                border-radius: 20px;
            }
        """)

        layout_panel = QVBoxLayout(self.panel_principal)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(15)

        # =================================================================
        # 3. FRANJA SUPERIOR DE CONTROLES (Buscador, Fecha y Botones)
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
        layout_franja.setSpacing(10)

        # Seleccionador de Fecha (QDateEdit con límites y estilos personalizados)
        self.lbl_fecha = QLabel("Fecha:")
        self.lbl_fecha.setStyleSheet("font-size: 14px; font-weight: bold; color: #163e7a;")
        layout_franja.addWidget(self.lbl_fecha)

        self.date_filtro = QDateEdit()
        self.date_filtro.setDate(QDate.currentDate())
        self.date_filtro.setCalendarPopup(True)
        self.date_filtro.setFixedHeight(38)
        
        # Restricciones de fecha (Rango: Hace 1 mes hasta hoy)
        hoy = QDate.currentDate()
        self.date_filtro.setMaximumDate(hoy)
        self.date_filtro.setMinimumDate(hoy.addMonths(-1))

        # Estilo estético para el QDateEdit y el QCalendarWidget emergente
        self.date_filtro.setStyleSheet("""
            QDateEdit {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 10px;
                padding-left: 10px;
                padding-right: 10px;
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
            QDateEdit:focus {
                border: 2px solid #0833a2;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 0px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)

        # Aplicar estilo al calendario popup emergente
        calendario = self.date_filtro.calendarWidget()
        calendario.setStyleSheet("""
            /* Fondo principal del calendario */
            QCalendarWidget QWidget {
                background-color: #ffffff;
                color: #333333;
                font-size: 13px;
            }
            /* Cabecera del mes y navegadores */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #163e7a;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QCalendarWidget QToolButton {
                color: #ffffff;
                background-color: transparent;
                font-weight: bold;
                border: none;
                margin: 2px;
                padding: 4px;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #3b6ba3;
            }
            QCalendarWidget QToolButton::menu-indicator {
                image: none;
            }
            /* Días de la semana (Lu, Ma, Mi, etc.) */
            QCalendarWidget QTableView {
                selection-background-color: #0833a2;
                selection-color: #ffffff;
                border: 1px solid #e0dede;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            /* Estilo para los días del mes en la grilla */
            QCalendarWidget QAbstractItemView:enabled {
                color: #333333;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #bbbbbb;
            }
        """)

        layout_franja.addWidget(self.date_filtro)

        # Buscador de Trabajadores por Cédula
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por cédula del trabajador...")
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
        self.btn_buscar.setFixedSize(95, 38)
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
        self.btn_buscar.clicked.connect(self.buscar_asistencia)
        layout_franja.addWidget(self.btn_buscar)

        # Botón Marcar Entrada
        self.btn_marcar_entrada = QPushButton("+ Entrada")
        self.btn_marcar_entrada.setFixedSize(105, 38)
        self.btn_marcar_entrada.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_marcar_entrada.setStyleSheet("""
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
        self.btn_marcar_entrada.clicked.connect(self.marcar_entrada)
        layout_franja.addWidget(self.btn_marcar_entrada)

        # Botón Marcar Salida
        self.btn_marcar_salida = QPushButton("Salida")
        self.btn_marcar_salida.setFixedSize(100, 38)
        self.btn_marcar_salida.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_marcar_salida.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 19px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.btn_marcar_salida.clicked.connect(self.marcar_salida)
        layout_franja.addWidget(self.btn_marcar_salida)

        # Botón Eliminar Registro
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setFixedSize(110, 38)
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 19px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.btn_eliminar.clicked.connect(self.eliminar_asistencia)
        layout_franja.addWidget(self.btn_eliminar)

        layout_panel.addWidget(self.franja_superior)

        # =================================================================
        # 4. TABLA DE ASISTENCIAS
        # =================================================================
        self.tabla_asistencias = QTableWidget()
        
        columnas = ["ID Asistencia", "Cédula Trabajador", "Fecha", "Hora Entrada", "Hora Salida"]
        self.tabla_asistencias.setColumnCount(len(columnas))
        self.tabla_asistencias.setHorizontalHeaderLabels(columnas)
        
        self.tabla_asistencias.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_asistencias.verticalHeader().setVisible(False)
        self.tabla_asistencias.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_asistencias.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.tabla_asistencias.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabla_asistencias.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tabla_asistencias.setStyleSheet("""
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

        self.tabla_asistencias.setRowCount(0)
        layout_panel.addWidget(self.tabla_asistencias)

        layout_contenedor.addWidget(self.panel_principal)
        self.scroll_area.setWidget(contenedor_scroll)
        layout_principal.addWidget(self.scroll_area)

    # =================================================================
    # LÓGICA / FUNCIONALIDADES INTEGRADAS
    # =================================================================
    def marcar_entrada(self):
        cedula = self.txt_buscar.text().strip()
        if not cedula:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese la cédula del trabajador para marcar entrada.")
            return

        fecha_actual = QDate.currentDate().toString("yyyy-MM-dd")
        hora_actual = QTime.currentTime().toString("hh:mm:ss")
        id_asistencia = str(self.tabla_asistencias.rowCount() + 1)

        row_position = self.tabla_asistencias.rowCount()
        self.tabla_asistencias.insertRow(row_position)
        self.tabla_asistencias.setItem(row_position, 0, QTableWidgetItem(id_asistencia))
        self.tabla_asistencias.setItem(row_position, 1, QTableWidgetItem(cedula))
        self.tabla_asistencias.setItem(row_position, 2, QTableWidgetItem(fecha_actual))
        self.tabla_asistencias.setItem(row_position, 3, QTableWidgetItem(hora_actual))
        self.tabla_asistencias.setItem(row_position, 4, QTableWidgetItem("---"))

        QMessageBox.information(self, "Éxito", f"Entrada registrada para la cédula {cedula} a las {hora_actual}.")

    def marcar_salida(self):
        fila_seleccionada = self.tabla_asistencias.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione un registro de la tabla para marcar la hora de salida.")
            return

        hora_actual = QTime.currentTime().toString("hh:mm:ss")
        self.tabla_asistencias.setItem(fila_seleccionada, 4, QTableWidgetItem(hora_actual))
        
        QMessageBox.information(self, "Éxito", f"Salida registrada exitosamente a las {hora_actual}.")

    def eliminar_asistencia(self):
        fila_seleccionada = self.tabla_asistencias.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione la fila de asistencia que desea eliminar.")
            return

        confirmacion = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar este registro de asistencia?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirmacion == QMessageBox.StandardButton.Yes:
            self.tabla_asistencias.removeRow(fila_seleccionada)
            QMessageBox.information(self, "Éxito", "El registro de asistencia ha sido eliminado correctamente.")

    def buscar_asistencia(self):
        cedula = self.txt_buscar.text().strip()
        fecha_sel = self.date_filtro.date().toString("yyyy-MM-dd")

        for row in range(self.tabla_asistencias.rowCount()):
            item_cedula = self.tabla_asistencias.item(row, 1)
            item_fecha = self.tabla_asistencias.item(row, 2)
            
            coincide_cedula = cedula.lower() in item_cedula.text().lower() if item_cedula else True
            coincide_fecha = item_fecha.text() == fecha_sel if item_fecha else True

            if coincide_cedula and coincide_fecha:
                self.tabla_asistencias.setRowHidden(row, False)
            else:
                self.tabla_asistencias.setRowHidden(row, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaAsistencias()
    ventana.show()
    sys.exit(app.exec())