import os
import re
import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtSvg import QSvgRenderer

try:
    from .perfil_datos import PestanaDatos
    from .perfil_seguridad import PestanaSeguridad
    from .perfil_actividad import PestanaActividad
except ImportError:
    from perfil_datos import PestanaDatos
    from perfil_seguridad import PestanaSeguridad
    from perfil_actividad import PestanaActividad

try:
    from usuarios.ventana_privilegios import obtener_permisos
except ImportError:
    try:
        from ..usuarios.ventana_privilegios import obtener_permisos
    except ImportError:
        from ventana_privilegios import obtener_permisos

try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from database import GestorBD


AZUL = "#0833a2"
FONDO = "#bfbdbe"
TEXTO = "#2c2c2c"
SECUNDARIO = "#777777"

NOMBRES_VENTANAS = {
    "asistencias": "Asistencias",
    "operativas": "Operativas",
    "reportes": "Reportes",
    "trabajadores": "Trabajadores",
    "usuarios": "Usuarios",
    "votacion": "Votación",
}

SECCIONES = (
    ("Mis datos", "iconodatos"),
    ("Seguridad", "iconoescudo"),
    ("Mi actividad", "iconoactividad"),
)


# ==================== ICONOS (rutas autocalculables) ====================
_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
CARPETAS_IMAGENES = [
    os.path.join(_DIRECTORIO, "..", "imagenes"),
    os.path.join(_DIRECTORIO, "imagenes"),
]
_cache_iconos = {}


def _clave_nombre(texto):
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


def icono_para_boton(clave, alto=16):
    pixmap = cargar_pixmap_svg(clave, alto)
    if not pixmap:
        return None
    icono = QIcon()
    icono.addPixmap(pixmap, QIcon.Mode.Normal)
    icono.addPixmap(pixmap, QIcon.Mode.Active)
    icono.addPixmap(pixmap, QIcon.Mode.Selected)
    return icono


class VentanaPerfil(QWidget):
    """Perfil real del usuario autenticado. Recibe siempre su id_usuario."""

    cerrar_sesion_solicitado = pyqtSignal()

    def __init__(self, id_usuario=None, parent=None, permisos=None, modo_prueba=False):
        super().__init__(parent)
        self.id_usuario = id_usuario
        self.modo_prueba = modo_prueba
        self.usuario = {}
        self.permisos_iniciales = permisos
        self.botones_seccion = []

        self.setObjectName("ventanaPerfil")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget#ventanaPerfil { background-color: #bfbdbe; }
            QLabel { color: #2c2c2c; background: transparent; border: none; }
            QFrame#tarjetaIdentidad, QFrame#tarjetaContenido {
                background-color: #ffffff; border: none; border-radius: 20px;
            }
            QStackedWidget#paginasPerfil {
                background-color: #ffffff; border: none;
            }
            QFrame#avatar {
                background: #eaf1fb; border: 1px solid #d7e3f6;
                border-radius: 34px;
            }
            QFrame#barraSecciones {
                background: #f4f6f9; border: 1.5px solid #0833a2; border-radius: 13px;
            }
        """)

        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(12, 12, 12, 12)
        raiz.setSpacing(12)

        # ---------------- TARJETA LATERAL DE IDENTIDAD ----------------
        self.tarjeta_identidad = QFrame()
        self.tarjeta_identidad.setObjectName("tarjetaIdentidad")
        self.tarjeta_identidad.setFixedWidth(265)
        identidad = QVBoxLayout(self.tarjeta_identidad)
        identidad.setContentsMargins(20, 22, 20, 20)
        identidad.setSpacing(10)

        self.avatar = QFrame()
        self.avatar.setObjectName("avatar")
        self.avatar.setFixedSize(68, 68)
        avatar_layout = QVBoxLayout(self.avatar)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_iniciales = QLabel("--")
        self.lbl_iniciales.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_iniciales.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {AZUL};")
        avatar_layout.addWidget(self.lbl_iniciales)
        identidad.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.lbl_nombre = QLabel("Cargando perfil…")
        self.lbl_nombre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nombre.setWordWrap(True)
        self.lbl_nombre.setStyleSheet("font-size: 16px; font-weight: bold;")
        identidad.addWidget(self.lbl_nombre)

        self.lbl_cedula = QLabel("Cédula: —")
        self.lbl_cedula.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cedula.setStyleSheet("font-size: 12px; color: #777777;")
        identidad.addWidget(self.lbl_cedula)

        self.lbl_rol = QLabel("Rol no disponible")
        self.lbl_rol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_rol.setStyleSheet("""
            QLabel { color: #0833a2; background: #eaf1fb; border: 1px solid #b8cbed;
                     border-radius: 12px; padding: 5px 12px; font-size: 11px; font-weight: bold; }
        """)
        identidad.addWidget(self.lbl_rol, alignment=Qt.AlignmentFlag.AlignHCenter)
        identidad.addSpacing(7)

        identidad.addWidget(self._subtitulo("INFORMACIÓN LABORAL"))
        self.lbl_departamento = self._dato_identidad("Departamento", "—", identidad)
        self.lbl_estado_laboral = self._dato_identidad("Estado laboral", "—", identidad)

        identidad.addSpacing(4)
        identidad.addWidget(self._subtitulo("ESTADO DE SESIÓN"))
        fila_estado = QHBoxLayout()
        self.punto_estado = QLabel("●")
        self.lbl_estado_sesion = QLabel("No disponible")
        self.lbl_estado_sesion.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777;")
        fila_estado.addWidget(self.punto_estado)
        fila_estado.addWidget(self.lbl_estado_sesion)
        fila_estado.addStretch()
        identidad.addLayout(fila_estado)

        self.lbl_ultimo_acceso = QLabel("Último acceso: —")
        self.lbl_ultimo_acceso.setWordWrap(True)
        self.lbl_ultimo_acceso.setStyleSheet("font-size: 11px; color: #777777;")
        identidad.addWidget(self.lbl_ultimo_acceso)

        identidad.addSpacing(4)
        identidad.addWidget(self._subtitulo("MIS ACCESOS"))
        self.lbl_accesos = QLabel("Consultando permisos…")
        self.lbl_accesos.setWordWrap(True)
        self.lbl_accesos.setStyleSheet("font-size: 12px; color: #555555;")
        identidad.addWidget(self.lbl_accesos)
        identidad.addStretch()

        self.btn_cerrar_sesion = QPushButton("Cerrar sesión")
        self.btn_cerrar_sesion.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cerrar_sesion.setFixedHeight(38)
        self.btn_cerrar_sesion.setStyleSheet("""
            QPushButton { background: #e0dede; color: #333333; border: none;
                          border-radius: 18px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background: #d0d0d0; }
        """)
        self.btn_cerrar_sesion.clicked.connect(self.cerrar_sesion_solicitado.emit)
        identidad.addWidget(self.btn_cerrar_sesion)
        raiz.addWidget(self.tarjeta_identidad)

        # ---------------- CONTENIDO DERECHO: TODO DENTRO DE TARJETA ----------------
        self.tarjeta_contenido = QFrame()
        self.tarjeta_contenido.setObjectName("tarjetaContenido")
        self.tarjeta_contenido.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        contenido = QVBoxLayout(self.tarjeta_contenido)
        contenido.setContentsMargins(20, 18, 20, 20)
        contenido.setSpacing(12)

        encabezado = QVBoxLayout()
        encabezado.setSpacing(3)
        titulo = QLabel("Mi perfil")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c2c2c;")
        subtitulo = QLabel(
            "Consulta tu información personal y administra la seguridad de tu cuenta."
        )
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet("font-size: 12px; color: #666666;")
        encabezado.addWidget(titulo)
        encabezado.addWidget(subtitulo)
        contenido.addLayout(encabezado)

        barra = QFrame()
        barra.setObjectName("barraSecciones")
        barra_layout = QHBoxLayout(barra)
        barra_layout.setContentsMargins(8, 7, 8, 7)
        barra_layout.setSpacing(6)

        for indice, (nombre, clave_icono) in enumerate(SECCIONES):
            icono_boton = icono_para_boton(clave_icono, 16)
            boton = QPushButton((" " if icono_boton else "") + nombre)
            if icono_boton:
                boton.setIcon(icono_boton)
                boton.setIconSize(QSize(16, 16))
            boton.setCheckable(True)
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.setMinimumHeight(38)
            boton.setStyleSheet(self._estilo_boton_seccion())
            boton.clicked.connect(
                lambda checked=False, i=indice: self.mostrar_seccion(i)
            )
            self.botones_seccion.append(boton)
            barra_layout.addWidget(boton)
        contenido.addWidget(barra)

        self.paginas = QStackedWidget()
        self.paginas.setObjectName("paginasPerfil")
        self.pagina_datos = PestanaDatos(self, modo_prueba=modo_prueba)
        self.pagina_seguridad = PestanaSeguridad(self, modo_prueba=modo_prueba)
        self.pagina_actividad = PestanaActividad(self, modo_prueba=modo_prueba)
        self.paginas.addWidget(self.pagina_datos)
        self.paginas.addWidget(self.pagina_seguridad)
        self.paginas.addWidget(self.pagina_actividad)
        contenido.addWidget(self.paginas, 1)

        raiz.addWidget(self.tarjeta_contenido, 1)

        self.pagina_datos.datos_actualizados.connect(self.cargar_identidad)
        self.pagina_seguridad.usuario_actualizado.connect(self._actualizar_nombre_usuario)

        self.mostrar_seccion(0)
        self.cargar_identidad()

    @staticmethod
    def _estilo_boton_seccion():
        return """
            QPushButton { background: transparent; color: #555555; border: 1.5px solid transparent;
                          border-radius: 10px; padding: 0 18px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background: #e9edf2; }
            QPushButton:checked { background: #eaf1fb; color: #0833a2; border: 1.5px solid #0833a2; }
        """

    @staticmethod
    def _subtitulo(texto):
        lbl = QLabel(texto)
        lbl.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #8a8a8a; letter-spacing: 1px;"
        )
        return lbl

    @staticmethod
    def _dato_identidad(etiqueta, valor, layout):
        lbl = QLabel(f"<b>{etiqueta}</b><br>{valor}")
        lbl.setTextFormat(Qt.TextFormat.RichText)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-size: 12px; color: #555555;")
        layout.addWidget(lbl)
        return lbl

    def mostrar_seccion(self, indice):
        if indice < 0 or indice >= self.paginas.count():
            return
        self.paginas.setCurrentIndex(indice)
        for i, boton in enumerate(self.botones_seccion):
            boton.setChecked(i == indice)

        if self.modo_prueba or self.id_usuario is None:
            return
        if indice == 0:
            self.pagina_datos.cargar(self.id_usuario)
        elif indice == 1:
            self.pagina_seguridad.cargar(
                self.id_usuario, self.usuario.get("nombre_usuario", "")
            )
        elif indice == 2:
            self.pagina_actividad.cargar(self.id_usuario)

    def _mostrar_identidad_demo(self):
        """Carga una identidad ficticia; no abre conexiones ni consulta MySQL."""
        from datetime import datetime
        self.id_usuario = 7
        self.usuario = {
            "id_usuario": 7,
            "nombre_usuario": "m.perez",
            "ultimo_acceso": datetime(2026, 11, 20, 9, 35),
            "en_linea": 1,
            "bloqueado": 0,
            "cedula_trabajador": 18456789,
            "nombres": "María",
            "apellidos": "Pérez",
            "nombre_departamento": "Recursos Humanos",
            "estado_laboral": "Trabajador fijo",
            "nombre_rol": "Recursos Humanos",
        }
        self.lbl_iniciales.setText("MP")
        self.lbl_nombre.setText("María Pérez")
        self.lbl_cedula.setText("Cédula: 18.456.789")
        self.lbl_rol.setText("Recursos Humanos")
        self.lbl_departamento.setText("<b>Departamento</b><br>Recursos Humanos")
        self.lbl_estado_laboral.setText("<b>Estado laboral</b><br>Trabajador fijo")
        self.punto_estado.setStyleSheet("color: #1b8a4b; font-size: 13px;")
        self.lbl_estado_sesion.setText("En línea · demostración")
        self.lbl_estado_sesion.setStyleSheet("font-size: 12px; font-weight: bold; color: #1b8a4b;")
        self.lbl_ultimo_acceso.setText("Último acceso: 20/11/2026 · 09:35")
        self.lbl_accesos.setText("Inicio · Perfil · Trabajadores · Operativas · Reportes")
        self.pagina_datos.mostrar({
            "cedula_trabajador": 18456789, "nombres": "María", "apellidos": "Pérez",
            "fecha_nacimiento": datetime(1990, 5, 12).date(), "sexo": "femenino",
            "telefono": "0412-1234567", "correo": "maria@correo.com",
            "direccion": "Las Cocuizas, Maturín", "nombre_departamento": "Recursos Humanos",
            "estado_laboral": "Trabajador fijo", "nombre_centro": "Liceo Miguel José Sanz",
            "nombre_parroquia": "San Simón", "nombre_municipio": "Maturín",
            "nombre_estado": "Monagas",
        })
        self.pagina_seguridad.cargar(7, "m.perez")
        self.pagina_actividad.mostrar_demo()

    def cargar_identidad(self):
        if self.modo_prueba:
            self._mostrar_identidad_demo()
            return
        if self.id_usuario is None:
            self._mostrar_sin_usuario(
                "No se recibió el identificador del usuario autenticado."
            )
            return

        fila = None
        accesos = []
        conexion = None
        cursor = None
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                raise RuntimeError("GestorBD no devolvió una conexión.")

            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    u.id_usuario, u.nombre_usuario, u.ultimo_acceso,
                    u.en_linea, u.bloqueado,
                    t.cedula_trabajador, t.nombres, t.apellidos,
                    d.nombre_departamento,
                    el.descripcion_estado AS estado_laboral,
                    r.nombre_rol
                FROM usuarios u
                LEFT JOIN trabajadores t
                    ON u.cedula_trabajador_fk = t.cedula_trabajador
                LEFT JOIN departamentos d
                    ON t.id_departamento_fk = d.id_departamento
                LEFT JOIN estados_laborales el
                    ON t.id_estado_laboral_fk = el.id_estado_laboral
                LEFT JOIN roles r ON u.id_rol_fk = r.id_rol
                WHERE u.id_usuario = %s
                LIMIT 1
            """, (self.id_usuario,))
            fila = cursor.fetchone()

            if fila:
                rol = fila.get("nombre_rol") or ""
                permisos_efectivos = obtener_permisos(self.id_usuario, rol)
                accesos = [
                    NOMBRES_VENTANAS.get(clave, clave.replace("_", " ").title())
                    for clave, permitido in permisos_efectivos.items()
                    if permitido
                ]

        except Exception as error:
            print(f"Error al cargar el perfil (usuario {self.id_usuario}): {error}")
            self._mostrar_sin_usuario("No se pudo consultar la base de datos.")
            return
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass

        if not fila:
            self._mostrar_sin_usuario(
                f"No existe un usuario con id_usuario={self.id_usuario}."
            )
            return

        self.usuario = fila
        nombre_completo = " ".join(
            str(x).strip()
            for x in (fila.get("nombres"), fila.get("apellidos"))
            if x and str(x).strip()
        ) or fila.get("nombre_usuario", "Usuario")

        iniciales = "".join(p[0] for p in nombre_completo.split()[:2]).upper()
        self.lbl_iniciales.setText(iniciales or "U")
        self.lbl_nombre.setText(nombre_completo)
        cedula = fila.get("cedula_trabajador")
        self.lbl_cedula.setText(
            f"Cédula: {self._formatear_cedula(cedula)}"
            if cedula else "Cédula: No vinculada"
        )
        self.lbl_rol.setText(fila.get("nombre_rol") or "Rol no asignado")
        self.lbl_departamento.setText(
            f"<b>Departamento</b><br>{fila.get('nombre_departamento') or 'No asignado'}"
        )
        self.lbl_estado_laboral.setText(
            f"<b>Estado laboral</b><br>{fila.get('estado_laboral') or 'No disponible'}"
        )

        bloqueado = bool(fila.get("bloqueado"))
        en_linea = bool(fila.get("en_linea"))
        if bloqueado:
            estado, color = "Cuenta bloqueada", "#c62828"
        elif en_linea:
            estado, color = "En línea", "#1b8a4b"
        else:
            estado, color = "Desconectado", "#8a93a3"
        self.punto_estado.setStyleSheet(f"color: {color}; font-size: 13px;")
        self.lbl_estado_sesion.setText(estado)
        self.lbl_estado_sesion.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {color};"
        )

        ultimo = fila.get("ultimo_acceso")
        if ultimo:
            try:
                ultimo = ultimo.strftime("%d/%m/%Y · %H:%M")
            except AttributeError:
                ultimo = str(ultimo)
        else:
            ultimo = "Sin registro"
        self.lbl_ultimo_acceso.setText(f"Último acceso: {ultimo}")

        if isinstance(self.permisos_iniciales, dict):
            nombres_accesos = [
                NOMBRES_VENTANAS.get(clave, str(clave).replace("_", " ").title())
                for clave, permitido in self.permisos_iniciales.items()
                if permitido
            ]
        elif self.permisos_iniciales is not None:
            nombres_accesos = [str(p) for p in self.permisos_iniciales]
        else:
            nombres_accesos = list(accesos)

        if nombres_accesos:
            self.lbl_accesos.setText("\n".join(f"•  {p}" for p in nombres_accesos))
        else:
            self.lbl_accesos.setText("Esta cuenta no tiene ventanas autorizadas.")

        if self.paginas.currentIndex() == 1:
            self.pagina_seguridad.cargar(
                self.id_usuario, fila.get("nombre_usuario", "")
            )

    def _actualizar_nombre_usuario(self, nuevo_nombre):
        self.usuario["nombre_usuario"] = nuevo_nombre

    def _mostrar_sin_usuario(self, mensaje):
        self.usuario = {}
        self.lbl_iniciales.setText("—")
        self.lbl_nombre.setText("Perfil no disponible")
        self.lbl_cedula.setText("Cédula: —")
        self.lbl_rol.setText("Rol no disponible")
        self.lbl_departamento.setText("<b>Departamento</b><br>—")
        self.lbl_estado_laboral.setText("<b>Estado laboral</b><br>—")
        self.lbl_estado_sesion.setText("No disponible")
        self.lbl_ultimo_acceso.setText("Último acceso: —")
        self.lbl_accesos.setText(mensaje)

    @staticmethod
    def _formatear_cedula(valor):
        try:
            return f"{int(valor):,}".replace(",", ".")
        except (TypeError, ValueError):
            return str(valor or "—")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPerfil(modo_prueba=True)
    ventana.setWindowTitle("Prueba independiente - Mi perfil (datos ficticios)")
    ventana.resize(1180, 760)
    ventana.show()
    sys.exit(app.exec())