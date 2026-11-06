import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QHeaderView, QScrollArea,
    QLabel, QTableWidgetItem, QMessageBox, QComboBox, QDialog
)
from PyQt6.QtCore import Qt, QDate

from .GestionIncidencias import DialogoGestionIncidencias
from .Gestionnovedades import DialogoFormularioNovedad


class VentanaOperativas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.catalogo_incidencias = [
            "Permiso Médico", 
            "Falta Injustificada", 
            "Vacaciones", 
            "Retraso Justificado", 
            "Comisión de Servicio"
        ]

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(0)

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

        contenedor_scroll = QWidget()
        contenedor_scroll.setStyleSheet("background-color: transparent;")
        layout_contenedor = QVBoxLayout(contenedor_scroll)
        layout_contenedor.setContentsMargins(0, 0, 0, 0)

        self.panel_principal = QFrame()
        self.panel_principal.setObjectName("panelOperativas")
        self.panel_principal.setStyleSheet("""
            QFrame#panelOperativas {
                background-color: #ffffff;
                border-radius: 20px;
            }
        """)

        layout_panel = QVBoxLayout(self.panel_principal)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(15)

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

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por cédula de trabajador...")
        self.txt_buscar.setFixedHeight(38)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 19px;
                padding-left: 15px;
                padding-right: 15px;
                color: black;
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #0833a2;
            }
        """)
        layout_franja.addWidget(self.txt_buscar, stretch=1)

        self.cmb_incidencia = QComboBox()
        self.actualizar_combo_incidencias()
        self.cmb_incidencia.setFixedHeight(38)
        self.cmb_incidencia.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 10px;
                padding-left: 10px;
                padding-right: 10px;
                color: black;
                font-size: 13px;
                font-weight: bold;
            }
            QComboBox:focus {
                border: 2px solid #0833a2;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 0px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        layout_franja.addWidget(self.cmb_incidencia)

        self.btn_gestionar_incidencias = QPushButton("Incidencias")
        self.btn_gestionar_incidencias.setFixedSize(115, 38)
        self.btn_gestionar_incidencias.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_gestionar_incidencias.setStyleSheet("""
            QPushButton {
                background-color: #163e7a;
                color: white;
                border-radius: 19px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #235299;
            }
        """)
        self.btn_gestionar_incidencias.clicked.connect(self.abrir_gestion_incidencias)
        layout_franja.addWidget(self.btn_gestionar_incidencias)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setFixedSize(85, 38)
        self.btn_buscar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar.setStyleSheet("""
            QPushButton {
                background-color: #0833a2;
                color: white;
                border-radius: 19px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3150ff;
            }
        """)
        self.btn_buscar.clicked.connect(self.filtrar_novedades)
        layout_franja.addWidget(self.btn_buscar)

        self.btn_agregar = QPushButton("+ Novedad")
        self.btn_agregar.setFixedSize(105, 38)
        self.btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 19px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_agregar.clicked.connect(self.agregar_novedad)
        layout_franja.addWidget(self.btn_agregar)

        self.btn_modificar = QPushButton("Modificar")
        self.btn_modificar.setFixedSize(110, 38)
        self.btn_modificar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_modificar.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #333333;
                border-radius: 19px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self.btn_modificar.clicked.connect(self.modificar_novedad)
        layout_franja.addWidget(self.btn_modificar)

        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setFixedSize(100, 38)
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 19px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.btn_eliminar.clicked.connect(self.eliminar_novedad)
        layout_franja.addWidget(self.btn_eliminar)

        layout_panel.addWidget(self.franja_superior)

        self.tabla_operativas = QTableWidget()
        columnas = ["ID", "Cédula", "Nombre Trabajador", "Incidencia", "Inicio", "Fin", "Justificación"]
        self.tabla_operativas.setColumnCount(len(columnas))
        self.tabla_operativas.setHorizontalHeaderLabels(columnas)
        
        self.tabla_operativas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_operativas.verticalHeader().setVisible(False)
        self.tabla_operativas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_operativas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.tabla_operativas.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabla_operativas.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tabla_operativas.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0dede;
                border-radius: 12px;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #163e7a;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
            }
            QHeaderView::section:first {
                border-top-left-radius: 12px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #e6f0ff;
                color: #0833a2;
            }
        """)

        self.tabla_operativas.setRowCount(0)
        layout_panel.addWidget(self.tabla_operativas)

        layout_contenedor.addWidget(self.panel_principal)
        self.scroll_area.setWidget(contenedor_scroll)
        layout_principal.addWidget(self.scroll_area)

    def actualizar_combo_incidencias(self):
        self.cmb_incidencia.clear()
        self.cmb_incidencia.addItem("Todas las Incidencias")
        self.cmb_incidencia.addItems(self.catalogo_incidencias)

    def abrir_gestion_incidencias(self):
        dialogo = DialogoGestionIncidencias(self.catalogo_incidencias, self)
        dialogo.exec()
        self.actualizar_combo_incidencias()

    def agregar_novedad(self):
        dialogo = DialogoFormularioNovedad(self.catalogo_incidencias, parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            if not datos["cedula"]:
                QMessageBox.warning(self, "Advertencia", "La cédula del trabajador es obligatoria.")
                return

            id_nov = str(self.tabla_operativas.rowCount() + 1)
            row_pos = self.tabla_operativas.rowCount()
            self.tabla_operativas.insertRow(row_pos)
            self.tabla_operativas.setItem(row_pos, 0, QTableWidgetItem(id_nov))
            self.tabla_operativas.setItem(row_pos, 1, QTableWidgetItem(datos["cedula"]))
            self.tabla_operativas.setItem(row_pos, 2, QTableWidgetItem(datos["nombre"]))
            self.tabla_operativas.setItem(row_pos, 3, QTableWidgetItem(datos["incidencia"]))
            self.tabla_operativas.setItem(row_pos, 4, QTableWidgetItem(datos["fecha_inicio"]))
            self.tabla_operativas.setItem(row_pos, 5, QTableWidgetItem(datos["fecha_fin"]))
            self.tabla_operativas.setItem(row_pos, 6, QTableWidgetItem(datos["justificacion"]))

            QMessageBox.information(self, "Éxito", "Novedad operativa registrada correctamente.")

    def modificar_novedad(self):
        fila = self.tabla_operativas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una novedad de la tabla para modificar.")
            return

        datos_actuales = {
            "cedula": self.tabla_operativas.item(fila, 1).text(),
            "nombre": self.tabla_operativas.item(fila, 2).text(),
            "incidencia": self.tabla_operativas.item(fila, 3).text(),
            "fecha_inicio": self.tabla_operativas.item(fila, 4).text(),
            "fecha_fin": self.tabla_operativas.item(fila, 5).text(),
            "justificacion": self.tabla_operativas.item(fila, 6).text()
        }

        dialogo = DialogoFormularioNovedad(self.catalogo_incidencias, datos_actuales=datos_actuales, parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            nuevos_datos = dialogo.obtener_datos()
            if not nuevos_datos["cedula"]:
                QMessageBox.warning(self, "Advertencia", "La cédula del trabajador es obligatoria.")
                return

            self.tabla_operativas.setItem(fila, 1, QTableWidgetItem(nuevos_datos["cedula"]))
            self.tabla_operativas.setItem(fila, 2, QTableWidgetItem(nuevos_datos["nombre"]))
            self.tabla_operativas.setItem(fila, 3, QTableWidgetItem(nuevos_datos["incidencia"]))
            self.tabla_operativas.setItem(fila, 4, QTableWidgetItem(nuevos_datos["fecha_inicio"]))
            self.tabla_operativas.setItem(fila, 5, QTableWidgetItem(nuevos_datos["fecha_fin"]))
            self.tabla_operativas.setItem(fila, 6, QTableWidgetItem(nuevos_datos["justificacion"]))

            QMessageBox.information(self, "Éxito", "Novedad operativa actualizada correctamente.")

    def eliminar_novedad(self):
        fila_seleccionada = self.tabla_operativas.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione el registro de novedad que desea eliminar en la tabla.")
            return

        confirmacion = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de eliminar esta novedad operativa del sistema?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirmacion == QMessageBox.StandardButton.Yes:
            self.tabla_operativas.removeRow(fila_seleccionada)
            QMessageBox.information(self, "Éxito", "El registro de novedad fue eliminado satisfactoriamente.")

    def filtrar_novedades(self):
        cedula = self.txt_buscar.text().strip().lower()
        incidencia_filtro = self.cmb_incidencia.currentText()

        for row in range(self.tabla_operativas.rowCount()):
            item_cedula = self.tabla_operativas.item(row, 1)
            item_incidencia = self.tabla_operativas.item(row, 3)

            coincide_cedula = cedula in item_cedula.text().lower() if item_cedula else True
            coincide_incidencia = (incidencia_filtro == "Todas las Incidencias" or item_incidencia.text() == incidencia_filtro) if item_incidencia else True

            if coincide_cedula and coincide_incidencia:
                self.tabla_operativas.setRowHidden(row, False)
            else:
                self.tabla_operativas.setRowHidden(row, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaOperativas()
    ventana.show()
    sys.exit(app.exec())