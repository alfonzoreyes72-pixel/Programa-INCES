import sys
import os
import tempfile
import unicodedata
from datetime import date
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QFrame,
    QLineEdit, QPlainTextEdit, QComboBox, QListView, QPushButton, QLabel,
    QDateEdit, QCheckBox, QButtonGroup, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QPointF
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QPen, QPolygonF

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


MAX_DESCRIPCION = 255
MAX_TIPO = 100

# Colores disponibles para los tipos de novedad: nombre -> (fondo, texto).
# Deben coincidir con los de ventana_operativas.py.
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
    """Dibuja la flecha de los combos y la guarda como imagen temporal"""
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


def normalizar(texto):
    """Minúsculas, sin tildes y sin espacios repetidos"""
    texto = unicodedata.normalize("NFD", " ".join(str(texto).split()))
    return "".join(c for c in texto if unicodedata.category(c) != "Mn").lower()


def limpiar(texto):
    return " ".join(str(texto).split())


def formatear_cedula(valor):
    """31776780 -> 31.776.780"""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(valor)


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
    QLineEdit, QPlainTextEdit {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 13px;
        color: #333333;
    }
    QLineEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #0833a2;
    }
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
    QDateEdit:disabled {
        background-color: #f0f0f0;
        color: #999999;
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
    QCheckBox {
        font-size: 13px;
        color: #333333;
        background: transparent;
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

ESTILO_BOTON_CANCELAR = """
    QPushButton { background-color: #e0dede; color: #333333; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
    QPushButton:hover { background-color: #d0d0d0; }
"""

ESTILO_BOTON_GUARDAR = """
    QPushButton { background-color: #163e7a; color: white; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
    QPushButton:hover { background-color: #235299; }
"""


def _consultar(sql, params=()):
    try:
        db = GestorBD()
        conexion = db.obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(sql, params)
            filas = cursor.fetchall()
            cursor.close()
            return filas
    except Exception as e:
        print(f"Error al consultar datos de las novedades operativas: {e}")
    return []


class DialogoNuevoTipo(QDialog):
    """Mini ventana para crear un tipo de novedad nuevo, con su color"""

    def __init__(self, parent=None, colores_usados=(), modo_prueba=False):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.modo_prueba = modo_prueba
        self.id_tipo = None

        self.setWindowTitle("Agregar tipo de novedad")
        self.setFixedSize(440, 330)
        self.setPalette(paleta_clara())
        self.setStyleSheet(ESTILO_VENTANA.replace("__FLECHA__", crear_icono_flecha()))

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        lbl_titulo = QLabel("Agregar tipo de novedad")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; background: transparent;")
        layout_principal.addWidget(lbl_titulo)

        card = QFrame()
        card.setObjectName("cardContenedor")
        card.setStyleSheet("QFrame#cardContenedor { background-color: #ffffff; border-radius: 15px; }")
        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(20, 18, 20, 18)
        layout_card.setSpacing(12)

        lbl_nombre = QLabel("Nombre:")
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej. Licencia de maternidad")
        self.txt_nombre.setMaxLength(MAX_TIPO)
        self.txt_nombre.setFixedHeight(36)
        layout_card.addWidget(lbl_nombre)
        layout_card.addWidget(self.txt_nombre)

        lbl_color = QLabel("Color:")
        layout_card.addWidget(lbl_color)

        fila_colores = QHBoxLayout()
        fila_colores.setSpacing(8)
        self.grupo_colores = QButtonGroup(self)
        self.grupo_colores.setExclusive(True)
        self.nombres_colores = list(COLORES_TIPO.keys())

        sugerido = next((c for c in self.nombres_colores if c not in colores_usados), self.nombres_colores[0])
        for indice, nombre_color in enumerate(self.nombres_colores):
            _, texto = COLORES_TIPO[nombre_color]
            boton = QPushButton()
            boton.setCheckable(True)
            boton.setAutoDefault(False)
            boton.setFixedSize(32, 32)
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.setToolTip(nombre_color.capitalize())
            boton.setStyleSheet(f"""
                QPushButton {{
                    background-color: {texto};
                    border: 3px solid #ffffff;
                    border-radius: 16px;
                }}
                QPushButton:hover {{ border: 3px solid #d0d7de; }}
                QPushButton:checked {{ border: 3px solid #2c2c2c; }}
            """)
            boton.setChecked(nombre_color == sugerido)
            self.grupo_colores.addButton(boton, indice)
            fila_colores.addWidget(boton)
        fila_colores.addStretch()
        layout_card.addLayout(fila_colores)

        layout_card.addStretch()
        layout_principal.addWidget(card)

        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedSize(100, 36)
        btn_cancelar.setAutoDefault(False)
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setStyleSheet(ESTILO_BOTON_CANCELAR)
        btn_cancelar.clicked.connect(self.reject)
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setFixedSize(100, 36)
        btn_guardar.setAutoDefault(False)
        btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guardar.setStyleSheet(ESTILO_BOTON_GUARDAR)
        btn_guardar.clicked.connect(self.guardar_tipo)
        layout_botones.addWidget(btn_cancelar)
        layout_botones.addWidget(btn_guardar)
        layout_principal.addLayout(layout_botones)

    def guardar_tipo(self):
        nombre = limpiar(self.txt_nombre.text())
        if not nombre:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingrese el nombre del tipo de novedad.")
            return

        indice = self.grupo_colores.checkedId()
        color = self.nombres_colores[indice] if indice >= 0 else "gris"

        if self.modo_prueba:
            QMessageBox.information(self, "Modo de prueba", "El tipo NO se guardó en la base de datos.")
            self.accept()
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                QMessageBox.critical(self, "Error de Conexión", "No se pudo conectar con la base de datos MySQL.")
                return
            cursor = conexion.cursor()
            cursor.execute("SELECT id_incidencia FROM incidencias WHERE tipo_incidencia = %s", (nombre,))
            if cursor.fetchone():
                cursor.close()
                QMessageBox.warning(self, "Tipo existente", "Ya existe un tipo de novedad con ese nombre.")
                return
            cursor.execute("INSERT INTO incidencias (tipo_incidencia, color) VALUES (%s, %s)", (nombre, color))
            self.id_tipo = cursor.lastrowid
            conexion.commit()
            cursor.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar:\n{e}")


class VentanaRegistroOperativa(QDialog):
    """Ventana modal para registrar una novedad operativa (reposo, vacaciones, permiso, etc.)"""

    def __init__(self, parent=None, modo_prueba=False):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.modo_prueba = modo_prueba
        self.cedula_resultado = None

        self.trabajadores = {}
        self.colores_usados = []

        titulo = "Nueva novedad operativa"
        self.setWindowTitle(titulo + (" (modo prueba)" if modo_prueba else ""))
        self.setFixedSize(540, 700)
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
        layout_card.setSpacing(12)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # ---------- Trabajador (se busca escribiendo) ----------
        self.cmb_trabajador = QComboBox()
        self.cmb_trabajador.setEditable(True)
        self.cmb_trabajador.setView(QListView())
        self.cmb_trabajador.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.cmb_trabajador.setFixedHeight(36)
        editor = self.cmb_trabajador.lineEdit()
        editor.setPlaceholderText("Escriba el nombre o la cédula")
        editor.setStyleSheet(
            "QLineEdit { border: none; background: transparent; padding: 0px; font-size: 13px; color: #333333; }"
            "QLineEdit:focus { border: none; }"
        )
        completador = self.cmb_trabajador.completer()
        completador.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completador.setFilterMode(Qt.MatchFlag.MatchContains)
        # Crear explícitamente la vista emergente antes de aplicarle estilos.
        # popup() puede devolver None si la vista aún no ha sido creada.
        completador.setPopup(QListView())
        completador.popup().setStyleSheet("""
            QListView { background-color: #ffffff; color: #333333; border: 1px solid #dcdcdc; outline: none;
                        font-size: 13px; selection-background-color: #e6f0ff; selection-color: #0833a2; }
            QListView::item { min-height: 28px; padding-left: 8px; }
        """)
        form.addRow("Trabajador:", self.cmb_trabajador)

        # ---------- Tipo de novedad ----------
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.setView(QListView())
        self.cmb_tipo.setFixedHeight(36)
        self.btn_nuevo_tipo = QPushButton("＋ Agregar tipo")
        self.btn_nuevo_tipo.setFlat(True)
        self.btn_nuevo_tipo.setAutoDefault(False)
        self.btn_nuevo_tipo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nuevo_tipo.setStyleSheet("""
            QPushButton { color: #0833a2; font-size: 12px; font-weight: bold; border: none; background: transparent; padding: 0px 4px; }
            QPushButton:hover { color: #3150ff; }
        """)
        self.btn_nuevo_tipo.clicked.connect(self.agregar_tipo)
        fila_tipo = QHBoxLayout()
        fila_tipo.setSpacing(8)
        fila_tipo.addWidget(self.cmb_tipo, stretch=1)
        fila_tipo.addWidget(self.btn_nuevo_tipo)
        form.addRow("Tipo de novedad:", fila_tipo)

        # ---------- Fechas ----------
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate())
        self.date_inicio.setFixedHeight(36)
        self.date_inicio.calendarWidget().setPalette(paleta_clara())
        self.date_inicio.calendarWidget().setStyleSheet(ESTILO_CALENDARIO)
        form.addRow("Fecha de inicio:", self.date_inicio)

        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setFixedHeight(36)
        self.date_fin.calendarWidget().setPalette(paleta_clara())
        self.date_fin.calendarWidget().setStyleSheet(ESTILO_CALENDARIO)
        form.addRow("Fecha de fin:", self.date_fin)

        self.chk_sin_fin = QCheckBox("Aún no tiene fecha de fin")
        self.chk_sin_fin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_sin_fin.setChecked(True)
        form.addRow("", self.chk_sin_fin)

        # ---------- Descripción ----------
        self.txt_descripcion = QPlainTextEdit()
        self.txt_descripcion.setPlaceholderText("Ej. Reposo por 15 días indicado por su médico")
        self.txt_descripcion.setFixedHeight(90)
        self.txt_descripcion.setTabChangesFocus(True)
        self.txt_descripcion.textChanged.connect(self.al_cambiar_descripcion)
        lbl_descripcion = QLabel("Descripción:")
        lbl_descripcion.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lbl_descripcion.setStyleSheet("padding-top: 8px;")
        form.addRow(lbl_descripcion, self.txt_descripcion)

        self.lbl_contador = QLabel(f"0/{MAX_DESCRIPCION}")
        self.lbl_contador.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_contador.setStyleSheet("font-size: 11px; font-weight: normal; color: #999999; background: transparent;")
        form.addRow("", self.lbl_contador)

        layout_card.addLayout(form)

        lbl_ayuda = QLabel("Si todavía no se sabe cuándo termina (por ejemplo, un reposo), deja marcada la casilla: "
                           "podrás poner la fecha de fin más adelante desde la lista de novedades.")
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
        self.btn_cancelar.setDefault(False)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet(ESTILO_BOTON_CANCELAR)
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFixedSize(100, 36)
        self.btn_guardar.setAutoDefault(False)
        self.btn_guardar.setDefault(False)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet(ESTILO_BOTON_GUARDAR)
        self.btn_guardar.clicked.connect(self.guardar_novedad)
        layout_botones.addWidget(self.btn_cancelar)
        layout_botones.addWidget(self.btn_guardar)
        layout_principal.addLayout(layout_botones)

        # Datos y señales
        self.cargar_trabajadores()
        self.cargar_tipos()
        self.actualizar_fecha_fin()
        self.date_inicio.dateChanged.connect(self.al_cambiar_inicio)
        self.chk_sin_fin.toggled.connect(self.actualizar_fecha_fin)

    # ==================== DATOS ====================
    def cargar_trabajadores(self):
        """Lista de trabajadores para escribir y elegir (los retirados no pueden tener novedades)"""
        filas = _consultar("""
            SELECT t.cedula_trabajador, t.nombres, t.apellidos, el.descripcion_estado AS estado_laboral
            FROM trabajadores t
            LEFT JOIN estados_laborales el ON t.id_estado_laboral_fk = el.id_estado_laboral
            ORDER BY t.nombres, t.apellidos
        """)
        self.trabajadores = {}
        self.cmb_trabajador.blockSignals(True)
        self.cmb_trabajador.clear()
        for fila in filas:
            if "retirado" in str(fila.get("estado_laboral") or "").lower():
                continue
            texto = f"{fila['nombres']} {fila['apellidos']} — C.I. {formatear_cedula(fila['cedula_trabajador'])}"
            self.cmb_trabajador.addItem(texto, fila["cedula_trabajador"])
            self.trabajadores[normalizar(texto)] = fila["cedula_trabajador"]
        self.cmb_trabajador.setCurrentIndex(-1)
        self.cmb_trabajador.setEditText("")
        self.cmb_trabajador.blockSignals(False)

    def cargar_tipos(self, seleccionar_id=None):
        filas = _consultar("SELECT id_incidencia, tipo_incidencia, COALESCE(color, 'gris') AS color FROM incidencias ORDER BY tipo_incidencia")
        self.colores_usados = [f["color"] for f in filas]
        self.cmb_tipo.clear()
        for fila in filas:
            self.cmb_tipo.addItem(fila["tipo_incidencia"], fila["id_incidencia"])
        indice = self.cmb_tipo.findData(seleccionar_id) if seleccionar_id is not None else -1
        self.cmb_tipo.setCurrentIndex(indice)

    def agregar_tipo(self):
        dialogo = DialogoNuevoTipo(self, self.colores_usados, self.modo_prueba)
        if dialogo.exec() and dialogo.id_tipo is not None:
            self.cargar_tipos(seleccionar_id=dialogo.id_tipo)

    # ==================== FECHAS Y DESCRIPCIÓN ====================
    def actualizar_fecha_fin(self, *_):
        """Con la casilla marcada la fecha de fin queda por definir; si no, nunca puede ser anterior al inicio"""
        if self.chk_sin_fin.isChecked():
            self.date_fin.setMinimumDate(QDate(1900, 1, 1))
            self.date_fin.setSpecialValueText("Por definir")
            self.date_fin.setDate(self.date_fin.minimumDate())
            self.date_fin.setEnabled(False)
        else:
            inicio = self.date_inicio.date()
            self.date_fin.setSpecialValueText("")
            self.date_fin.setMinimumDate(inicio)
            self.date_fin.setDate(inicio)
            self.date_fin.setEnabled(True)

    def al_cambiar_inicio(self, nueva_fecha):
        if not self.chk_sin_fin.isChecked():
            self.date_fin.setMinimumDate(nueva_fecha)

    def al_cambiar_descripcion(self):
        texto = self.txt_descripcion.toPlainText()
        if len(texto) > MAX_DESCRIPCION:
            texto = texto[:MAX_DESCRIPCION]
            self.txt_descripcion.blockSignals(True)
            self.txt_descripcion.setPlainText(texto)
            self.txt_descripcion.blockSignals(False)
            cursor = self.txt_descripcion.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.txt_descripcion.setTextCursor(cursor)
        self.lbl_contador.setText(f"{len(texto)}/{MAX_DESCRIPCION}")

    # ==================== GUARDADO ====================
    def guardar_novedad(self):
        cedula = self.trabajadores.get(normalizar(self.cmb_trabajador.currentText()))
        if cedula is None:
            QMessageBox.warning(self, "Trabajador", "Por favor, escriba y elija un trabajador de la lista.")
            return

        id_tipo = self.cmb_tipo.currentData()
        if id_tipo is None:
            QMessageBox.warning(self, "Tipo de novedad", "Por favor, seleccione el tipo de novedad.")
            return

        inicio = self.date_inicio.date().toPyDate()
        fin = None if self.chk_sin_fin.isChecked() else self.date_fin.date().toPyDate()
        if fin is not None and fin < inicio:
            QMessageBox.warning(self, "Fechas", "La fecha de fin no puede ser anterior a la fecha de inicio.")
            return

        descripcion = limpiar(self.txt_descripcion.toPlainText())
        if not descripcion:
            QMessageBox.warning(self, "Campo vacío", "Por favor, escriba una descripción de la novedad.")
            return

        if self.modo_prueba:
            QMessageBox.information(
                self, "Modo de prueba",
                "Las validaciones son correctas.\n\nModo de prueba: la novedad NO se guardó en la base de datos."
            )
            self.cedula_resultado = cedula
            self.accept()
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                QMessageBox.critical(self, "Error de Conexión", "No se pudo conectar con la base de datos MySQL.")
                return

            cursor = conexion.cursor(dictionary=True)

            cursor.execute("""
                SELECT i.tipo_incidencia AS tipo, n.fecha_inicio, n.fecha_fin
                FROM novedades_operativas n
                JOIN incidencias i ON n.id_incidencia_fk = i.id_incidencia
                WHERE n.cedula_trabajador_fk = %s
                  AND n.fecha_inicio <= %s
                  AND (n.fecha_fin IS NULL OR n.fecha_fin >= %s)
            """, (cedula, (fin or date(9999, 12, 31)).strftime("%Y-%m-%d"), inicio.strftime("%Y-%m-%d")))
            solapadas = cursor.fetchall()
            if solapadas:
                detalle = "\n".join(
                    f"• {s['tipo']}: {s['fecha_inicio'].strftime('%d/%m/%Y')} → "
                    + (s['fecha_fin'].strftime('%d/%m/%Y') if s['fecha_fin'] else "sin fecha de fin")
                    for s in solapadas[:3]
                )
                respuesta = QMessageBox.question(
                    self, "Novedades que se solapan",
                    "Este trabajador ya tiene una novedad en esas fechas:\n\n" + detalle +
                    "\n\n¿Deseas registrar esta novedad de todas formas?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if respuesta != QMessageBox.StandardButton.Yes:
                    cursor.close()
                    return

            cursor.execute("""
                INSERT INTO novedades_operativas
                    (cedula_trabajador_fk, id_incidencia_fk, fecha_inicio, fecha_fin, justificacion)
                VALUES (%s, %s, %s, %s, %s)
            """, (cedula, id_tipo, inicio.strftime("%Y-%m-%d"),
                  fin.strftime("%Y-%m-%d") if fin else None, descripcion))
            conexion.commit()
            cursor.close()

            self.cedula_resultado = cedula
            QMessageBox.information(self, "Éxito", "Novedad registrada correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(paleta_clara())
    ventana = VentanaRegistroOperativa(modo_prueba=True)
    ventana.exec()
    sys.exit(0)