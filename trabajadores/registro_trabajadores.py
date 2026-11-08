import sys
import tempfile
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFormLayout,
    QComboBox, QDateEdit, QWidget, QFrame, QListView
)
from PyQt6.QtCore import Qt, QDate, QPointF
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QPen, QPolygonF


def paleta_clara():
    """Paleta clara forzada para ignorar el modo oscuro del sistema operativo."""
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor("#f4f6f9"))
    p.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))
    p.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor("#f4f6f9"))
    p.setColor(QPalette.ColorRole.Text, QColor("#333333"))
    p.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.ButtonText, QColor("#333333"))
    p.setColor(QPalette.ColorRole.Highlight, QColor("#e6f0ff"))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#0833a2"))
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#999999"))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor("#333333"))
    return p


def crear_icono_flecha():
    ruta = Path(tempfile.gettempdir()) / "inces_flecha_abajo.png"
    pm = QPixmap(12, 12)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    lapiz = QPen(QColor("#8a93a3"))
    lapiz.setWidthF(1.6)
    lapiz.setCapStyle(Qt.PenCapStyle.RoundCap)
    lapiz.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(lapiz)
    painter.drawPolyline(QPolygonF([
        QPointF(2.5, 4.2), QPointF(6.0, 7.8), QPointF(9.5, 4.2)
    ]))
    painter.end()
    pm.save(str(ruta), "PNG")
    return ruta.as_posix()


ESTILO_VENTANA = """
    QDialog {
        background-color: #bfbdbe;
    }
    QLabel {
        font-size: 13px;
        font-weight: bold;
        color: #2c2c2c;
        background: transparent;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 13px;
        color: #333333;
    }
    QLineEdit:focus {
        border: 2px solid #0833a2;
    }
    QLineEdit:read-only {
        background-color: #f0f0f0;
        color: #666666;
    }

    /* ---- QComboBox ---- */
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 13px;
        color: #333333;
    }
    QComboBox:focus {
        border: 2px solid #0833a2;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 28px;
        border: none;
        background: transparent;
    }
    QComboBox::down-arrow {
        image: url(__FLECHA__);
        width: 12px;
        height: 12px;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #dcdcdc;
        outline: none;
        selection-background-color: #e6f0ff;
        selection-color: #0833a2;
    }
    QComboBox QAbstractItemView::item {
        min-height: 28px;
        padding-left: 8px;
        color: #333333;
        background-color: #ffffff;
    }
    QComboBox QAbstractItemView::item:selected,
    QComboBox QAbstractItemView::item:hover {
        background-color: #e6f0ff;
        color: #0833a2;
    }

    /* ---- QDateEdit ---- */
    QDateEdit {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding-left: 10px;
        padding-right: 10px;
        color: #333333;
        font-size: 13px;
    }
    QDateEdit:focus {
        border: 2px solid #0833a2;
    }
    QDateEdit::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 28px;
        border: none;
        background: transparent;
    }
    QDateEdit::down-arrow {
        image: url(__FLECHA__);
        width: 12px;
        height: 12px;
    }
"""

ESTILO_SCROLL = """
    QScrollArea {
        border: none;
        background: transparent;
    }
    QScrollArea > QWidget {
        background: transparent;
    }
    QScrollArea > QWidget > QWidget {
        background: transparent;
    }

    /* Barra de desplazamiento vertical: delgada, redondeada y discreta */
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
        margin: 2px 0px 2px 0px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background: #d3d8e0;
        border-radius: 4px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background: #aeb6c2;
    }
    QScrollBar::handle:vertical:pressed {
        background: #8a93a3;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
        background: none;
        border: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: transparent;
    }
"""


class RegistroTrabajadores(QDialog):
    """Ventana modal para el registro y modificación de trabajadores con diseño unificado"""
    def __init__(self, titulo="Registrar Trabajador", datos=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setFixedSize(520, 620)
        self.setPalette(paleta_clara())

        self.setStyleSheet(ESTILO_VENTANA.replace("__FLECHA__", crear_icono_flecha()))

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        # Título principal de la ventana modal
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; background: transparent;")
        layout_principal.addWidget(lbl_titulo)

        # Tarjeta contenedora blanca principal
        card_contenedor = QFrame()
        card_contenedor.setObjectName("cardContenedor")
        card_contenedor.setStyleSheet("""
            QFrame#cardContenedor {
                background-color: #ffffff;
                border-radius: 15px;
            }
        """)
        layout_card = QVBoxLayout(card_contenedor)
        layout_card.setContentsMargins(20, 20, 12, 20)
        layout_card.setSpacing(15)

        # Área de formulario con desplazamiento vertical interno
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(ESTILO_SCROLL)

        contenedor_form = QWidget()
        contenedor_form.setObjectName("contenedorForm")
        contenedor_form.setStyleSheet("QWidget#contenedorForm { background: transparent; }")
        form_layout = QFormLayout(contenedor_form)
        form_layout.setContentsMargins(0, 0, 10, 0)
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # Campos de entrada estructurados según la base de datos
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Ej. 18783456")

        self.txt_nombres = QLineEdit()
        self.txt_nombres.setPlaceholderText("Nombres completos")

        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setPlaceholderText("Apellidos completos")

        self.date_nacimiento = QDateEdit()
        self.date_nacimiento.setCalendarPopup(True)
        self.date_nacimiento.setDate(QDate(1990, 1, 1))
        self.date_nacimiento.setFixedHeight(36)

        calendario = self.date_nacimiento.calendarWidget()
        calendario.setPalette(paleta_clara())
        calendario.setStyleSheet("""
            QCalendarWidget QWidget {
                background-color: #ffffff;
                color: #333333;
                font-size: 13px;
            }
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
            QCalendarWidget QTableView {
                selection-background-color: #0833a2;
                selection-color: #ffffff;
                border: 1px solid #e0dede;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #333333;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #bbbbbb;
            }
        """)

        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Ej. 04141234567")

        self.txt_correo = QLineEdit()
        self.txt_correo.setPlaceholderText("correo@inces.gob.ve")

        self.cmb_sexo = QComboBox()
        self.cmb_sexo.addItems(["Masculino", "Femenino", "Otro"])

        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("Dirección de habitación")

        self.cmb_departamento = QComboBox()
        self.cmb_departamento.addItems(["Tecnología", "Recursos Humanos", "Administración", "Formación"])

        self.cmb_estado_laboral = QComboBox()
        self.cmb_estado_laboral.addItems(["Fijo", "Temporal"])

        self.cmb_centro_votacion = QComboBox()
        self.cmb_centro_votacion.addItems([
            "Liceo Bolivariano Monagas",
            "Escuela Técnica Luis Caballero Mejías",
            "U.E. Francisco de Miranda"
        ])

        for combo in (self.cmb_sexo, self.cmb_departamento,
                      self.cmb_estado_laboral, self.cmb_centro_votacion):
            combo.setView(QListView())
            combo.setFixedHeight(36)

        # Añadir al formulario
        form_layout.addRow("Cédula:", self.txt_cedula)
        form_layout.addRow("Nombres:", self.txt_nombres)
        form_layout.addRow("Apellidos:", self.txt_apellidos)
        form_layout.addRow("Fecha Nacimiento:", self.date_nacimiento)
        form_layout.addRow("Teléfono:", self.txt_telefono)
        form_layout.addRow("Correo:", self.txt_correo)
        form_layout.addRow("Sexo:", self.cmb_sexo)
        form_layout.addRow("Dirección:", self.txt_direccion)
        form_layout.addRow("Departamento:", self.cmb_departamento)
        form_layout.addRow("Estado Laboral:", self.cmb_estado_laboral)
        form_layout.addRow("Centro Votación:", self.cmb_centro_votacion)

        scroll.setWidget(contenedor_form)
        layout_card.addWidget(scroll)
        layout_principal.addWidget(card_contenedor)

        # Botones inferiores de acción
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(100, 36)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
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
        self.btn_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(self.btn_cancelar)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFixedSize(100, 36)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
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
        self.btn_guardar.clicked.connect(self.accept)
        layout_botones.addWidget(self.btn_guardar)

        layout_principal.addLayout(layout_botones)

        # Cargar datos si se trata de una modificación
        if datos:
            self.txt_cedula.setText(str(datos.get("cedula", "")))
            self.txt_cedula.setReadOnly(True)
            nombres_split = datos.get("nombre", "").split(" ", 1)
            self.txt_nombres.setText(nombres_split[0] if len(nombres_split) > 0 else "")
            self.txt_apellidos.setText(nombres_split[1] if len(nombres_split) > 1 else "")
            self.txt_telefono.setText(datos.get("telefono", ""))
            self.txt_correo.setText(datos.get("correo", ""))
            self.txt_direccion.setText(datos.get("direccion", ""))

            self._seleccionar(self.cmb_sexo, datos.get("sexo"))
            self._seleccionar(self.cmb_departamento, datos.get("departamento"))
            self._seleccionar(self.cmb_estado_laboral, datos.get("estado_laboral"))
            self._seleccionar(self.cmb_centro_votacion, datos.get("centro_votacion"))

            fecha = datos.get("fecha_nacimiento")
            if isinstance(fecha, QDate):
                self.date_nacimiento.setDate(fecha)
            elif isinstance(fecha, str) and fecha:
                f = QDate.fromString(fecha, "yyyy-MM-dd")
                if f.isValid():
                    self.date_nacimiento.setDate(f)

    @staticmethod
    def _seleccionar(combo, texto):
        if not texto:
            return
        idx = combo.findText(str(texto))
        if idx >= 0:
            combo.setCurrentIndex(idx)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(paleta_clara())
    ventana = RegistroTrabajadores()
    ventana.show()
    sys.exit(app.exec())