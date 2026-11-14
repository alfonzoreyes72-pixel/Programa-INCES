import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLabel, QWidget
)
from PyQt6.QtCore import Qt

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


# Ventanas cuyo acceso se controla por usuario: (clave interna, nombre visible).
# Inicio y Perfil quedan fuera porque todos los usuarios las necesitan.
VENTANAS = [
    ("usuarios", "Usuarios"),
    ("trabajadores", "Trabajadores"),
    ("votacion", "Centros de Votación"),
    ("asistencias", "Asistencias"),
    ("operativas", "Novedades Operativas"),
    ("reportes", "Reportes"),
]


def permisos_por_defecto(rol):
    """Accesos que corresponden a cada rol cuando el usuario aún no tiene privilegios guardados."""
    rol_lower = str(rol).lower()
    permisos = {clave: True for clave, _ in VENTANAS}

    if "administrador" in rol_lower:
        return permisos
    if "secretario" in rol_lower:
        for clave in ("usuarios", "trabajadores", "votacion", "operativas"):
            permisos[clave] = False
    elif "recursos" in rol_lower:
        for clave in ("usuarios", "asistencias"):
            permisos[clave] = False
    else:
        for clave in ("usuarios", "trabajadores", "votacion", "asistencias"):
            permisos[clave] = False
    return permisos


def asegurar_tabla_privilegios(cursor):
    """Crea la tabla de privilegios por usuario si todavía no existe."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS privilegios_ventanas (
            id_usuario_fk INT(11) NOT NULL,
            ventana VARCHAR(40) NOT NULL,
            permitido TINYINT(1) NOT NULL DEFAULT 1,
            PRIMARY KEY (id_usuario_fk, ventana),
            CONSTRAINT privilegios_ventanas_ibfk_1 FOREIGN KEY (id_usuario_fk)
                REFERENCES usuarios (id_usuario) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
    """)


def obtener_permisos(id_usuario, rol):
    """
    Devuelve {clave_ventana: True/False} para el usuario.
    Parte de los valores por defecto del rol y los sobrescribe con lo guardado en la BD.
    """
    permisos = permisos_por_defecto(rol)

    if id_usuario is not None:
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                asegurar_tabla_privilegios(cursor)
                cursor.execute(
                    "SELECT ventana, permitido FROM privilegios_ventanas WHERE id_usuario_fk = %s",
                    (id_usuario,)
                )
                for fila in cursor.fetchall():
                    if fila["ventana"] in permisos:
                        permisos[fila["ventana"]] = bool(fila["permitido"])
                cursor.close()
        except Exception as e:
            print(f"Error al leer los privilegios del usuario: {e}")

    # El administrador siempre conserva acceso a Usuarios para no quedarse sin poder gestionarlos
    if "administrador" in str(rol).lower():
        permisos["usuarios"] = True

    return permisos


class FilaPrivilegio(QFrame):
    """Fila con paloma de acceso y nombre de la ventana, con el mismo diseño de las filas de usuarios"""

    def __init__(self, nombre, marcado=True, bloqueado=False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)

        self.setStyleSheet("""
            FilaPrivilegio {
                background-color: #f4f6f9;
                border-radius: 10px;
                border: 1px solid #e2e6eb;
                border-left: 5px solid #163e7a;
            }
            FilaPrivilegio:hover {
                background-color: #eef2f7;
                border: 1px solid #d0d7de;
                border-left: 5px solid #163e7a;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(20)

        # 1. Paloma para marcar y desmarcar el acceso
        self.paloma = QPushButton("✓")
        self.paloma.setCheckable(True)
        self.paloma.setChecked(marcado)
        self.paloma.setFixedSize(28, 28)
        self.paloma.setEnabled(not bloqueado)
        self.paloma.setCursor(Qt.CursorShape.PointingHandCursor)
        self.paloma.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #ffffff;
                border: 2px solid #b8c2d1;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #163e7a;
            }
            QPushButton:checked {
                background-color: #163e7a;
                border: 2px solid #163e7a;
                color: #ffffff;
            }
            QPushButton:disabled {
                border: 2px solid #d0d7de;
            }
            QPushButton:checked:disabled {
                background-color: #8fa6c9;
                border: 2px solid #8fa6c9;
            }
        """)

        contenedor_paloma = QWidget()
        contenedor_paloma.setFixedWidth(60)
        layout_paloma = QHBoxLayout(contenedor_paloma)
        layout_paloma.setContentsMargins(0, 0, 0, 0)
        layout_paloma.addWidget(self.paloma)
        layout_paloma.addStretch()

        # 2. Nombre de la ventana
        self.lbl_nombre = QLabel(nombre)
        self.lbl_nombre.setStyleSheet("font-size: 13px; font-weight: bold; color: #163e7a; border: none; background: transparent;")

        layout.addWidget(contenedor_paloma)
        layout.addWidget(self.lbl_nombre, stretch=1)

        if bloqueado:
            self.setToolTip("El administrador siempre conserva el acceso a Usuarios.")
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def esta_marcado(self):
        return self.paloma.isChecked()

    def mousePressEvent(self, event):
        # Al presionar en cualquier parte de la fila se marca o desmarca la paloma
        if self.paloma.isEnabled():
            self.paloma.toggle()
        super().mousePressEvent(event)


class VentanaPrivilegios(QDialog):
    """Ventana modal para asignar a un usuario el acceso a las ventanas del sistema"""

    def __init__(self, datos_usuario, parent=None):
        super().__init__(parent)

        self.id_usuario = datos_usuario.get("id_usuario")
        self.nombre_usuario = datos_usuario.get("usuario", "N/D")
        self.rol = datos_usuario.get("rol", "")

        self.setWindowTitle("Asignar privilegios")
        self.setModal(True)
        self.setMinimumSize(520, 600)
        self.resize(560, 660)
        self.setStyleSheet("QDialog { background-color: #bfbdbe; }")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Panel principal blanco, igual al de la ventana de usuarios
        self.panel = QFrame()
        self.panel.setObjectName("panelPrivilegios")
        self.panel.setStyleSheet("""
            QFrame#panelPrivilegios {
                background-color: #ffffff;
                border-radius: 20px;
                border: none;
            }
        """)
        layout_principal.addWidget(self.panel)

        layout_panel = QVBoxLayout(self.panel)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(15)

        lbl_titulo = QLabel("Asignar privilegios")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(lbl_titulo)

        lbl_subtitulo = QLabel(f"Usuario: {self.nombre_usuario}   |   Rol: {self.rol}")
        lbl_subtitulo.setStyleSheet("font-size: 13px; color: #777777; border: none; background: transparent;")
        layout_panel.addWidget(lbl_subtitulo)

        # Encabezados de la tabla (con fondo gris claro)
        barra_encabezados = QFrame()
        barra_encabezados.setObjectName("barraEncabezados")
        barra_encabezados.setFixedHeight(38)
        barra_encabezados.setStyleSheet("""
            QFrame#barraEncabezados {
                background-color: #e9edf2;
                border-radius: 10px;
                border: none;
            }
        """)

        headers_layout = QHBoxLayout(barra_encabezados)
        headers_layout.setContentsMargins(15, 0, 15, 0)
        headers_layout.setSpacing(20)

        lbl_h1 = QLabel("Acceso")
        lbl_h1.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
        lbl_h1.setFixedWidth(60)

        lbl_h2 = QLabel("Ventana Disponible")
        lbl_h2.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")

        headers_layout.addWidget(lbl_h1)
        headers_layout.addWidget(lbl_h2, stretch=1)
        layout_panel.addWidget(barra_encabezados)

        # Filas con una paloma por cada ventana
        permisos = obtener_permisos(self.id_usuario, self.rol)
        es_admin = "administrador" in str(self.rol).lower()

        self.filas = {}
        layout_filas = QVBoxLayout()
        layout_filas.setSpacing(8)
        for clave, nombre in VENTANAS:
            bloqueado = es_admin and clave == "usuarios"
            fila = FilaPrivilegio(nombre, marcado=permisos.get(clave, False), bloqueado=bloqueado)
            self.filas[clave] = fila
            layout_filas.addWidget(fila)
        layout_panel.addLayout(layout_filas)

        layout_panel.addStretch()

        # Mensaje de error (solo se muestra si falla el guardado)
        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("font-size: 12px; font-weight: bold; color: #d32f2f; border: none; background: transparent;")
        self.lbl_estado.hide()
        layout_panel.addWidget(self.lbl_estado)

        # Botones inferiores
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(12)
        layout_botones.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(140, 40)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e0dede;
                color: #333333;
                border-radius: 20px;
                border: 2px solid #e0dede;
                padding: 5px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0cdcd;
                border: 2px solid #d0cdcd;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFixedSize(140, 40)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #0833a2;
                color: white;
                border-radius: 20px;
                border: 2px solid #0833a2;
                padding: 5px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3150ff;
                border: 2px solid #3150ff;
            }
        """)
        self.btn_guardar.clicked.connect(self.guardar_privilegios)

        layout_botones.addWidget(self.btn_cancelar)
        layout_botones.addWidget(self.btn_guardar)
        layout_panel.addLayout(layout_botones)

    def guardar_privilegios(self):
        datos = [
            (self.id_usuario, clave, 1 if fila.esta_marcado() else 0)
            for clave, fila in self.filas.items()
        ]

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                asegurar_tabla_privilegios(cursor)
                cursor.executemany(
                    """
                    INSERT INTO privilegios_ventanas (id_usuario_fk, ventana, permitido)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE permitido = VALUES(permitido)
                    """,
                    datos
                )
                conexion.commit()
                cursor.close()
                self.accept()
                return
        except Exception as e:
            print(f"Error al guardar los privilegios: {e}")

        self.lbl_estado.setText("No se pudieron guardar los privilegios. Intenta de nuevo.")
        self.lbl_estado.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrivilegios({"id_usuario": 2, "usuario": "Jesus", "rol": "Recursos Humanos"})
    ventana.exec()
    sys.exit(0)