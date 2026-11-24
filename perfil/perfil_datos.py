import sys
import os
import re
from datetime import date, datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLineEdit,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


# Iconos opcionales (se buscan en la carpeta 'imagenes'; si no existen, simplemente no se muestran):
#   icono-identificacion.svg (azul)
ICONO_IDENTIFICACION = "iconoidentificacion"
ICONO_TELEFONO = "icono telefono"  # reservado por si luego se modela
MAX_TELEFONO = 20
MAX_CORREO = 100
MAX_DIRECCION = 255


# ==================== ICONOS (rutas autocalculables) ====================
_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
CARPETAS_IMAGENES = [
    os.path.join(_DIRECTORIO, '..', 'imagenes'),
    os.path.join(_DIRECTORIO, 'imagenes'),
]


def _clave_nombre(texto):
    return re.sub(r"[^a-z0-9]", "", os.path.splitext(str(texto))[0].lower())


def buscar_icono(clave):
    clave = _clave_nombre(clave)
    for carpeta in CARPETAS_IMAGENES:
        carpeta = os.path.abspath(carpeta)
        if not os.path.isdir(carpeta):
            continue
        for archivo in os.listdir(carpeta):
            if archivo.lower().endswith(".svg") and _clave_nombre(archivo) == clave:
                return os.path.join(carpeta, archivo)
    return None


def cargar_pixmap_svg(clave, alto):
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


def crear_titulo(texto, clave_icono, tamano=16):
    """Título de una tarjeta con su icono opcional delante"""
    contenedor = QWidget()
    contenedor.setStyleSheet("background: transparent;")
    layout = QHBoxLayout(contenedor)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    pixmap = cargar_pixmap_svg(clave_icono, tamano + 2)
    if pixmap:
        icono = QLabel()
        icono.setPixmap(pixmap)
        icono.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(icono)
    lbl = QLabel(texto)
    lbl.setStyleSheet(f"font-size: {tamano}px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
    layout.addWidget(lbl)
    layout.addStretch()
    return contenedor


# ==================== UTILIDADES ====================
def formatear_cedula(valor):
    """31776780 -> 31.776.780"""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(valor)


def fecha_texto(valor):
    if isinstance(valor, datetime):
        valor = valor.date()
    return valor.strftime("%d/%m/%Y") if isinstance(valor, date) else ""


def texto(valor):
    return "" if valor is None else str(valor)


# ==================== ESTILOS ====================
ESTILO_CAMPO = """
    QLineEdit {
        background-color: #f4f6f9;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 13px;
        color: #333333;
    }
    QLineEdit:focus { border: 2px solid #0833a2; }
    QLineEdit:read-only { background-color: #f0f0f0; color: #666666; border: 1px solid #e6e6e6; }
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
    QPushButton:hover { background-color: #3150ff; border: 2px solid #3150ff; }
"""

ESTILO_BOTON_SECUNDARIO = """
    QPushButton {
        background-color: #e0dede;
        color: #333333;
        border: none;
        border-radius: 18px;
        padding: 0px 18px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #d0d0d0; }
"""


class PestanaDatos(QWidget):
    """Pestaña con los datos del trabajador; solo teléfono, correo y dirección los puede editar el propio usuario"""
    datos_actualizados = pyqtSignal()

    def __init__(self, parent=None, modo_prueba=False):
        super().__init__(parent)
        # En modo prueba la pestaña funciona completa pero NO escribe en la base de datos
        self.modo_prueba = modo_prueba
        self.cedula = None
        self.original = {"telefono": "", "correo": "", "direccion": ""}

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget { background-color: #ffffff; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        sin_fondo = "border: none; background: transparent;"

        def crear_tarjeta(nombre):
            tarjeta = QFrame()
            tarjeta.setObjectName(nombre)
            tarjeta.setStyleSheet(
                f"QFrame#{nombre} {{ background-color: #ffffff; border-radius: 20px; border: 1.5px solid #0833a2; }}"
            )
            layout_tarjeta = QVBoxLayout(tarjeta)
            layout_tarjeta.setContentsMargins(24, 18, 24, 18)
            layout_tarjeta.setSpacing(10)
            return tarjeta, layout_tarjeta

        def etiqueta(texto_etiqueta):
            lbl = QLabel(texto_etiqueta)
            lbl.setStyleSheet(f"font-size: 12px; font-weight: bold; color: #555555; {sin_fondo}")
            return lbl

        def entrada(solo_lectura, max_largo=255):
            campo = QLineEdit()
            campo.setReadOnly(solo_lectura)
            campo.setMaxLength(max_largo)
            campo.setFixedHeight(36)
            campo.setStyleSheet(ESTILO_CAMPO)
            return campo

        # ==================== INFORMACIÓN REGISTRADA (solo lectura) ====================
        tarjeta_info, layout_info = crear_tarjeta("tarjetaInformacion")
        layout_info.addWidget(crear_titulo("Información registrada", ICONO_IDENTIFICACION, 16))

        lbl_nota = QLabel("Estos datos los administra Recursos Humanos. Para corregirlos, comunícate con ellos.")
        lbl_nota.setWordWrap(True)
        lbl_nota.setStyleSheet(f"font-size: 12px; color: #777777; {sin_fondo}")
        layout_info.addWidget(lbl_nota)

        cuadricula = QGridLayout()
        cuadricula.setHorizontalSpacing(14)
        cuadricula.setVerticalSpacing(6)
        cuadricula.setColumnStretch(0, 1)
        cuadricula.setColumnStretch(1, 1)
        cuadricula.setColumnStretch(2, 1)

        self.campos_lectura = {}
        distribucion = [
            ("cedula", "Cédula", 0, 0, 1), ("nombres", "Nombres", 0, 1, 1), ("apellidos", "Apellidos", 0, 2, 1),
            ("fecha_nacimiento", "Fecha de nacimiento", 2, 0, 1), ("sexo", "Sexo", 2, 1, 1),
            ("estado_laboral", "Estado laboral", 2, 2, 1),
            ("departamento", "Departamento", 4, 0, 1), ("centro", "Centro de votación", 4, 1, 2),
        ]
        for clave, titulo, fila, columna, ancho in distribucion:
            campo = entrada(True)
            self.campos_lectura[clave] = campo
            cuadricula.addWidget(etiqueta(titulo), fila, columna, 1, ancho)
            cuadricula.addWidget(campo, fila + 1, columna, 1, ancho)
        layout_info.addLayout(cuadricula)
        layout.addWidget(tarjeta_info)

        # ==================== DATOS DE CONTACTO (editables) ====================
        tarjeta_contacto, layout_contacto = crear_tarjeta("tarjetaContacto")
        layout_contacto.addWidget(crear_titulo("Datos de contacto", "", 16))

        lbl_nota2 = QLabel("Puedes mantener actualizados tu teléfono, correo y dirección.")
        lbl_nota2.setStyleSheet(f"font-size: 12px; color: #777777; {sin_fondo}")
        layout_contacto.addWidget(lbl_nota2)

        cuadricula2 = QGridLayout()
        cuadricula2.setHorizontalSpacing(14)
        cuadricula2.setVerticalSpacing(6)
        cuadricula2.setColumnStretch(0, 1)
        cuadricula2.setColumnStretch(1, 1)

        self.txt_telefono = entrada(False, MAX_TELEFONO)
        self.txt_telefono.setPlaceholderText("Ej. 0412-1234567")
        self.txt_correo = entrada(False, MAX_CORREO)
        self.txt_correo.setPlaceholderText("Ej. nombre@correo.com")
        self.txt_direccion = entrada(False, MAX_DIRECCION)
        self.txt_direccion.setPlaceholderText("Dirección de habitación")

        cuadricula2.addWidget(etiqueta("Teléfono"), 0, 0)
        cuadricula2.addWidget(self.txt_telefono, 1, 0)
        cuadricula2.addWidget(etiqueta("Correo electrónico"), 0, 1)
        cuadricula2.addWidget(self.txt_correo, 1, 1)
        cuadricula2.addWidget(etiqueta("Dirección"), 2, 0, 1, 2)
        cuadricula2.addWidget(self.txt_direccion, 3, 0, 1, 2)
        layout_contacto.addLayout(cuadricula2)

        fila_botones = QHBoxLayout()
        fila_botones.addStretch()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(110, 36)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet(ESTILO_BOTON_SECUNDARIO)
        self.btn_cancelar.clicked.connect(self.restablecer)
        self.btn_guardar = QPushButton("Guardar cambios")
        self.btn_guardar.setFixedHeight(36)
        self.btn_guardar.setMinimumWidth(160)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet(ESTILO_BOTON_AZUL)
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        fila_botones.addWidget(self.btn_cancelar)
        fila_botones.addWidget(self.btn_guardar)
        layout_contacto.addLayout(fila_botones)

        layout.addWidget(tarjeta_contacto)
        layout.addStretch()

    # ==================== DATOS ====================
    def cargar(self, id_usuario):
        """Lee de la base de datos los datos del trabajador vinculado al usuario"""
        fila = None
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("""
                    SELECT t.cedula_trabajador, t.nombres, t.apellidos, t.fecha_nacimiento, t.sexo,
                           t.telefono, t.correo, t.direccion, d.nombre_departamento,
                           el.descripcion_estado AS estado_laboral, cv.nombre_centro,
                           p.nombre_parroquia, m.nombre_municipio, e.nombre_estado
                    FROM usuarios u
                    JOIN trabajadores t ON u.cedula_trabajador_fk = t.cedula_trabajador
                    LEFT JOIN departamentos d ON t.id_departamento_fk = d.id_departamento
                    LEFT JOIN estados_laborales el ON t.id_estado_laboral_fk = el.id_estado_laboral
                    LEFT JOIN centros_votacion cv ON t.id_centro_votacion_fk = cv.id_centro_votacion
                    LEFT JOIN parroquias p ON cv.id_parroquia_fk = p.id_parroquia
                    LEFT JOIN municipios m ON p.id_municipio_fk = m.id_municipio
                    LEFT JOIN estados e ON m.id_estado_fk = e.id_estado
                    WHERE u.id_usuario = %s
                """, (id_usuario,))
                fila = cursor.fetchone()
                cursor.close()
        except Exception as e:
            print(f"Error al cargar los datos del perfil: {e}")
        self.mostrar(fila)

    def mostrar(self, fila):
        """Pone los datos de la fila en los campos (fila vacía = campos en blanco)"""
        fila = fila or {}
        self.cedula = fila.get("cedula_trabajador")

        centro = texto(fila.get("nombre_centro"))
        ubicacion = ", ".join(p for p in (texto(fila.get("nombre_parroquia")), texto(fila.get("nombre_municipio")),
                                          texto(fila.get("nombre_estado"))) if p)
        if centro and ubicacion:
            centro = f"{centro} ({ubicacion})"

        valores = {
            "cedula": formatear_cedula(self.cedula) if self.cedula else "",
            "nombres": texto(fila.get("nombres")), "apellidos": texto(fila.get("apellidos")),
            "fecha_nacimiento": fecha_texto(fila.get("fecha_nacimiento")),
            "sexo": texto(fila.get("sexo")).capitalize(), "estado_laboral": texto(fila.get("estado_laboral")),
            "departamento": texto(fila.get("nombre_departamento")), "centro": centro,
        }
        for clave, campo in self.campos_lectura.items():
            campo.setText(valores.get(clave, ""))
            campo.setCursorPosition(0)

        self.original = {
            "telefono": texto(fila.get("telefono")), "correo": texto(fila.get("correo")),
            "direccion": texto(fila.get("direccion")),
        }
        self.restablecer()

    def restablecer(self):
        self.txt_telefono.setText(self.original["telefono"])
        self.txt_correo.setText(self.original["correo"])
        self.txt_direccion.setText(self.original["direccion"])

    # ==================== GUARDADO ====================
    def guardar_cambios(self):
        telefono = self.txt_telefono.text().strip()
        correo = self.txt_correo.text().strip()
        direccion = " ".join(self.txt_direccion.text().split())

        if not telefono:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingresa tu teléfono.")
            return
        if not re.fullmatch(r"[0-9+()\-\s]{7,20}", telefono):
            QMessageBox.warning(self, "Teléfono inválido", "El teléfono solo puede llevar números, espacios y los signos + - ( ).")
            return
        if not correo:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingresa tu correo electrónico.")
            return
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            QMessageBox.warning(self, "Correo inválido", "El correo electrónico no parece válido. Ejemplo: nombre@correo.com")
            return
        if not direccion:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingresa tu dirección.")
            return

        nuevos = {"telefono": telefono, "correo": correo, "direccion": direccion}
        if nuevos == self.original:
            QMessageBox.information(self, "Sin cambios", "No hay cambios que guardar.")
            return

        # Modo prueba: se valida todo pero no se escribe en la base de datos
        if self.modo_prueba:
            QMessageBox.information(
                self, "Modo de prueba",
                "Las validaciones son correctas.\n\nModo de prueba: los cambios NO se guardaron en la base de datos."
            )
            return

        if self.cedula is None:
            QMessageBox.warning(self, "Sin trabajador", "Tu usuario no tiene un trabajador vinculado.")
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                QMessageBox.critical(self, "Error de Conexión", "No se pudo conectar con la base de datos MySQL.")
                return
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE trabajadores SET telefono = %s, correo = %s, direccion = %s WHERE cedula_trabajador = %s",
                (telefono, correo, direccion, self.cedula)
            )
            conexion.commit()
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar:\n{e}")
            return

        self.original = nuevos
        self.restablecer()
        self.datos_actualizados.emit()
        QMessageBox.information(self, "Éxito", "Tus datos de contacto se actualizaron correctamente.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = QWidget()
    ventana.setStyleSheet("background-color: #bfbdbe;")
    layout = QVBoxLayout(ventana)
    layout.setContentsMargins(20, 20, 20, 20)
    pestana = PestanaDatos(modo_prueba=True)
    pestana.mostrar({
        "cedula_trabajador": 18456789, "nombres": "María", "apellidos": "Pérez", "fecha_nacimiento": date(1990, 5, 12),
        "sexo": "femenino", "telefono": "0412-1234567", "correo": "maria@correo.com", "direccion": "Las Cocuizas, Maturín",
        "nombre_departamento": "Recursos Humanos", "estado_laboral": "Trabajador fijo",
        "nombre_centro": "Liceo Miguel José Sanz", "nombre_parroquia": "San Simon",
        "nombre_municipio": "Maturin", "nombre_estado": "Monagas",
    })
    layout.addWidget(pestana)
    ventana.resize(950, 600)
    ventana.show()
    sys.exit(app.exec())