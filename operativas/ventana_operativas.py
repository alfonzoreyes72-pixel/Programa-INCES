import sys
import os
import re
import tempfile
import unicodedata
from datetime import date, datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit,
    QPushButton, QLabel, QScrollArea, QComboBox, QListView, QSizePolicy,
    QMessageBox
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QPolygonF, QIcon
from PyQt6.QtSvg import QSvgRenderer

_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.abspath(os.path.join(_DIRECTORIO, '..'))
for _ruta in (_DIRECTORIO, _RAIZ):
    if os.path.isdir(_ruta) and _ruta not in sys.path:
        sys.path.insert(0, _ruta)

# Importación del gestor de base de datos
from database import GestorBD

# Importación de las ventanas modales de novedades operativas
try:
    from .registro_operativas import VentanaRegistroOperativa
except ImportError:
    from registro_operativas import VentanaRegistroOperativa

try:
    from .finalizar_novedad import VentanaFinalizarNovedad
except ImportError:
    from finalizar_novedad import VentanaFinalizarNovedad


MAX_FILAS = 150
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

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

TIPOS_INICIALES = [
    ("Reposo médico", "rojo"),
    ("Vacaciones", "verde"),
    ("Permiso", "ambar"),
    ("Comisión de servicio", "morado"),
]

ESTADOS = {
    "en_curso": ("En curso", "#1b8a4b"),
    "programada": ("Programada", "#235299"),
    "finalizada": ("Finalizada", "#8a93a3"),
}

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

ESTILO_BOTON_AZUL = """
    QPushButton {
        background-color: #0833a2;
        color: white;
        border: 2px solid #0833a2;
        border-radius: 18px;
        padding: 0px 18px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #3150ff;
        border: 2px solid #3150ff;
    }
    QPushButton:disabled {
        background-color: #a9b8dc;
        border: 2px solid #a9b8dc;
        color: #ffffff;
    }
"""


# ==================== ICONOS (rutas autocalculables) ====================
CARPETAS_IMAGENES = [
    os.path.join(_DIRECTORIO, '..', 'imagenes'),
    os.path.join(_DIRECTORIO, 'imagenes'),
]


def _clave_nombre(texto):
    """'icono-lupa.svg' -> 'iconolupa' (ignora signos, espacios y mayúsculas)"""
    return re.sub(r"[^a-z0-9]", "", os.path.splitext(str(texto))[0].lower())


def buscar_icono(clave):
    for carpeta in CARPETAS_IMAGENES:
        carpeta = os.path.abspath(carpeta)
        if not os.path.isdir(carpeta):
            continue
        for archivo in os.listdir(carpeta):
            if archivo.lower().endswith(".svg") and _clave_nombre(archivo) == clave:
                return os.path.join(carpeta, archivo)
    return None


def cargar_pixmap_svg(clave, alto):
    """Dibuja un SVG con el alto indicado (manteniendo su proporción) y nitidez para pantallas HD"""
    ruta = buscar_icono(clave)
    if not ruta:
        return None
    renderer = QSvgRenderer(ruta)
    if not renderer.isValid():
        return None
    tam = renderer.defaultSize()
    proporcion = tam.width() / tam.height() if tam.height() else 1
    escala = 2
    alto_px = int(alto * escala)
    ancho_px = max(1, int(round(alto_px * proporcion)))
    pixmap = QPixmap(ancho_px, alto_px)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(escala)
    return pixmap


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


# ==================== UTILIDADES ====================
def normalizar(texto):
    """Minúsculas y sin tildes, para buscar sin importar acentos"""
    texto = unicodedata.normalize("NFD", str(texto))
    return "".join(c for c in texto if unicodedata.category(c) != "Mn").lower().strip()


def a_fecha(valor):
    """Convierte lo que devuelve la base de datos en un date (o None)"""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return datetime.strptime(str(valor)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


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


def iniciales(nombre):
    texto = str(nombre).strip()
    return texto[0].upper() if texto else "?"


def describir_periodo(datos, hoy):
    """Texto del período ('10 nov 2026 → sin fecha de fin') y de su duración ('9 días y contando')"""
    inicio, fin, estado = datos["fecha_inicio"], datos["fecha_fin"], datos["estado"]
    if fin is None:
        periodo = f"{formatear_fecha(inicio)} → sin fecha de fin"
    else:
        periodo = f"{formatear_fecha(inicio)} → {formatear_fecha(fin)}"

    if estado == "programada":
        detalle = f"Inicia en {texto_dias((inicio - hoy).days)}"
        if fin is not None:
            detalle = f"{texto_dias((fin - inicio).days + 1)} · {detalle.lower()}"
    elif fin is None:
        detalle = f"{texto_dias((hoy - inicio).days + 1)} y contando"
    else:
        detalle = texto_dias((fin - inicio).days + 1)
    return periodo, detalle


def dias_transcurridos(datos, hoy):
    """Días de la novedad que ya pasaron (las programadas todavía no cuentan)"""
    if datos["estado"] == "programada":
        return 0
    fin = datos["fecha_fin"] or hoy
    return (min(fin, hoy) - datos["fecha_inicio"]).days + 1


def calcular_estado(inicio, fin, hoy):
    """Programada, en curso o finalizada, según las fechas (no se guarda en la base de datos)"""
    if inicio > hoy:
        return "programada"
    if fin is None or fin >= hoy:
        return "en_curso"
    return "finalizada"


def preparar_base_de_datos():
    """
    - La fecha de fin pasa a permitir vacío (novedades que se cierran más adelante).
    - Los tipos de novedad tienen un color.
    - Si no hay ningún tipo de novedad registrado, se crean los iniciales.
    """
    try:
        db = GestorBD()
        conexion = db.obtener_conexion()
        if not conexion:
            return
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IS_NULLABLE FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'novedades_operativas' AND COLUMN_NAME = 'fecha_fin'
        """)
        fila = cursor.fetchone()
        if fila and str(fila[0]).upper() == "NO":
            cursor.execute("ALTER TABLE novedades_operativas MODIFY fecha_fin DATE NULL")

        cursor.execute("SHOW COLUMNS FROM incidencias LIKE 'color'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE incidencias ADD COLUMN color VARCHAR(20) NOT NULL DEFAULT 'gris'")

        cursor.execute("SELECT COUNT(*) FROM incidencias")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO incidencias (tipo_incidencia, color) VALUES (%s, %s)",
                TIPOS_INICIALES
            )

        conexion.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al preparar la base de datos de novedades operativas: {e}")


# ==================== COMPONENTES ====================
class TarjetaMetrica(QFrame):
    """Tarjeta superior: número, título y descripción; al presionarla filtra por ese estado"""
    cliqueada = pyqtSignal(str)

    def __init__(self, titulo, descripcion, color, filtro, parent=None):
        super().__init__(parent)
        self.filtro = filtro
        self.color = color
        self.activa = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.aplicar_estilo()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(4)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; border: none; background: transparent;")

        self.lbl_valor = QLabel("0")
        self.lbl_valor.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color}; border: none; background: transparent;")

        self.lbl_desc = QLabel(descripcion)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("font-size: 11px; color: #777777; border: none; background: transparent;")

        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_valor)
        layout.addWidget(self.lbl_desc)

    def aplicar_estilo(self):
        if self.activa:
            fondo, hover, borde = "#eef4fd", "#e6f0ff", "2px solid #0833a2"
        else:
            fondo, hover, borde = "#ffffff", "#f8fafc", "none"
        self.setStyleSheet(f"""
            TarjetaMetrica {{
                background-color: {fondo};
                border-radius: 15px;
                border: {borde};
                border-left: 6px solid {self.color};
            }}
            TarjetaMetrica:hover {{
                background-color: {hover};
            }}
        """)

    def set_valor(self, valor):
        self.lbl_valor.setText(str(valor))

    def set_activa(self, valor):
        if self.activa != valor:
            self.activa = valor
            self.aplicar_estilo()

    def mousePressEvent(self, event):
        self.cliqueada.emit(self.filtro)
        super().mousePressEvent(event)


def _columna(widget, estirable):
    """Las columnas flexibles ignoran el tamaño de su contenido, así encabezado y filas quedan alineados"""
    if estirable:
        widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    return widget


class FilaNovedad(QFrame):
    """Fila de la tabla: trabajador, tipo, período, estado y acción"""
    finalizar_solicitada = pyqtSignal(dict)
    cliqueada = pyqtSignal(dict)

    ANCHO_TIPO = 170
    ANCHO_ESTADO = 130
    ANCHO_ACCION = 90

    def __init__(self, datos, hoy, parent=None):
        super().__init__(parent)
        self.datos = datos
        self.setFixedHeight(66)
        self.seleccionada = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.aplicar_estilo()

        estado = datos["estado"]
        atenuada = estado == "finalizada"
        color_principal = "#8a93a3" if atenuada else "#333333"
        color_secundario = "#a0a7b4" if atenuada else "#777777"
        sin_estilo = "border: none; background: transparent;"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(20)

        col_trabajador = QWidget()
        lt = QVBoxLayout(col_trabajador)
        lt.setContentsMargins(0, 0, 0, 0)
        lt.setSpacing(2)
        lbl_nombre = QLabel(str(datos["trabajador"]))
        lbl_nombre.setTextFormat(Qt.TextFormat.PlainText)
        lbl_nombre.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color_principal}; {sin_estilo}")
        lbl_cedula = QLabel(f"C.I. {formatear_cedula(datos['cedula'])}")
        lbl_cedula.setStyleSheet(f"font-size: 12px; color: {color_secundario}; {sin_estilo}")
        lt.addStretch()
        lt.addWidget(lbl_nombre)
        lt.addWidget(lbl_cedula)
        lt.addStretch()

        fondo, texto = COLORES_TIPO.get(datos["color"], COLORES_TIPO["gris"])
        borde = texto  # La pastilla lleva el borde del mismo color del tipo
        if atenuada:
            fondo, texto, borde = "#eceff3", "#7b8494", "#b8c0cc"
        col_tipo = QWidget()
        col_tipo.setFixedWidth(self.ANCHO_TIPO)
        ltipo = QHBoxLayout(col_tipo)
        ltipo.setContentsMargins(0, 0, 0, 0)
        lbl_tipo = QLabel(str(datos["tipo"]))
        lbl_tipo.setTextFormat(Qt.TextFormat.PlainText)
        lbl_tipo.setToolTip(str(datos.get("justificacion") or ""))
        # Pastilla: borde de color, relleno suave del mismo color y texto del color del tipo
        lbl_tipo.setFixedHeight(28)  # Mismo alto que el botón Finalizar
        lbl_tipo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tipo.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {texto}; background-color: {fondo};"
            f"border: 1.5px solid {borde}; border-radius: 14px; padding: 0px 14px;"
        )
        ltipo.addWidget(lbl_tipo)
        ltipo.addStretch()

        _, fin = datos["fecha_inicio"], datos["fecha_fin"]
        periodo, detalle = describir_periodo(datos, hoy)

        col_periodo = QWidget()
        lp = QVBoxLayout(col_periodo)
        lp.setContentsMargins(0, 0, 0, 0)
        lp.setSpacing(2)
        lbl_periodo = QLabel(periodo)
        lbl_periodo.setStyleSheet(f"font-size: 13px; color: {color_principal}; {sin_estilo}")
        lbl_detalle = QLabel(detalle)
        lbl_detalle.setStyleSheet(f"font-size: 12px; color: {color_secundario}; {sin_estilo}")
        lp.addStretch()
        lp.addWidget(lbl_periodo)
        lp.addWidget(lbl_detalle)
        lp.addStretch()

        texto_estado, color_punto = ESTADOS[estado]
        lbl_estado = QLabel(f"<span style='color:{color_punto};'>●</span>&nbsp; {texto_estado}")
        lbl_estado.setTextFormat(Qt.TextFormat.RichText)
        lbl_estado.setFixedWidth(self.ANCHO_ESTADO)
        lbl_estado.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color_principal}; {sin_estilo}")

        col_accion = QWidget()
        col_accion.setFixedWidth(self.ANCHO_ACCION)
        la = QHBoxLayout(col_accion)
        la.setContentsMargins(0, 0, 0, 0)
        if estado == "en_curso" and fin is None:
            btn = QPushButton("Finalizar")
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #163e7a;
                    border: 1.5px solid #163e7a;
                    border-radius: 14px;
                    padding: 0px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #eef2f7; }
            """)
            btn.clicked.connect(lambda: self.finalizar_solicitada.emit(self.datos))
            la.addWidget(btn)

        layout.addWidget(_columna(col_trabajador, True), stretch=3)
        layout.addWidget(col_tipo)
        layout.addWidget(_columna(col_periodo, True), stretch=3)
        layout.addWidget(lbl_estado)
        layout.addWidget(col_accion)

    def aplicar_estilo(self):
        if self.seleccionada:
            fondo, hover, borde = "#eef4fd", "#e6f0ff", "2px solid #0833a2"
        else:
            fondo, hover, borde = "#f4f6f9", "#eef2f7", "1px solid #e2e6eb"
        self.setStyleSheet(f"""
            FilaNovedad {{
                background-color: {fondo};
                border-radius: 10px;
                border: {borde};
            }}
            FilaNovedad:hover {{
                background-color: {hover};
            }}
        """)

    def set_seleccionada(self, valor):
        if self.seleccionada != valor:
            self.seleccionada = valor
            self.aplicar_estilo()

    def mousePressEvent(self, event):
        self.cliqueada.emit(self.datos)
        super().mousePressEvent(event)


class VentanaOperativas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.novedades = []
        self.hoy = date.today()
        self.widgets_filas = []
        self.widgets_historial = []
        self.cedula_seleccionada = None

        layout_raiz = QHBoxLayout(self)
        # Márgenes y separación compactos para reservar espacio al panel lateral.
        layout_raiz.setContentsMargins(12, 12, 12, 12)
        layout_raiz.setSpacing(12)

        contenedor_izq = QWidget()
        contenedor_izq.setMinimumWidth(0)
        contenedor_izq.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        contenedor_izq.setStyleSheet("background: transparent;")
        layout_principal = QVBoxLayout(contenedor_izq)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(20)

        # ==================== TARJETAS SUPERIORES ====================
        layout_tarjetas = QHBoxLayout()
        layout_tarjetas.setSpacing(12)

        self.tarjetas = {
            "en_curso": TarjetaMetrica("En curso hoy", "Trabajadores con una novedad activa.", "#163e7a", "en_curso"),
            "sin_fin": TarjetaMetrica("Sin fecha de fin", "Novedades abiertas por cerrar.", "#235299", "sin_fin"),
            "programada": TarjetaMetrica("Programadas", "Novedades que aún no comienzan.", "#3b6ba3", "programada"),
            "finalizada": TarjetaMetrica("Finalizadas", "Novedades ya concluidas.", "#4d7fc2", "finalizada"),
        }
        for tarjeta in self.tarjetas.values():
            tarjeta.cliqueada.connect(self.al_presionar_tarjeta)
            layout_tarjetas.addWidget(tarjeta)
        layout_principal.addLayout(layout_tarjetas)

        # ==================== PANEL BLANCO (filtros y tabla) ====================
        panel = QFrame()
        panel.setObjectName("panelOperativas")
        panel.setStyleSheet("""
            QFrame#panelOperativas {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_panel = QVBoxLayout(panel)
        layout_panel.setContentsMargins(20, 18, 20, 18)
        layout_panel.setSpacing(14)

        fila_titulo = QHBoxLayout()
        lbl_titulo = QLabel("Novedades operativas")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        self.lbl_contador = QLabel("")
        self.lbl_contador.setStyleSheet("font-size: 13px; font-weight: bold; color: #777777; border: none; background: transparent;")
        fila_titulo.addWidget(lbl_titulo)
        fila_titulo.addStretch()
        fila_titulo.addWidget(self.lbl_contador)
        layout_panel.addLayout(fila_titulo)

        fila_controles = QHBoxLayout()
        fila_controles.setSpacing(10)
        fila_controles.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por trabajador o cédula...")
        self.txt_buscar.setToolTip("Buscar por nombre, cédula o descripción")
        self.txt_buscar.setMinimumWidth(200)
        self.txt_buscar.setFixedHeight(36)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #f4f6f9;
                border: 1px solid #dcdcdc;
                border-radius: 18px;
                padding-left: 15px;
                padding-right: 15px;
                color: black;
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit:focus { border: 2px solid #0833a2; }
        """)
        pixmap_lupa = cargar_pixmap_svg("iconolupa", 16)
        self.accion_lupa = None
        if pixmap_lupa:
            self.accion_lupa = self.txt_buscar.addAction(QIcon(pixmap_lupa), QLineEdit.ActionPosition.LeadingPosition)
        self.txt_buscar.textChanged.connect(self.al_escribir_busqueda)

        estilo_combo = """
            QComboBox {
                background-color: #f4f6f9;
                border: 1px solid #dcdcdc;
                border-radius: 18px;
                padding-left: 15px;
                padding-right: 30px;
                color: #333333;
                font-size: 13px;
                font-weight: bold;
            }
            QComboBox:focus, QComboBox:on { border: 2px solid #0833a2; }
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
        """.replace("__FLECHA__", crear_icono_flecha())

        estilo_etiqueta_filtro = "font-size: 11px; color: #000000; border: none; background: transparent; padding-left: 6px;"

        bloque_tipo = QWidget()
        bloque_tipo.setStyleSheet("background: transparent; border: none;")
        layout_tipo = QVBoxLayout(bloque_tipo)
        layout_tipo.setContentsMargins(0, 0, 0, 0)
        layout_tipo.setSpacing(3)
        lbl_tipo_filtro = QLabel("Tipo de incidencia")
        lbl_tipo_filtro.setStyleSheet(estilo_etiqueta_filtro)
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.setView(QListView())
        self.cmb_tipo.setFixedSize(185, 36)
        self.cmb_tipo.setStyleSheet(estilo_combo)
        self.cmb_tipo.setToolTip("Filtrar por tipo de novedad")
        layout_tipo.addWidget(lbl_tipo_filtro)
        layout_tipo.addWidget(self.cmb_tipo)

        bloque_estado = QWidget()
        bloque_estado.setStyleSheet("background: transparent; border: none;")
        layout_estado = QVBoxLayout(bloque_estado)
        layout_estado.setContentsMargins(0, 0, 0, 0)
        layout_estado.setSpacing(3)
        lbl_estado_filtro = QLabel("Estado")
        lbl_estado_filtro.setStyleSheet(estilo_etiqueta_filtro)
        self.cmb_estado = QComboBox()
        self.cmb_estado.setView(QListView())
        self.cmb_estado.setFixedSize(185, 36)
        self.cmb_estado.setStyleSheet(estilo_combo)
        self.cmb_estado.setToolTip("Filtrar por estado")
        self.cmb_estado.addItem("Todos los estados", None)
        self.cmb_estado.addItem("En curso", "en_curso")
        self.cmb_estado.addItem("Sin fecha de fin", "sin_fin")
        self.cmb_estado.addItem("Programada", "programada")
        self.cmb_estado.addItem("Finalizada", "finalizada")
        layout_estado.addWidget(lbl_estado_filtro)
        layout_estado.addWidget(self.cmb_estado)

        self.btn_nueva = QPushButton("＋  Nueva novedad")
        self.btn_nueva.setFixedHeight(36)
        self.btn_nueva.setMinimumWidth(170)
        self.btn_nueva.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nueva.setStyleSheet(ESTILO_BOTON_AZUL)
        self.btn_nueva.clicked.connect(self.nueva_novedad)

        fila_controles.addWidget(self.txt_buscar, stretch=1)
        fila_controles.addWidget(bloque_tipo)
        fila_controles.addWidget(bloque_estado)
        fila_controles.addSpacing(10)
        fila_controles.addWidget(self.btn_nueva)
        layout_panel.addLayout(fila_controles)

        barra = QFrame()
        barra.setObjectName("barraEncabezados")
        barra.setFixedHeight(38)
        barra.setStyleSheet("""
            QFrame#barraEncabezados {
                background-color: #e9edf2;
                border-radius: 10px;
                border: none;
            }
        """)
        layout_barra = QHBoxLayout(barra)
        layout_barra.setContentsMargins(15, 0, 15, 0)
        layout_barra.setSpacing(20)

        def encabezado(texto, ancho=None):
            lbl = QLabel(texto)
            lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
            if ancho:
                lbl.setFixedWidth(ancho)
            return lbl

        layout_barra.addWidget(_columna(encabezado("Trabajador"), True), stretch=3)
        layout_barra.addWidget(encabezado("Tipo", FilaNovedad.ANCHO_TIPO))
        layout_barra.addWidget(_columna(encabezado("Período"), True), stretch=3)
        layout_barra.addWidget(encabezado("Estado", FilaNovedad.ANCHO_ESTADO))
        layout_barra.addWidget(encabezado("", FilaNovedad.ANCHO_ACCION))
        layout_panel.addWidget(barra)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(ESTILO_SCROLL)

        contenedor = QWidget()
        contenedor.setStyleSheet("background: transparent;")
        self.layout_filas = QVBoxLayout(contenedor)
        self.layout_filas.setContentsMargins(0, 0, 8, 0)
        self.layout_filas.setSpacing(8)
        self.layout_filas.addStretch()
        self.scroll.setWidget(contenedor)
        layout_panel.addWidget(self.scroll, stretch=1)

        self.lbl_vacio = QLabel("")
        self.lbl_vacio.setWordWrap(True)
        self.lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_vacio.setStyleSheet("font-size: 13px; font-weight: bold; color: #777777; border: none; background: transparent; padding: 30px;")
        self.lbl_vacio.hide()
        self.layout_filas.insertWidget(0, self.lbl_vacio)

        layout_principal.addWidget(panel, stretch=1)
        layout_raiz.addWidget(contenedor_izq, stretch=1)

        self.panel_historial = self._crear_panel_historial()
        # El panel conserva un ancho controlado y no empuja su borde derecho
        # fuera del área visible de la ventana.
        self.panel_historial.setMinimumWidth(260)
        self.panel_historial.setMaximumWidth(290)
        self.panel_historial.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        layout_raiz.addWidget(self.panel_historial, stretch=0)
        self.panel_historial.hide()

        preparar_base_de_datos()
        self.cargar_datos()
        self.cmb_tipo.currentIndexChanged.connect(self.aplicar_filtros)
        self.cmb_estado.currentIndexChanged.connect(self.al_cambiar_estado)

    # ==================== DATOS ====================
    def cargar_datos(self):
        tipo_actual = self.cmb_tipo.currentData()
        hoy = date.today()
        novedades = []
        tipos = []

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)

                cursor.execute("SELECT id_incidencia, tipo_incidencia FROM incidencias ORDER BY tipo_incidencia")
                tipos = cursor.fetchall()

                cursor.execute("""
                    SELECT n.id_novedad, n.cedula_trabajador_fk AS cedula,
                           CONCAT(t.nombres, ' ', t.apellidos) AS trabajador,
                           i.id_incidencia, i.tipo_incidencia AS tipo, COALESCE(i.color, 'gris') AS color,
                           n.fecha_inicio, n.fecha_fin, n.justificacion
                    FROM novedades_operativas n
                    JOIN trabajadores t ON n.cedula_trabajador_fk = t.cedula_trabajador
                    JOIN incidencias i ON n.id_incidencia_fk = i.id_incidencia
                """)
                filas = cursor.fetchall()
                cursor.close()

                for fila in filas:
                    inicio = a_fecha(fila["fecha_inicio"])
                    if inicio is None:
                        continue
                    fila["fecha_inicio"] = inicio
                    fila["fecha_fin"] = a_fecha(fila["fecha_fin"])
                    fila["estado"] = calcular_estado(inicio, fila["fecha_fin"], hoy)
                    novedades.append(fila)
        except Exception as e:
            print(f"Error al cargar las novedades operativas: {e}")

        prioridad = {"en_curso": 0, "programada": 1, "finalizada": 2}
        novedades.sort(key=lambda n: n["fecha_inicio"], reverse=True)
        novedades.sort(key=lambda n: prioridad[n["estado"]])
        self.novedades = novedades
        self.hoy = hoy

        self.cmb_tipo.blockSignals(True)
        self.cmb_tipo.clear()
        self.cmb_tipo.addItem("Todos los tipos", None)
        for t in tipos:
            self.cmb_tipo.addItem(t["tipo_incidencia"], t["id_incidencia"])
        self.cmb_tipo.setCurrentIndex(max(0, self.cmb_tipo.findData(tipo_actual)))
        self.cmb_tipo.blockSignals(False)

        self.actualizar_metricas()
        self.aplicar_filtros()

        if self.cedula_seleccionada is not None:
            if any(n["cedula"] == self.cedula_seleccionada for n in self.novedades):
                self.mostrar_historial(self.cedula_seleccionada)
            else:
                self.cerrar_historial()

    def actualizar_metricas(self):
        en_curso = {n["cedula"] for n in self.novedades if n["estado"] == "en_curso"}
        self.tarjetas["en_curso"].set_valor(len(en_curso))
        self.tarjetas["sin_fin"].set_valor(sum(1 for n in self.novedades if n["fecha_fin"] is None))
        self.tarjetas["programada"].set_valor(sum(1 for n in self.novedades if n["estado"] == "programada"))
        self.tarjetas["finalizada"].set_valor(sum(1 for n in self.novedades if n["estado"] == "finalizada"))

    # ==================== FILTROS ====================
    def al_presionar_tarjeta(self, filtro):
        nuevo = None if self.cmb_estado.currentData() == filtro else filtro
        self.cmb_estado.setCurrentIndex(max(0, self.cmb_estado.findData(nuevo)))

    def al_cambiar_estado(self):
        filtro = self.cmb_estado.currentData()
        for clave, tarjeta in self.tarjetas.items():
            tarjeta.set_activa(clave == filtro)
        self.aplicar_filtros()

    def al_escribir_busqueda(self, texto):
        if self.accion_lupa is not None:
            self.accion_lupa.setVisible(not texto)
        self.aplicar_filtros()

    def aplicar_filtros(self):
        id_tipo = self.cmb_tipo.currentData()
        estado = self.cmb_estado.currentData()
        texto = normalizar(self.txt_buscar.text())
        digitos = re.sub(r"\D", "", self.txt_buscar.text())

        resultado = []
        for n in self.novedades:
            if id_tipo is not None and n["id_incidencia"] != id_tipo:
                continue
            if estado == "sin_fin":
                if n["fecha_fin"] is not None:
                    continue
            elif estado is not None and n["estado"] != estado:
                continue
            if texto:
                coincide = (texto in normalizar(n["trabajador"])
                            or texto in normalizar(n["tipo"])
                            or texto in normalizar(n["justificacion"] or "")
                            or (digitos and digitos in str(n["cedula"])))
                if not coincide:
                    continue
            resultado.append(n)

        self.dibujar_filas(resultado)

    def dibujar_filas(self, novedades):
        for widget in self.widgets_filas:
            self.layout_filas.removeWidget(widget)
            widget.deleteLater()
        self.widgets_filas = []

        total = len(novedades)
        self.lbl_contador.setText(f"{total} novedad" + ("" if total == 1 else "es"))

        if total == 0:
            if not self.novedades:
                self.lbl_vacio.setText("Aún no hay novedades registradas. Presiona «Nueva novedad» para agregar la primera.")
            else:
                self.lbl_vacio.setText("No se encontraron novedades con esos filtros.")
            self.lbl_vacio.show()
            return

        self.lbl_vacio.hide()

        for datos in novedades[:MAX_FILAS]:
            fila = FilaNovedad(datos, self.hoy)
            fila.finalizar_solicitada.connect(self.finalizar_novedad)
            fila.cliqueada.connect(self.seleccionar_trabajador)
            fila.set_seleccionada(self.cedula_seleccionada is not None and datos["cedula"] == self.cedula_seleccionada)
            self.layout_filas.insertWidget(self.layout_filas.count() - 1, fila)
            self.widgets_filas.append(fila)

        if total > MAX_FILAS:
            aviso = QLabel(f"Mostrando las primeras {MAX_FILAS} de {total}. Usa los filtros o el buscador para ver las demás.")
            aviso.setAlignment(Qt.AlignmentFlag.AlignCenter)
            aviso.setStyleSheet("font-size: 12px; color: #777777; border: none; background: transparent; padding: 8px;")
            self.layout_filas.insertWidget(self.layout_filas.count() - 1, aviso)
            self.widgets_filas.append(aviso)

    # ==================== HISTORIAL DEL TRABAJADOR ====================
    def _crear_panel_historial(self):
        panel = QFrame()
        panel.setObjectName("panelHistorial")
        panel.setMinimumWidth(260)
        panel.setMaximumWidth(290)
        panel.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        panel.setStyleSheet("""
            QFrame#panelHistorial {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        fila_cerrar = QHBoxLayout()
        fila_cerrar.addStretch()
        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(28, 28)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #f4f6f9;
                color: #555555;
                border-radius: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #e0dede; color: black; }
        """)
        btn_cerrar.clicked.connect(self.cerrar_historial)
        fila_cerrar.addWidget(btn_cerrar)
        layout.addLayout(fila_cerrar)

        self.lbl_avatar = QLabel("A")
        self.lbl_avatar.setFixedSize(75, 75)
        self.lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_avatar.setStyleSheet("""
            QLabel {
                background-color: #163e7a;
                color: white;
                font-size: 30px;
                font-weight: bold;
                border-radius: 37px;
            }
        """)
        fila_avatar = QHBoxLayout()
        fila_avatar.addStretch()
        fila_avatar.addWidget(self.lbl_avatar)
        fila_avatar.addStretch()
        layout.addLayout(fila_avatar)

        self.lbl_nombre_hist = QLabel("Trabajador")
        self.lbl_nombre_hist.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nombre_hist.setWordWrap(True)
        self.lbl_nombre_hist.setStyleSheet("font-size: 16px; font-weight: bold; color: #163e7a; border: none; background: transparent;")
        layout.addWidget(self.lbl_nombre_hist)

        self.lbl_cedula_hist = QLabel("")
        self.lbl_cedula_hist.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cedula_hist.setStyleSheet("font-size: 12px; color: #777777; border: none; background: transparent;")
        layout.addWidget(self.lbl_cedula_hist)

        separador = QFrame()
        separador.setFixedHeight(1)
        separador.setStyleSheet("background-color: #f0f0f0; border: none;")
        layout.addWidget(separador)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(ESTILO_SCROLL)

        contenido = QWidget()
        contenido.setStyleSheet("background: transparent;")
        self.layout_historial = QVBoxLayout(contenido)
        self.layout_historial.setContentsMargins(0, 0, 8, 0)
        self.layout_historial.setSpacing(10)
        self.layout_historial.addStretch()
        scroll.setWidget(contenido)
        layout.addWidget(scroll, stretch=1)

        return panel

    def seleccionar_trabajador(self, datos):
        if (
            self.cedula_seleccionada is not None
            and self.cedula_seleccionada == datos.get("cedula")
            and self.panel_historial.isVisible()
        ):
            self.cerrar_historial()
            return

        self.cedula_seleccionada = datos["cedula"]
        self.marcar_filas()
        self.mostrar_historial(self.cedula_seleccionada)

    def marcar_filas(self):
        for fila in self.widgets_filas:
            if isinstance(fila, FilaNovedad):
                fila.set_seleccionada(self.cedula_seleccionada is not None
                                      and fila.datos["cedula"] == self.cedula_seleccionada)

    def cerrar_historial(self):
        self.cedula_seleccionada = None
        self.panel_historial.hide()
        self.marcar_filas()

    def mostrar_historial(self, cedula):
        registros = [n for n in self.novedades if n["cedula"] == cedula]
        if not registros:
            self.cerrar_historial()
            return
        registros.sort(key=lambda n: n["fecha_inicio"], reverse=True)

        nombre = registros[0]["trabajador"]
        self.lbl_avatar.setText(iniciales(nombre))
        self.lbl_nombre_hist.setText(str(nombre))
        self.lbl_cedula_hist.setText(f"C.I. {formatear_cedula(cedula)}")

        for widget in self.widgets_historial:
            self.layout_historial.removeWidget(widget)
            widget.deleteLater()
        self.widgets_historial = []

        sin_estilo = "border: none; background: transparent;"

        def agregar(widget):
            self.layout_historial.insertWidget(self.layout_historial.count() - 1, widget)
            self.widgets_historial.append(widget)

        total_dias = sum(dias_transcurridos(n, self.hoy) for n in registros)
        por_tipo = {}
        for n in registros:
            clave = (n["tipo"], n["color"])
            cantidad, dias = por_tipo.get(clave, (0, 0))
            por_tipo[clave] = (cantidad + 1, dias + dias_transcurridos(n, self.hoy))

        resumen = QFrame()
        resumen.setObjectName("resumenHistorial")
        resumen.setStyleSheet("""
            QFrame#resumenHistorial {
                background-color: #f4f6f9;
                border-radius: 10px;
                border: 1px solid #e2e6eb;
            }
        """)
        layout_resumen = QVBoxLayout(resumen)
        layout_resumen.setContentsMargins(12, 10, 12, 10)
        layout_resumen.setSpacing(8)

        lbl_total = QLabel(f"{len(registros)} novedad" + ("" if len(registros) == 1 else "es")
                           + f" · {texto_dias(total_dias)} en total")
        lbl_total.setStyleSheet(f"font-size: 13px; font-weight: bold; color: #2c2c2c; {sin_estilo}")
        layout_resumen.addWidget(lbl_total)

        for (tipo, color), (cantidad, dias) in sorted(por_tipo.items(), key=lambda kv: -kv[1][0]):
            fondo, texto = COLORES_TIPO.get(color, COLORES_TIPO["gris"])
            fila = QHBoxLayout()
            fila.setSpacing(8)
            chip = QLabel(str(tipo))
            chip.setTextFormat(Qt.TextFormat.PlainText)
            chip.setFixedHeight(24)
            chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chip.setStyleSheet(
                f"font-size: 11px; font-weight: bold; color: {texto}; background-color: {fondo};"
                f"border: 1.5px solid {texto}; border-radius: 12px; padding: 0px 12px;"
            )
            detalle = QLabel(f"×{cantidad} · {texto_dias(dias)}")
            detalle.setStyleSheet(f"font-size: 12px; color: #555555; {sin_estilo}")
            fila.addWidget(chip)
            fila.addStretch()
            fila.addWidget(detalle)
            layout_resumen.addLayout(fila)
        agregar(resumen)

        lbl_historial = QLabel("Historial")
        lbl_historial.setStyleSheet(f"font-size: 13px; font-weight: bold; color: #2c2c2c; {sin_estilo} margin-top: 4px;")
        agregar(lbl_historial)

        for n in registros:
            _, texto = COLORES_TIPO.get(n["color"], COLORES_TIPO["gris"])
            periodo, detalle = describir_periodo(n, self.hoy)
            texto_estado, color_punto = ESTADOS[n["estado"]]

            tarjeta = QFrame()
            tarjeta.setObjectName("itemHistorial")
            tarjeta.setStyleSheet(f"""
                QFrame#itemHistorial {{
                    background-color: #f4f6f9;
                    border-radius: 10px;
                    border: none;
                    border-left: 4px solid {texto};
                }}
            """)
            lt = QVBoxLayout(tarjeta)
            lt.setContentsMargins(12, 10, 12, 10)
            lt.setSpacing(4)

            fila_tipo = QHBoxLayout()
            lbl_tipo = QLabel(str(n["tipo"]))
            lbl_tipo.setTextFormat(Qt.TextFormat.PlainText)
            lbl_tipo.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {texto}; {sin_estilo}")
            lbl_estado = QLabel(f"<span style='color:{color_punto};'>●</span>&nbsp; {texto_estado}")
            lbl_estado.setTextFormat(Qt.TextFormat.RichText)
            lbl_estado.setStyleSheet(f"font-size: 12px; color: #555555; {sin_estilo}")
            fila_tipo.addWidget(lbl_tipo)
            fila_tipo.addStretch()
            fila_tipo.addWidget(lbl_estado)
            lt.addLayout(fila_tipo)

            lbl_periodo = QLabel(periodo)
            lbl_periodo.setWordWrap(True)
            lbl_periodo.setStyleSheet(f"font-size: 12px; color: #333333; {sin_estilo}")
            lt.addWidget(lbl_periodo)

            lbl_detalle = QLabel(detalle)
            lbl_detalle.setStyleSheet(f"font-size: 12px; color: #777777; {sin_estilo}")
            lt.addWidget(lbl_detalle)

            descripcion = str(n.get("justificacion") or "").strip()
            if descripcion:
                lbl_desc = QLabel(descripcion)
                lbl_desc.setTextFormat(Qt.TextFormat.PlainText)
                lbl_desc.setWordWrap(True)
                lbl_desc.setStyleSheet(f"font-size: 12px; color: #555555; {sin_estilo} padding-top: 2px;")
                lt.addWidget(lbl_desc)

            agregar(tarjeta)

        self.panel_historial.show()

    def showEvent(self, event):
        super().showEvent(event)
        self.cargar_datos()

    # ==================== ACCIONES ====================
    def nueva_novedad(self):
        """Abre la ventana modal para registrar una novedad sin cerrar la ventana principal."""
        try:
            # Asociar el diálogo a esta ventana evita que quede desligado de su contenedor.
            dialogo = VentanaRegistroOperativa(parent=self)
            resultado = dialogo.exec()

            if resultado == QDialog.DialogCode.Accepted:
                self.txt_buscar.blockSignals(True)
                self.txt_buscar.clear()
                self.txt_buscar.blockSignals(False)
                if self.accion_lupa is not None:
                    self.accion_lupa.setVisible(True)

                self.cmb_tipo.blockSignals(True)
                self.cmb_tipo.setCurrentIndex(0)
                self.cmb_tipo.blockSignals(False)

                self.cmb_estado.blockSignals(True)
                self.cmb_estado.setCurrentIndex(0)
                self.cmb_estado.blockSignals(False)
                for tarjeta in self.tarjetas.values():
                    tarjeta.set_activa(False)

                self.cargar_datos()
                if dialogo.cedula_resultado is not None:
                    self.seleccionar_trabajador({"cedula": dialogo.cedula_resultado})
        except Exception as e:
            QMessageBox.critical(
                self, "Error al abrir el registro",
                f"No se pudo abrir o completar el registro de la novedad.\n\nDetalle: {e}"
            )

    def finalizar_novedad(self, datos):
        """Abre la ventana modal para poner la fecha de fin a la novedad indicada."""
        try:
            dialogo = VentanaFinalizarNovedad(datos, parent=self)
            resultado = dialogo.exec()
            if resultado == QDialog.DialogCode.Accepted:
                self.cargar_datos()
                if (dialogo.cedula_resultado is not None
                        and self.cedula_seleccionada == dialogo.cedula_resultado):
                    self.mostrar_historial(dialogo.cedula_resultado)
        except Exception as e:
            QMessageBox.critical(
                self, "Error al finalizar la novedad",
                f"No se pudo completar la operación.\n\nDetalle: {e}"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaOperativas()
    ventana.setStyleSheet("background-color: #bfbdbe;")
    ventana.resize(1100, 650)
    ventana.show()
    sys.exit(app.exec())