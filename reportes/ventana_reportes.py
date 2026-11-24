import sys
import os
import re
import tempfile
from datetime import date, datetime
from math import ceil
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QPushButton, QLabel,
    QComboBox, QListView, QDateEdit, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QStackedWidget, QMenu, QWidgetAction, QCheckBox, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QPoint, QPointF, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QPolygonF, QIcon, QBrush
from PyQt6.QtSvg import QSvgRenderer

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD

# Importación de la ventana modal de exportación (PDF y Excel)
try:
    from .exportar_reporte import VentanaExportarReporte
except ImportError:
    from exportar_reporte import VentanaExportarReporte


# ==================== CONFIGURACIÓN DE LOS REPORTES ====================
ORDEN = ["trabajadores", "asistencias", "usuarios", "novedades"]

TIPOS = {
    "trabajadores": {"titulo": "Trabajadores", "descripcion": "Todos sus datos", "reporte": "Reporte de trabajadores",
                     "color": "#163e7a"},
    "asistencias": {"titulo": "Asistencias", "descripcion": "Entradas y salidas", "reporte": "Reporte de asistencias",
                    "color": "#235299"},
    "usuarios": {"titulo": "Usuarios", "descripcion": "Cuentas y roles", "reporte": "Reporte de usuarios",
                 "color": "#3b6ba3"},
    "novedades": {"titulo": "Novedades", "descripcion": "Reposos y permisos", "reporte": "Reporte de novedades operativas",
                  "color": "#4d7fc2"},
}

# Columnas de cada reporte: (clave, título, visible por defecto)
COLUMNAS = {
    "trabajadores": [
        ("cedula", "Cédula", True), ("nombres", "Nombres", True), ("apellidos", "Apellidos", True),
        ("fecha_nacimiento", "Fecha de nacimiento", True), ("telefono", "Teléfono", True),
        ("correo", "Correo", True), ("sexo", "Sexo", True), ("direccion", "Dirección", True),
        ("departamento", "Departamento", True), ("estado_laboral", "Estado laboral", True),
        ("centro", "Centro de votación", True), ("parroquia", "Parroquia", False),
        ("municipio", "Municipio", False), ("estado", "Estado", False),
    ],
    "asistencias": [
        ("fecha", "Fecha", True), ("trabajador", "Trabajador", True), ("cedula", "Cédula", True),
        ("departamento", "Departamento", True), ("entrada", "Hora de entrada", True),
        ("salida", "Hora de salida", True), ("horas", "Horas trabajadas", True),
    ],
    "usuarios": [
        ("usuario", "Usuario", True), ("trabajador", "Trabajador", True), ("cedula", "Cédula", True),
        ("rol", "Rol", True), ("cuenta", "Cuenta", True), ("conexion", "Conexión", True),
        ("ultimo_acceso", "Último acceso", True),
    ],
    "novedades": [
        ("trabajador", "Trabajador", True), ("cedula", "Cédula", True), ("departamento", "Departamento", True),
        ("tipo", "Tipo", True), ("inicio", "Inicio", True), ("fin", "Fin", True), ("dias", "Duración", True),
        ("estado", "Estado", True), ("descripcion", "Descripción", True),
    ],
}

# Columnas que en la vista previa llevan un punto de color delante
COLUMNAS_CON_PUNTO = {"novedades": {"estado"}, "usuarios": {"conexion"}}

# Filtros de cada reporte: (clave, etiqueta, clase de control)
FILTROS = {
    "trabajadores": [
        ("departamento", "Departamento", "combo"), ("estado_laboral", "Estado laboral", "combo"),
        ("sexo", "Sexo", "combo"), ("estado_cv", "Estado (votación)", "combo"),
        ("municipio_cv", "Municipio (votación)", "combo"),
    ],
    "asistencias": [
        ("desde", "Desde", "fecha"), ("hasta", "Hasta", "fecha"), ("departamento", "Departamento", "combo"),
    ],
    "usuarios": [
        ("rol", "Rol", "combo"), ("cuenta", "Cuenta", "combo"), ("conexion", "Conexión", "combo"),
    ],
    "novedades": [
        ("desde", "Desde", "fecha"), ("hasta", "Hasta", "fecha"), ("tipo", "Tipo", "combo"),
        ("estado", "Estado", "combo"),
    ],
}

# Listas fijas: (tipo, filtro) -> (texto de "todos", [(texto, valor)])
LISTAS_FIJAS = {
    ("trabajadores", "sexo"): ("Todos", [("Masculino", "masculino"), ("Femenino", "femenino")]),
    ("novedades", "estado"): ("Todos los estados", [("En curso", "en_curso"), ("Sin fecha de fin", "sin_fin"),
                                                    ("Programada", "programada"), ("Finalizada", "finalizada")]),
    ("usuarios", "cuenta"): ("Todas", [("Activas", "activa"), ("Bloqueadas", "bloqueada")]),
    ("usuarios", "conexion"): ("Todas", [("En línea", "en_linea"), ("Fuera de línea", "fuera")]),
}

# Listas que vienen de la base de datos: (tipo, filtro) -> (catálogo, texto de "todos")
LISTAS_CATALOGO = {
    ("trabajadores", "departamento"): ("departamentos", "Todos los departamentos"),
    ("trabajadores", "estado_laboral"): ("estados_laborales", "Todos"),
    ("trabajadores", "estado_cv"): ("estados", "Todos los estados"),
    ("asistencias", "departamento"): ("departamentos", "Todos los departamentos"),
    ("usuarios", "rol"): ("roles", "Todos los roles"),
    ("novedades", "tipo"): ("incidencias", "Todos los tipos"),
}

CONSULTAS_CATALOGO = {
    "departamentos": "SELECT id_departamento AS id, nombre_departamento AS nombre FROM departamentos ORDER BY nombre_departamento",
    "estados_laborales": "SELECT id_estado_laboral AS id, descripcion_estado AS nombre FROM estados_laborales ORDER BY descripcion_estado",
    "estados": "SELECT id_estado AS id, nombre_estado AS nombre FROM estados ORDER BY nombre_estado",
    "roles": "SELECT id_rol AS id, nombre_rol AS nombre FROM roles ORDER BY nombre_rol",
    "incidencias": "SELECT id_incidencia AS id, tipo_incidencia AS nombre FROM incidencias ORDER BY tipo_incidencia",
}

# Colores del texto de los tipos de novedad (los mismos de ventana_operativas.py)
COLORES_TEXTO_TIPO = {
    "rojo": "#b71c1c", "verde": "#1b6e3a", "ambar": "#8a5a00", "azul": "#163e7a",
    "morado": "#4b2f8a", "rosa": "#9c2a5c", "turquesa": "#0f6b5e", "gris": "#4a5568",
}
COLORES_ESTADO_NOVEDAD = {"en_curso": "#1b8a4b", "programada": "#235299", "finalizada": "#8a93a3"}
TEXTO_ESTADO_NOVEDAD = {"en_curso": "En curso", "programada": "Programada", "finalizada": "Finalizada"}

# Un usuario cuenta como "en línea" si su programa dio señal de vida en los últimos 90 segundos
CONDICION_EN_LINEA = "(u.ultima_actividad IS NOT NULL AND u.ultima_actividad >= NOW() - INTERVAL 90 SECOND)"

# Iconos buscados en la carpeta 'imagenes' sin importar guiones, paréntesis, espacios o mayúsculas:
#   icono-trabajadores(azul).svg   icono-asistencias(azul).svg
#   icono-usuarios(azul).svg       icono-operativas(azul).svg
ICONOS = {
    "trabajadores": "iconotrabajadoresazul",
    "asistencias": "iconoasistenciasazul",
    "usuarios": "iconousuariosazul",
    "novedades": "iconooperativasazul",
    "generar": "iconogenerarreporte",
    "pdf": "iconopdf",
    "excel": "iconoexcel",
    "columnas": "iconocolumnas",
    "limpiar": "iconolimpiar",
    "calendario": "iconocalendario",
    "lupa": "iconolupa",
}


# ==================== ICONOS (rutas autocalculables) ====================
# Las imágenes viven en la carpeta 'imagenes' de la raíz del proyecto (junto a ventana_principal.py).
# La ruta se calcula a partir de la ubicación de este archivo, así funciona en cualquier computadora.
_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
CARPETAS_IMAGENES = [
    os.path.join(_DIRECTORIO, '..', 'imagenes'),
    os.path.join(_DIRECTORIO, 'imagenes'),
]
_cache_iconos = {}


def _clave_nombre(texto):
    """'icono-trabajadores(azul).svg' -> 'iconotrabajadoresazul' (ignora signos, espacios y mayúsculas)"""
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
    llave = (clave, alto)
    if llave in _cache_iconos:
        return _cache_iconos[llave]

    pixmap = None
    ruta = buscar_icono(clave)
    if ruta:
        renderer = QSvgRenderer(ruta)
        if renderer.isValid():
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

    _cache_iconos[llave] = pixmap
    return pixmap


def icono_para_boton(nombre, alto=16):
    """QIcon igual en estado normal y deshabilitado (para que el icono blanco no se vea grisáceo); None si no existe"""
    pixmap = cargar_pixmap_svg(ICONOS[nombre], alto)
    if not pixmap:
        return None
    icono = QIcon()
    icono.addPixmap(pixmap, QIcon.Mode.Normal)
    icono.addPixmap(pixmap, QIcon.Mode.Disabled)
    return icono


def crear_icono_flecha():
    """Dibuja la flecha de las listas desplegables y la guarda como imagen temporal"""
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
def a_fecha(valor):
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


def fecha_texto(valor):
    d = a_fecha(valor)
    return d.strftime("%d/%m/%Y") if d else ""


def hora_texto(valor):
    """TIME de la base de datos (timedelta o time) -> '08:30'"""
    if valor is None:
        return ""
    if hasattr(valor, "total_seconds"):
        segundos = int(valor.total_seconds())
        return f"{segundos // 3600:02d}:{(segundos % 3600) // 60:02d}"
    if hasattr(valor, "strftime"):
        return valor.strftime("%H:%M")
    return str(valor)[:5]


def formatear_cedula(valor):
    """31776780 -> 31.776.780"""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(valor)


def texto_dias(n):
    return f"{n} día" + ("" if n == 1 else "s")


def calcular_estado(inicio, fin, hoy):
    """Programada, en curso o finalizada, según las fechas"""
    if inicio > hoy:
        return "programada"
    if fin is None or fin >= hoy:
        return "en_curso"
    return "finalizada"


def texto(valor):
    return "" if valor is None else str(valor)


def patron_busqueda(cadena):
    return f"%{cadena}%"


# ==================== ESTILOS ====================
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

ESTILO_BOTON_SECUNDARIO = """
    QPushButton {
        background-color: #ffffff;
        color: #163e7a;
        border: 2px solid #163e7a;
        border-radius: 18px;
        padding: 0px 16px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #eef2f7; }
"""

ESTILO_BOTON_PAGINA = """
    QPushButton {
        background-color: #f4f6f9;
        color: #163e7a;
        border: 1px solid #dcdcdc;
        border-radius: 16px;
        font-size: 15px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #e6f0ff; }
    QPushButton:disabled { color: #c3c9d4; background-color: #f4f6f9; }
"""

ESTILO_CAMPO = """
    __CLASE__ {
        background-color: #f4f6f9;
        border: 1px solid #dcdcdc;
        border-radius: 18px;
        padding-left: 15px;
        padding-right: 30px;
        color: #333333;
        font-size: 13px;
        font-weight: bold;
    }
    __CLASE__:focus, __CLASE__:on { border: 2px solid #0833a2; }
    __CLASE__:disabled { background-color: #eceff3; color: #aaaaaa; }
    __CLASE__::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 28px;
        border: none;
        background: transparent;
    }
    __CLASE__::down-arrow {
        image: url(__IMAGEN__);
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

ESTILO_CALENDARIO = """
    QCalendarWidget QWidget { background-color: #ffffff; color: #333333; font-size: 13px; }
    QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #163e7a; border-top-left-radius: 8px; border-top-right-radius: 8px; }
    QCalendarWidget QToolButton { color: #ffffff; background-color: transparent; font-weight: bold; border: none; margin: 2px; padding: 4px; border-radius: 4px; }
    QCalendarWidget QToolButton:hover { background-color: #3b6ba3; }
    QCalendarWidget QTableView { selection-background-color: #0833a2; selection-color: #ffffff; border: 1px solid #e0dede; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }
    QCalendarWidget QAbstractItemView:enabled { color: #333333; }
"""

ESTILO_TABLA = """
    QTableWidget {
        background-color: #ffffff;
        alternate-background-color: #f8fafc;
        border: none;
        font-size: 12px;
        color: #333333;
        selection-background-color: #e6f0ff;
        selection-color: #163e7a;
        outline: none;
    }
    QTableWidget::item { padding-left: 8px; padding-right: 8px; border: none; }
    QHeaderView::section {
        background-color: #e9edf2;
        color: #777777;
        font-size: 12px;
        font-weight: bold;
        padding: 8px 10px;
        border: none;
        border-right: 1px solid #ffffff;
    }
    QTableCornerButton::section { background-color: #e9edf2; border: none; }
    QScrollBar:vertical { background: transparent; width: 8px; margin: 2px 0px 2px 0px; border: none; }
    QScrollBar::handle:vertical { background: #d3d8e0; border-radius: 4px; min-height: 30px; }
    QScrollBar::handle:vertical:hover { background: #aeb6c2; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; background: none; border: none; }
    QScrollBar:horizontal { background: transparent; height: 8px; margin: 0px 2px 0px 2px; border: none; }
    QScrollBar::handle:horizontal { background: #d3d8e0; border-radius: 4px; min-width: 30px; }
    QScrollBar::handle:horizontal:hover { background: #aeb6c2; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; background: none; border: none; }
"""


# ==================== COMPONENTES ====================
class TarjetaTipoReporte(QFrame):
    """Tarjeta para elegir el tipo de reporte; la elegida queda con borde azul y fondo celeste"""
    cliqueada = pyqtSignal(str)

    def __init__(self, clave, parent=None):
        super().__init__(parent)
        self.clave = clave
        self.color = TIPOS[clave]["color"]
        self.activa = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(70)
        self.aplicar_estilo()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)

        self.lbl_icono = QLabel()
        self.lbl_icono.setFixedSize(30, 30)
        self.lbl_icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_icono.setStyleSheet("border: none; background: transparent;")
        pixmap = cargar_pixmap_svg(ICONOS[clave], 26)
        if pixmap:
            self.lbl_icono.setPixmap(pixmap)
        layout.addWidget(self.lbl_icono)

        textos = QVBoxLayout()
        textos.setSpacing(2)
        lbl_titulo = QLabel(TIPOS[clave]["titulo"])
        lbl_titulo.setStyleSheet("font-size: 13px; font-weight: bold; color: #333333; border: none; background: transparent;")
        lbl_desc = QLabel(TIPOS[clave]["descripcion"])
        lbl_desc.setStyleSheet("font-size: 11px; color: #777777; border: none; background: transparent;")
        textos.addStretch()
        textos.addWidget(lbl_titulo)
        textos.addWidget(lbl_desc)
        textos.addStretch()
        layout.addLayout(textos, stretch=1)

    def aplicar_estilo(self):
        if self.activa:
            fondo, hover, borde = "#eef4fd", "#e6f0ff", "2px solid #0833a2"
        else:
            fondo, hover, borde = "#ffffff", "#f8fafc", "none"
        self.setStyleSheet(f"""
            TarjetaTipoReporte {{
                background-color: {fondo};
                border-radius: 15px;
                border: {borde};
                border-left: 6px solid {self.color};
            }}
            TarjetaTipoReporte:hover {{
                background-color: {hover};
            }}
        """)

    def set_activa(self, valor):
        if self.activa != valor:
            self.activa = valor
            self.aplicar_estilo()

    def mousePressEvent(self, event):
        self.cliqueada.emit(self.clave)
        super().mousePressEvent(event)


class VentanaReportes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tipo_actual = "trabajadores"
        self.reporte = None  # Último reporte generado: filas, filtros, fecha
        self.pagina = 0
        self.filtros = {}  # tipo -> {clave: control}
        self.combos_catalogo = []  # (combo, catálogo, texto de "todos")
        self.columnas_visibles = {t: {c[0] for c in COLUMNAS[t] if c[2]} for t in ORDEN}

        ruta_calendario = buscar_icono(ICONOS["calendario"])
        self._imagen_flecha = crear_icono_flecha()
        self._imagen_fecha = ruta_calendario.replace("\\", "/") if ruta_calendario else self._imagen_flecha

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        # ==================== TARJETAS DE TIPO DE REPORTE ====================
        layout_tipos = QHBoxLayout()
        layout_tipos.setSpacing(12)
        self.tarjetas_tipo = {}
        for clave in ORDEN:
            tarjeta = TarjetaTipoReporte(clave)
            tarjeta.cliqueada.connect(self.cambiar_tipo)
            self.tarjetas_tipo[clave] = tarjeta
            layout_tipos.addWidget(tarjeta)
        layout_principal.addLayout(layout_tipos)

        # ==================== PANEL BLANCO ====================
        panel = QFrame()
        panel.setObjectName("panelReportes")
        panel.setStyleSheet("""
            QFrame#panelReportes {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_panel = QVBoxLayout(panel)
        layout_panel.setContentsMargins(20, 18, 20, 18)
        layout_panel.setSpacing(12)

        sin_fondo = "border: none; background: transparent;"

        fila_titulo = QHBoxLayout()
        self.lbl_titulo_panel = QLabel(TIPOS[self.tipo_actual]["reporte"])
        self.lbl_titulo_panel.setStyleSheet(f"font-size: 18px; font-weight: bold; color: #2c2c2c; {sin_fondo}")
        lbl_pista = QLabel("Los filtros cambian según el reporte")
        lbl_pista.setStyleSheet(f"font-size: 12px; color: #777777; {sin_fondo}")
        fila_titulo.addWidget(self.lbl_titulo_panel)
        fila_titulo.addStretch()
        fila_titulo.addWidget(lbl_pista)
        layout_panel.addLayout(fila_titulo)

        # ---------- Filtros (una página por tipo de reporte) ----------
        self.pila_filtros = QStackedWidget()
        self.pila_filtros.setStyleSheet("QStackedWidget { background: transparent; }")
        for clave in ORDEN:
            self.pila_filtros.addWidget(self._crear_pagina_filtros(clave))
        layout_panel.addWidget(self.pila_filtros)

        # ---------- Búsqueda y botones ----------
        fila_busqueda = QHBoxLayout()
        fila_busqueda.setSpacing(10)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por nombre o cédula...")
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
        pixmap_lupa = cargar_pixmap_svg(ICONOS["lupa"], 16)
        self.accion_lupa = None
        if pixmap_lupa:
            self.accion_lupa = self.txt_buscar.addAction(QIcon(pixmap_lupa), QLineEdit.ActionPosition.LeadingPosition)
        self.txt_buscar.textChanged.connect(self.al_escribir_busqueda)
        self.txt_buscar.returnPressed.connect(self.generar_reporte)

        self.btn_columnas = self._crear_boton("Columnas", "columnas", ESTILO_BOTON_SECUNDARIO, 120)
        self.btn_columnas.setToolTip("Elegir las columnas que se muestran y se exportan")
        self.btn_columnas.clicked.connect(self.mostrar_menu_columnas)

        self.btn_limpiar = self._crear_boton("Limpiar", "limpiar", ESTILO_BOTON_SECUNDARIO, 110)
        self.btn_limpiar.setToolTip("Quitar los filtros")
        self.btn_limpiar.clicked.connect(self.limpiar_filtros)

        self.btn_generar = self._crear_boton("Generar reporte", "generar", ESTILO_BOTON_AZUL, 170)
        self.btn_generar.clicked.connect(self.generar_reporte)

        fila_busqueda.addWidget(self.txt_buscar, stretch=1)
        fila_busqueda.addWidget(self.btn_columnas)
        fila_busqueda.addWidget(self.btn_limpiar)
        fila_busqueda.addWidget(self.btn_generar)
        layout_panel.addLayout(fila_busqueda)

        # ---------- Resultado: contador y botones de exportación ----------
        fila_resultado = QHBoxLayout()
        fila_resultado.setSpacing(10)
        self.lbl_contador = QLabel("")
        self.lbl_contador.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_contador.setStyleSheet(f"font-size: 13px; color: #333333; {sin_fondo}")
        fila_resultado.addWidget(self.lbl_contador)
        fila_resultado.addStretch()

        self.btn_pdf = self._crear_boton("Exportar PDF", "pdf", ESTILO_BOTON_AZUL, 150)
        self.btn_pdf.clicked.connect(lambda: self.exportar("pdf"))
        self.btn_excel = self._crear_boton("Exportar Excel", "excel", ESTILO_BOTON_AZUL, 160)
        self.btn_excel.clicked.connect(lambda: self.exportar("excel"))
        fila_resultado.addWidget(self.btn_pdf)
        fila_resultado.addWidget(self.btn_excel)
        layout_panel.addLayout(fila_resultado)

        # ---------- Vista previa: mensaje o tabla ----------
        self.pila_vista = QStackedWidget()
        self.pila_vista.setStyleSheet("QStackedWidget { background: transparent; }")

        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setWordWrap(True)
        self.lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mensaje.setStyleSheet(f"font-size: 13px; font-weight: bold; color: #777777; padding: 30px; {sin_fondo}")
        self.pila_vista.addWidget(self.lbl_mensaje)

        self.tabla = QTableWidget()
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)
        self.tabla.setWordWrap(False)
        self.tabla.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.tabla.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tabla.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(34)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setHighlightSections(False)
        self.tabla.setStyleSheet(ESTILO_TABLA)
        self.pila_vista.addWidget(self.tabla)

        layout_panel.addWidget(self.pila_vista, stretch=1)

        # ---------- Paginación ----------
        fila_paginas = QHBoxLayout()
        fila_paginas.setSpacing(8)
        self.btn_anterior = QPushButton("‹")
        self.btn_anterior.setFixedSize(32, 32)
        self.btn_anterior.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_anterior.setStyleSheet(ESTILO_BOTON_PAGINA)
        self.btn_anterior.clicked.connect(lambda: self.cambiar_pagina(-1))
        self.lbl_pagina = QLabel("")
        self.lbl_pagina.setStyleSheet(f"font-size: 12px; font-weight: bold; color: #777777; {sin_fondo}")
        self.btn_siguiente = QPushButton("›")
        self.btn_siguiente.setFixedSize(32, 32)
        self.btn_siguiente.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_siguiente.setStyleSheet(ESTILO_BOTON_PAGINA)
        self.btn_siguiente.clicked.connect(lambda: self.cambiar_pagina(1))

        lbl_por_pagina = QLabel("Filas por página:")
        lbl_por_pagina.setStyleSheet(f"font-size: 12px; color: #777777; {sin_fondo}")
        self.cmb_por_pagina = QComboBox()
        self.cmb_por_pagina.setView(QListView())
        self.cmb_por_pagina.setFixedSize(90, 32)
        self.cmb_por_pagina.setStyleSheet(
            ESTILO_CAMPO.replace("__CLASE__", "QComboBox").replace("__IMAGEN__", self._imagen_flecha)
        )
        for cantidad in (25, 50, 100):
            self.cmb_por_pagina.addItem(str(cantidad), cantidad)
        self.cmb_por_pagina.setCurrentIndex(1)
        self.cmb_por_pagina.currentIndexChanged.connect(self.al_cambiar_filas_por_pagina)

        fila_paginas.addStretch()
        fila_paginas.addWidget(self.btn_anterior)
        fila_paginas.addWidget(self.lbl_pagina)
        fila_paginas.addWidget(self.btn_siguiente)
        fila_paginas.addStretch()
        fila_paginas.addWidget(lbl_por_pagina)
        fila_paginas.addWidget(self.cmb_por_pagina)
        layout_panel.addLayout(fila_paginas)

        layout_principal.addWidget(panel, stretch=1)

        # Datos iniciales
        self.cargar_catalogos()
        self.cambiar_tipo("trabajadores")

    # ==================== CONSTRUCCIÓN DE FILTROS ====================
    def _crear_boton(self, texto_boton, icono, estilo, ancho_minimo):
        icono_boton = icono_para_boton(icono, 16)
        boton = QPushButton((" " if icono_boton else "") + texto_boton)
        if icono_boton:
            boton.setIcon(icono_boton)
            boton.setIconSize(QSize(16, 16))
        boton.setFixedHeight(36)
        boton.setMinimumWidth(ancho_minimo)
        boton.setCursor(Qt.CursorShape.PointingHandCursor)
        boton.setStyleSheet(estilo)
        return boton

    def _campo(self, etiqueta, control):
        """Etiqueta pequeña encima del control"""
        contenedor = QWidget()
        contenedor.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        lbl = QLabel(etiqueta)
        lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #777777; border: none; background: transparent;")
        layout.addWidget(lbl)
        layout.addWidget(control)
        return contenedor

    def _crear_fecha(self, clave):
        control = QDateEdit()
        control.setCalendarPopup(True)
        control.setFixedHeight(36)
        control.setDisplayFormat("dd/MM/yyyy")
        control.setStyleSheet(
            ESTILO_CAMPO.replace("__CLASE__", "QDateEdit").replace("__IMAGEN__", self._imagen_fecha)
        )
        control.calendarWidget().setStyleSheet(ESTILO_CALENDARIO)
        control.setDate(self._fecha_por_defecto(clave))
        return control

    @staticmethod
    def _fecha_por_defecto(clave):
        hoy = QDate.currentDate()
        return QDate(hoy.year(), hoy.month(), 1) if clave == "desde" else hoy

    def _crear_combo(self, tipo, clave):
        combo = QComboBox()
        combo.setView(QListView())
        combo.setFixedHeight(36)
        combo.setStyleSheet(
            ESTILO_CAMPO.replace("__CLASE__", "QComboBox").replace("__IMAGEN__", self._imagen_flecha)
        )

        if (tipo, clave) in LISTAS_FIJAS:
            texto_todos, opciones = LISTAS_FIJAS[(tipo, clave)]
            combo.addItem(texto_todos, None)
            for etiqueta, valor in opciones:
                combo.addItem(etiqueta, valor)
        elif (tipo, clave) in LISTAS_CATALOGO:
            catalogo, texto_todos = LISTAS_CATALOGO[(tipo, clave)]
            combo.addItem(texto_todos, None)
            self.combos_catalogo.append((combo, catalogo, texto_todos))
        else:  # Municipio de votación: depende del estado elegido
            combo.addItem("Todos los municipios", None)
            combo.setEnabled(False)
        return combo

    def _crear_pagina_filtros(self, tipo):
        pagina = QWidget()
        pagina.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        controles = {}
        for clave, etiqueta, clase in FILTROS[tipo]:
            control = self._crear_fecha(clave) if clase == "fecha" else self._crear_combo(tipo, clave)
            controles[clave] = control
            layout.addWidget(self._campo(etiqueta, control), stretch=1)
        self.filtros[tipo] = controles

        if tipo == "trabajadores":
            self.cmb_estado_cv = controles["estado_cv"]
            self.cmb_municipio_cv = controles["municipio_cv"]
            self.cmb_estado_cv.currentIndexChanged.connect(self.cargar_municipios_cv)
        return pagina

    # ==================== CATÁLOGOS ====================
    def _consultar_seguro(self, sql, params=()):
        try:
            return self._ejecutar(sql, params)
        except Exception as e:
            print(f"Error al cargar las listas de los filtros: {e}")
            return []

    def _llenar_combo(self, combo, filas, texto_todos):
        """Recarga las opciones de un filtro conservando lo que estaba elegido"""
        actual = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(texto_todos, None)
        for fila in filas:
            combo.addItem(str(fila["nombre"]), fila["id"])
        combo.setCurrentIndex(max(0, combo.findData(actual)))
        combo.blockSignals(False)

    def cargar_catalogos(self):
        cache = {}
        for combo, catalogo, texto_todos in self.combos_catalogo:
            if catalogo not in cache:
                cache[catalogo] = self._consultar_seguro(CONSULTAS_CATALOGO[catalogo])
            self._llenar_combo(combo, cache[catalogo], texto_todos)
        self.cargar_municipios_cv()

    def cargar_municipios_cv(self, *_):
        id_estado = self.cmb_estado_cv.currentData()
        filas = []
        if id_estado is not None:
            filas = self._consultar_seguro(
                "SELECT id_municipio AS id, nombre_municipio AS nombre FROM municipios "
                "WHERE id_estado_fk = %s ORDER BY nombre_municipio", (id_estado,)
            )
        self._llenar_combo(self.cmb_municipio_cv, filas, "Todos los municipios")
        self.cmb_municipio_cv.setEnabled(id_estado is not None)

    def showEvent(self, event):
        super().showEvent(event)
        # Cada vez que se entra a la ventana se actualizan las listas de los filtros
        self.cargar_catalogos()

    # ==================== TIPO DE REPORTE Y FILTROS ====================
    def cambiar_tipo(self, clave):
        self.tipo_actual = clave
        for k, tarjeta in self.tarjetas_tipo.items():
            tarjeta.set_activa(k == clave)
        self.pila_filtros.setCurrentIndex(ORDEN.index(clave))
        self.lbl_titulo_panel.setText(TIPOS[clave]["reporte"])
        self.txt_buscar.clear()

        # El reporte que se veía era de otro tipo: se limpia la vista previa
        self.reporte = None
        self.pagina = 0
        self.actualizar_vista()

    def limpiar_filtros(self):
        for clave, control in self.filtros[self.tipo_actual].items():
            if isinstance(control, QDateEdit):
                control.setDate(self._fecha_por_defecto(clave))
            else:
                control.setCurrentIndex(0)
        self.txt_buscar.clear()

    def al_escribir_busqueda(self, texto_escrito):
        # La lupa se oculta al empezar a escribir y vuelve cuando el campo queda vacío
        if self.accion_lupa is not None:
            self.accion_lupa.setVisible(not texto_escrito)

    # ==================== COLUMNAS ====================
    def columnas_actuales(self):
        tipo = self.reporte["tipo"] if self.reporte else self.tipo_actual
        return [(clave, titulo) for clave, titulo, _ in COLUMNAS[tipo] if clave in self.columnas_visibles[tipo]]

    def mostrar_menu_columnas(self):
        tipo = self.tipo_actual
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #ffffff; border: 1px solid #dcdcdc; padding: 4px; }
        """)
        estilo_check = """
            QCheckBox { padding: 7px 14px; font-size: 13px; color: #333333; background: transparent; }
            QCheckBox:hover { background-color: #f4f6f9; }
        """
        for clave, titulo, _ in COLUMNAS[tipo]:
            casilla = QCheckBox(titulo)
            casilla.setChecked(clave in self.columnas_visibles[tipo])
            casilla.setCursor(Qt.CursorShape.PointingHandCursor)
            casilla.setStyleSheet(estilo_check)
            casilla.setMinimumWidth(200)
            casilla.toggled.connect(lambda marcada, c=clave, w=casilla: self.alternar_columna(c, marcada, w))
            accion = QWidgetAction(menu)
            accion.setDefaultWidget(casilla)
            menu.addAction(accion)
        menu.exec(self.btn_columnas.mapToGlobal(QPoint(0, self.btn_columnas.height() + 4)))

    def alternar_columna(self, clave, marcada, casilla):
        visibles = self.columnas_visibles[self.tipo_actual]
        if marcada:
            visibles.add(clave)
        elif len(visibles) <= 1:
            # Siempre debe quedar al menos una columna
            casilla.blockSignals(True)
            casilla.setChecked(True)
            casilla.blockSignals(False)
            return
        else:
            visibles.discard(clave)
        if self.reporte:
            self.actualizar_vista()

    # ==================== CONSULTAS ====================
    def _ejecutar(self, sql, params=()):
        db = GestorBD()
        conexion = db.obtener_conexion()
        if not conexion:
            raise RuntimeError("No se pudo conectar con la base de datos.")
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()

    def _columnas_tabla(self, tabla):
        """Nombres de las columnas que existen en una tabla (algunas se crean al usar otras ventanas)"""
        return {fila["Field"] for fila in self._ejecutar(f"SHOW COLUMNS FROM {tabla}")}

    def _filtro_texto(self, combo, etiqueta, filtros, sql_condicion, params, valor_sql=None):
        """Agrega un filtro de lista si hay algo elegido; devuelve el SQL extendido"""
        valor = combo.currentData()
        if valor is None:
            return ""
        params.append(valor if valor_sql is None else valor_sql)
        filtros.append((etiqueta, combo.currentText()))
        return sql_condicion

    # ----- Trabajadores -----
    def _consultar_trabajadores(self, buscar):
        f = self.filtros["trabajadores"]
        sql = """
            SELECT t.cedula_trabajador, t.nombres, t.apellidos, t.fecha_nacimiento, t.telefono, t.correo,
                   t.sexo, t.direccion, d.nombre_departamento, el.descripcion_estado AS estado_laboral,
                   cv.nombre_centro, p.nombre_parroquia, m.nombre_municipio, e.nombre_estado
            FROM trabajadores t
            LEFT JOIN departamentos d ON t.id_departamento_fk = d.id_departamento
            LEFT JOIN estados_laborales el ON t.id_estado_laboral_fk = el.id_estado_laboral
            LEFT JOIN centros_votacion cv ON t.id_centro_votacion_fk = cv.id_centro_votacion
            LEFT JOIN parroquias p ON cv.id_parroquia_fk = p.id_parroquia
            LEFT JOIN municipios m ON p.id_municipio_fk = m.id_municipio
            LEFT JOIN estados e ON m.id_estado_fk = e.id_estado
            WHERE 1=1
        """
        params, filtros = [], []
        sql += self._filtro_texto(f["departamento"], "Departamento", filtros, " AND t.id_departamento_fk = %s", params)
        sql += self._filtro_texto(f["estado_laboral"], "Estado laboral", filtros, " AND t.id_estado_laboral_fk = %s", params)
        sql += self._filtro_texto(f["sexo"], "Sexo", filtros, " AND LOWER(t.sexo) = %s", params)
        sql += self._filtro_texto(f["estado_cv"], "Estado (votación)", filtros, " AND e.id_estado = %s", params)
        sql += self._filtro_texto(f["municipio_cv"], "Municipio (votación)", filtros, " AND m.id_municipio = %s", params)

        if buscar:
            sql += (" AND (t.nombres LIKE %s OR t.apellidos LIKE %s OR CONCAT(t.nombres, ' ', t.apellidos) LIKE %s"
                    " OR t.correo LIKE %s OR t.telefono LIKE %s OR CAST(t.cedula_trabajador AS CHAR) LIKE %s)")
            params += [patron_busqueda(buscar)] * 5 + [patron_busqueda(buscar.replace(".", ""))]
            filtros.append(("Búsqueda", buscar))
        sql += " ORDER BY t.apellidos, t.nombres"

        filas = []
        for r in self._ejecutar(sql, params):
            estado_laboral = texto(r["estado_laboral"])
            fila = {
                "cedula": formatear_cedula(r["cedula_trabajador"]), "nombres": texto(r["nombres"]),
                "apellidos": texto(r["apellidos"]), "fecha_nacimiento": fecha_texto(r["fecha_nacimiento"]),
                "telefono": texto(r["telefono"]), "correo": texto(r["correo"]),
                "sexo": texto(r["sexo"]).capitalize(), "direccion": texto(r["direccion"]),
                "departamento": texto(r["nombre_departamento"]), "estado_laboral": estado_laboral,
                "centro": texto(r["nombre_centro"]), "parroquia": texto(r["nombre_parroquia"]),
                "municipio": texto(r["nombre_municipio"]), "estado": texto(r["nombre_estado"]),
                "_colores": {},
            }
            if "retirado" in estado_laboral.lower():
                fila["_colores"] = {"estado_laboral": "#d32f2f", "nombres": "#d32f2f", "apellidos": "#d32f2f"}
            filas.append(fila)
        return filas, filtros, ""

    # ----- Asistencias -----
    def _consultar_asistencias(self, buscar):
        f = self.filtros["asistencias"]
        desde = f["desde"].date().toPyDate()
        hasta = f["hasta"].date().toPyDate()
        if desde > hasta:
            raise ValueError("La fecha «Desde» no puede ser posterior a «Hasta».")

        sql = """
            SELECT a.fecha, a.hora_entrada, a.hora_salida, t.cedula_trabajador,
                   CONCAT(t.nombres, ' ', t.apellidos) AS trabajador, d.nombre_departamento
            FROM asistencias a
            JOIN trabajadores t ON a.cedula_trabajador_fk = t.cedula_trabajador
            LEFT JOIN departamentos d ON t.id_departamento_fk = d.id_departamento
            WHERE a.fecha BETWEEN %s AND %s
        """
        params = [desde, hasta]
        filtros = [("Desde", desde.strftime("%d/%m/%Y")), ("Hasta", hasta.strftime("%d/%m/%Y"))]
        sql += self._filtro_texto(f["departamento"], "Departamento", filtros, " AND t.id_departamento_fk = %s", params)

        if buscar:
            sql += (" AND (t.nombres LIKE %s OR t.apellidos LIKE %s OR CONCAT(t.nombres, ' ', t.apellidos) LIKE %s"
                    " OR CAST(t.cedula_trabajador AS CHAR) LIKE %s)")
            params += [patron_busqueda(buscar)] * 3 + [patron_busqueda(buscar.replace(".", ""))]
            filtros.append(("Búsqueda", buscar))
        sql += " ORDER BY a.fecha DESC, t.apellidos, t.nombres"

        filas = []
        for r in self._ejecutar(sql, params):
            horas = ""
            entrada, salida = r["hora_entrada"], r["hora_salida"]
            if hasattr(entrada, "total_seconds") and hasattr(salida, "total_seconds") and salida > entrada:
                minutos = int((salida - entrada).total_seconds() // 60)
                horas = f"{minutos // 60} h {minutos % 60:02d} min"
            filas.append({
                "fecha": fecha_texto(r["fecha"]), "trabajador": texto(r["trabajador"]),
                "cedula": formatear_cedula(r["cedula_trabajador"]), "departamento": texto(r["nombre_departamento"]),
                "entrada": hora_texto(entrada), "salida": hora_texto(salida), "horas": horas, "_colores": {},
            })
        periodo = f"{desde.strftime('%d/%m/%Y')} – {hasta.strftime('%d/%m/%Y')}"
        return filas, filtros, periodo

    # ----- Usuarios -----
    def _consultar_usuarios(self, buscar):
        f = self.filtros["usuarios"]
        existentes = self._columnas_tabla("usuarios")
        ultimo_acceso = "u.ultimo_acceso" if "ultimo_acceso" in existentes else "NULL"
        bloqueado = "COALESCE(u.bloqueado, 0)" if "bloqueado" in existentes else "0"
        en_linea = CONDICION_EN_LINEA if "ultima_actividad" in existentes else "0"

        sql = f"""
            SELECT u.nombre_usuario, CONCAT(t.nombres, ' ', t.apellidos) AS trabajador, t.cedula_trabajador,
                   r.nombre_rol, {ultimo_acceso} AS ultimo_acceso, {bloqueado} AS bloqueado, {en_linea} AS en_linea
            FROM usuarios u
            LEFT JOIN trabajadores t ON u.cedula_trabajador_fk = t.cedula_trabajador
            LEFT JOIN roles r ON u.id_rol_fk = r.id_rol
            WHERE 1=1
        """
        params, filtros = [], []
        sql += self._filtro_texto(f["rol"], "Rol", filtros, " AND u.id_rol_fk = %s", params)

        cuenta = f["cuenta"].currentData()
        if cuenta and "bloqueado" in existentes:
            sql += " AND COALESCE(u.bloqueado, 0) = %s"
            params.append(1 if cuenta == "bloqueada" else 0)
            filtros.append(("Cuenta", f["cuenta"].currentText()))

        conexion = f["conexion"].currentData()
        if conexion and "ultima_actividad" in existentes:
            sql += f" AND {'' if conexion == 'en_linea' else 'NOT '}{CONDICION_EN_LINEA}"
            filtros.append(("Conexión", f["conexion"].currentText()))

        if buscar:
            sql += (" AND (u.nombre_usuario LIKE %s OR t.nombres LIKE %s OR t.apellidos LIKE %s"
                    " OR CONCAT(t.nombres, ' ', t.apellidos) LIKE %s OR CAST(t.cedula_trabajador AS CHAR) LIKE %s)")
            params += [patron_busqueda(buscar)] * 4 + [patron_busqueda(buscar.replace(".", ""))]
            filtros.append(("Búsqueda", buscar))
        sql += " ORDER BY u.nombre_usuario"

        filas = []
        for r in self._ejecutar(sql, params):
            acceso = r["ultimo_acceso"]
            esta_bloqueado = bool(r["bloqueado"])
            esta_en_linea = bool(r["en_linea"])
            fila = {
                "usuario": texto(r["nombre_usuario"]), "trabajador": texto(r["trabajador"]),
                "cedula": formatear_cedula(r["cedula_trabajador"]) if r["cedula_trabajador"] else "",
                "rol": texto(r["nombre_rol"]), "cuenta": "Bloqueada" if esta_bloqueado else "Activa",
                "conexion": "En línea" if esta_en_linea else "Fuera de línea",
                "ultimo_acceso": acceso.strftime("%d/%m/%Y %H:%M") if hasattr(acceso, "strftime") else "Nunca",
                "_colores": {
                    "conexion": "#1b8a4b" if esta_en_linea else "#d32f2f",
                },
            }
            if esta_bloqueado:
                fila["_colores"]["cuenta"] = "#d32f2f"
            filas.append(fila)
        return filas, filtros, ""

    # ----- Novedades operativas -----
    def _consultar_novedades(self, buscar):
        f = self.filtros["novedades"]
        desde = f["desde"].date().toPyDate()
        hasta = f["hasta"].date().toPyDate()
        if desde > hasta:
            raise ValueError("La fecha «Desde» no puede ser posterior a «Hasta».")

        color = "COALESCE(i.color, 'gris')" if "color" in self._columnas_tabla("incidencias") else "'gris'"
        sql = f"""
            SELECT t.cedula_trabajador, CONCAT(t.nombres, ' ', t.apellidos) AS trabajador, d.nombre_departamento,
                   i.tipo_incidencia AS tipo, {color} AS color, n.fecha_inicio, n.fecha_fin, n.justificacion
            FROM novedades_operativas n
            JOIN trabajadores t ON n.cedula_trabajador_fk = t.cedula_trabajador
            JOIN incidencias i ON n.id_incidencia_fk = i.id_incidencia
            LEFT JOIN departamentos d ON t.id_departamento_fk = d.id_departamento
            WHERE n.fecha_inicio <= %s AND (n.fecha_fin IS NULL OR n.fecha_fin >= %s)
        """
        params = [hasta, desde]
        filtros = [("Desde", desde.strftime("%d/%m/%Y")), ("Hasta", hasta.strftime("%d/%m/%Y"))]
        sql += self._filtro_texto(f["tipo"], "Tipo", filtros, " AND n.id_incidencia_fk = %s", params)

        if buscar:
            sql += (" AND (t.nombres LIKE %s OR t.apellidos LIKE %s OR CONCAT(t.nombres, ' ', t.apellidos) LIKE %s"
                    " OR n.justificacion LIKE %s OR i.tipo_incidencia LIKE %s OR CAST(t.cedula_trabajador AS CHAR) LIKE %s)")
            params += [patron_busqueda(buscar)] * 5 + [patron_busqueda(buscar.replace(".", ""))]
            filtros.append(("Búsqueda", buscar))
        sql += " ORDER BY n.fecha_inicio DESC"

        estado_elegido = f["estado"].currentData()
        if estado_elegido:
            filtros.append(("Estado", f["estado"].currentText()))

        hoy = date.today()
        filas = []
        for r in self._ejecutar(sql, params):
            inicio, fin = a_fecha(r["fecha_inicio"]), a_fecha(r["fecha_fin"])
            if inicio is None:
                continue
            estado = calcular_estado(inicio, fin, hoy)
            if estado_elegido == "sin_fin":
                if fin is not None:
                    continue
            elif estado_elegido and estado != estado_elegido:
                continue

            if estado == "programada":
                duracion = ""
            elif fin is None:
                duracion = texto_dias((hoy - inicio).days + 1) + " (en curso)"
            else:
                duracion = texto_dias((fin - inicio).days + 1)

            filas.append({
                "trabajador": texto(r["trabajador"]), "cedula": formatear_cedula(r["cedula_trabajador"]),
                "departamento": texto(r["nombre_departamento"]), "tipo": texto(r["tipo"]),
                "inicio": inicio.strftime("%d/%m/%Y"), "fin": fin.strftime("%d/%m/%Y") if fin else "Sin fecha de fin",
                "dias": duracion, "estado": TEXTO_ESTADO_NOVEDAD[estado], "descripcion": texto(r["justificacion"]),
                "_colores": {
                    "tipo": COLORES_TEXTO_TIPO.get(r["color"], "#4a5568"),
                    "estado": COLORES_ESTADO_NOVEDAD[estado],
                },
            })
        periodo = f"{desde.strftime('%d/%m/%Y')} – {hasta.strftime('%d/%m/%Y')}"
        return filas, filtros, periodo

    # ==================== GENERAR Y MOSTRAR ====================
    def generar_reporte(self):
        tipo = self.tipo_actual
        buscar = self.txt_buscar.text().strip()

        error = None
        resultado = None
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            resultado = getattr(self, f"_consultar_{tipo}")(buscar)
        except ValueError as e:
            error = ("aviso", str(e))
        except Exception as e:
            error = ("error", f"No se pudo generar el reporte:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

        if error:
            if error[0] == "aviso":
                QMessageBox.warning(self, "Revisa los filtros", error[1])
            else:
                QMessageBox.critical(self, "Error", error[1])
            return

        filas, filtros, periodo = resultado
        self.reporte = {"tipo": tipo, "filas": filas, "filtros": filtros, "periodo": periodo, "fecha": datetime.now()}
        self.pagina = 0
        self.actualizar_vista()

    def al_cambiar_filas_por_pagina(self, *_):
        self.pagina = 0
        if self.reporte:
            self.actualizar_vista()

    def cambiar_pagina(self, delta):
        self.pagina += delta
        self.actualizar_vista()

    def actualizar_vista(self):
        """Muestra el mensaje o la página actual de la tabla, y activa o apaga los botones que dependen de ello"""
        sin_reporte = self.reporte is None
        total = 0 if sin_reporte else len(self.reporte["filas"])

        self.btn_pdf.setEnabled(total > 0)
        self.btn_excel.setEnabled(total > 0)

        if sin_reporte:
            self.lbl_contador.setText("Sin reporte generado")
            self.lbl_mensaje.setText("Elige el tipo de reporte, ajusta los filtros y presiona «Generar reporte».")
            self.pila_vista.setCurrentIndex(0)
            self._actualizar_paginacion(0, 1)
            return

        fecha = self.reporte["fecha"]
        self.lbl_contador.setText(
            f"<b>{total} registro{'' if total == 1 else 's'}</b> "
            f"<span style='color:#777777;'>· generado el {fecha:%d/%m/%Y %H:%M}</span>"
        )
        if total == 0:
            self.lbl_mensaje.setText("No hay registros con esos filtros.")
            self.pila_vista.setCurrentIndex(0)
            self._actualizar_paginacion(0, 1)
            return

        por_pagina = self.cmb_por_pagina.currentData()
        paginas = max(1, ceil(total / por_pagina))
        self.pagina = max(0, min(self.pagina, paginas - 1))
        self._llenar_tabla(por_pagina)
        self.pila_vista.setCurrentIndex(1)
        self._actualizar_paginacion(self.pagina, paginas)

    def _actualizar_paginacion(self, pagina, paginas):
        self.lbl_pagina.setText(f"Página {pagina + 1} de {paginas}" if self.reporte and self.reporte["filas"] else "")
        self.btn_anterior.setEnabled(pagina > 0)
        self.btn_siguiente.setEnabled(pagina < paginas - 1)

    def _llenar_tabla(self, por_pagina):
        tipo = self.reporte["tipo"]
        columnas = self.columnas_actuales()
        inicio = self.pagina * por_pagina
        filas_pagina = self.reporte["filas"][inicio:inicio + por_pagina]
        con_punto = COLUMNAS_CON_PUNTO.get(tipo, set())

        self.tabla.setUpdatesEnabled(False)
        self.tabla.clear()
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels([titulo for _, titulo in columnas])
        self.tabla.setRowCount(len(filas_pagina))
        for r, fila in enumerate(filas_pagina):
            colores = fila.get("_colores", {})
            for c, (clave, _) in enumerate(columnas):
                contenido = str(fila.get(clave, ""))
                if clave in con_punto and contenido:
                    contenido = "● " + contenido
                item = QTableWidgetItem(contenido)
                if clave in colores:
                    item.setForeground(QBrush(QColor(colores[clave])))
                self.tabla.setItem(r, c, item)

        self.tabla.resizeColumnsToContents()
        for c in range(len(columnas)):
            self.tabla.setColumnWidth(c, max(90, min(self.tabla.columnWidth(c) + 16, 320)))
        self.tabla.setUpdatesEnabled(True)

    # ==================== EXPORTAR ====================
    def exportar(self, formato):
        """Abre la ventana de exportación con el reporte generado y las columnas que están visibles"""
        if not self.reporte or not self.reporte["filas"]:
            return

        columnas = self.columnas_actuales()
        titulo = TIPOS[self.reporte["tipo"]]["reporte"]
        if self.reporte["periodo"]:
            titulo += f" · {self.reporte['periodo']}"

        datos = {
            "tipo": self.reporte["tipo"],
            "titulo": titulo,
            "encabezados": [titulo_columna for _, titulo_columna in columnas],
            "filas": [[fila.get(clave, "") for clave, _ in columnas] for fila in self.reporte["filas"]],
            "filtros": self.reporte["filtros"],
            "fecha_generacion": self.reporte["fecha"],
        }
        dialogo = VentanaExportarReporte(datos, formato, self.window())
        dialogo.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaReportes()
    ventana.setStyleSheet("background-color: #bfbdbe;")
    ventana.resize(1100, 700)
    ventana.show()
    sys.exit(app.exec())