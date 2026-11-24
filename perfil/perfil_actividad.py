import os
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt

try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from database import GestorBD

try:
    from usuarios.ventana_privilegios import obtener_permisos
except ImportError:
    try:
        from ..usuarios.ventana_privilegios import obtener_permisos
    except ImportError:
        from ventana_privilegios import obtener_permisos

ETIQUETAS = {
    "usuarios": "Usuarios",
    "trabajadores": "Trabajadores",
    "votacion": "Centros de Votación",
    "asistencias": "Asistencias",
    "operativas": "Novedades Operativas",
    "reportes": "Reportes",
}


class PestanaActividad(QWidget):
    """Resumen real de cuenta/sesión; no simula un historial de auditoría."""

    def __init__(self, parent=None, modo_prueba=False):
        super().__init__(parent)
        self.modo_prueba = modo_prueba
        self.id_usuario = None
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget { background-color: #ffffff; }")
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaActividad")
        tarjeta.setStyleSheet(
            "QFrame#tarjetaActividad { background-color: #ffffff; border: 1.5px solid #0833a2; border-radius: 18px; }"
        )
        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        titulo = QLabel("Mi actividad")
        titulo.setStyleSheet("font-size: 17px; font-weight: bold; color: #2c2c2c; background: transparent; border: none;")
        layout.addWidget(titulo)
        descripcion = QLabel("Resumen de tu cuenta, estado de sesión y ventanas habilitadas.")
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("font-size: 12px; color: #777777; background: transparent; border: none;")
        layout.addWidget(descripcion)

        self.lbl_estado = QLabel("Estado de cuenta: —")
        self.lbl_ultimo = QLabel("Último acceso: —")
        self.lbl_usuario = QLabel("Usuario: —")
        for lbl in (self.lbl_estado, self.lbl_ultimo, self.lbl_usuario):
            lbl.setStyleSheet(
                "font-size: 13px; color: #444444; background: #f4f6f9; "
                "border: 1px solid #e2e6eb; border-radius: 9px; padding: 10px;"
            )
            layout.addWidget(lbl)

        subtitulo = QLabel("VENTANAS AUTORIZADAS")
        subtitulo.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #8a8a8a; letter-spacing: 1px; background: transparent; border: none;"
        )
        layout.addWidget(subtitulo)
        self.lbl_permisos = QLabel("Cargando permisos…")
        self.lbl_permisos.setWordWrap(True)
        self.lbl_permisos.setStyleSheet(
            "font-size: 12px; color: #555555; background: #f4f6f9; "
            "border: 1px solid #e2e6eb; border-radius: 9px; padding: 12px;"
        )
        layout.addWidget(self.lbl_permisos)

        self.lbl_historial = QLabel(
            "El historial cronológico de acciones requiere una tabla de auditoría; "
            "el esquema actual solo permite consultar el último acceso y el estado de sesión."
        )
        self.lbl_historial.setWordWrap(True)
        self.lbl_historial.setStyleSheet(
            "font-size: 11px; color: #163e7a; background: #eaf1fb; "
            "border: 1px solid #b8cbed; border-radius: 9px; padding: 11px;"
        )
        layout.addWidget(self.lbl_historial)
        layout.addStretch()
        raiz.addWidget(tarjeta)

    def cargar(self, id_usuario):
        self.id_usuario = id_usuario
        if self.modo_prueba:
            self.mostrar_demo()
            return
        if id_usuario is None:
            self._limpiar("No se recibió el identificador de la sesión.")
            return
        cursor = None
        try:
            conexion = GestorBD().obtener_conexion()
            if not conexion:
                raise RuntimeError("No se pudo conectar con la base de datos.")
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT u.nombre_usuario, u.ultimo_acceso, u.en_linea, u.bloqueado,
                          r.nombre_rol
                   FROM usuarios u
                   LEFT JOIN roles r ON r.id_rol = u.id_rol_fk
                   WHERE u.id_usuario = %s LIMIT 1""",
                (id_usuario,)
            )
            fila = cursor.fetchone()
            if not fila:
                self._limpiar("No existe la cuenta asociada a esta sesión.")
                return

            if fila.get("bloqueado"):
                estado = "Cuenta bloqueada"
            elif fila.get("en_linea"):
                estado = "En línea"
            else:
                estado = "Desconectado"
            ultimo = fila.get("ultimo_acceso")
            if ultimo:
                try:
                    ultimo = ultimo.strftime("%d/%m/%Y · %H:%M")
                except AttributeError:
                    ultimo = str(ultimo)
            else:
                ultimo = "Sin registro"

            rol = fila.get("nombre_rol") or ""
            self.lbl_estado.setText(f"Estado de cuenta: {estado}")
            self.lbl_ultimo.setText(f"Último acceso registrado: {ultimo}")
            self.lbl_usuario.setText(
                f"Usuario: {fila.get('nombre_usuario') or '—'}   ·   Rol: {rol or 'Sin rol'}"
            )
            permisos = obtener_permisos(id_usuario, rol)
            habilitadas = [ETIQUETAS.get(k, k) for k, v in permisos.items() if v]
            self.lbl_permisos.setText(
                "\n".join(f"•  {nombre}" for nombre in habilitadas)
                if habilitadas else "No hay ventanas habilitadas para esta cuenta."
            )
        except Exception as error:
            print(f"Error al cargar actividad del usuario {id_usuario}: {error}")
            self._limpiar("No se pudo consultar la actividad de la cuenta.")
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass

    def mostrar_demo(self):
        """Muestra datos ficticios sin consultar ni modificar MySQL."""
        self.lbl_estado.setText("Estado de cuenta: En línea (demostración)")
        self.lbl_ultimo.setText("Último acceso registrado: 20/11/2026 · 09:35")
        self.lbl_usuario.setText("Usuario: m.perez   ·   Rol: Recursos Humanos")
        self.lbl_permisos.setText(
            "•  Inicio\n•  Perfil\n•  Trabajadores\n•  Operativas\n•  Reportes"
        )

    def _limpiar(self, mensaje):
        self.lbl_estado.setText("Estado de cuenta: No disponible")
        self.lbl_ultimo.setText("Último acceso: —")
        self.lbl_usuario.setText("Usuario: —")
        self.lbl_permisos.setText(mensaje)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = QWidget()
    ventana.setWindowTitle("Prueba independiente - Mi actividad")
    ventana.setStyleSheet("background-color: #bfbdbe;")
    layout = QVBoxLayout(ventana)
    layout.setContentsMargins(20, 20, 20, 20)
    pestana = PestanaActividad(modo_prueba=True)
    pestana.mostrar_demo()
    layout.addWidget(pestana)
    ventana.resize(850, 560)
    ventana.show()
    sys.exit(app.exec())