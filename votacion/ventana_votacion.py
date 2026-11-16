import sys
import os
import re
import tempfile
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QLineEdit, QPushButton, QLabel, QScrollArea, QComboBox, QListView, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QPoint, QRect, QRectF, QSize, QEvent, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QPen, QColor, QPolygonF, QIcon
from PyQt6.QtSvg import QSvgRenderer

# --- Aseguramos que la raíz del proyecto y la carpeta votacion/ estén en sys.path ---
# De esta forma se puede importar database (que vive en la raíz) y agregar_centro (que
# vive en votacion/) sin importar si el archivo se ejecuta solo o desde ventana_principal.py.
_DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
_DIR_RAIZ = os.path.abspath(os.path.join(_DIR_ACTUAL, '..'))
for _ruta in (_DIR_RAIZ, _DIR_ACTUAL):
    if _ruta not in sys.path:
        sys.path.insert(0, _ruta)

from database import GestorBD
from agregar_centro import VentanaAgregarCentro


ANCHO_MIN_TARJETA = 290
ALTO_MIN_TARJETA = 150
ESPACIADO = 15

# Estilo del área de desplazamiento (el mismo del registro de trabajadores)
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


# ==================== ICONOS (rutas autocalculables) ====================
_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
CARPETAS_IMAGENES = [
    os.path.join(_DIRECTORIO, '..', 'imagenes'),
    os.path.join(_DIRECTORIO, 'imagenes'),
]
_cache_iconos = {}


def _clave_nombre(texto):
    """'icono-trabajador(azul).svg' -> 'iconotrabajadorazul' (ignora signos, espacios y mayúsculas)"""
    return re.sub(r"[^a-z0-9]", "", os.path.splitext(str(texto))[0].lower())


def buscar_icono(clave):
    """Busca el SVG cuyo nombre coincida con la clave, sin importar guiones, paréntesis o espacios"""
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


def crear_label_icono(clave, alto):
    """QLabel con el icono; si el archivo no existe, queda oculto sin ocupar espacio"""
    lbl = QLabel()
    lbl.setStyleSheet("background: transparent; border: none;")
    pixmap = cargar_pixmap_svg(clave, alto)
    if pixmap:
        lbl.setPixmap(pixmap)
        lbl.setFixedSize(int(round(pixmap.width() / pixmap.devicePixelRatio())), alto)
    else:
        lbl.setFixedSize(0, 0)
        lbl.hide()
    return lbl


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


def formatear_cedula(valor):
    """31776780 -> 31.776.780"""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(valor)


class PildoraTrabajadores(QFrame):
    """Etiqueta con la cantidad de trabajadores; al presionarla se despliega la lista"""
    clicked = pyqtSignal()

    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.setObjectName("pildora")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Ver los trabajadores de este centro")
        self.setStyleSheet("""
            QFrame#pildora {
                background-color: #e6f0ff;
                border: none;
                border-radius: 10px;
            }
            QFrame#pildora:hover {
                background-color: #d3e4ff;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)
        layout.addWidget(crear_label_icono("iconotrabajadorazul", 13))

        lbl_total = QLabel(f"{total} trabajador" + ("" if total == 1 else "es"))
        lbl_total.setStyleSheet("font-size: 11px; font-weight: bold; color: #163e7a; border: none; background: transparent;")
        layout.addWidget(lbl_total)

        lbl_flecha = QLabel("▾")
        lbl_flecha.setStyleSheet("font-size: 11px; font-weight: bold; color: #163e7a; border: none; background: transparent;")
        layout.addWidget(lbl_flecha)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        event.accept()


class PopupTrabajadores(QFrame):
    """Vista desplegable optimizada con los nombres y cédulas de los trabajadores"""
    ANCHO_PANEL = 420
    ALTO_FILA = 54
    SEPARACION = 6
    FILAS_VISIBLES = 5
    MARGEN_SOMBRA = 12

    def __init__(self, nombre_centro, trabajadores, pildora_origen=None, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
                         | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(self.ANCHO_PANEL + self.MARGEN_SOMBRA * 2)
        self.pildora_origen = pildora_origen
        self._filas_indexadas = []  # [(widget_fila, clave_busqueda)]

        externo = QVBoxLayout(self)
        externo.setContentsMargins(self.MARGEN_SOMBRA, self.MARGEN_SOMBRA, self.MARGEN_SOMBRA, self.MARGEN_SOMBRA)

        panel = QFrame()
        panel.setObjectName("panelPopup")
        panel.setStyleSheet("""
            QFrame#panelPopup {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 15px;
            }
        """)
        externo.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        estilo_label = "border: none; background: transparent;"

        # Encabezado: icono, título y cantidad
        fila_encabezado = QHBoxLayout()
        fila_encabezado.setSpacing(8)
        fila_encabezado.addWidget(crear_label_icono("iconotrabajadorazul", 15))
        lbl_titulo = QLabel("Trabajadores registrados")
        lbl_titulo.setStyleSheet(f"font-size: 14px; font-weight: bold; color: #163e7a; {estilo_label}")
        fila_encabezado.addWidget(lbl_titulo)
        fila_encabezado.addStretch()
        lbl_cantidad = QLabel(str(len(trabajadores)))
        lbl_cantidad.setStyleSheet("""
            font-size: 12px; font-weight: bold; color: #163e7a;
            background-color: #e6f0ff; border: none; border-radius: 10px; padding: 2px 10px;
        """)
        fila_encabezado.addWidget(lbl_cantidad)
        layout.addLayout(fila_encabezado)

        lbl_centro = QLabel(str(nombre_centro))
        lbl_centro.setTextFormat(Qt.TextFormat.PlainText)
        lbl_centro.setWordWrap(True)
        lbl_centro.setStyleSheet(f"font-size: 11px; color: #777777; {estilo_label}")
        layout.addWidget(lbl_centro)

        if not trabajadores:
            lbl_vacio = QLabel("Este centro de votación aún no tiene trabajadores registrados.")
            lbl_vacio.setWordWrap(True)
            lbl_vacio.setStyleSheet(f"font-size: 12px; font-weight: bold; color: #4a4a4a; padding: 10px 0px; {estilo_label}")
            layout.addWidget(lbl_vacio)
            return

        # Barra de búsqueda con el mismo estilo e icono de lupa que la ventana madre
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por nombre o cédula...")
        self.txt_buscar.setFixedHeight(34)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #f4f6f9;
                border: 1px solid #dcdcdc;
                border-radius: 17px;
                padding-left: 14px;
                padding-right: 14px;
                color: black;
                font-size: 12px;
                font-weight: bold;
            }
            QLineEdit:focus { border: 2px solid #0833a2; }
        """)
        pixmap_lupa = cargar_pixmap_svg("iconolupa", 15)
        self.accion_lupa = None
        if pixmap_lupa:
            self.accion_lupa = self.txt_buscar.addAction(QIcon(pixmap_lupa), QLineEdit.ActionPosition.LeadingPosition)
        self.txt_buscar.textChanged.connect(self._al_buscar)
        layout.addWidget(self.txt_buscar)

        # Lista con desplazamiento cuando hay más de 5 trabajadores
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(ESTILO_SCROLL)

        self.contenedor_filas = QWidget()
        self.contenedor_filas.setStyleSheet("background: transparent;")
        layout_filas = QVBoxLayout(self.contenedor_filas)
        layout_filas.setContentsMargins(0, 0, 8, 0)
        layout_filas.setSpacing(self.SEPARACION)

        self.lbl_sin_res = QLabel("No se encontraron trabajadores con esa búsqueda.")
        self.lbl_sin_res.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sin_res.setWordWrap(True)
        self.lbl_sin_res.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #777777; padding: 16px; border: none; background: transparent;"
        )
        self.lbl_sin_res.hide()
        layout_filas.addWidget(self.lbl_sin_res)

        # Se crean las filas una única vez para filtrar sin recrear widgets
        for t in trabajadores:
            fila, clave = self._crear_fila(t)
            self._filas_indexadas.append((fila, clave))
            layout_filas.addWidget(fila)

        layout_filas.addStretch()
        self.scroll.setWidget(self.contenedor_filas)

        visibles = min(len(trabajadores), self.FILAS_VISIBLES)
        alto = visibles * self.ALTO_FILA + (visibles - 1) * self.SEPARACION
        if len(trabajadores) > self.FILAS_VISIBLES:
            alto += 30
        self.scroll.setFixedHeight(alto)
        layout.addWidget(self.scroll)

    def paintEvent(self, event):
        """Dibuja una sombra suave sin desenfoque por CPU para máximo rendimiento"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        m = self.MARGEN_SOMBRA
        base = QRectF(m, m, self.width() - m * 2, self.height() - m * 2)
        capas = [
            (8, 16, 4),
            (6, 15, 8),
            (4, 15, 14),
            (2, 15, 22),
        ]
        for expand, radio, alpha in capas:
            painter.setBrush(QColor(0, 0, 0, alpha))
            rect = base.adjusted(-expand, -expand + 3, expand, expand + 3)
            path = QPainterPath()
            path.addRoundedRect(rect, radio, radio)
            painter.drawPath(path)

    def _al_buscar(self, texto):
        if self.accion_lupa is not None:
            self.accion_lupa.setVisible(not texto)

        consulta = texto.strip().lower()
        consulta_sin_puntos = consulta.replace(".", "")
        hay_visibles = False

        self.contenedor_filas.setUpdatesEnabled(False)
        for fila, clave in self._filas_indexadas:
            visible = (
                not consulta
                or consulta in clave
                or (consulta_sin_puntos and consulta_sin_puntos in clave)
            )
            fila.setVisible(visible)
            if visible:
                hay_visibles = True
        self.lbl_sin_res.setVisible(not hay_visibles)
        self.contenedor_filas.setUpdatesEnabled(True)

    def mousePressEvent(self, event):
        # Si se hace clic fuera del popup justo sobre la misma píldora que lo abrió,
        # se cierra y se consume el evento para evitar que se reabra inmediatamente.
        if self.pildora_origen is not None and not self.rect().contains(event.pos()):
            pos_global = event.globalPosition().toPoint()
            rect_pildora = QRect(
                self.pildora_origen.mapToGlobal(QPoint(0, 0)),
                self.pildora_origen.size()
            )
            if rect_pildora.contains(pos_global):
                self.close()
                event.accept()
                return
        super().mousePressEvent(event)

    def _crear_fila(self, t):
        estado = str(t.get("estado_laboral") or "")
        retirado = "retirado" in estado.lower()
        color_nombre = "#d32f2f" if retirado else "#333333"
        fondo = "#fdecec" if retirado else "#f4f6f9"

        fila = QFrame()
        fila.setObjectName("filaTrabajador")
        fila.setFixedHeight(self.ALTO_FILA)
        fila.setStyleSheet(f"""
            QFrame#filaTrabajador {{
                background-color: {fondo};
                border-radius: 10px;
                border: none;
            }}
        """)
        layout = QHBoxLayout(fila)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)

        estilo_label = "border: none; background: transparent;"

        textos = QVBoxLayout()
        textos.setSpacing(2)
        nombre = f"{t.get('nombres', '')} {t.get('apellidos', '')}".strip()
        cedula_raw = str(t.get("cedula_trabajador") or "")
        cedula_fmt = formatear_cedula(cedula_raw)

        lbl_nombre = QLabel(nombre)
        lbl_nombre.setTextFormat(Qt.TextFormat.PlainText)
        lbl_nombre.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color_nombre}; {estilo_label}")
        lbl_cedula = QLabel(f"C.I. {cedula_fmt}")
        lbl_cedula.setStyleSheet(f"font-size: 12px; color: #777777; {estilo_label}")
        textos.addStretch()
        textos.addWidget(lbl_nombre)
        textos.addWidget(lbl_cedula)
        textos.addStretch()
        layout.addLayout(textos, stretch=1)

        if estado:
            lbl_estado = QLabel(estado)
            lbl_estado.setStyleSheet(
                f"font-size: 11px; font-weight: bold; color: {'#d32f2f' if retirado else '#163e7a'}; {estilo_label}"
            )
            layout.addWidget(lbl_estado)

        clave_busqueda = f"{nombre.lower()} {cedula_raw} {cedula_fmt.lower()}"
        return fila, clave_busqueda


class TarjetaCentro(QFrame):
    """Tarjeta blanca con borde azul que representa un centro de votación"""
    cliqueada = pyqtSignal(object)
    ver_trabajadores = pyqtSignal(object, object)  # (tarjeta, píldora)

    MARGEN_IZQ = 18
    MARGEN_DER = 15
    MARGEN_V = 15
    SEPARACION = 8
    ESPACIO_ICONO = 6

    def __init__(self, datos, parent=None):
        super().__init__(parent)
        self.datos = datos
        self.seleccionada = False
        self._pulida = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(ANCHO_MIN_TARJETA)
        self.setMinimumHeight(ALTO_MIN_TARJETA)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.aplicar_estilo()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.MARGEN_IZQ, self.MARGEN_V, self.MARGEN_DER, self.MARGEN_V)
        layout.setSpacing(self.SEPARACION)

        estilo_label = "border: none; background: transparent;"

        # Nombre del centro
        self.lbl_nombre = QLabel(str(datos.get("nombre_centro", "N/D")))
        self.lbl_nombre.setTextFormat(Qt.TextFormat.PlainText)
        self.lbl_nombre.setWordWrap(True)
        self.lbl_nombre.setStyleSheet(f"font-size: 15px; font-weight: bold; color: #163e7a; {estilo_label}")

        # Ubicación (parroquia · municipio, estado) con el icono de ubicación
        self.icono_ubicacion = crear_label_icono("iconoubicacion", 16)
        self.lbl_ubicacion = QLabel(f"{datos.get('parroquia', 'N/D')} · {datos.get('municipio', 'N/D')}, {datos.get('estado', 'N/D')}")
        self.lbl_ubicacion.setTextFormat(Qt.TextFormat.PlainText)
        self.lbl_ubicacion.setWordWrap(True)
        self.lbl_ubicacion.setStyleSheet(f"font-size: 12px; font-weight: bold; color: #555555; {estilo_label}")

        fila_ubicacion = QHBoxLayout()
        fila_ubicacion.setContentsMargins(0, 0, 0, 0)
        fila_ubicacion.setSpacing(self.ESPACIO_ICONO)
        fila_ubicacion.addWidget(self.icono_ubicacion, alignment=Qt.AlignmentFlag.AlignTop)
        fila_ubicacion.addWidget(self.lbl_ubicacion, stretch=1)

        # Dirección completa
        direccion = str(datos.get("direccion_centro", "")).strip()
        self.lbl_direccion = QLabel(direccion or "Sin dirección registrada")
        self.lbl_direccion.setTextFormat(Qt.TextFormat.PlainText)
        self.lbl_direccion.setWordWrap(True)
        self.lbl_direccion.setStyleSheet(f"font-size: 12px; color: #777777; {estilo_label}")

        # Etiqueta con la cantidad de trabajadores
        total = int(datos.get("total_trabajadores", 0) or 0)
        self.pildora = PildoraTrabajadores(total)
        self.pildora.clicked.connect(lambda: self.ver_trabajadores.emit(self, self.pildora))

        layout.addWidget(self.lbl_nombre)
        layout.addLayout(fila_ubicacion)
        layout.addWidget(self.lbl_direccion)
        layout.addStretch()
        layout.addWidget(self.pildora, alignment=Qt.AlignmentFlag.AlignLeft)

    def calcular_alto(self, ancho_tarjeta):
        """Alto necesario para que todo el texto se lea completo con el ancho dado"""
        if not self._pulida:
            for widget in [self, *self.findChildren(QWidget)]:
                widget.ensurePolished()
            self._pulida = True

        ancho = max(60, ancho_tarjeta - 8 - self.MARGEN_IZQ - self.MARGEN_DER - 2)
        ancho_texto_ubic = max(40, ancho - self.icono_ubicacion.width() - self.ESPACIO_ICONO)

        alto_nombre = self.lbl_nombre.heightForWidth(ancho)
        alto_ubic = max(self.lbl_ubicacion.heightForWidth(ancho_texto_ubic), self.icono_ubicacion.height())
        alto_dir = self.lbl_direccion.heightForWidth(ancho)
        alto_pildora = self.pildora.sizeHint().height()

        alto = (2 * self.MARGEN_V + 4 + alto_nombre + alto_ubic + alto_dir
                + alto_pildora + 4 * self.SEPARACION + 4)
        return max(ALTO_MIN_TARJETA, alto)

    def aplicar_estilo(self):
        if self.seleccionada:
            fondo, hover, borde, izquierdo = "#eef4fd", "#e6f0ff", "2px solid #0833a2", "6px solid #0833a2"
        else:
            fondo, hover, borde, izquierdo = "#ffffff", "#f8fafc", "none", "6px solid #163e7a"

        self.setStyleSheet(f"""
            TarjetaCentro {{
                background-color: {fondo};
                border-radius: 15px;
                border: {borde};
                border-left: {izquierdo};
            }}
            TarjetaCentro:hover {{
                background-color: {hover};
            }}
        """)

    def set_seleccionada(self, valor):
        self.seleccionada = valor
        self.aplicar_estilo()

    def mousePressEvent(self, event):
        self.cliqueada.emit(self)
        super().mousePressEvent(event)


class VentanaVotacion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tarjetas = []
        self.tarjeta_seleccionada = None
        self._columnas = 0
        self.popup_trabajadores = None

        self.timer_busqueda = QTimer(self)
        self.timer_busqueda.setSingleShot(True)
        self.timer_busqueda.setInterval(250)
        self.timer_busqueda.timeout.connect(self.cargar_centros)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        # ==================== TARJETA SUPERIOR (título, filtros y botones) ====================
        panel_superior = QFrame()
        panel_superior.setObjectName("panelSuperior")
        panel_superior.setStyleSheet("""
            QFrame#panelSuperior {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        layout_superior = QVBoxLayout(panel_superior)
        layout_superior.setContentsMargins(20, 18, 20, 18)
        layout_superior.setSpacing(14)

        fila_titulo = QHBoxLayout()
        lbl_titulo = QLabel("Centros de votación")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        self.lbl_contador = QLabel("")
        self.lbl_contador.setStyleSheet("font-size: 13px; font-weight: bold; color: #777777; border: none; background: transparent;")
        fila_titulo.addWidget(lbl_titulo)
        fila_titulo.addStretch()
        fila_titulo.addWidget(self.lbl_contador)
        layout_superior.addLayout(fila_titulo)

        fila_controles = QHBoxLayout()
        fila_controles.setSpacing(10)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por nombre o dirección...")
        self.txt_buscar.setToolTip("Buscar por nombre, dirección o parroquia")
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
            QComboBox:disabled { background-color: #eceff3; color: #aaaaaa; }
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

        self.cmb_estado = QComboBox()
        self.cmb_estado.setView(QListView())
        self.cmb_estado.setFixedSize(185, 36)
        self.cmb_estado.setStyleSheet(estilo_combo)
        self.cmb_estado.setToolTip("Filtrar por estado")

        self.cmb_municipio = QComboBox()
        self.cmb_municipio.setView(QListView())
        self.cmb_municipio.setFixedSize(185, 36)
        self.cmb_municipio.setStyleSheet(estilo_combo)
        self.cmb_municipio.setToolTip("Filtrar por municipio")

        estilo_boton_azul = """
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

        self.btn_modificar = QPushButton(" Modificar")
        self.btn_modificar.setFixedHeight(36)
        self.btn_modificar.setMinimumWidth(130)
        self.btn_modificar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_modificar.setEnabled(False)
        self.btn_modificar.setToolTip("Selecciona un centro de votación para modificarlo")
        self.btn_modificar.setStyleSheet(estilo_boton_azul)
        pixmap_lapiz = cargar_pixmap_svg("iconolapiz", 16)
        if pixmap_lapiz:
            icono_lapiz = QIcon()
            icono_lapiz.addPixmap(pixmap_lapiz, QIcon.Mode.Normal)
            icono_lapiz.addPixmap(pixmap_lapiz, QIcon.Mode.Disabled)
            self.btn_modificar.setIcon(icono_lapiz)
            self.btn_modificar.setIconSize(QSize(16, 16))
        self.btn_modificar.clicked.connect(self.modificar_centro)

        self.btn_agregar = QPushButton("＋  Agregar centro")
        self.btn_agregar.setFixedHeight(36)
        self.btn_agregar.setMinimumWidth(160)
        self.btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar.setStyleSheet(estilo_boton_azul)
        self.btn_agregar.clicked.connect(self.agregar_centro)

        fila_controles.addWidget(self.txt_buscar, stretch=1)
        fila_controles.addWidget(self.cmb_estado)
        fila_controles.addWidget(self.cmb_municipio)
        fila_controles.addSpacing(10)
        fila_controles.addWidget(self.btn_modificar)
        fila_controles.addWidget(self.btn_agregar)
        layout_superior.addLayout(fila_controles)

        layout_principal.addWidget(panel_superior)

        # ==================== ÁREA DE TARJETAS ====================
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(ESTILO_SCROLL)

        contenedor = QWidget()
        contenedor.setStyleSheet("background: transparent;")
        layout_contenedor = QVBoxLayout(contenedor)
        layout_contenedor.setContentsMargins(0, 0, 0, 0)
        layout_contenedor.setSpacing(0)

        self.zona_tarjetas = QWidget()
        self.zona_tarjetas.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.zona_tarjetas)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(ESPACIADO)
        layout_contenedor.addWidget(self.zona_tarjetas)

        self.lbl_vacio = QLabel("No se encontraron centros de votación con esos filtros.")
        self.lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_vacio.setStyleSheet("font-size: 14px; font-weight: bold; color: #4a4a4a; background: transparent; padding: 40px;")
        self.lbl_vacio.hide()
        layout_contenedor.addWidget(self.lbl_vacio)

        layout_contenedor.addStretch()
        self.scroll.setWidget(contenedor)
        layout_principal.addWidget(self.scroll, stretch=1)

        self.cargar_estados()
        self.cmb_estado.currentIndexChanged.connect(self.al_cambiar_estado)
        self.cmb_municipio.currentIndexChanged.connect(self.cargar_centros)
        self.cargar_centros()

        self.scroll.viewport().installEventFilter(self)

    # ==================== BASE DE DATOS ====================
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
            print(f"Error al consultar los centros de votación: {e}")
        return []

    # ==================== FILTROS ====================
    def cargar_estados(self):
        self.cmb_estado.blockSignals(True)
        self.cmb_estado.clear()
        self.cmb_estado.addItem("Todos los estados", None)
        for fila in self._consultar("SELECT id_estado, nombre_estado FROM estados ORDER BY nombre_estado"):
            self.cmb_estado.addItem(fila["nombre_estado"], fila["id_estado"])
        self.cmb_estado.setCurrentIndex(0)
        self.cmb_estado.blockSignals(False)
        self.cargar_municipios()

    def cargar_municipios(self):
        self.cmb_municipio.blockSignals(True)
        self.cmb_municipio.clear()
        self.cmb_municipio.addItem("Todos los municipios", None)

        id_estado = self.cmb_estado.currentData()
        if id_estado is None:
            self.cmb_municipio.setEnabled(False)
        else:
            self.cmb_municipio.setEnabled(True)
            filas = self._consultar(
                "SELECT id_municipio, nombre_municipio FROM municipios WHERE id_estado_fk = %s ORDER BY nombre_municipio",
                (id_estado,)
            )
            for fila in filas:
                self.cmb_municipio.addItem(fila["nombre_municipio"], fila["id_municipio"])

        self.cmb_municipio.setCurrentIndex(0)
        self.cmb_municipio.blockSignals(False)

    def al_cambiar_estado(self):
        self.cargar_municipios()
        self.cargar_centros()

    def al_escribir_busqueda(self, texto):
        if self.accion_lupa is not None:
            self.accion_lupa.setVisible(not texto)
        self.timer_busqueda.start()

    # ==================== TARJETAS ====================
    def cargar_centros(self):
        self.tarjeta_seleccionada = None
        self.btn_modificar.setEnabled(False)
        for tarjeta in self.tarjetas:
            self.grid.removeWidget(tarjeta)
            tarjeta.deleteLater()
        self.tarjetas = []

        sql = """
            SELECT cv.id_centro_votacion, cv.nombre_centro, cv.direccion_centro,
                   p.id_parroquia, p.nombre_parroquia AS parroquia,
                   m.id_municipio, m.nombre_municipio AS municipio,
                   e.id_estado, e.nombre_estado AS estado,
                   (SELECT COUNT(*) FROM trabajadores t
                    WHERE t.id_centro_votacion_fk = cv.id_centro_votacion) AS total_trabajadores
            FROM centros_votacion cv
            JOIN parroquias p ON cv.id_parroquia_fk = p.id_parroquia
            JOIN municipios m ON p.id_municipio_fk = m.id_municipio
            JOIN estados e ON m.id_estado_fk = e.id_estado
            WHERE 1=1
        """
        params = []

        id_estado = self.cmb_estado.currentData()
        if id_estado is not None:
            sql += " AND e.id_estado = %s"
            params.append(id_estado)

        id_municipio = self.cmb_municipio.currentData()
        if id_municipio is not None:
            sql += " AND m.id_municipio = %s"
            params.append(id_municipio)

        texto = self.txt_buscar.text().strip()
        if texto:
            sql += " AND (cv.nombre_centro LIKE %s OR cv.direccion_centro LIKE %s OR p.nombre_parroquia LIKE %s)"
            patron = f"%{texto}%"
            params.extend([patron, patron, patron])

        sql += " ORDER BY cv.nombre_centro"

        centros = self._consultar(sql, tuple(params))

        for datos in centros:
            tarjeta = TarjetaCentro(datos, self.zona_tarjetas)
            tarjeta.cliqueada.connect(self.alternar_seleccion)
            tarjeta.ver_trabajadores.connect(self.mostrar_trabajadores)
            self.tarjetas.append(tarjeta)

        total = len(self.tarjetas)
        self.lbl_contador.setText(f"{total} centro" + ("" if total == 1 else "s") + " de votación")
        self.lbl_vacio.setVisible(total == 0)

        self.reacomodar(forzar=True)

    def reacomodar(self, forzar=False):
        ancho = self.scroll.viewport().width()
        columnas = max(1, (ancho + ESPACIADO) // (ANCHO_MIN_TARJETA + ESPACIADO))

        if forzar or columnas != self._columnas:
            self._columnas = columnas
            for tarjeta in self.tarjetas:
                self.grid.removeWidget(tarjeta)
            for i, tarjeta in enumerate(self.tarjetas):
                self.grid.addWidget(tarjeta, i // columnas, i % columnas)
                tarjeta.show()
            for c in range(30):
                self.grid.setColumnStretch(c, 1 if c < columnas else 0)

        if self.tarjetas:
            ancho_tarjeta = (ancho - ESPACIADO * (columnas - 1)) // columnas
            alto = max(t.calcular_alto(ancho_tarjeta) for t in self.tarjetas)
            for tarjeta in self.tarjetas:
                tarjeta.setFixedHeight(alto)

    def eventFilter(self, obj, event):
        if obj is self.scroll.viewport() and event.type() == QEvent.Type.Resize:
            self.reacomodar()
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        self.reacomodar(forzar=True)

    def seleccionar_tarjeta(self, tarjeta):
        """Marca como seleccionada la tarjeta indicada"""
        if self.tarjeta_seleccionada is not tarjeta:
            if self.tarjeta_seleccionada is not None:
                self.tarjeta_seleccionada.set_seleccionada(False)
            tarjeta.set_seleccionada(True)
            self.tarjeta_seleccionada = tarjeta
        self.btn_modificar.setEnabled(True)

    def mostrar_trabajadores(self, tarjeta, pildora):
        """Despliega, debajo de la etiqueta, la lista de trabajadores del centro de votación"""
        self.seleccionar_tarjeta(tarjeta)

        if self.popup_trabajadores is not None:
            try:
                if self.popup_trabajadores.isVisible():
                    misma_pildora = self.popup_trabajadores.pildora_origen is pildora
                    self.popup_trabajadores.close()
                    if misma_pildora:
                        return
            except RuntimeError:
                pass
            self.popup_trabajadores = None

        trabajadores = self._consultar("""
            SELECT t.cedula_trabajador, t.nombres, t.apellidos, el.descripcion_estado AS estado_laboral
            FROM trabajadores t
            LEFT JOIN estados_laborales el ON t.id_estado_laboral_fk = el.id_estado_laboral
            WHERE t.id_centro_votacion_fk = %s
            ORDER BY t.nombres, t.apellidos
        """, (tarjeta.datos["id_centro_votacion"],))

        self.popup_trabajadores = PopupTrabajadores(
            tarjeta.datos.get("nombre_centro", ""), trabajadores, pildora, self.window()
        )
        popup = self.popup_trabajadores
        popup.destroyed.connect(lambda: setattr(self, "popup_trabajadores", None))
        popup.adjustSize()

        pantalla = pildora.screen().availableGeometry()
        debajo = pildora.mapToGlobal(QPoint(0, pildora.height()))
        x = debajo.x() - 12
        y = debajo.y() - 8
        if y + popup.height() > pantalla.bottom():
            y = pildora.mapToGlobal(QPoint(0, 0)).y() - popup.height() + 8
        x = max(pantalla.left(), min(x, pantalla.right() - popup.width()))
        popup.move(x, y)
        popup.show()

    def alternar_seleccion(self, tarjeta):
        if self.tarjeta_seleccionada is tarjeta:
            tarjeta.set_seleccionada(False)
            self.tarjeta_seleccionada = None
            self.btn_modificar.setEnabled(False)
        else:
            self.seleccionar_tarjeta(tarjeta)

    # ==================== ACCIONES ====================
    def agregar_centro(self):
        dialogo = VentanaAgregarCentro(self.window())
        if dialogo.exec():
            estado_actual = self.cmb_estado.currentData()
            municipio_actual = self.cmb_municipio.currentData()

            self.cargar_estados()

            # Si el filtro actual ocultaría el nuevo centro, se muestra todos o la ubicación creada
            if estado_actual is not None and estado_actual != dialogo.id_estado_resultado:
                idx_est = 0
            else:
                idx_est = self.cmb_estado.findData(estado_actual)
            self.cmb_estado.setCurrentIndex(max(0, idx_est))
            self.cargar_municipios()

            if municipio_actual is not None and municipio_actual != dialogo.id_municipio_resultado:
                idx_mun = 0
            else:
                idx_mun = self.cmb_municipio.findData(municipio_actual)
            self.cmb_municipio.setCurrentIndex(max(0, idx_mun))

            self.cargar_centros()

            if dialogo.id_centro is not None:
                for tarjeta in self.tarjetas:
                    if tarjeta.datos.get("id_centro_votacion") == dialogo.id_centro:
                        self.seleccionar_tarjeta(tarjeta)
                        self.scroll.ensureWidgetVisible(tarjeta)
                        break

    def modificar_centro(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaVotacion()
    ventana.setStyleSheet("background-color: #bfbdbe;")
    ventana.resize(1100, 650)
    ventana.show()
    sys.exit(app.exec())