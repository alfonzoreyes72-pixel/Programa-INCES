import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QHeaderView, 
    QLabel, QTableWidgetItem, QMessageBox, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt

class DialogoGestionIncidencias(QDialog):
    """Ventana emergente (CRUD) para gestionar los tipos de incidencias"""
    def __init__(self, lista_incidencias, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Catálogo de Incidencias")
        self.setFixedSize(550, 480)
        self.setStyleSheet("background-color: #f4f6f9;")
        self.lista_incidencias = lista_incidencias

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18)

        lbl_titulo = QLabel("⚙️ Administración de Incidencias Operativas")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #163e7a;")
        layout.addWidget(lbl_titulo)

        self.tabla_incidencias = QTableWidget()
        self.tabla_incidencias.setColumnCount(2)
        self.tabla_incidencias.setHorizontalHeaderLabels(["ID", "Tipo de Incidencia"])
        self.tabla_incidencias.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_incidencias.verticalHeader().setVisible(False)
        self.tabla_incidencias.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_incidencias.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 12px;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #163e7a;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QHeaderView::section:first {
                border-top-left-radius: 12px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 12px;
            }
        """)
        layout.addWidget(self.tabla_incidencias)
        self.cargar_datos_iniciales()

        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e0dede;")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(12)

        self.txt_nombre_incidencia = QLineEdit()
        self.txt_nombre_incidencia.setPlaceholderText("Ej. Permiso por paternidad, Suspensión...")
        self.txt_nombre_incidencia.setFixedHeight(40)
        self.txt_nombre_incidencia.setStyleSheet("background-color: #f9f9f9; border: 1px solid #dcdcdc; border-radius: 8px; padding-left: 10px; font-size: 14px;")
        
        lbl_form = QLabel("<b>Nueva Incidencia:</b>")
        lbl_form.setStyleSheet("color: #163e7a; font-size: 14px;")
        form_layout.addRow(lbl_form, self.txt_nombre_incidencia)
        layout.addWidget(form_frame)

        layout_botones = QHBoxLayout()
        
        self.btn_agregar = QPushButton("➕ Agregar Incidencia")
        self.btn_agregar.setFixedHeight(42)
        self.btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 21px; font-size: 14px;")
        self.btn_agregar.clicked.connect(self.agregar_incidencia)
        layout_botones.addWidget(self.btn_agregar)

        self.btn_eliminar = QPushButton("🗑️ Eliminar Seleccionada")
        self.btn_eliminar.setFixedHeight(42)
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; border-radius: 21px; font-size: 14px;")
        self.btn_eliminar.clicked.connect(self.eliminar_incidencia)
        layout_botones.addWidget(self.btn_eliminar)

        layout.addLayout(layout_botones)

    def cargar_datos_iniciales(self):
        self.tabla_incidencias.setRowCount(0)
        for idx, inc in enumerate(self.lista_incidencias, start=1):
            row = self.tabla_incidencias.rowCount()
            self.tabla_incidencias.insertRow(row)
            self.tabla_incidencias.setItem(row, 0, QTableWidgetItem(str(idx)))
            self.tabla_incidencias.setItem(row, 1, QTableWidgetItem(inc))

    def agregar_incidencia(self):
        texto = self.txt_nombre_incidencia.text().strip()
        if not texto:
            QMessageBox.warning(self, "Advertencia", "El nombre de la incidencia no puede estar vacío.")
            return
        if texto in self.lista_incidencias:
            QMessageBox.warning(self, "Advertencia", "Esta incidencia ya se encuentra registrada.")
            return

        self.lista_incidencias.append(texto)
        self.cargar_datos_iniciales()
        self.txt_nombre_incidencia.clear()
        QMessageBox.information(self, "Éxito", "Incidencia agregada correctamente.")

    def eliminar_incidencia(self):
        fila = self.tabla_incidencias.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una incidencia de la tabla para eliminar.")
            return
        
        item = self.tabla_incidencias.item(fila, 1)
        if item:
            nombre = item.text()
            if nombre in self.lista_incidencias:
                self.lista_incidencias.remove(nombre)
            self.cargar_datos_iniciales()
            QMessageBox.information(self, "Éxito", "Incidencia eliminada correctamente.")