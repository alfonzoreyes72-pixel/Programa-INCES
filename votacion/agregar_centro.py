import sys
import os
import tempfile
import unicodedata
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QFrame,
    QLineEdit, QPlainTextEdit, QComboBox, QListView, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QPen, QPolygonF

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


MAX_NOMBRE = 100
MAX_ESTADO = 60
MAX_MUNICIPIO = 60
MAX_PARROQUIA = 100
MAX_DIRECCION = 255


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
    """Minúsculas, sin tildes y sin espacios repetidos, para comparar nombres ('Maturín' = 'maturin')"""
    texto = unicodedata.normalize("NFD", " ".join(str(texto).split()))
    return "".join(c for c in texto if unicodedata.category(c) != "Mn").lower()


def limpiar(texto):
    """Quita espacios al inicio, al final y los repetidos"""
    return " ".join(str(texto).split())


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
    QComboBox:disabled {
        background-color: #f0f0f0;
        color: #aaaaaa;
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
"""

ESTILO_LISTA_AUTOCOMPLETAR = """
    QListView {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #dcdcdc;
        outline: none;
        font-size: 13px;
        selection-background-color: #e6f0ff;
        selection-color: #0833a2;
    }
    QListView::item {
        min-height: 28px;
        padding-left: 8px;
    }
"""


class VentanaAgregarCentro(QDialog):
    """Ventana modal para registrar un nuevo centro de votación"""

    def __init__(self, parent=None, modo_prueba=False):
        super().__init__(parent)

        # En modo prueba la ventana funciona completa pero NO escribe en la base de datos
        self.modo_prueba = modo_prueba

        # Datos del centro recién registrado (la ventana de votación los usa para mostrarlo)
        self.id_centro = None
        self.id_estado_resultado = None
        self.id_municipio_resultado = None

        # Catálogos: {nombre normalizado: (id, nombre)} y la selección actual de cada nivel
        self.estados = {}
        self.municipios = {}
        self.parroquias = {}
        self.id_estado = None
        self.id_municipio = None
        self.id_parroquia = None

        titulo = "Agregar centro de votación"
        self.setWindowTitle(titulo + (" (modo prueba)" if modo_prueba else ""))
        self.setFixedSize(540, 690)
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
        layout_card.setContentsMargins(20, 18, 20, 18)
        layout_card.setSpacing(12)

        estilo_seccion = "font-size: 12px; font-weight: bold; color: #163e7a; background: transparent;"

        # ---------- Sección: datos del centro ----------
        lbl_seccion_datos = QLabel("DATOS DEL CENTRO")
        lbl_seccion_datos.setStyleSheet(estilo_seccion)
        layout_card.addWidget(lbl_seccion_datos)

        form_datos = QFormLayout()
        form_datos.setContentsMargins(0, 0, 0, 0)
        form_datos.setSpacing(14)
        form_datos.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej. Liceo Miguel José Sanz")
        self.txt_nombre.setMaxLength(MAX_NOMBRE)
        self.txt_nombre.setFixedHeight(36)
        form_datos.addRow("Nombre:", self.txt_nombre)
        layout_card.addLayout(form_datos)

        # ---------- Sección: ubicación ----------
        lbl_seccion_ubicacion = QLabel("UBICACIÓN")
        lbl_seccion_ubicacion.setStyleSheet(estilo_seccion + " margin-top: 6px;")
        layout_card.addWidget(lbl_seccion_ubicacion)

        form_ubicacion = QFormLayout()
        form_ubicacion.setContentsMargins(0, 0, 0, 0)
        form_ubicacion.setSpacing(14)
        form_ubicacion.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.cmb_estado = self._crear_combo_editable("Seleccione o escriba el estado", MAX_ESTADO)
        self.cmb_municipio = self._crear_combo_editable("Seleccione o escriba el municipio", MAX_MUNICIPIO)
        self.cmb_parroquia = self._crear_combo_editable("Seleccione o escriba la parroquia", MAX_PARROQUIA)
        self.cmb_municipio.setEnabled(False)
        self.cmb_parroquia.setEnabled(False)

        form_ubicacion.addRow("Estado:", self.cmb_estado)
        form_ubicacion.addRow("Municipio:", self.cmb_municipio)
        form_ubicacion.addRow("Parroquia:", self.cmb_parroquia)

        self.txt_direccion = QPlainTextEdit()
        self.txt_direccion.setPlaceholderText("Ej. Avenida Bolívar, diagonal a la Redoma Juana Ramírez, al lado de la Casa de la Cultura")
        self.txt_direccion.setFixedHeight(84)
        self.txt_direccion.setTabChangesFocus(True)
        self.txt_direccion.textChanged.connect(self.al_cambiar_direccion)

        lbl_direccion = QLabel("Dirección:")
        lbl_direccion.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lbl_direccion.setStyleSheet("padding-top: 8px;")
        form_ubicacion.addRow(lbl_direccion, self.txt_direccion)

        self.lbl_contador = QLabel(f"0/{MAX_DIRECCION}")
        self.lbl_contador.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_contador.setStyleSheet("font-size: 11px; font-weight: normal; color: #999999; background: transparent;")
        form_ubicacion.addRow("", self.lbl_contador)

        layout_card.addLayout(form_ubicacion)

        lbl_ayuda = QLabel("Elige una opción de la lista o escribe una nueva: si el estado, municipio o parroquia "
                           "aún no existe, se registrará al guardar.")
        lbl_ayuda.setWordWrap(True)
        lbl_ayuda.setStyleSheet("font-size: 11px; font-weight: normal; color: #777777; background: transparent;")
        layout_card.addWidget(lbl_ayuda)

        layout_card.addStretch()
        layout_principal.addWidget(card_contenedor)

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

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFixedSize(100, 36)
        self.btn_guardar.setAutoDefault(False)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton { background-color: #163e7a; color: white; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #235299; }
        """)
        self.btn_guardar.clicked.connect(self.guardar_centro)
        layout_botones.addWidget(self.btn_guardar)

        layout_principal.addLayout(layout_botones)

        # Catálogo inicial y señales en cascada
        self.cargar_estados()
        self.cmb_estado.editTextChanged.connect(self.al_cambiar_estado)
        self.cmb_municipio.editTextChanged.connect(self.al_cambiar_municipio)
        self.cmb_parroquia.editTextChanged.connect(self.al_cambiar_parroquia)

    # ==================== COMPONENTES ====================
    def _crear_combo_editable(self, texto_guia, max_caracteres):
        """Lista desplegable en la que también se puede escribir (con autocompletado)"""
        combo = QComboBox()
        combo.setEditable(True)

        # La vista se crea una sola vez y se estiliza directamente; setView() la propaga
        # automáticamente al popup del autocompletador (combo.completer()).
        vista = QListView()
        vista.setStyleSheet(ESTILO_LISTA_AUTOCOMPLETAR)
        combo.setView(vista)

        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setFixedHeight(36)

        # El campo de texto interno no debe dibujar un segundo borde dentro del combo
        editor = combo.lineEdit()
        editor.setPlaceholderText(texto_guia)
        editor.setMaxLength(max_caracteres)
        editor.setStyleSheet(
            "QLineEdit { border: none; background: transparent; padding: 0px; font-size: 13px; color: #333333; }"
            "QLineEdit:focus { border: none; }"
        )

        # En algunas versiones de PyQt6 el popup del autocompletador no existe hasta
        # que se invoca; se protege contra None para evitar el AttributeError.
        completador = combo.completer()
        if completador is not None:
            completador.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completador.setFilterMode(Qt.MatchFlag.MatchContains)
            popup = completador.popup()
            if popup is not None and popup is not vista:
                popup.setStyleSheet(ESTILO_LISTA_AUTOCOMPLETAR)

        combo.setCurrentIndex(-1)
        return combo

    def al_cambiar_direccion(self):
        texto = self.txt_direccion.toPlainText()
        if len(texto) > MAX_DIRECCION:
            texto = texto[:MAX_DIRECCION]
            self.txt_direccion.blockSignals(True)
            self.txt_direccion.setPlainText(texto)
            self.txt_direccion.blockSignals(False)
            cursor = self.txt_direccion.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.txt_direccion.setTextCursor(cursor)
        self.lbl_contador.setText(f"{len(texto)}/{MAX_DIRECCION}")

    # ==================== CATÁLOGOS EN CASCADA ====================
    def _consultar(self, sql, params=()):
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
            print(f"Error al consultar los datos de ubicación: {e}")
        return []

    def _llenar_combo(self, combo, filas, col_id, col_nombre):
        """Carga los elementos del combo sin disparar señales; devuelve {normalizado: (id, nombre)}"""
        catalogo = {}
        combo.blockSignals(True)
        combo.clear()
        for fila in filas:
            combo.addItem(fila[col_nombre], fila[col_id])
            catalogo[normalizar(fila[col_nombre])] = (fila[col_id], fila[col_nombre])
        combo.setCurrentIndex(-1)
        combo.setEditText("")
        combo.blockSignals(False)
        return catalogo

    def _vaciar_combo(self, combo):
        combo.blockSignals(True)
        combo.clear()
        combo.setEditText("")
        combo.blockSignals(False)

    def cargar_estados(self):
        filas = self._consultar("SELECT id_estado, nombre_estado FROM estados ORDER BY nombre_estado")
        self.estados = self._llenar_combo(self.cmb_estado, filas, "id_estado", "nombre_estado")

    def _reiniciar_municipios(self):
        self._vaciar_combo(self.cmb_municipio)
        self.municipios = {}
        self.id_municipio = None
        self._reiniciar_parroquias()

    def _reiniciar_parroquias(self):
        self._vaciar_combo(self.cmb_parroquia)
        self.parroquias = {}
        self.id_parroquia = None
        self.cmb_parroquia.setEnabled(False)

    def al_cambiar_estado(self, texto):
        entrada = self.estados.get(normalizar(texto))
        nuevo_id = entrada[0] if entrada else None
        escrito = bool(limpiar(texto))

        if nuevo_id != self.id_estado or not escrito:
            self.id_estado = nuevo_id
            self._reiniciar_municipios()
            if nuevo_id is not None:
                filas = self._consultar(
                    "SELECT id_municipio, nombre_municipio FROM municipios WHERE id_estado_fk = %s ORDER BY nombre_municipio",
                    (nuevo_id,)
                )
                self.municipios = self._llenar_combo(self.cmb_municipio, filas, "id_municipio", "nombre_municipio")

        self.cmb_municipio.setEnabled(escrito)

    def al_cambiar_municipio(self, texto):
        entrada = self.municipios.get(normalizar(texto))
        nuevo_id = entrada[0] if entrada else None
        escrito = bool(limpiar(texto))

        if nuevo_id != self.id_municipio or not escrito:
            self.id_municipio = nuevo_id
            self._reiniciar_parroquias()
            if nuevo_id is not None:
                filas = self._consultar(
                    "SELECT id_parroquia, nombre_parroquia FROM parroquias WHERE id_municipio_fk = %s ORDER BY nombre_parroquia",
                    (nuevo_id,)
                )
                self.parroquias = self._llenar_combo(self.cmb_parroquia, filas, "id_parroquia", "nombre_parroquia")

        self.cmb_parroquia.setEnabled(escrito)

    def al_cambiar_parroquia(self, texto):
        entrada = self.parroquias.get(normalizar(texto))
        self.id_parroquia = entrada[0] if entrada else None

    # ==================== GUARDADO ====================
    def guardar_centro(self):
        nombre = limpiar(self.txt_nombre.text())
        estado = limpiar(self.cmb_estado.currentText())
        municipio = limpiar(self.cmb_municipio.currentText())
        parroquia = limpiar(self.cmb_parroquia.currentText())
        direccion = limpiar(self.txt_direccion.toPlainText())

        if not nombre:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingrese el nombre del centro de votación.")
            return
        if not estado:
            QMessageBox.warning(self, "Campo vacío", "Por favor, indique el estado donde se encuentra el centro.")
            return
        if not municipio:
            QMessageBox.warning(self, "Campo vacío", "Por favor, indique el municipio donde se encuentra el centro.")
            return
        if not parroquia:
            QMessageBox.warning(self, "Campo vacío", "Por favor, indique la parroquia donde se encuentra el centro.")
            return
        if not direccion:
            QMessageBox.warning(self, "Campo vacío", "Por favor, escriba la dirección del centro de votación.")
            return

        # Si se escribió algo que no existe todavía, se pide confirmar para evitar errores de escritura
        nuevos = []
        if self.id_estado is None:
            nuevos.append(f"• Estado: {estado}")
        if self.id_municipio is None:
            nuevos.append(f"• Municipio: {municipio}")
        if self.id_parroquia is None:
            nuevos.append(f"• Parroquia: {parroquia}")

        if nuevos:
            respuesta = QMessageBox.question(
                self, "Registrar ubicación nueva",
                "Se registrarán estos datos nuevos:\n\n" + "\n".join(nuevos) +
                "\n\nRevisa que estén bien escritos. ¿Deseas continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if respuesta != QMessageBox.StandardButton.Yes:
                return

        # Modo prueba: se valida todo pero no se escribe en la base de datos
        if self.modo_prueba:
            QMessageBox.information(
                self, "Modo de prueba",
                "Las validaciones son correctas.\n\nModo de prueba: el centro NO se guardó en la base de datos."
            )
            self.accept()
            return

        conexion = None
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                QMessageBox.critical(self, "Error de Conexión", "No se pudo conectar con la base de datos MySQL.")
                return

            cursor = conexion.cursor()

            # El mismo centro no puede registrarse dos veces en la misma parroquia
            if self.id_parroquia is not None:
                cursor.execute(
                    "SELECT id_centro_votacion FROM centros_votacion WHERE nombre_centro = %s AND id_parroquia_fk = %s",
                    (nombre, self.id_parroquia)
                )
                if cursor.fetchone():
                    cursor.close()
                    QMessageBox.warning(
                        self, "Centro existente",
                        "Ya existe un centro de votación con ese nombre en esa parroquia."
                    )
                    return

            id_estado = self.id_estado
            if id_estado is None:
                cursor.execute("INSERT INTO estados (nombre_estado) VALUES (%s)", (estado,))
                id_estado = cursor.lastrowid

            id_municipio = self.id_municipio
            if id_municipio is None:
                cursor.execute(
                    "INSERT INTO municipios (nombre_municipio, id_estado_fk) VALUES (%s, %s)",
                    (municipio, id_estado)
                )
                id_municipio = cursor.lastrowid

            id_parroquia = self.id_parroquia
            if id_parroquia is None:
                cursor.execute(
                    "INSERT INTO parroquias (nombre_parroquia, id_municipio_fk) VALUES (%s, %s)",
                    (parroquia, id_municipio)
                )
                id_parroquia = cursor.lastrowid

            cursor.execute(
                "INSERT INTO centros_votacion (nombre_centro, direccion_centro, id_parroquia_fk) VALUES (%s, %s, %s)",
                (nombre, direccion, id_parroquia)
            )
            self.id_centro = cursor.lastrowid
            self.id_estado_resultado = id_estado
            self.id_municipio_resultado = id_municipio

            conexion.commit()
            cursor.close()
            QMessageBox.information(self, "Éxito", "Centro de votación registrado correctamente.")
            self.accept()
        except Exception as e:
            if conexion:
                try:
                    conexion.rollback()
                except Exception:
                    pass
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar:\n{e}")


if __name__ == "__main__":
    # Al ejecutar este archivo solo se abre en modo prueba: se puede probar toda la ventana
    # (lee los estados reales, pero no escribe nada en la base de datos).
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(paleta_clara())
    ventana = VentanaAgregarCentro(modo_prueba=True)
    ventana.exec()
    sys.exit(0)