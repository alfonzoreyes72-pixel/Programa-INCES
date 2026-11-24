import sys
import os
import re

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit,
    QPushButton, QLabel, QCheckBox, QMessageBox
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


MIN_CLAVE = 6
BORDE_AZUL_OSCURO = "#0833a2"
BORDE_AZUL_CLARO = "#9ab6e6"

# Iconos opcionales (se buscan en la carpeta 'imagenes'; si no existen, simplemente no se muestran):
#   icono-candado.svg (azul)   icono-escudo.svg (azul)
ICONO_CANDADO = "iconocandado"
ICONO_ESCUDO = "iconoescudo"

COLOR_DEBIL = "#d32f2f"
COLOR_ACEPTABLE = "#c77700"
COLOR_BUENA = "#1b8a4b"
COLOR_BARRA_VACIA = "#e0dede"


# ==================== ICONOS (rutas autocalculables) ====================
_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
CARPETAS_IMAGENES = [
    os.path.join(_DIRECTORIO, '..', 'imagenes'),
    os.path.join(_DIRECTORIO, 'imagenes'),
]


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


def calcular_fortaleza(clave):
    """Devuelve (nivel 0-3, texto, color) de una contraseña"""
    if not clave:
        return 0, "", COLOR_BARRA_VACIA
    puntos = 0
    puntos += len(clave) >= MIN_CLAVE
    puntos += len(clave) >= 8
    puntos += bool(re.search(r"[A-Za-z]", clave)) and bool(re.search(r"\d", clave))
    puntos += (bool(re.search(r"[a-z]", clave)) and bool(re.search(r"[A-Z]", clave))) or bool(re.search(r"[^A-Za-z0-9]", clave))
    if len(clave) < MIN_CLAVE or puntos <= 1:
        return 1, "Débil", COLOR_DEBIL
    if puntos == 2:
        return 2, "Aceptable", COLOR_ACEPTABLE
    return 3, "Buena" if puntos == 3 else "Muy segura", COLOR_BUENA


class PestanaSeguridad(QWidget):
    """Pestaña para cambiar el nombre de usuario y la contraseña de quien tiene la sesión iniciada"""
    usuario_actualizado = pyqtSignal(str)

    def __init__(self, parent=None, modo_prueba=False):
        super().__init__(parent)
        self.modo_prueba = modo_prueba
        self.id_usuario = None
        self.nombre_usuario = ""

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget { background-color: #ffffff; }")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        sin_fondo = "border: none; background: transparent;"

        # ==================== TARJETA DEL FORMULARIO ====================
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaSeguridad")
        tarjeta.setStyleSheet(
            f"QFrame#tarjetaSeguridad {{ background-color: #ffffff; border-radius: 20px; border: 1.5px solid {BORDE_AZUL_OSCURO}; }}"
        )
        layout_tarjeta = QVBoxLayout(tarjeta)
        layout_tarjeta.setContentsMargins(24, 20, 24, 20)
        layout_tarjeta.setSpacing(6)

        layout_tarjeta.addWidget(crear_titulo("Credenciales de acceso", ICONO_CANDADO, 18))
        lbl_sub = QLabel("Cambia tu usuario o tu contraseña. Por seguridad, se pide la contraseña actual.")
        lbl_sub.setWordWrap(True)
        lbl_sub.setStyleSheet(f"font-size: 12px; color: #777777; {sin_fondo}")
        layout_tarjeta.addWidget(lbl_sub)
        layout_tarjeta.addSpacing(8)

        def campo(etiqueta, placeholder, clave=False, max_largo=60):
            lbl = QLabel(etiqueta)
            lbl.setStyleSheet(f"font-size: 12px; font-weight: bold; color: #555555; {sin_fondo}")
            entrada = QLineEdit()
            entrada.setPlaceholderText(placeholder)
            entrada.setMaxLength(max_largo)
            entrada.setFixedHeight(36)
            entrada.setStyleSheet(ESTILO_CAMPO)
            if clave:
                entrada.setEchoMode(QLineEdit.EchoMode.Password)
            layout_tarjeta.addWidget(lbl)
            layout_tarjeta.addWidget(entrada)
            return entrada

        self.txt_usuario = campo("Nombre de usuario", "Nombre de usuario", max_largo=20)
        layout_tarjeta.addSpacing(4)
        self.txt_actual = campo("Contraseña actual", "Escribe tu contraseña actual", clave=True)
        layout_tarjeta.addSpacing(4)
        self.txt_nueva = campo("Nueva contraseña", f"Mínimo {MIN_CLAVE} caracteres", clave=True)

        # Barra de fortaleza (tres segmentos)
        fila_fortaleza = QHBoxLayout()
        fila_fortaleza.setSpacing(4)
        self.barras = []
        for _ in range(3):
            barra = QFrame()
            barra.setFixedHeight(6)
            barra.setStyleSheet(f"background-color: {COLOR_BARRA_VACIA}; border: none; border-radius: 3px;")
            self.barras.append(barra)
            fila_fortaleza.addWidget(barra, stretch=1)
        self.lbl_fortaleza = QLabel("")
        self.lbl_fortaleza.setFixedWidth(90)
        self.lbl_fortaleza.setStyleSheet(f"font-size: 12px; font-weight: bold; color: #777777; {sin_fondo}")
        fila_fortaleza.addWidget(self.lbl_fortaleza)
        layout_tarjeta.addLayout(fila_fortaleza)

        layout_tarjeta.addSpacing(4)
        self.txt_confirmar = campo("Confirmar nueva contraseña", "Repite la nueva contraseña", clave=True)

        self.chk_mostrar = QCheckBox("Mostrar contraseñas")
        self.chk_mostrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_mostrar.setStyleSheet("QCheckBox { font-size: 12px; color: #555555; background: transparent; }")
        layout_tarjeta.addSpacing(4)
        layout_tarjeta.addWidget(self.chk_mostrar)

        layout_tarjeta.addStretch()

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
        layout_tarjeta.addLayout(fila_botones)

        layout.addWidget(tarjeta, stretch=3)

        # ==================== TARJETA DE RECOMENDACIONES ====================
        recomendaciones = QFrame()
        recomendaciones.setObjectName("tarjetaRecomendaciones")
        recomendaciones.setStyleSheet(
            f"QFrame#tarjetaRecomendaciones {{ background-color: #eaf1fb; border-radius: 20px; border: 1.5px solid {BORDE_AZUL_CLARO}; }}"
        )
        layout_rec = QVBoxLayout(recomendaciones)
        layout_rec.setContentsMargins(22, 20, 22, 20)
        layout_rec.setSpacing(10)
        layout_rec.addWidget(crear_titulo("Recomendaciones", ICONO_ESCUDO, 15))
        for texto in (
            "Usa al menos 8 caracteres.",
            "Combina letras y números.",
            "Mezcla mayúsculas, minúsculas o símbolos.",
            "No uses tu cédula ni tu fecha de nacimiento.",
            "No compartas tu contraseña con nadie.",
        ):
            lbl = QLabel(f"•  {texto}")
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"font-size: 12px; color: #163e7a; {sin_fondo}")
            layout_rec.addWidget(lbl)
        layout_rec.addStretch()
        layout.addWidget(recomendaciones, stretch=2)

        # Señales
        self.txt_nueva.textChanged.connect(self.actualizar_fortaleza)
        self.chk_mostrar.toggled.connect(self.alternar_visibilidad)

    # ==================== DATOS ====================
    def cargar(self, id_usuario, nombre_usuario):
        """Se llama al entrar a la pestaña: muestra el usuario actual y limpia las contraseñas"""
        self.id_usuario = id_usuario
        self.nombre_usuario = str(nombre_usuario or "")
        self.restablecer()

    def restablecer(self):
        self.txt_usuario.setText(self.nombre_usuario)
        for campo in (self.txt_actual, self.txt_nueva, self.txt_confirmar):
            campo.clear()
        self.chk_mostrar.setChecked(False)

    def alternar_visibilidad(self, mostrar):
        modo = QLineEdit.EchoMode.Normal if mostrar else QLineEdit.EchoMode.Password
        for campo in (self.txt_actual, self.txt_nueva, self.txt_confirmar):
            campo.setEchoMode(modo)

    def actualizar_fortaleza(self, clave):
        nivel, texto, color = calcular_fortaleza(clave.strip())
        for i, barra in enumerate(self.barras):
            fondo = color if i < nivel else COLOR_BARRA_VACIA
            barra.setStyleSheet(f"background-color: {fondo}; border: none; border-radius: 3px;")
        self.lbl_fortaleza.setText(texto)
        self.lbl_fortaleza.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {color}; border: none; background: transparent;")

    # ==================== GUARDADO ====================
    def guardar_cambios(self):
        usuario = self.txt_usuario.text().strip()
        actual = self.txt_actual.text().strip()
        nueva = self.txt_nueva.text().strip()
        confirmar = self.txt_confirmar.text().strip()
        cambia_clave = bool(nueva or confirmar)
        cambia_usuario = usuario != self.nombre_usuario

        if not usuario:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingresa tu nombre de usuario.")
            return
        if len(usuario) < 3:
            QMessageBox.warning(self, "Usuario inválido", "El nombre de usuario debe tener al menos 3 caracteres.")
            return
        if " " in usuario:
            QMessageBox.warning(self, "Usuario inválido", "El nombre de usuario no puede contener espacios.")
            return

        if not cambia_usuario and not cambia_clave:
            QMessageBox.information(self, "Sin cambios", "No hay cambios que guardar.")
            return

        if not actual:
            QMessageBox.warning(self, "Contraseña actual", "Escribe tu contraseña actual para confirmar los cambios.")
            return

        if cambia_clave:
            if len(nueva) < MIN_CLAVE:
                QMessageBox.warning(self, "Contraseña inválida", f"La nueva contraseña debe tener al menos {MIN_CLAVE} caracteres.")
                return
            if nueva != confirmar:
                QMessageBox.warning(self, "Contraseñas distintas", "La nueva contraseña y su confirmación no coinciden.")
                return
            if nueva == actual:
                QMessageBox.warning(self, "Contraseña repetida", "La nueva contraseña debe ser distinta de la actual.")
                return

        if self.modo_prueba:
            QMessageBox.information(
                self, "Modo de prueba",
                "Las validaciones son correctas.\n\nModo de prueba: los cambios NO se guardaron en la base de datos."
            )
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                QMessageBox.critical(self, "Error de Conexión", "No se pudo conectar con la base de datos MySQL.")
                return

            cursor = conexion.cursor(dictionary=True)

            cursor.execute(
                "SELECT id_usuario FROM usuarios WHERE id_usuario = %s AND `contraseña` = %s",
                (self.id_usuario, actual)
            )
            if not cursor.fetchone():
                cursor.close()
                QMessageBox.warning(self, "Contraseña incorrecta", "La contraseña actual no es correcta.")
                return

            if cambia_usuario:
                cursor.execute(
                    "SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s AND id_usuario <> %s",
                    (usuario, self.id_usuario)
                )
                if cursor.fetchone():
                    cursor.close()
                    QMessageBox.warning(self, "Usuario existente", "Ya existe otro usuario con ese nombre. Elige uno distinto.")
                    return

            if cambia_clave:
                cursor.execute(
                    "UPDATE usuarios SET nombre_usuario = %s, `contraseña` = %s WHERE id_usuario = %s",
                    (usuario, nueva, self.id_usuario)
                )
            else:
                cursor.execute(
                    "UPDATE usuarios SET nombre_usuario = %s WHERE id_usuario = %s",
                    (usuario, self.id_usuario)
                )
            conexion.commit()
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar:\n{e}")
            return

        self.nombre_usuario = usuario
        self.restablecer()
        self.usuario_actualizado.emit(usuario)
        QMessageBox.information(
            self, "Éxito",
            "Tus credenciales se actualizaron correctamente.\n\nLa próxima vez, inicia sesión con tus datos nuevos."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = QWidget()
    ventana.setStyleSheet("background-color: #bfbdbe;")
    layout = QVBoxLayout(ventana)
    layout.setContentsMargins(20, 20, 20, 20)
    pestana = PestanaSeguridad(modo_prueba=True)
    pestana.cargar(0, "usuario_prueba")
    layout.addWidget(pestana)
    ventana.resize(950, 600)
    ventana.show()
    sys.exit(app.exec())