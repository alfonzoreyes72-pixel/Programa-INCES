import sys
import re
import tempfile
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFormLayout,
    QComboBox, QDateEdit, QWidget, QFrame, QListView, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QPointF, QEvent
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QPen, QPolygonF


def formatear_digitos_cedula(digitos):
    """'31776780' -> '31.776.780' (puntos por miles, de derecha a izquierda)"""
    partes = []
    while digitos:
        partes.insert(0, digitos[-3:])
        digitos = digitos[:-3]
    return ".".join(partes)

# Importación del gestor de base de datos global desde la raíz
try:
    from database import GestorBD
except ImportError:
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


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
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
        background: none;
        border: none;
    }
"""


class DialogoRegistrarDepartamento(QDialog):
    """Ventana modal para registrar un nuevo departamento"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nuevo Departamento")
        self.setFixedSize(380, 220)
        self.setPalette(paleta_clara())
        self.setStyleSheet(ESTILO_VENTANA.replace("__FLECHA__", crear_icono_flecha()))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        lbl = QLabel("Registrar Nuevo Departamento")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c2c2c; background: transparent;")
        layout.addWidget(lbl)

        card = QFrame()
        card.setStyleSheet("background-color: #ffffff; border-radius: 12px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)

        self.txt_nombre_depto = QLineEdit()
        self.txt_nombre_depto.setPlaceholderText("Nombre del nuevo departamento")
        card_layout.addWidget(self.txt_nombre_depto)
        layout.addWidget(card)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedSize(90, 32)
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #e0dede; color: #333333; border-radius: 16px; font-weight: bold; border: none; } QPushButton:hover { background-color: #d0d0d0; }")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setFixedSize(90, 32)
        btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guardar.setStyleSheet("QPushButton { background-color: #163e7a; color: white; border-radius: 16px; font-weight: bold; border: none; } QPushButton:hover { background-color: #235299; }")
        btn_guardar.clicked.connect(self.guardar_departamento)
        btn_layout.addWidget(btn_guardar)

        layout.addLayout(btn_layout)

    def guardar_departamento(self):
        nombre = self.txt_nombre_depto.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingrese el nombre del departamento.")
            return
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS departamentos (
                        id_departamento INT AUTO_INCREMENT PRIMARY KEY,
                        nombre_departamento VARCHAR(100) NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
                """)
                cursor.execute("INSERT INTO departamentos (nombre_departamento) VALUES (%s)", (nombre,))
                conexion.commit()
                cursor.close()
                QMessageBox.information(self, "Éxito", "Departamento registrado correctamente.")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el departamento:\n{e}")


class RegistroTrabajadores(QDialog):
    """Ventana modal para el registro y modificación de trabajadores"""
    def __init__(self, titulo="Registrar Trabajador", datos=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setFixedSize(520, 670)
        self.setPalette(paleta_clara())
        self.setStyleSheet(ESTILO_VENTANA.replace("__FLECHA__", crear_icono_flecha()))

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; background: transparent;")
        layout_principal.addWidget(lbl_titulo)

        card_contenedor = QFrame()
        card_contenedor.setObjectName("cardContenedor")
        card_contenedor.setStyleSheet("QFrame#cardContenedor { background-color: #ffffff; border-radius: 15px; }")
        layout_card = QVBoxLayout(card_contenedor)
        layout_card.setContentsMargins(20, 20, 12, 20)
        layout_card.setSpacing(15)

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

        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Ej. 12.345.678")
        self.txt_cedula.setMaxLength(11)
        # El usuario solo escribe los números: los puntos se colocan automáticamente
        self.txt_cedula.textChanged.connect(self.al_cambiar_cedula)

        self.txt_nombres = QLineEdit()
        self.txt_nombres.setPlaceholderText("Nombres completos")

        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setPlaceholderText("Apellidos completos")

        self.date_nacimiento = QDateEdit()
        self.date_nacimiento.setCalendarPopup(True)
        # Sin fecha elegida: se muestra el texto indicativo (la fecha mínima actúa como "vacío")
        self.date_nacimiento.setMinimumDate(QDate(1900, 1, 1))
        self.date_nacimiento.setSpecialValueText("Seleccione la fecha")
        self.date_nacimiento.setDate(self.date_nacimiento.minimumDate())
        self.date_nacimiento.setFixedHeight(36)

        calendario = self.date_nacimiento.calendarWidget()
        calendario.setPalette(paleta_clara())
        calendario.setStyleSheet("""
            QCalendarWidget QWidget { background-color: #ffffff; color: #333333; font-size: 13px; }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #163e7a; border-top-left-radius: 8px; border-top-right-radius: 8px; }
            QCalendarWidget QToolButton { color: #ffffff; background-color: transparent; font-weight: bold; border: none; margin: 2px; padding: 4px; border-radius: 4px; }
            QCalendarWidget QToolButton:hover { background-color: #3b6ba3; }
            QCalendarWidget QTableView { selection-background-color: #0833a2; selection-color: #ffffff; border: 1px solid #e0dede; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }
            QCalendarWidget QAbstractItemView:enabled { color: #333333; }
        """)

        calendario.installEventFilter(self)

        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Ej. 0412-1234567")

        self.txt_correo = QLineEdit()
        self.txt_correo.setPlaceholderText("correo@inces.gob.ve")

        self.cmb_sexo = QComboBox()
        self.cmb_sexo.addItems(["Masculino", "Femenino"])
        self.cmb_sexo.setCurrentIndex(-1)

        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("Dirección de habitación")

        # Selector de Departamento con enlace corto debajo
        self.cmb_departamento = QComboBox()
        self.lbl_link_depto = QLabel('<a href="#" style="color: #163e7a; text-decoration: none;">¿No encuentras el departamento? Pulsa aquí</a>')
        self.lbl_link_depto.setOpenExternalLinks(False)
        self.lbl_link_depto.linkActivated.connect(self.abrir_registro_departamento)
        self.lbl_link_depto.setStyleSheet("font-size: 11px; font-weight: normal; color: #163e7a; background: transparent;")

        contenedor_depto = QWidget()
        contenedor_depto.setStyleSheet("background: transparent;")
        d_layout = QVBoxLayout(contenedor_depto)
        d_layout.setContentsMargins(0, 0, 0, 0)
        d_layout.setSpacing(4)
        d_layout.addWidget(self.cmb_departamento)
        d_layout.addWidget(self.lbl_link_depto)

        self.cmb_estado_laboral = QComboBox()

        # Selectores en cascada para la ubicación del centro de votación
        self.cmb_estado_cv = QComboBox()
        self.cmb_municipio_cv = QComboBox()
        self.cmb_centro_votacion = QComboBox()

        for combo in (self.cmb_sexo, self.cmb_departamento, self.cmb_estado_laboral,
                      self.cmb_estado_cv, self.cmb_municipio_cv, self.cmb_centro_votacion):
            combo.setView(QListView())
            combo.setFixedHeight(36)
            combo.setPlaceholderText("Seleccione...")

        # Cargar catálogos iniciales desde la base de datos
        self.cargar_datos_maestros()

        # Conectar señales enlazadas de forma segura para evitar bucles de eventos
        self.cmb_estado_cv.currentIndexChanged.connect(self.cargar_municipios)
        self.cmb_municipio_cv.currentIndexChanged.connect(self.cargar_centros_votacion)

        form_layout.addRow("Cédula:", self.txt_cedula)
        form_layout.addRow("Nombres:", self.txt_nombres)
        form_layout.addRow("Apellidos:", self.txt_apellidos)
        form_layout.addRow("Fecha Nacimiento:", self.date_nacimiento)
        form_layout.addRow("Teléfono:", self.txt_telefono)
        form_layout.addRow("Correo:", self.txt_correo)
        form_layout.addRow("Sexo:", self.cmb_sexo)
        form_layout.addRow("Dirección:", self.txt_direccion)
        form_layout.addRow("Departamento:", contenedor_depto)
        form_layout.addRow("Estado Laboral:", self.cmb_estado_laboral)
        form_layout.addRow("Estado (Votación):", self.cmb_estado_cv)
        form_layout.addRow("Municipio (Votación):", self.cmb_municipio_cv)
        form_layout.addRow("Centro de Votación:", self.cmb_centro_votacion)

        scroll.setWidget(contenedor_form)
        layout_card.addWidget(scroll)
        layout_principal.addWidget(card_contenedor)

        layout_botones = QHBoxLayout()
        layout_botones.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(100, 36)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton { background-color: #e0dede; color: #333333; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #d0d0d0; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(self.btn_cancelar)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFixedSize(100, 36)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton { background-color: #163e7a; color: white; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #235299; }
        """)
        self.btn_guardar.clicked.connect(self.guardar_en_bd)
        layout_botones.addWidget(self.btn_guardar)

        layout_principal.addLayout(layout_botones)

        self.es_modificacion = False
        if datos:
            self.es_modificacion = True
            self.txt_cedula.setText(formatear_digitos_cedula(re.sub(r"\D", "", str(datos.get("cedula", "")))))
            self.txt_cedula.setReadOnly(True)
            if datos.get("nombres") is not None:
                self.txt_nombres.setText(datos.get("nombres", ""))
                self.txt_apellidos.setText(datos.get("apellidos", ""))
            else:
                nombres_split = datos.get("nombre", "").split(" ", 1)
                self.txt_nombres.setText(nombres_split[0] if len(nombres_split) > 0 else "")
                self.txt_apellidos.setText(nombres_split[1] if len(nombres_split) > 1 else "")
            self.txt_telefono.setText(datos.get("telefono", ""))
            self.txt_correo.setText(datos.get("correo", ""))
            self.txt_direccion.setText(datos.get("direccion", ""))
            self.cargar_datos_trabajador(datos)

    def al_cambiar_cedula(self, texto):
        """Da formato de miles a la cédula mientras se escribe, conservando la posición del cursor"""
        posicion = self.txt_cedula.cursorPosition()
        digitos_antes = sum(c.isdigit() for c in texto[:posicion])
        digitos = "".join(c for c in texto if c.isdigit())[:9]
        formateado = formatear_digitos_cedula(digitos)
        if formateado == texto:
            return

        self.txt_cedula.blockSignals(True)
        self.txt_cedula.setText(formateado)
        self.txt_cedula.blockSignals(False)

        nueva_posicion, contados = 0, 0
        while nueva_posicion < len(formateado) and contados < digitos_antes:
            if formateado[nueva_posicion].isdigit():
                contados += 1
            nueva_posicion += 1
        self.txt_cedula.setCursorPosition(nueva_posicion)

    def eventFilter(self, obj, event):
        # Al abrir el calendario sin fecha elegida, se muestra el año 2000 en lugar de 1900
        if obj is self.date_nacimiento.calendarWidget() and event.type() == QEvent.Type.Show:
            if self.date_nacimiento.date() == self.date_nacimiento.minimumDate():
                obj.setCurrentPage(2000, 1)
        return super().eventFilter(obj, event)

    @staticmethod
    def _a_qdate(valor):
        """Convierte la fecha que llega de la base de datos en un QDate"""
        if hasattr(valor, "year"):
            return QDate(valor.year, valor.month, valor.day)
        fecha = QDate.fromString(str(valor), "yyyy-MM-dd")
        return fecha if fecha.isValid() else None

    @staticmethod
    def _seleccionar(combo, id_valor, texto):
        """Selecciona en el combo por id (o por texto si no hay id); si no encuentra, queda en blanco"""
        indice = -1
        if id_valor is not None:
            indice = combo.findData(id_valor)
        if indice < 0 and texto:
            indice = combo.findText(str(texto))
        combo.setCurrentIndex(indice)

    def cargar_datos_trabajador(self, datos):
        """Muestra en la fecha y los selectores los datos registrados del trabajador"""
        fecha = self._a_qdate(datos.get("fecha_nacimiento"))
        if fecha:
            self.date_nacimiento.setDate(fecha)

        self.cmb_sexo.setCurrentIndex(
            self.cmb_sexo.findText(str(datos.get("sexo", "")), Qt.MatchFlag.MatchFixedString)
        )
        self._seleccionar(self.cmb_departamento, datos.get("id_departamento"), datos.get("departamento"))
        self._seleccionar(self.cmb_estado_laboral, datos.get("id_estado_laboral"), datos.get("estado_laboral"))
        self.seleccionar_centro_votacion(datos)

    def seleccionar_centro_votacion(self, datos):
        """Selecciona estado, municipio y centro de votación del trabajador, en cascada"""
        id_centro = datos.get("id_centro_votacion")
        id_estado = id_municipio = None

        if id_centro is not None:
            try:
                db = GestorBD()
                conexion = db.obtener_conexion()
                if conexion:
                    cursor = conexion.cursor(dictionary=True)
                    cursor.execute("""
                        SELECT m.id_municipio, m.id_estado_fk
                        FROM centros_votacion cv
                        JOIN parroquias p ON cv.id_parroquia_fk = p.id_parroquia
                        JOIN municipios m ON p.id_municipio_fk = m.id_municipio
                        WHERE cv.id_centro_votacion = %s
                    """, (id_centro,))
                    fila = cursor.fetchone()
                    cursor.close()
                    if fila:
                        id_estado, id_municipio = fila["id_estado_fk"], fila["id_municipio"]
            except Exception as e:
                print(f"Error al ubicar el centro de votación del trabajador: {e}")

        if id_estado is not None:
            # Cada selección carga automáticamente la lista del siguiente selector
            self.cmb_estado_cv.setCurrentIndex(self.cmb_estado_cv.findData(id_estado))
            self.cmb_municipio_cv.setCurrentIndex(self.cmb_municipio_cv.findData(id_municipio))
            self.cmb_centro_votacion.setCurrentIndex(self.cmb_centro_votacion.findData(id_centro))
        else:
            # Respaldo: buscar por los nombres que trae la lista de trabajadores
            self._seleccionar(self.cmb_estado_cv, None, datos.get("estado_cv"))
            self._seleccionar(self.cmb_municipio_cv, None, datos.get("municipio_cv"))
            self._seleccionar(self.cmb_centro_votacion, None, datos.get("centro_cv"))

    def abrir_registro_departamento(self):
        """Abre la ventana modal para registrar un nuevo departamento y actualiza el ComboBox"""
        dialogo = DialogoRegistrarDepartamento(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_departamentos()
            # Se deja seleccionado el departamento recién registrado
            nuevo = dialogo.txt_nombre_depto.text().strip()
            self.cmb_departamento.setCurrentIndex(self.cmb_departamento.findText(nuevo))

    def cargar_departamentos(self):
        """Carga los departamentos desde la base de datos"""
        self.cmb_departamento.clear()
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS departamentos (
                        id_departamento INT AUTO_INCREMENT PRIMARY KEY,
                        nombre_departamento VARCHAR(100) NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
                """)
                conexion.commit()

                cursor.execute("SELECT id_departamento, nombre_departamento FROM departamentos")
                for d in cursor.fetchall():
                    self.cmb_departamento.addItem(d["nombre_departamento"], d["id_departamento"])
                self.cmb_departamento.setCurrentIndex(-1)
                cursor.close()
        except Exception as e:
            print(f"Error al cargar departamentos: {e}")

    def cargar_datos_maestros(self):
        """Carga departamentos, estados laborales y estados geográficos desde la BD"""
        self.cargar_departamentos()
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)

                # Estados Laborales
                cursor.execute("SELECT id_estado_laboral, descripcion_estado FROM estados_laborales")
                for el in cursor.fetchall():
                    self.cmb_estado_laboral.addItem(el["descripcion_estado"], el["id_estado_laboral"])
                self.cmb_estado_laboral.setCurrentIndex(-1)

                # Estados Geográficos
                cursor.execute("SELECT id_estado, nombre_estado FROM estados")
                estados = cursor.fetchall()
                for est in estados:
                    self.cmb_estado_cv.addItem(est["nombre_estado"], est["id_estado"])
                self.cmb_estado_cv.setCurrentIndex(-1)

                cursor.close()
        except Exception as e:
            print(f"Error al cargar datos maestros: {e}")

    def cargar_municipios(self):
        """Carga los municipios del estado elegido; quedan en blanco hasta que se elija uno"""
        self.cmb_municipio_cv.blockSignals(True)
        self.cmb_municipio_cv.clear()
        self.cmb_centro_votacion.clear()
        id_estado = self.cmb_estado_cv.currentData()
        if id_estado is None:
            self.cmb_municipio_cv.blockSignals(False)
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT id_municipio, nombre_municipio FROM municipios WHERE id_estado_fk = %s", (id_estado,))
                for mun in cursor.fetchall():
                    self.cmb_municipio_cv.addItem(mun["nombre_municipio"], mun["id_municipio"])
                cursor.close()
        except Exception as e:
            print(f"Error al cargar municipios: {e}")

        self.cmb_municipio_cv.setCurrentIndex(-1)
        self.cmb_municipio_cv.blockSignals(False)

    def cargar_centros_votacion(self):
        """Carga los centros de votación del municipio elegido; quedan en blanco hasta que se elija uno"""
        self.cmb_centro_votacion.clear()
        id_municipio = self.cmb_municipio_cv.currentData()
        if id_municipio is None:
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                sql = """
                    SELECT DISTINCT c.id_centro_votacion, c.nombre_centro 
                    FROM centros_votacion c
                    JOIN parroquias p ON c.id_parroquia_fk = p.id_parroquia
                    WHERE p.id_municipio_fk = %s
                """
                cursor.execute(sql, (id_municipio,))
                for cv in cursor.fetchall():
                    self.cmb_centro_votacion.addItem(cv["nombre_centro"], cv["id_centro_votacion"])
                cursor.close()
        except Exception as e:
            print(f"Error al cargar centros de votación: {e}")

        self.cmb_centro_votacion.setCurrentIndex(-1)

    def guardar_en_bd(self):
        cedula = re.sub(r"\D", "", self.txt_cedula.text())  # En la base de datos se guarda sin puntos
        nombres = self.txt_nombres.text().strip()
        apellidos = self.txt_apellidos.text().strip()
        fecha_nac = self.date_nacimiento.date().toString("yyyy-MM-dd")
        telefono = self.txt_telefono.text().strip()
        correo = self.txt_correo.text().strip()
        sexo = self.cmb_sexo.currentText()
        direccion = self.txt_direccion.text().strip()
        
        id_departamento = self.cmb_departamento.currentData()
        id_estado_laboral = self.cmb_estado_laboral.currentData()
        id_centro_votacion = self.cmb_centro_votacion.currentData()

        if not cedula or not nombres or not apellidos:
            QMessageBox.warning(self, "Campos incompletos", "Por favor, complete la cédula, nombres y apellidos.")
            return

        if self.date_nacimiento.date() == self.date_nacimiento.minimumDate():
            QMessageBox.warning(self, "Fecha de nacimiento", "Por favor, seleccione la fecha de nacimiento.")
            return

        if self.cmb_sexo.currentIndex() < 0:
            QMessageBox.warning(self, "Sexo", "Por favor, seleccione el sexo.")
            return

        if id_departamento is None:
            QMessageBox.warning(self, "Departamento", "Por favor, seleccione un departamento.")
            return

        if id_estado_laboral is None:
            QMessageBox.warning(self, "Estado laboral", "Por favor, seleccione el estado laboral.")
            return

        if not id_centro_votacion:
            QMessageBox.warning(self, "Centro de Votación", "Por favor, seleccione un centro de votación válido.")
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                if self.es_modificacion:
                    sql = """
                        UPDATE trabajadores SET 
                        nombres = %s, apellidos = %s, fecha_nacimiento = %s, 
                        telefono = %s, correo = %s, sexo = %s, direccion = %s,
                        id_departamento_fk = %s, id_estado_laboral_fk = %s, id_centro_votacion_fk = %s
                        WHERE cedula_trabajador = %s
                    """
                    cursor.execute(sql, (nombres, apellidos, fecha_nac, telefono, correo, sexo, direccion, 
                                         id_departamento, id_estado_laboral, id_centro_votacion, cedula))
                else:
                    sql = """
                        INSERT INTO trabajadores 
                        (cedula_trabajador, nombres, apellidos, fecha_nacimiento, telefono, correo, sexo, direccion, id_departamento_fk, id_estado_laboral_fk, id_centro_votacion_fk)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (cedula, nombres, apellidos, fecha_nac, telefono, correo, sexo, direccion, 
                                         id_departamento, id_estado_laboral, id_centro_votacion))
                
                conexion.commit()
                cursor.close()
                QMessageBox.information(self, "Éxito", "Trabajador guardado correctamente en la base de datos.")
                self.accept()
            else:
                QMessageBox.critical(self, "Error de Conexión", "No se pudo conectar con la base de datos MySQL.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(paleta_clara())
    ventana = RegistroTrabajadores()
    ventana.show()
    sys.exit(app.exec())