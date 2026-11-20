import sys
import os
import tempfile
from datetime import date, datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QFrame,
    QPushButton, QLabel, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QPointF
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QPen, QPolygonF

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

# Colores de los tipos de novedad: nombre -> (fondo, texto). Deben coincidir con ventana_operativas.py.
COLORES_TIPO = {
    "rojo": ("#fdecec", "#b71c1c"),
    "verde": ("#e6f4ea", "#1b6e3a"),
    "ambar": ("#fff3dc", "#8a5a00"),
    "azul": ("#e6f0ff", "#163e7a"),
    "morado": ("#efe9fb", "#4b2f8a"),
    "rosa": ("#fde8f1", "#9c2a5c"),
    "turquesa": ("#e0f5f2", "#0f6b5e"),
    "gris": ("#eceff3", "#4a5568"),
}


def paleta_clara():
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor("#bfbdbe"))
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
    """Dibuja la flecha del selector de fecha y la guarda como imagen temporal"""
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


def a_fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return datetime.strptime(str(valor)[:10], "%Y-%m-%d").date()


def formatear_fecha(d):
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


def formatear_cedula(valor):
    """31776780 -> 31.776.780"""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(valor)


def texto_dias(n):
    return f"{n} día" + ("" if n == 1 else "s")


# Misma estética de inputs que la ventana de registro de trabajadores
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

ESTILO_CALENDARIO = """
    QCalendarWidget QWidget { background-color: #ffffff; color: #333333; font-size: 13px; }
    QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #163e7a; border-top-left-radius: 8px; border-top-right-radius: 8px; }
    QCalendarWidget QToolButton { color: #ffffff; background-color: transparent; font-weight: bold; border: none; margin: 2px; padding: 4px; border-radius: 4px; }
    QCalendarWidget QToolButton:hover { background-color: #3b6ba3; }
    QCalendarWidget QTableView { selection-background-color: #0833a2; selection-color: #ffffff; border: 1px solid #e0dede; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }
    QCalendarWidget QAbstractItemView:enabled { color: #333333; }
"""


class VentanaFinalizarNovedad(QDialog):
    """Ventana modal para ponerle la fecha de fin a una novedad que quedó abierta"""

    def __init__(self, datos, parent=None, modo_prueba=False):
        super().__init__(parent)

        # En modo prueba la ventana funciona completa pero NO escribe en la base de datos
        self.modo_prueba = modo_prueba

        self.datos = datos
        self.id_novedad = datos.get("id_novedad")
        self.fecha_inicio = a_fecha(datos["fecha_inicio"])
        self.cedula_resultado = datos.get("cedula")

        hoy = date.today()
        fondo_tipo, texto_tipo = COLORES_TIPO.get(datos.get("color", "gris"), COLORES_TIPO["gris"])

        titulo = "Finalizar novedad"
        self.setWindowTitle(titulo + (" (modo prueba)" if modo_prueba else ""))
        self.setFixedSize(520, 540)
        self.setPalette(paleta_clara())
        self.setStyleSheet(ESTILO_VENTANA.replace("__FLECHA__", crear_icono_flecha()))

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; background: transparent;")
        layout_principal.addWidget(lbl_titulo)

        card = QFrame()
        card.setObjectName("cardContenedor")
        card.setStyleSheet("QFrame#cardContenedor { background-color: #ffffff; border-radius: 15px; }")
        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(20, 18, 20, 18)
        layout_card.setSpacing(14)

        # ---------- Datos de la novedad que se va a finalizar ----------
        info = QFrame()
        info.setObjectName("infoNovedad")
        info.setStyleSheet(f"""
            QFrame#infoNovedad {{
                background-color: #f4f6f9;
                border-radius: 10px;
                border: 1px solid #e2e6eb;
                border-left: 5px solid {texto_tipo};
            }}
        """)
        layout_info = QVBoxLayout(info)
        layout_info.setContentsMargins(15, 12, 15, 12)
        layout_info.setSpacing(6)

        sin_estilo = "border: none; background: transparent;"

        lbl_nombre = QLabel(str(datos.get("trabajador", "N/D")))
        lbl_nombre.setTextFormat(Qt.TextFormat.PlainText)
        lbl_nombre.setWordWrap(True)
        lbl_nombre.setStyleSheet(f"font-size: 15px; font-weight: bold; color: #163e7a; {sin_estilo}")
        layout_info.addWidget(lbl_nombre)

        lbl_cedula = QLabel(f"C.I. {formatear_cedula(datos.get('cedula', ''))}")
        lbl_cedula.setStyleSheet(f"font-size: 12px; font-weight: normal; color: #777777; {sin_estilo}")
        layout_info.addWidget(lbl_cedula)

        fila_tipo = QHBoxLayout()
        lbl_tipo = QLabel(str(datos.get("tipo", "N/D")))
        lbl_tipo.setTextFormat(Qt.TextFormat.PlainText)
        lbl_tipo.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {texto_tipo}; background-color: {fondo_tipo};"
            "border: none; border-radius: 11px; padding: 4px 12px;"
        )
        fila_tipo.addWidget(lbl_tipo)
        fila_tipo.addStretch()
        layout_info.addLayout(fila_tipo)

        dias = (hoy - self.fecha_inicio).days + 1
        texto_desde = f"Desde el {formatear_fecha(self.fecha_inicio)}"
        if dias > 0:
            texto_desde += f" · {texto_dias(dias)} y contando"
        lbl_desde = QLabel(texto_desde)
        lbl_desde.setStyleSheet(f"font-size: 13px; font-weight: normal; color: #333333; {sin_estilo}")
        layout_info.addWidget(lbl_desde)

        descripcion = str(datos.get("justificacion") or "").strip()
        if descripcion:
            lbl_desc = QLabel(descripcion)
            lbl_desc.setTextFormat(Qt.TextFormat.PlainText)
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet(f"font-size: 12px; font-weight: normal; color: #555555; {sin_estilo}")
            layout_info.addWidget(lbl_desc)

        layout_card.addWidget(info)

        # ---------- Fecha de fin ----------
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setFixedHeight(36)
        self.date_fin.setMinimumDate(QDate(self.fecha_inicio.year, self.fecha_inicio.month, self.fecha_inicio.day))
        propuesta = max(hoy, self.fecha_inicio)  # Por defecto, hoy
        self.date_fin.setDate(QDate(propuesta.year, propuesta.month, propuesta.day))
        self.date_fin.calendarWidget().setPalette(paleta_clara())
        self.date_fin.calendarWidget().setStyleSheet(ESTILO_CALENDARIO)
        form.addRow("Fecha de fin:", self.date_fin)
        layout_card.addLayout(form)

        lbl_ayuda = QLabel("Si eliges hoy o una fecha futura, la novedad seguirá en curso hasta que termine ese día; "
                           "después pasará a «Finalizada».")
        lbl_ayuda.setWordWrap(True)
        lbl_ayuda.setStyleSheet("font-size: 11px; font-weight: normal; color: #777777; background: transparent;")
        layout_card.addWidget(lbl_ayuda)

        layout_card.addStretch()
        layout_principal.addWidget(card)

        # ---------- Botones ----------
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(100, 36)
        self.btn_cancelar.setAutoDefault(False)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton { background-color: #e0dede; color: #333333; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #d0d0d0; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(self.btn_cancelar)

        self.btn_finalizar = QPushButton("Finalizar")
        self.btn_finalizar.setFixedSize(110, 36)
        self.btn_finalizar.setAutoDefault(False)
        self.btn_finalizar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_finalizar.setStyleSheet("""
            QPushButton { background-color: #163e7a; color: white; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #235299; }
        """)
        self.btn_finalizar.clicked.connect(self.finalizar)
        layout_botones.addWidget(self.btn_finalizar)

        layout_principal.addLayout(layout_botones)

    def finalizar(self):
        fin = self.date_fin.date().toPyDate()
        if fin < self.fecha_inicio:
            QMessageBox.warning(self, "Fecha de fin", "La fecha de fin no puede ser anterior a la fecha de inicio.")
            return

        # Modo prueba: se valida todo pero no se escribe en la base de datos
        if self.modo_prueba:
            QMessageBox.information(
                self, "Modo de prueba",
                "Las validaciones son correctas.\n\nModo de prueba: la novedad NO se modificó en la base de datos."
            )
            self.accept()
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                QMessageBox.critical(self, "Error de Conexión", "No se pudo conectar con la base de datos MySQL.")
                return

            cursor = conexion.cursor()
            # Solo se finaliza si sigue abierta (por si otro usuario ya la cerró)
            cursor.execute(
                "UPDATE novedades_operativas SET fecha_fin = %s WHERE id_novedad = %s AND fecha_fin IS NULL",
                (fin.strftime("%Y-%m-%d"), self.id_novedad)
            )
            if cursor.rowcount == 0:
                conexion.rollback()
                cursor.close()
                QMessageBox.warning(
                    self, "Novedad no disponible",
                    "Esta novedad ya no está abierta: es posible que otra persona ya la haya finalizado."
                )
                self.reject()
                return

            conexion.commit()
            cursor.close()
            QMessageBox.information(self, "Éxito", "Novedad finalizada correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(paleta_clara())
    datos_prueba = {
        "id_novedad": 0,
        "cedula": 12345678,
        "trabajador": "María Pérez (datos de prueba)",
        "tipo": "Reposo médico",
        "color": "rojo",
        "fecha_inicio": date.today(),
        "fecha_fin": None,
        "justificacion": "Reposo por 15 días indicado por su médico",
    }
    ventana = VentanaFinalizarNovedad(datos_prueba, modo_prueba=True)
    ventana.exec()
    sys.exit(0)