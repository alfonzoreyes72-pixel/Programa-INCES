import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox, QDialog, QFormLayout, QDateEdit
)
from PyQt6.QtCore import Qt, QDate

class DialogoFormularioNovedad(QDialog):
    """Formulario emergente con calendarios flexibles (permite fechas futuras en Fecha Fin)"""
    def __init__(self, catalogo_incidencias, datos_actuales=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Novedad Operativa")
        self.setFixedSize(520, 520)
        self.setStyleSheet("background-color: #f4f6f9;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18)

        lbl_titulo = QLabel("📝 Registro y Modificación de Novedad")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #163e7a;")
        layout.addWidget(lbl_titulo)

        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e0dede;")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        def estilizar_lbl(texto):
            l = QLabel(texto)
            l.setStyleSheet("color: #163e7a; font-size: 14px; font-weight: bold;")
            return l

        estilo_calendario_popup = """
            QDateEdit {
                background-color: #f9f9f9;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 2px solid #0833a2;
            }
        """

        # Cédula
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Ingrese número de cédula...")
        self.txt_cedula.setFixedHeight(40)
        self.txt_cedula.setStyleSheet("background-color: #f9f9f9; border: 1px solid #dcdcdc; border-radius: 8px; padding-left: 10px; font-size: 14px;")
        self.txt_cedula.textChanged.connect(self.autocompletar_nombre_trabajador)
        form_layout.addRow(estilizar_lbl("Cédula Trabajador:"), self.txt_cedula)

        # Nombre del Trabajador (Autocompletado automático)
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Se completará automáticamente...")
        self.txt_nombre.setReadOnly(True)
        self.txt_nombre.setFixedHeight(40)
        self.txt_nombre.setStyleSheet("background-color: #eef2f7; border: 1px solid #dcdcdc; border-radius: 8px; padding-left: 10px; font-size: 14px; color: #555;")
        form_layout.addRow(estilizar_lbl("Nombre Trabajador:"), self.txt_nombre)

        # Incidencia
        self.cmb_incidencia = QComboBox()
        self.cmb_incidencia.addItems(catalogo_incidencias)
        self.cmb_incidencia.setFixedHeight(40)
        self.cmb_incidencia.setStyleSheet("background-color: #f9f9f9; border: 1px solid #dcdcdc; border-radius: 8px; padding-left: 10px; font-size: 14px;")
        form_layout.addRow(estilizar_lbl("Tipo de Incidencia:"), self.cmb_incidencia)

        # Fecha Inicio
        hoy = QDate.currentDate()
        self.date_inicio = QDateEdit()
        self.date_inicio.setDate(hoy)
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setMaximumDate(hoy)
        self.date_inicio.setMinimumDate(hoy.addMonths(-1))
        self.date_inicio.setFixedHeight(40)
        self.date_inicio.setStyleSheet(estilo_calendario_popup)
        form_layout.addRow(estilizar_lbl("Fecha Inicio:"), self.date_inicio)

        # Fecha Fin (Flexibilidad para vacaciones o permisos largos en el futuro)
        self.date_fin = QDateEdit()
        self.date_fin.setDate(hoy)
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setMinimumDate(hoy.addMonths(-1))
        self.date_fin.setMaximumDate(hoy.addYears(1))
        self.date_fin.setFixedHeight(40)
        self.date_fin.setStyleSheet(estilo_calendario_popup)
        form_layout.addRow(estilizar_lbl("Fecha Fin:"), self.date_fin)

        # Justificación
        self.txt_justificacion = QLineEdit()
        self.txt_justificacion.setPlaceholderText("Motivo o detalles de la novedad...")
        self.txt_justificacion.setFixedHeight(40)
        self.txt_justificacion.setStyleSheet("background-color: #f9f9f9; border: 1px solid #dcdcdc; border-radius: 8px; padding-left: 10px; font-size: 14px;")
        form_layout.addRow(estilizar_lbl("Justificación:"), self.txt_justificacion)

        layout.addWidget(form_frame)

        if datos_actuales:
            self.txt_cedula.setText(datos_actuales["cedula"])
            self.txt_nombre.setText(datos_actuales["nombre"])
            self.cmb_incidencia.setCurrentText(datos_actuales["incidencia"])
            self.date_inicio.setDate(QDate.fromString(datos_actuales["fecha_inicio"], "yyyy-MM-dd"))
            self.date_fin.setDate(QDate.fromString(datos_actuales["fecha_fin"], "yyyy-MM-dd"))
            self.txt_justificacion.setText(datos_actuales["justificacion"])

        layout_botones = QHBoxLayout()
        self.btn_guardar = QPushButton("💾 Guardar Novedad")
        self.btn_guardar.setFixedHeight(42)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 21px; font-size: 14px;")
        self.btn_guardar.clicked.connect(self.accept)
        layout_botones.addWidget(self.btn_guardar)

        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.setFixedHeight(42)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("background-color: #6c757d; color: white; font-weight: bold; border-radius: 21px; font-size: 14px;")
        self.btn_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(self.btn_cancelar)

        layout.addLayout(layout_botones)

    def autocompletar_nombre_trabajador(self):
        cedula = self.txt_cedula.text().strip()
        base_datos_ficticia = {
            "32753323": "Jesús López",
            "25489632": "María Rodríguez",
            "28765432": "Carlos Pérez"
        }
        if cedula in base_datos_ficticia:
            self.txt_nombre.setText(base_datos_ficticia[cedula])
        else:
            self.txt_nombre.setText("Trabajador no encontrado (Verificar Cédula)")

    def obtener_datos(self):
        return {
            "cedula": self.txt_cedula.text().strip(),
            "nombre": self.txt_nombre.text().strip(),
            "incidencia": self.cmb_incidencia.currentText(),
            "fecha_inicio": self.date_inicio.date().toString("yyyy-MM-dd"),
            "fecha_fin": self.date_fin.date().toString("yyyy-MM-dd"),
            "justificacion": self.txt_justificacion.text().strip()
        }