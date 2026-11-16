import re
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QLabel, QScrollArea, QSizePolicy,
    QMenu, QWidgetAction
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD

# Importación de la ventana modal de privilegios
try:
    from .ventana_privilegios import VentanaPrivilegios
except ImportError:
    from ventana_privilegios import VentanaPrivilegios

# Importación de la ventana modal de cambio de rol
try:
    from .cambio_rol import VentanaCambioRol
except ImportError:
    from cambio_rol import VentanaCambioRol

# Importación de la ventana modal de eliminación de usuario
try:
    from .ventana_eliminacion import VentanaEliminacion
except ImportError:
    from ventana_eliminacion import VentanaEliminacion

# Importación de la ventana modal de bloqueo / devolución de acceso
try:
    from .ventana_acceso import VentanaAcceso, asegurar_columna_bloqueado
except ImportError:
    from ventana_acceso import VentanaAcceso, asegurar_columna_bloqueado

# Importación de la ventana modal de actualización de credenciales
try:
    from .actualizar_credenciales import VentanaCredenciales
except ImportError:
    from actualizar_credenciales import VentanaCredenciales


class FilaUsuario(QFrame):
    """Componente interactivo para cada fila de usuario con diseño en contenedor gris"""
    cliqueado = pyqtSignal(dict)
    rol_actualizado = pyqtSignal()
    usuario_eliminado = pyqtSignal()
    acceso_actualizado = pyqtSignal()
    credenciales_actualizadas = pyqtSignal()

    def __init__(self, datos_usuario, parent=None, id_usuario_actual=None):
        super().__init__(parent)
        self.datos = datos_usuario
        self.id_usuario_actual = id_usuario_actual  # Usuario con la sesión iniciada
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(60)
        
        self.setStyleSheet("""
            FilaUsuario {
                background-color: #f4f6f9;
                border-radius: 10px;
                border: 1px solid #e2e6eb;
            }
            FilaUsuario:hover {
                background-color: #eef2f7;
                border: 1px solid #d0d7de;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(20)

        # 1. Nombre de usuario
        self.lbl_usuario = QLabel(self.datos.get("usuario", "N/D"))
        self.lbl_usuario.setStyleSheet("font-size: 13px; font-weight: bold; color: #163e7a; border: none; background: transparent;")
        self.lbl_usuario.setFixedWidth(140)

        # 2. Trabajador vinculado
        self.lbl_trabajador = QLabel(self.datos.get("trabajador_vinculado", "N/D"))
        self.lbl_trabajador.setStyleSheet("font-size: 13px; color: #333333; border: none; background: transparent;")
        
        # 2.1 Cédula del trabajador
        self.lbl_cedula = QLabel(str(self.datos.get("cedula", "N/D")))
        self.lbl_cedula.setStyleSheet("font-size: 13px; color: #333333; border: none; background: transparent;")
        self.lbl_cedula.setFixedWidth(110)

        # 3. Rol asignado
        self.lbl_rol = QLabel(self.datos.get("rol", "N/D"))
        self.lbl_rol.setStyleSheet("font-size: 13px; font-weight: bold; color: #555555; border: none; background: transparent;")
        self.lbl_rol.setFixedWidth(140)

        # 4. Último acceso
        self.lbl_acceso = QLabel(str(self.datos.get("ultimo_acceso", "N/D")))
        self.lbl_acceso.setStyleSheet("font-size: 12px; color: #666666; border: none; background: transparent;")
        self.lbl_acceso.setFixedWidth(150)

        # 5. Botón de opciones con tres puntos en vertical (⋮)
        self.btn_puntos = QPushButton("⋮")
        self.btn_puntos.setFixedSize(32, 32)
        self.btn_puntos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_puntos.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #555555;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #dcdcdc;
            }
            QPushButton:hover {
                background-color: #e0dede;
                color: black;
            }
        """)

        # Usuario con el acceso bloqueado: sus datos se ven en gris y tachados
        if self.datos.get("bloqueado"):
            for lbl in (self.lbl_usuario, self.lbl_trabajador, self.lbl_cedula, self.lbl_rol, self.lbl_acceso):
                lbl.setStyleSheet(re.sub(
                    r"color:\s*#[0-9a-fA-F]+;",
                    "color: #9e9e9e; text-decoration: line-through;",
                    lbl.styleSheet()
                ))

        layout.addWidget(self.lbl_usuario)
        layout.addWidget(self.lbl_trabajador, stretch=1)
        layout.addWidget(self.lbl_cedula)
        layout.addWidget(self.lbl_rol)
        layout.addWidget(self.lbl_acceso)
        layout.addWidget(self.btn_puntos)

        self.btn_puntos.clicked.connect(self.mostrar_menu_opciones)

    def mostrar_menu_opciones(self):
        """Despliega el menú de opciones del usuario (por ahora sin funcionalidad)"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                padding: 4px;
            }
        """)

        estilo_normal = """
            QPushButton {
                background-color: transparent;
                color: #333333;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f4f6f9;
            }
        """
        estilo_peligro = """
            QPushButton {
                background-color: transparent;
                color: #d32f2f;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #fdecec;
            }
        """

        # Si el usuario está bloqueado, la opción pasa a devolver el acceso
        texto_acceso = "Devolver acceso" if self.datos.get("bloqueado") else "Bloquear acceso"

        # (texto, estilo, función a ejecutar); None = funcionalidad pendiente
        opciones = [
            ("Asignar privilegios", estilo_normal, self.abrir_privilegios),
            ("Cambiar rol", estilo_normal, self.abrir_cambio_rol),
            ("Actualizar credenciales", estilo_normal, self.abrir_credenciales),
            (texto_acceso, estilo_normal, self.abrir_acceso),
            ("Eliminar usuario", estilo_peligro, self.abrir_eliminacion),
        ]

        elegida = []
        for texto, estilo, funcion in opciones:
            boton = QPushButton(texto)
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.setMinimumWidth(200)
            boton.setStyleSheet(estilo)
            boton.clicked.connect(lambda _=False, f=funcion: elegida.append(f))
            boton.clicked.connect(menu.close)
            accion = QWidgetAction(menu)
            accion.setDefaultWidget(boton)
            menu.addAction(accion)

        # Alinear el borde derecho del menú con el del botón de tres puntos
        ancho_menu = menu.sizeHint().width()
        posicion = self.btn_puntos.mapToGlobal(
            QPoint(self.btn_puntos.width() - ancho_menu, self.btn_puntos.height() + 4)
        )
        menu.exec(posicion)

        # La acción se ejecuta cuando el menú ya se cerró
        if elegida and elegida[0]:
            elegida[0]()

    def abrir_privilegios(self):
        """Abre la ventana modal para marcar/desmarcar las ventanas a las que accede el usuario"""
        ventana = VentanaPrivilegios(self.datos, self.window())
        ventana.exec()

    def abrir_cambio_rol(self):
        """Abre la ventana modal para elegir el nuevo rol del usuario"""
        ventana = VentanaCambioRol(self.datos, self.window())
        if ventana.exec():
            # Se guardó un cambio: se avisa para refrescar la lista y los contadores
            self.rol_actualizado.emit()

    def abrir_eliminacion(self):
        """Abre la ventana modal de confirmación para eliminar al usuario"""
        ventana = VentanaEliminacion(self.datos, self.window(), self.id_usuario_actual)
        if ventana.exec():
            # Se eliminó el usuario: se avisa para refrescar la lista y los contadores
            self.usuario_eliminado.emit()

    def abrir_credenciales(self):
        """Abre la ventana modal para actualizar el usuario y la contraseña"""
        ventana = VentanaCredenciales(self.datos, self.window())
        if ventana.exec():
            # Se guardaron los cambios: se avisa para refrescar la lista
            self.credenciales_actualizadas.emit()

    def abrir_acceso(self):
        """Abre la ventana modal para bloquear el acceso del usuario o devolvérselo"""
        ventana = VentanaAcceso(self.datos, self.window(), self.id_usuario_actual)
        if ventana.exec():
            # Se cambió el estado del acceso: se avisa para refrescar la lista
            self.acceso_actualizado.emit()

    def mousePressEvent(self, event):
        self.cliqueado.emit(self.datos)
        super().mousePressEvent(event)


class TarjetaMetricaRol(QFrame):
    """Tarjeta superior interactiva con número, título y descripción detallada del rol"""
    cliqueada = pyqtSignal(str)

    def __init__(self, titulo, valor, descripcion, color_borde, filtro_rol="", parent=None):
        super().__init__(parent)
        self.filtro_rol = filtro_rol
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
        layout.setSpacing(4)
        
        self.lbl_tit = QLabel(titulo)
        self.lbl_tit.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; border: none; background: transparent;")
        
        self.lbl_val = QLabel(valor)
        self.lbl_val.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color_borde}; border: none; background: transparent;")
        
        self.lbl_desc = QLabel(descripcion)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("font-size: 11px; color: #777777; border: none; background: transparent;")

        layout.addWidget(self.lbl_tit)
        layout.addWidget(self.lbl_val)
        layout.addWidget(self.lbl_desc)

    def mousePressEvent(self, event):
        self.cliqueada.emit(self.filtro_rol)
        super().mousePressEvent(event)


class VentanaUsuarios(QWidget):
    def __init__(self, parent=None, id_usuario_actual=None):
        super().__init__(parent)

        self.id_usuario_actual = id_usuario_actual  # Usuario con la sesión iniciada
        self.filtro_actual = "todos"

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        # 1. Cuatro tarjetas superiores interactivas con sus roles y descripciones
        layout_tarjetas = QHBoxLayout()
        layout_tarjetas.setSpacing(12)

        self.card_todos = TarjetaMetricaRol(
            "Total Usuarios", "0", 
            "Cuentas totales registradas en el sistema.", 
            "#163e7a", "todos"
        )
        self.card_todos.cliqueada.connect(self.cambiar_filtro_rol)

        self.card_admin = TarjetaMetricaRol(
            "Administrador", "0", 
            "Control total de configuración y gestión global.", 
            "#235299", "Administrador"
        )
        self.card_admin.cliqueada.connect(self.cambiar_filtro_rol)

        self.card_rrhh = TarjetaMetricaRol(
            "Recursos Humanos", "0", 
            "Administración de expedientes y personal.", 
            "#3b6ba3", "Recursos Humanos"
        )
        self.card_rrhh.cliqueada.connect(self.cambiar_filtro_rol)

        self.card_sec = TarjetaMetricaRol(
            "Secretario/a", "0", 
            "Control de las asistencias diarias.", 
            "#4d7fc2", "Secretario/a"
        )
        self.card_sec.cliqueada.connect(self.cambiar_filtro_rol)

        layout_tarjetas.addWidget(self.card_todos)
        layout_tarjetas.addWidget(self.card_admin)
        layout_tarjetas.addWidget(self.card_rrhh)
        layout_tarjetas.addWidget(self.card_sec)
        layout_principal.addLayout(layout_tarjetas)

        # 2. Panel Principal del Listado
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

        self.lbl_titulo_lista = QLabel("Usuarios del sistema")
        self.lbl_titulo_lista.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;")
        layout_panel.addWidget(self.lbl_titulo_lista)

        # Barra de búsqueda superior
        controles_layout = QHBoxLayout()
        controles_layout.setSpacing(10)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("🔍 Buscar por usuario o trabajador...")
        self.txt_buscar.setFixedSize(280, 36)
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
        self.txt_buscar.textChanged.connect(lambda: self.cargar_usuarios_desde_bd())
        controles_layout.addWidget(self.txt_buscar)
        controles_layout.addStretch()

        layout_panel.addLayout(controles_layout)

        # Encabezados de columnas de la tabla (con fondo gris claro)
        self.barra_encabezados = QFrame()
        self.barra_encabezados.setObjectName("barraEncabezados")
        self.barra_encabezados.setFixedHeight(38)
        self.barra_encabezados.setStyleSheet("""
            QFrame#barraEncabezados {
                background-color: #e9edf2;
                border-radius: 10px;
                border: none;
            }
        """)

        headers_layout = QHBoxLayout(self.barra_encabezados)
        headers_layout.setContentsMargins(15, 0, 15, 0)
        headers_layout.setSpacing(20)
        
        lbl_h1 = QLabel("Usuario")
        lbl_h1.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
        lbl_h1.setFixedWidth(140)

        lbl_h2 = QLabel("Trabajador Vinculado")
        lbl_h2.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")

        lbl_h2b = QLabel("Cédula")
        lbl_h2b.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
        lbl_h2b.setFixedWidth(110)

        lbl_h3 = QLabel("Rol Asignado")
        lbl_h3.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
        lbl_h3.setFixedWidth(140)

        lbl_h4 = QLabel("Último Acceso")
        lbl_h4.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
        lbl_h4.setFixedWidth(150)

        lbl_h5 = QLabel("")
        lbl_h5.setStyleSheet("background: transparent;")
        lbl_h5.setFixedWidth(32)

        headers_layout.addWidget(lbl_h1)
        headers_layout.addWidget(lbl_h2, stretch=1)
        headers_layout.addWidget(lbl_h2b)
        headers_layout.addWidget(lbl_h3)
        headers_layout.addWidget(lbl_h4)
        headers_layout.addWidget(lbl_h5)
        layout_panel.addWidget(self.barra_encabezados)

        # Scroll Area para la lista de usuarios
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.contenedor_filas = QWidget()
        self.contenedor_filas.setStyleSheet("background: transparent; border: none;")
        self.layout_filas = QVBoxLayout(self.contenedor_filas)
        self.layout_filas.setContentsMargins(0, 0, 0, 0)
        self.layout_filas.setSpacing(8)
        self.layout_filas.addStretch()

        self.scroll_area.setWidget(self.contenedor_filas)
        layout_panel.addWidget(self.scroll_area)

        layout_principal.addWidget(self.panel_listado)

        # Cargar métricas y datos iniciales
        self.asegurar_columna_ultimo_acceso()
        asegurar_columna_bloqueado()
        self.actualizar_metricas_roles()
        self.cargar_usuarios_desde_bd()

    def cambiar_filtro_rol(self, rol):
        self.filtro_actual = rol
        if rol == "todos":
            self.lbl_titulo_lista.setText("Usuarios del sistema")
        else:
            self.lbl_titulo_lista.setText(f"Usuarios del sistema - {rol}")
        self.cargar_usuarios_desde_bd()

    def asegurar_columna_ultimo_acceso(self):
        """La tabla usuarios no tiene 'ultimo_acceso'; se agrega una sola vez si falta."""
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SHOW COLUMNS FROM usuarios LIKE 'ultimo_acceso'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE usuarios ADD COLUMN ultimo_acceso DATETIME NULL")
                    conexion.commit()
                cursor.close()
        except Exception as e:
            print(f"Error al verificar la columna ultimo_acceso: {e}")

    def actualizar_metricas_roles(self):
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)

                # Consultas para los contadores de cada widget
                cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
                res_total = cursor.fetchone()
                self.card_todos.lbl_val.setText(str(res_total['total'] if res_total else 0))

                consulta_rol = """
                    SELECT COUNT(*) AS total
                    FROM usuarios u
                    INNER JOIN roles r ON u.id_rol_fk = r.id_rol
                    WHERE r.nombre_rol = %s
                """

                cursor.execute(consulta_rol, ('Administrador',))
                res_admin = cursor.fetchone()
                self.card_admin.lbl_val.setText(str(res_admin['total'] if res_admin else 0))

                cursor.execute(consulta_rol, ('Recursos Humanos',))
                res_rrhh = cursor.fetchone()
                self.card_rrhh.lbl_val.setText(str(res_rrhh['total'] if res_rrhh else 0))

                cursor.execute(consulta_rol, ('Secretario/a',))
                res_sec = cursor.fetchone()
                self.card_sec.lbl_val.setText(str(res_sec['total'] if res_sec else 0))

                cursor.close()
        except Exception as e:
            print(f"Error al actualizar métricas de usuarios: {e}")

    def cargar_usuarios_desde_bd(self):
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
                
                sql = """
                    SELECT 
                        u.id_usuario AS id_usuario,
                        COALESCE(u.bloqueado, 0) AS bloqueado,
                        u.nombre_usuario AS usuario,
                        COALESCE(CONCAT(t.nombres, ' ', t.apellidos), 'Sin vincular') AS trabajador_vinculado,
                        COALESCE(t.cedula_trabajador, 'N/D') AS cedula,
                        COALESCE(r.nombre_rol, 'Sin rol') AS rol,
                        COALESCE(DATE_FORMAT(u.ultimo_acceso, '%Y-%m-%d %H:%i'), 'Nunca') AS ultimo_acceso
                    FROM usuarios u
                    LEFT JOIN trabajadores t ON u.cedula_trabajador_fk = t.cedula_trabajador
                    LEFT JOIN roles r ON u.id_rol_fk = r.id_rol
                    WHERE 1=1
                """
                
                params = []

                if self.filtro_actual != "todos":
                    sql += " AND r.nombre_rol = %s"
                    params.append(self.filtro_actual)

                if texto_busqueda:
                    sql += """ AND (u.nombre_usuario LIKE %s 
                                   OR t.nombres LIKE %s 
                                   OR t.apellidos LIKE %s 
                                   OR CONCAT(t.nombres, ' ', t.apellidos) LIKE %s)"""
                    patron = f"%{texto_busqueda}%"
                    params.extend([patron, patron, patron, patron])

                sql += " ORDER BY u.id_usuario"

                cursor.execute(sql, tuple(params))
                usuarios = cursor.fetchall()
                cursor.close()

                for u in usuarios:
                    fila = FilaUsuario(u, id_usuario_actual=self.id_usuario_actual)
                    fila.rol_actualizado.connect(self.cargar_usuarios_desde_bd)
                    fila.usuario_eliminado.connect(self.cargar_usuarios_desde_bd)
                    fila.acceso_actualizado.connect(self.cargar_usuarios_desde_bd)
                    fila.credenciales_actualizadas.connect(self.cargar_usuarios_desde_bd)
                    self.layout_filas.insertWidget(self.layout_filas.count() - 1, fila)

                self.actualizar_metricas_roles()

        except Exception as e:
            print(f"Error al listar usuarios desde la BD: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaUsuarios()
    ventana.resize(1100, 650)
    ventana.show()
    sys.exit(app.exec())