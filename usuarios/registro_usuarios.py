import sys
import os
import re
import tempfile
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QFrame,
    QLineEdit, QComboBox, QListView, QPushButton, QLabel, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QPen, QPolygonF

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
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
    """Dibuja la flecha de la lista desplegable y la guarda como imagen temporal"""
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


def formatear_digitos_cedula(digitos):
    """'31776780' -> '31.776.780' (puntos por miles, de derecha a izquierda)"""
    partes = []
    while digitos:
        partes.insert(0, digitos[-3:])
        digitos = digitos[:-3]
    return ".".join(partes)


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
    QCheckBox {
        font-size: 12px;
        color: #555555;
        background: transparent;
    }
"""

# Estados posibles al comprobar la cédula escrita
MENSAJES_TRABAJADOR = {
    "no_existe": ("✖ No hay ningún trabajador registrado con esa cédula.", "#d32f2f"),
    "retirado": ("✖ Este trabajador está retirado y no puede tener una cuenta.", "#d32f2f"),
    "ya_tiene_cuenta": ("✖ Este trabajador ya tiene una cuenta de usuario.", "#d32f2f"),
}


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
        print(f"Error al consultar datos para el registro de usuarios: {e}")
    return []


class VentanaRegistroUsuario(QDialog):
    """Ventana modal para registrar un usuario; solo se admiten trabajadores que ya estén en la base de datos"""

    def __init__(self, parent=None, permitir_admin=False, modo_prueba=False):
        super().__init__(parent)

        # Solo un administrador puede crear otras cuentas de administrador
        self.permitir_admin = permitir_admin
        # En modo prueba la ventana funciona completa pero NO escribe en la base de datos
        self.modo_prueba = modo_prueba

        self.id_usuario_nuevo = None
        self.roles = {}  # {id_rol: nombre_rol} de los roles que se pueden asignar

        titulo = "Registrar usuario"
        self.setWindowTitle(titulo + (" (modo prueba)" if modo_prueba else ""))
        self.setFixedSize(540, 600)
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

        # ---------- Cédula del trabajador (con puntos automáticos) ----------
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Ej. 12.345.678")
        self.txt_cedula.setMaxLength(11)
        self.txt_cedula.setFixedHeight(36)
        self.txt_cedula.textChanged.connect(self.al_cambiar_cedula)
        form.addRow("Cédula del trabajador:", self.txt_cedula)

        self.lbl_trabajador = QLabel("Escribe la cédula de un trabajador registrado en el sistema.")
        self.lbl_trabajador.setWordWrap(True)
        self.lbl_trabajador.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
        form.addRow("", self.lbl_trabajador)

        # ---------- Usuario y contraseña ----------
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Nombre de usuario")
        self.txt_usuario.setMaxLength(20)
        self.txt_usuario.setFixedHeight(36)
        form.addRow("Nombre de usuario:", self.txt_usuario)

        self.txt_clave = QLineEdit()
        self.txt_clave.setPlaceholderText("Contraseña")
        self.txt_clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_clave.setMaxLength(60)
        self.txt_clave.setFixedHeight(36)
        form.addRow("Contraseña:", self.txt_clave)

        self.chk_mostrar = QCheckBox("Mostrar contraseña")
        self.chk_mostrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_mostrar.toggled.connect(self.alternar_visibilidad)
        form.addRow("", self.chk_mostrar)

        # ---------- Rol ----------
        self.cmb_rol = QComboBox()
        self.cmb_rol.setView(QListView())
        self.cmb_rol.setFixedHeight(36)
        self.cmb_rol.setPlaceholderText("Seleccione el rol")
        form.addRow("Rol:", self.cmb_rol)

        layout_card.addLayout(form)

        texto_ayuda = ("Solo se pueden crear cuentas para trabajadores que ya estén registrados "
                       "en el sistema.")
        if not self.permitir_admin:
            texto_ayuda += " No está disponible el rol de Administrador."
        lbl_ayuda = QLabel(texto_ayuda)
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
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton { background-color: #e0dede; color: #333333; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #d0d0d0; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(self.btn_cancelar)

        self.btn_guardar = QPushButton("Registrar")
        self.btn_guardar.setFixedSize(100, 36)
        self.btn_guardar.setAutoDefault(False)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton { background-color: #163e7a; color: white; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #235299; }
        """)
        self.btn_guardar.clicked.connect(self.guardar_usuario)
        layout_botones.addWidget(self.btn_guardar)

        layout_principal.addLayout(layout_botones)

        # La cédula se comprueba un instante después de dejar de escribir
        self.timer_verificacion = QTimer(self)
        self.timer_verificacion.setSingleShot(True)
        self.timer_verificacion.setInterval(300)
        self.timer_verificacion.timeout.connect(self.mostrar_estado_trabajador)

        self.cargar_roles()

    # ==================== DATOS ====================
    def cargar_roles(self):
        """Roles que se pueden asignar (sin Administrador, salvo que quien registra sea administrador)"""
        self.roles = {}
        self.cmb_rol.clear()
        for fila in _consultar("SELECT id_rol, nombre_rol FROM roles ORDER BY id_rol"):
            if not self.permitir_admin and "admin" in str(fila["nombre_rol"]).lower():
                continue
            self.roles[fila["id_rol"]] = fila["nombre_rol"]
            self.cmb_rol.addItem(fila["nombre_rol"], fila["id_rol"])
        self.cmb_rol.setCurrentIndex(-1)

    # ==================== CÉDULA ====================
    def _digitos_cedula(self):
        return re.sub(r"\D", "", self.txt_cedula.text())

    def al_cambiar_cedula(self, texto):
        """Da formato de miles a la cédula mientras se escribe, conservando la posición del cursor"""
        posicion = self.txt_cedula.cursorPosition()
        digitos_antes = sum(c.isdigit() for c in texto[:posicion])
        digitos = "".join(c for c in texto if c.isdigit())[:9]
        formateado = formatear_digitos_cedula(digitos)

        if formateado != texto:
            self.txt_cedula.blockSignals(True)
            self.txt_cedula.setText(formateado)
            self.txt_cedula.blockSignals(False)

            nueva_posicion, contados = 0, 0
            while nueva_posicion < len(formateado) and contados < digitos_antes:
                if formateado[nueva_posicion].isdigit():
                    contados += 1
                nueva_posicion += 1
            self.txt_cedula.setCursorPosition(nueva_posicion)

        self.timer_verificacion.start()

    def evaluar_trabajador(self, digitos):
        """
        Comprueba la cédula en la base de datos. Devuelve (código, nombre):
        'ok', 'no_existe', 'retirado' o 'ya_tiene_cuenta'.
        """
        filas = _consultar("""
            SELECT t.nombres, t.apellidos, el.descripcion_estado AS estado_laboral,
                   (SELECT COUNT(*) FROM usuarios u WHERE u.cedula_trabajador_fk = t.cedula_trabajador) AS cuentas
            FROM trabajadores t
            LEFT JOIN estados_laborales el ON t.id_estado_laboral_fk = el.id_estado_laboral
            WHERE t.cedula_trabajador = %s
        """, (digitos,))
        if not filas:
            return "no_existe", ""

        fila = filas[0]
        nombre = f"{fila['nombres']} {fila['apellidos']}".strip()
        if "retirado" in str(fila.get("estado_laboral") or "").lower():
            return "retirado", nombre
        if fila["cuentas"] > 0:
            return "ya_tiene_cuenta", nombre
        return "ok", nombre

    def mostrar_estado_trabajador(self):
        digitos = self._digitos_cedula()
        if len(digitos) < 6:
            self.lbl_trabajador.setText("Escribe la cédula de un trabajador registrado en el sistema.")
            self.lbl_trabajador.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
            return

        codigo, nombre = self.evaluar_trabajador(digitos)
        if codigo == "ok":
            texto, color = f"✔ Trabajador: {nombre}", "#1b6e3a"
        else:
            texto, color = MENSAJES_TRABAJADOR[codigo]
        self.lbl_trabajador.setText(texto)
        self.lbl_trabajador.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {color}; background: transparent;")

    def alternar_visibilidad(self, mostrar):
        self.txt_clave.setEchoMode(QLineEdit.EchoMode.Normal if mostrar else QLineEdit.EchoMode.Password)

    # ==================== GUARDADO ====================
    def guardar_usuario(self):
        digitos = self._digitos_cedula()
        usuario = self.txt_usuario.text().strip()
        clave = self.txt_clave.text().strip()
        id_rol = self.cmb_rol.currentData()

        if not digitos:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingrese la cédula del trabajador.")
            return
        if not usuario:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingrese el nombre de usuario.")
            return
        if len(usuario) < 3:
            QMessageBox.warning(self, "Usuario inválido", "El nombre de usuario debe tener al menos 3 caracteres.")
            return
        if " " in usuario:
            QMessageBox.warning(self, "Usuario inválido", "El nombre de usuario no puede contener espacios.")
            return
        if not clave:
            QMessageBox.warning(self, "Campo vacío", "Por favor, ingrese la contraseña.")
            return
        if len(clave) < 4:
            QMessageBox.warning(self, "Contraseña inválida", "La contraseña debe tener al menos 4 caracteres.")
            return
        if id_rol is None:
            QMessageBox.warning(self, "Rol", "Por favor, seleccione el rol del usuario.")
            return

        # Medidas de seguridad: se vuelve a comprobar todo en la base de datos al guardar
        if id_rol not in self.roles:
            QMessageBox.warning(self, "Rol no permitido", "No tienes permiso para asignar ese rol.")
            return

        codigo, _nombre = self.evaluar_trabajador(digitos)
        if codigo == "no_existe":
            QMessageBox.warning(
                self, "Acceso Denegado",
                "La cédula ingresada no pertenece a ningún trabajador registrado en el sistema."
            )
            return
        if codigo == "retirado":
            QMessageBox.warning(self, "Trabajador retirado", "Este trabajador está retirado y no puede tener una cuenta de usuario.")
            return
        if codigo == "ya_tiene_cuenta":
            QMessageBox.warning(self, "Registro Existente", "Ya existe una cuenta de usuario asociada a esta cédula.")
            return

        if _consultar("SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s", (usuario,)):
            QMessageBox.warning(self, "Usuario existente", "Ya existe otro usuario con ese nombre. Elige uno distinto.")
            return

        # Modo prueba: se valida todo pero no se escribe en la base de datos
        if self.modo_prueba:
            QMessageBox.information(
                self, "Modo de prueba",
                "Las validaciones son correctas.\n\nModo de prueba: el usuario NO se guardó en la base de datos."
            )
            self.accept()
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                QMessageBox.critical(self, "Error de Conexión", "No se pudo conectar con la base de datos MySQL.")
                return

            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nombre_usuario, `contraseña`, cedula_trabajador_fk, id_rol_fk) "
                "VALUES (%s, %s, %s, %s)",
                (usuario, clave, digitos, id_rol)
            )
            self.id_usuario_nuevo = cursor.lastrowid
            conexion.commit()
            cursor.close()

            QMessageBox.information(self, "Éxito", "¡Usuario registrado correctamente!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar:\n{e}")


if __name__ == "__main__":
    # Al ejecutar este archivo solo se abre en modo prueba: se puede probar toda la ventana
    # (consulta los trabajadores y roles reales, pero no escribe nada en la base de datos).
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(paleta_clara())
    ventana = VentanaRegistroUsuario(permitir_admin=True, modo_prueba=True)
    ventana.exec()
    sys.exit(0)