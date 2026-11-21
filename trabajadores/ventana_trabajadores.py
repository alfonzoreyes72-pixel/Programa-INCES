import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QLabel, QScrollArea, QSizePolicy, QDialog
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

# Importación de la ventana modal de registro
try:
    from .registro_trabajadores import RegistroTrabajadores
except ImportError:
    from registro_trabajadores import RegistroTrabajadores

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


def formatear_cedula(valor):
    """31776780 -> 31.776.780"""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(valor)


# ==================== ICONOS (rutas autocalculables) ====================
# Las imágenes viven en la carpeta 'imagenes' de la raíz del proyecto (junto a ventana_principal.py).
# La ruta se calcula a partir de la ubicación de este archivo, así funciona en cualquier computadora.
_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
CARPETAS_IMAGENES = [
    os.path.join(_DIRECTORIO, '..', 'imagenes'),
    os.path.join(_DIRECTORIO, 'imagenes'),
]


def _clave_nombre(texto):
    """'icono-lapiz.svg' -> 'iconolapiz' (ignora signos, espacios y mayúsculas)"""
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


ESTILO_BOTON_AZUL = """
    QPushButton {
        background-color: #0833a2;
        color: white;
        border: 2px solid #0833a2;
        border-radius: 18px;
        padding: 0px 14px;
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


class FilaTrabajador(QFrame):
    """Componente interactivo para cada fila de trabajador en la lista"""
    cliqueado = pyqtSignal(dict)

    def __init__(self, datos_trabajador, parent=None):
        super().__init__(parent)
        self.datos = datos_trabajador
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        
        # Trabajador retirado: fila en rojo pálido y nombre en rojo
        self.es_retirado = "retirado" in str(self.datos.get("estado_laboral", "")).lower()
        self.seleccionada = False
        color_nombre = "#d32f2f" if self.es_retirado else "#333333"
        self.aplicar_estilo()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)

        self.lbl_nombre = QLabel(self.datos["nombre"])
        self.lbl_nombre.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color_nombre}; border: none; background: transparent;")
        
        self.lbl_cedula = QLabel(formatear_cedula(self.datos["cedula"]))
        self.lbl_cedula.setStyleSheet("font-size: 14px; font-weight: bold; color: #555555; border: none; background: transparent;")

        layout.addWidget(self.lbl_nombre)
        layout.addStretch()
        layout.addWidget(self.lbl_cedula)

    def aplicar_estilo(self):
        """Fila normal, retirada (rojo pálido) y/o seleccionada (borde azul)"""
        if self.seleccionada:
            fondo = "#fdecec" if self.es_retirado else "#eef4fd"
            fondo_hover = "#fadcdc" if self.es_retirado else "#e6f0ff"
            borde = "border: 2px solid #0833a2;"
        else:
            fondo = "#fdecec" if self.es_retirado else "transparent"
            fondo_hover = "#fadcdc" if self.es_retirado else "#e8ebf0"
            borde = "border: none; border-bottom: 1px solid #eaeaea;"

        self.setStyleSheet(f"""
            FilaTrabajador {{
                background-color: {fondo};
                border-radius: 10px;
                {borde}
            }}
            FilaTrabajador:hover {{
                background-color: {fondo_hover};
            }}
        """)

    def set_seleccionada(self, valor):
        if self.seleccionada != valor:
            self.seleccionada = valor
            self.aplicar_estilo()

    def mousePressEvent(self, event):
        self.cliqueado.emit(self.datos)
        super().mousePressEvent(event)


class TarjetaMetricaInteractiva(QFrame):
    """Tarjeta superior interactiva que permite filtrar al hacer clic"""
    cliqueada = pyqtSignal(str)

    def __init__(self, titulo, valor, color_borde, filtro_tipo="", parent=None):
        super().__init__(parent)
        self.filtro_tipo = filtro_tipo
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 15px;
                border-left: 6px solid {color_borde};
                border-top: none;
                border-right: none;
                border-bottom: none;
            }}
            QFrame:hover {{
                background-color: #f8fafc;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        
        self.lbl_tit = QLabel(titulo)
        self.lbl_tit.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; border: none; background: transparent;")
        
        self.lbl_val = QLabel(valor)
        self.lbl_val.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color_borde}; border: none; background: transparent;")
        
        layout.addWidget(self.lbl_tit)
        layout.addWidget(self.lbl_val)

    def mousePressEvent(self, event):
        self.cliqueada.emit(self.filtro_tipo)
        super().mousePressEvent(event)


class VentanaTrabajadores(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.trabajador_seleccionado = None
        self.filtro_actual = "todos"

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        self.contenedor_izq = QWidget()
        layout_izq = QVBoxLayout(self.contenedor_izq)
        layout_izq.setContentsMargins(0, 0, 0, 0)
        layout_izq.setSpacing(15)

        # 1. Tarjetas Superiores
        layout_tarjetas = QHBoxLayout()
        layout_tarjetas.setSpacing(15)

        self.card_total = TarjetaMetricaInteractiva("Total Trabajadores", "0", "#163e7a", "todos")
        self.card_total.cliqueada.connect(self.cambiar_filtro_metrica)

        self.card_fijo = TarjetaMetricaInteractiva("Contrato Fijo", "0", "#235299", "fijo")
        self.card_fijo.cliqueada.connect(self.cambiar_filtro_metrica)

        self.card_foraneos = TarjetaMetricaInteractiva("Votantes Foráneos", "0", "#3b6ba3", "foraneos")
        self.card_foraneos.cliqueada.connect(self.cambiar_filtro_metrica)

        layout_tarjetas.addWidget(self.card_total)
        layout_tarjetas.addWidget(self.card_fijo)
        layout_tarjetas.addWidget(self.card_foraneos)
        layout_izq.addLayout(layout_tarjetas)

        # 2. Panel del Listado
        self.panel_listado = QFrame()
        self.panel_listado.setObjectName("panelListado")
        self.panel_listado.setStyleSheet("""
            QFrame#panelListado {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        
        self.panel_listado.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout_panel = QVBoxLayout(self.panel_listado)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(15)

        self.lbl_titulo_lista = QLabel("Listado de trabajadores")
        self.lbl_titulo_lista.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(self.lbl_titulo_lista)

        controles_layout = QHBoxLayout()
        controles_layout.setSpacing(10)

        self.btn_agregar = QPushButton("+ Agregar")
        self.btn_agregar.setFixedSize(110, 36)
        self.btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar.setStyleSheet(ESTILO_BOTON_AZUL)
        self.btn_agregar.clicked.connect(self.abrir_dialogo_agregar)
        controles_layout.addWidget(self.btn_agregar)

        # Modificar: solo se activa cuando hay un trabajador seleccionado (se ve en azul apagado si no)
        self.btn_modificar = QPushButton(" Modificar")
        self.btn_modificar.setFixedSize(130, 36)
        self.btn_modificar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_modificar.setEnabled(False)
        self.btn_modificar.setToolTip("Selecciona un trabajador para modificarlo")
        self.btn_modificar.setStyleSheet(ESTILO_BOTON_AZUL)
        pixmap_lapiz = cargar_pixmap_svg("iconolapiz", 16)
        if pixmap_lapiz:
            # El mismo icono blanco en estado normal y deshabilitado, para que no se vea grisáceo
            icono_lapiz = QIcon()
            icono_lapiz.addPixmap(pixmap_lapiz, QIcon.Mode.Normal)
            icono_lapiz.addPixmap(pixmap_lapiz, QIcon.Mode.Disabled)
            self.btn_modificar.setIcon(icono_lapiz)
            self.btn_modificar.setIconSize(QSize(16, 16))
        self.btn_modificar.clicked.connect(self.abrir_dialogo_modificar)
        controles_layout.addWidget(self.btn_modificar)

        controles_layout.addStretch()

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("🔍 Buscar por cédula o nombre...")
        self.txt_buscar.setFixedSize(240, 36)
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
        self.txt_buscar.textChanged.connect(lambda: self.cargar_trabajadores_desde_bd())
        controles_layout.addWidget(self.txt_buscar)

        layout_panel.addLayout(controles_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.contenedor_filas = QWidget()
        self.contenedor_filas.setStyleSheet("background: transparent; border: none;")
        self.layout_filas = QVBoxLayout(self.contenedor_filas)
        self.layout_filas.setContentsMargins(0, 0, 0, 0)
        self.layout_filas.setSpacing(5)
        self.layout_filas.addStretch()

        self.scroll_area.setWidget(self.contenedor_filas)
        layout_panel.addWidget(self.scroll_area)

        layout_izq.addWidget(self.panel_listado)
        layout_principal.addWidget(self.contenedor_izq, stretch=3)

        # 3. Tarjeta Lateral de Detalle
        self.panel_detalles = QFrame()
        self.panel_detalles.setObjectName("panelDetalles")
        self.panel_detalles.setFixedWidth(310)
        self.panel_detalles.setStyleSheet("""
            QFrame#panelDetalles {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        
        layout_detalles = QVBoxLayout(self.panel_detalles)
        layout_detalles.setContentsMargins(20, 20, 20, 20)
        layout_detalles.setSpacing(12)

        header_detalles = QHBoxLayout()
        header_detalles.addStretch()
        self.btn_cerrar_detalle = QPushButton("✕")
        self.btn_cerrar_detalle.setFixedSize(28, 28)
        self.btn_cerrar_detalle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cerrar_detalle.setStyleSheet("""
            QPushButton {
                background-color: #f4f6f9;
                color: #555555;
                border-radius: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #e0dede; color: black; }
        """)
        self.btn_cerrar_detalle.clicked.connect(self.ocultar_detalles)
        header_detalles.addWidget(self.btn_cerrar_detalle)
        layout_detalles.addLayout(header_detalles)

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
        
        avatar_layout = QHBoxLayout()
        avatar_layout.addStretch()
        avatar_layout.addWidget(self.lbl_avatar)
        avatar_layout.addStretch()
        layout_detalles.addLayout(avatar_layout)

        self.lbl_nombre_detalle = QLabel("Nombre del Trabajador")
        self.lbl_nombre_detalle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nombre_detalle.setWordWrap(True)
        self.lbl_nombre_detalle.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_nombre_detalle.setStyleSheet("font-size: 16px; font-weight: bold; color: #163e7a; border: none; background: transparent;")
        layout_detalles.addWidget(self.lbl_nombre_detalle)

        separador = QFrame()
        separador.setFixedHeight(1)
        separador.setStyleSheet("background-color: #f0f0f0; border: none;")
        layout_detalles.addWidget(separador)

        self.scroll_detalles = QScrollArea()
        self.scroll_detalles.setWidgetResizable(True)
        self.scroll_detalles.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #f4f6f9; width: 8px; border-radius: 4px; margin: 0px; }
            QScrollBar::handle:vertical { background: #c0c0c0; border-radius: 4px; min-height: 20px; }
        """)

        self.contenido_scroll_detalles = QWidget()
        self.contenido_scroll_detalles.setStyleSheet("background: transparent; border: none;")
        layout_scroll_detalles = QVBoxLayout(self.contenido_scroll_detalles)
        layout_scroll_detalles.setContentsMargins(0, 0, 5, 0)
        layout_scroll_detalles.setSpacing(10)

        self.lbl_detalles_contenido = QLabel()
        self.lbl_detalles_contenido.setWordWrap(True)
        self.lbl_detalles_contenido.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_detalles_contenido.setStyleSheet("font-size: 13px; color: #444444; border: none; background: transparent; line-height: 140%;")
        layout_scroll_detalles.addWidget(self.lbl_detalles_contenido)
        layout_scroll_detalles.addStretch()

        self.scroll_detalles.setWidget(self.contenido_scroll_detalles)
        layout_detalles.addWidget(self.scroll_detalles)
        
        layout_principal.addWidget(self.panel_detalles)
        self.panel_detalles.hide()

        self.actualizar_metricas_globales()
        self.cargar_trabajadores_desde_bd()

    def showEvent(self, event):
        super().showEvent(event)
        # Al volver a esta ventana se recargan los datos, para ver los cambios hechos en otras ventanas
        # (por ejemplo, un centro de votación que se modificó); se conservan filtros, búsqueda y selección
        self.cargar_trabajadores_desde_bd()

    def cambiar_filtro_metrica(self, tipo_filtro):
        self.filtro_actual = tipo_filtro
        if tipo_filtro == "foraneos":
            self.lbl_titulo_lista.setText("Listado de trabajadores - Votantes Foráneos")
        elif tipo_filtro == "fijo":
            self.lbl_titulo_lista.setText("Listado de trabajadores - Contrato Fijo")
        else:
            self.lbl_titulo_lista.setText("Listado de trabajadores")
        self.cargar_trabajadores_desde_bd()

    def actualizar_metricas_globales(self):
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                
                cursor.execute("SELECT COUNT(*) AS total FROM trabajadores")
                res_total = cursor.fetchone()
                self.card_total.lbl_val.setText(str(res_total['total'] if res_total else 0))

                cursor.execute("SELECT COUNT(*) AS total FROM trabajadores t JOIN estados_laborales el ON t.id_estado_laboral_fk = el.id_estado_laboral WHERE el.descripcion_estado LIKE '%fijo%'")
                res_fijo = cursor.fetchone()
                self.card_fijo.lbl_val.setText(str(res_fijo['total'] if res_fijo else 0))

                sql_foraneos = """
                    SELECT COUNT(*) AS total FROM trabajadores t
                    JOIN centros_votacion cv ON t.id_centro_votacion_fk = cv.id_centro_votacion
                    JOIN parroquias p ON cv.id_parroquia_fk = p.id_parroquia
                    JOIN municipios m ON p.id_municipio_fk = m.id_municipio
                    WHERE LOWER(m.nombre_municipio) NOT LIKE '%maturín%' AND LOWER(m.nombre_municipio) NOT LIKE '%maturin%'
                """
                cursor.execute(sql_foraneos)
                res_foraneos = cursor.fetchone()
                self.card_foraneos.lbl_val.setText(str(res_foraneos['total'] if res_foraneos else 0))

                cursor.close()
        except Exception as e:
            print(f"Error al actualizar métricas: {e}")

    def cargar_trabajadores_desde_bd(self):
        while self.layout_filas.count() > 1:
            item = self.layout_filas.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        texto_busqueda = self.txt_buscar.text().strip()

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                
                # Asegurar que la tabla departamentos exista por seguridad
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS departamentos (
                        id_departamento INT AUTO_INCREMENT PRIMARY KEY,
                        nombre_departamento VARCHAR(100) NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
                """)
                conexion.commit()

                sql = """
                    SELECT 
                        t.cedula_trabajador AS cedula,
                        CONCAT(t.nombres, ' ', t.apellidos) AS nombre,
                        t.fecha_nacimiento,
                        t.telefono,
                        t.correo,
                        t.sexo,
                        t.direccion,
                        t.nombres AS nombres,
                        t.apellidos AS apellidos,
                        t.id_departamento_fk AS id_departamento,
                        t.id_estado_laboral_fk AS id_estado_laboral,
                        t.id_centro_votacion_fk AS id_centro_votacion,
                        COALESCE(el.descripcion_estado, 'N/D') AS estado_laboral,
                        COALESCE(d.nombre_departamento, 'N/D') AS departamento,
                        COALESCE(e.nombre_estado, 'N/D') AS estado_cv,
                        COALESCE(m.nombre_municipio, 'N/D') AS municipio_cv,
                        COALESCE(cv.nombre_centro, 'N/D') AS centro_cv
                    FROM trabajadores t
                    LEFT JOIN estados_laborales el ON t.id_estado_laboral_fk = el.id_estado_laboral
                    LEFT JOIN departamentos d ON t.id_departamento_fk = d.id_departamento
                    LEFT JOIN centros_votacion cv ON t.id_centro_votacion_fk = cv.id_centro_votacion
                    LEFT JOIN parroquias p ON cv.id_parroquia_fk = p.id_parroquia
                    LEFT JOIN municipios m ON p.id_municipio_fk = m.id_municipio
                    LEFT JOIN estados e ON m.id_estado_fk = e.id_estado
                    WHERE 1=1
                """
                
                params = []

                if self.filtro_actual == "foraneos":
                    sql += " AND (LOWER(m.nombre_municipio) NOT LIKE '%maturín%' AND LOWER(m.nombre_municipio) NOT LIKE '%maturin%')"
                elif self.filtro_actual == "fijo":
                    sql += " AND LOWER(el.descripcion_estado) LIKE '%fijo%'"

                if texto_busqueda:
                    sql += """ AND (CAST(t.cedula_trabajador AS CHAR) LIKE %s 
                                   OR t.nombres LIKE %s 
                                   OR t.apellidos LIKE %s 
                                   OR CONCAT(t.nombres, ' ', t.apellidos) LIKE %s)"""
                    patron = f"%{texto_busqueda}%"
                    # La cédula se guarda sin puntos, así que también se busca sin ellos
                    patron_cedula = f"%{texto_busqueda.replace('.', '')}%"
                    params.extend([patron_cedula, patron, patron, patron])

                cursor.execute(sql, tuple(params))
                trabajadores = cursor.fetchall()
                cursor.close()

                trabajadores_normales = [
                    t for t in trabajadores
                    if "retirado" not in str(t.get("estado_laboral", "")).lower()
                ]
                trabajadores_retirados = [
                    t for t in trabajadores
                    if "retirado" in str(t.get("estado_laboral", "")).lower()
                ]

                def agregar_fila(trabajador):
                    fila = FilaTrabajador(trabajador)
                    fila.cliqueado.connect(self.mostrar_detalles_trabajador)
                    self.layout_filas.insertWidget(self.layout_filas.count() - 1, fila)

                for t in trabajadores_normales:
                    agregar_fila(t)

                if trabajadores_retirados:
                    separador_retirados = QWidget()
                    separador_retirados.setStyleSheet("background: transparent;")
                    sep_layout = QHBoxLayout(separador_retirados)
                    sep_layout.setContentsMargins(4, 14, 4, 5)
                    sep_layout.setSpacing(10)
                    linea_izq = QFrame()
                    linea_izq.setFixedHeight(1)
                    linea_izq.setStyleSheet("background-color: #dfe3e9; border: none;")
                    titulo_retirados = QLabel("Trabajadores retirados")
                    titulo_retirados.setStyleSheet(
                        "font-size: 11px; font-weight: bold; color: #8b929d; "
                        "background: transparent; border: none;"
                    )
                    linea_der = QFrame()
                    linea_der.setFixedHeight(1)
                    linea_der.setStyleSheet("background-color: #dfe3e9; border: none;")
                    sep_layout.addWidget(linea_izq, 1)
                    sep_layout.addWidget(titulo_retirados)
                    sep_layout.addWidget(linea_der, 1)
                    self.layout_filas.insertWidget(self.layout_filas.count() - 1, separador_retirados)

                    for t in trabajadores_retirados:
                        agregar_fila(t)

                # Si el trabajador seleccionado sigue en la lista, se mantiene marcado y se refrescan sus datos
                if self.trabajador_seleccionado is not None:
                    for t in trabajadores:
                        if t["cedula"] == self.trabajador_seleccionado["cedula"]:
                            self.mostrar_detalles_trabajador(t)
                            break

                self.actualizar_metricas_globales()

        except Exception as e:
            print(f"Error al listar trabajadores desde la BD: {e}")

    def mostrar_detalles_trabajador(self, datos):
        self.trabajador_seleccionado = datos
        nombre = datos['nombre']
        inicial = nombre[0].upper() if nombre else "?"
        
        self.lbl_avatar.setText(inicial)
        self.lbl_nombre_detalle.setText(nombre)

        secuencia_cv = f"{datos.get('estado_cv', 'N/D')} - {datos.get('municipio_cv', 'N/D')} - {datos.get('centro_cv', 'N/D')}"

        # Si el trabajador está retirado, solo su estado laboral se muestra en rojo
        estado_laboral = datos.get('estado_laboral', 'N/D')
        if "retirado" in str(estado_laboral).lower():
            estado_laboral = f"<span style='color:#d32f2f; font-weight:bold;'>{estado_laboral}</span>"

        texto = f"""
        <b>Cédula:</b> {formatear_cedula(datos['cedula'])}<br><br>
        <b>Fecha de Nacimiento:</b> {datos.get('fecha_nacimiento', 'N/D')}<br><br>
        <b>Teléfono:</b> {datos.get('telefono', 'N/D')}<br><br>
        <b>Correo:</b> {datos.get('correo', 'N/D')}<br><br>
        <b>Sexo:</b> {datos.get('sexo', 'N/D')}<br><br>
        <b>Dirección:</b> {datos.get('direccion', 'N/D')}<br><br>
        <b>Departamento:</b> {datos.get('departamento', 'N/D')}<br><br>
        <b>Estado Laboral:</b> {estado_laboral}<br><br>
        <b>Centro de Votación:</b><br>{secuencia_cv}
        """
        self.lbl_detalles_contenido.setText(texto)
        self.panel_detalles.show()

        # El trabajador queda marcado en la lista y se habilita el botón Modificar
        self.marcar_fila_seleccionada(datos["cedula"])
        self.btn_modificar.setEnabled(True)

    def marcar_fila_seleccionada(self, cedula):
        """Dibuja el borde azul en la fila de ese trabajador (None = ninguna)"""
        for i in range(self.layout_filas.count()):
            fila = self.layout_filas.itemAt(i).widget()
            if isinstance(fila, FilaTrabajador):
                fila.set_seleccionada(cedula is not None and fila.datos["cedula"] == cedula)

    def ocultar_detalles(self):
        # Al cerrar la tarjeta lateral se deselecciona al trabajador y se desactiva Modificar
        self.trabajador_seleccionado = None
        self.panel_detalles.hide()
        self.marcar_fila_seleccionada(None)
        self.btn_modificar.setEnabled(False)

    def abrir_dialogo_agregar(self):
        dialogo = RegistroTrabajadores("Registrar Nuevo Trabajador", parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_trabajadores_desde_bd()

    def abrir_dialogo_modificar(self):
        if not self.trabajador_seleccionado:
            return
        dialogo = RegistroTrabajadores("Modificar Trabajador", datos=self.trabajador_seleccionado, parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_trabajadores_desde_bd()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaTrabajadores()
    ventana.resize(1100, 650)
    ventana.show()
    sys.exit(app.exec())