import sys
import os
import re

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtSvg import QSvgRenderer

# Importación del gestor de base de datos
try:
    from database import GestorBD
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from database import GestorBD


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


class VentanaEliminarCentro(QDialog):
    """Ventana modal de confirmación para eliminar un centro de votación."""

    def __init__(self, datos_centro, parent=None):
        super().__init__(parent)
        self.datos = datos_centro or {}
        self.id_centro = self.datos.get("id_centro_votacion")
        self.eliminado = False

        self.setWindowTitle("Eliminar centro de votación")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setModal(True)
        if parent is not None:
            self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setFixedWidth(480)
        self.setStyleSheet("""
            QDialog {
                background-color: #bfbdbe;
            }
        """)

        self.total_trabajadores = self._contar_trabajadores_vinculados()
        self.tiene_trabajadores = self.total_trabajadores > 0

        self._construir_ui()
        self._centrar_en_padre()

    def _centrar_en_padre(self):
        self.adjustSize()
        padre = self.parentWidget()
        if padre is not None and padre.isVisible():
            geo_padre = padre.window().geometry()
            x = geo_padre.x() + (geo_padre.width() - self.width()) // 2
            y = geo_padre.y() + (geo_padre.height() - self.height()) // 2
            self.move(max(0, x), max(0, y))

    def _contar_trabajadores_vinculados(self):
        """Consulta en BD el número actual de trabajadores asignados al centro."""
        if self.id_centro is None:
            return int(self.datos.get("total_trabajadores", 0) or 0)
        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM trabajadores WHERE id_centro_votacion_fk = %s",
                    (self.id_centro,)
                )
                fila = cursor.fetchone()
                cursor.close()
                if fila is not None:
                    return int(fila["total"] or 0)
        except Exception as e:
            print(f"Error al verificar trabajadores del centro: {e}")
        return int(self.datos.get("total_trabajadores", 0) or 0)

    def _construir_ui(self):
        layout_raiz = QVBoxLayout(self)
        layout_raiz.setContentsMargins(16, 16, 16, 16)
        layout_raiz.setSpacing(0)

        self.panel = QFrame()
        self.panel.setObjectName("panelEliminarCentro")
        self.panel.setStyleSheet("""
            QFrame#panelEliminarCentro {
                background-color: #ffffff;
                border-radius: 20px;
                border: 1px solid #e2e6eb;
            }
        """)
        layout_raiz.addWidget(self.panel)

        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        # ==================== CABECERA ====================
        fila_header = QHBoxLayout()
        fila_header.setSpacing(12)

        badge_icono = QFrame()
        badge_icono.setFixedSize(44, 44)
        badge_icono.setStyleSheet("""
            QFrame {
                background-color: #fdecec;
                border: 1px solid #f2b8b8;
                border-radius: 12px;
            }
        """)
        layout_badge = QVBoxLayout(badge_icono)
        layout_badge.setContentsMargins(0, 0, 0, 0)
        layout_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_icono = QLabel()
        lbl_icono.setStyleSheet("background: transparent; border: none;")
        pixmap_basura = cargar_pixmap_svg("iconobasura", 20)
        if pixmap_basura:
            lbl_icono.setPixmap(pixmap_basura)
        else:
            lbl_icono.setText("🗑")
            lbl_icono.setStyleSheet("font-size: 18px; color: #d32f2f; background: transparent; border: none;")
        layout_badge.addWidget(lbl_icono)

        col_titulos = QVBoxLayout()
        col_titulos.setSpacing(2)

        lbl_titulo = QLabel("Eliminar centro de votación")
        lbl_titulo.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #2c2c2c; border: none; background: transparent;"
        )

        lbl_subtitulo = QLabel("Confirma los detalles antes de borrar el registro.")
        lbl_subtitulo.setStyleSheet(
            "font-size: 12px; color: #777777; border: none; background: transparent;"
        )

        col_titulos.addWidget(lbl_titulo)
        col_titulos.addWidget(lbl_subtitulo)

        fila_header.addWidget(badge_icono)
        fila_header.addLayout(col_titulos, stretch=1)
        layout.addLayout(fila_header)

        # ==================== TARJETA RESUMEN DEL CENTRO ====================
        tarjeta_info = QFrame()
        tarjeta_info.setObjectName("fichaCentro")
        tarjeta_info.setStyleSheet("""
            QFrame#fichaCentro {
                background-color: #f4f6f9;
                border-radius: 14px;
                border: none;
                border-left: 5px solid #163e7a;
            }
        """)
        layout_info = QVBoxLayout(tarjeta_info)
        layout_info.setContentsMargins(16, 12, 16, 12)
        layout_info.setSpacing(4)

        nombre_centro = str(self.datos.get("nombre_centro") or "Centro sin nombre")
        parroquia = str(self.datos.get("parroquia") or "N/D")
        municipio = str(self.datos.get("municipio") or "N/D")
        estado = str(self.datos.get("estado") or "N/D")
        direccion = str(self.datos.get("direccion_centro") or "").strip() or "Sin dirección registrada"

        lbl_nombre = QLabel(nombre_centro)
        lbl_nombre.setTextFormat(Qt.TextFormat.PlainText)
        lbl_nombre.setWordWrap(True)
        lbl_nombre.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #163e7a; border: none; background: transparent;"
        )

        lbl_ubic = QLabel(f"{parroquia} · {municipio}, {estado}")
        lbl_ubic.setTextFormat(Qt.TextFormat.PlainText)
        lbl_ubic.setWordWrap(True)
        lbl_ubic.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #555555; border: none; background: transparent;"
        )

        lbl_dir = QLabel(direccion)
        lbl_dir.setTextFormat(Qt.TextFormat.PlainText)
        lbl_dir.setWordWrap(True)
        lbl_dir.setStyleSheet(
            "font-size: 11px; color: #777777; border: none; background: transparent;"
        )

        layout_info.addWidget(lbl_nombre)
        layout_info.addWidget(lbl_ubic)
        layout_info.addWidget(lbl_dir)
        layout.addWidget(tarjeta_info)

        # ==================== AVISO SOBRE TRABAJADORES ====================
        caja_aviso = QFrame()
        caja_aviso.setObjectName("cajaAvisoCentro")
        if self.tiene_trabajadores:
            caja_aviso.setStyleSheet("""
                QFrame#cajaAvisoCentro {
                    background-color: #fdecec;
                    border: 1px solid #f2b8b8;
                    border-radius: 12px;
                }
            """)
            plural = "trabajador asignado" if self.total_trabajadores == 1 else "trabajadores asignados"
            titulo_aviso = f"No se puede eliminar ({self.total_trabajadores} {plural})"
            texto_aviso = (
                "Este centro de votación tiene trabajadores ahí registrados y no puede "
                "eliminarse mientras tenga trabajadores asignados. Reasigna o retira primero "
                "a dichos trabajadores para poder borrar este centro."
            )
            color_titulo_aviso = "#b71c1c"
            color_texto_aviso = "#7f1d1d"
        else:
            caja_aviso.setStyleSheet("""
                QFrame#cajaAvisoCentro {
                    background-color: #fff8e6;
                    border: 1px solid #f3d999;
                    border-radius: 12px;
                }
            """)
            titulo_aviso = "Requisito para eliminar"
            texto_aviso = (
                "Si el centro de votación tiene trabajadores ahí, no puede eliminarse. "
                "Este centro no tiene trabajadores asignados actualmente; marca la casilla "
                "de abajo para confirmar la eliminación."
            )
            color_titulo_aviso = "#8a5a00"
            color_texto_aviso = "#6b4700"

        layout_aviso = QVBoxLayout(caja_aviso)
        layout_aviso.setContentsMargins(14, 10, 14, 10)
        layout_aviso.setSpacing(3)

        lbl_tit_aviso = QLabel(titulo_aviso)
        lbl_tit_aviso.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {color_titulo_aviso}; border: none; background: transparent;"
        )
        lbl_txt_aviso = QLabel(texto_aviso)
        lbl_txt_aviso.setWordWrap(True)
        lbl_txt_aviso.setStyleSheet(
            f"font-size: 11px; color: {color_texto_aviso}; border: none; background: transparent;"
        )

        layout_aviso.addWidget(lbl_tit_aviso)
        layout_aviso.addWidget(lbl_txt_aviso)
        layout.addWidget(caja_aviso)

        # ==================== CHECK DE CONFIRMACIÓN ====================
        self.chk_confirmar = QCheckBox(
            "Confirmo que deseo eliminar este centro de votación."
        )
        self.chk_confirmar.setCursor(
            Qt.CursorShape.ForbiddenCursor if self.tiene_trabajadores else Qt.CursorShape.PointingHandCursor
        )
        self.chk_confirmar.setEnabled(not self.tiene_trabajadores)
        self.chk_confirmar.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                spacing: 8px;
                background: transparent;
                border: none;
            }
            QCheckBox:disabled {
                color: #9e9e9e;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 2px solid #b8c2d1;
                background-color: #f4f6f9;
            }
            QCheckBox::indicator:hover:enabled {
                border: 2px solid #d32f2f;
            }
            QCheckBox::indicator:checked {
                background-color: #d32f2f;
                border: 2px solid #d32f2f;
            }
            QCheckBox::indicator:disabled {
                background-color: #eceff3;
                border: 2px solid #d5dbe3;
            }
        """)
        self.chk_confirmar.toggled.connect(self._actualizar_estado_boton)
        layout.addWidget(self.chk_confirmar)

        # Mensaje de error en caso de fallo de BD
        self.lbl_error = QLabel("")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #d32f2f; background: transparent; border: none;"
        )
        self.lbl_error.hide()
        layout.addWidget(self.lbl_error)

        # ==================== BOTONES INFERIORES ====================
        fila_botones = QHBoxLayout()
        fila_botones.setSpacing(10)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedHeight(36)
        self.btn_cancelar.setMinimumWidth(115)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #f4f6f9;
                color: #333333;
                border: 1px solid #dcdcdc;
                border-radius: 18px;
                padding: 0px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e6eaf0;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_eliminar = QPushButton(" Eliminar centro")
        self.btn_eliminar.setFixedHeight(36)
        self.btn_eliminar.setMinimumWidth(155)
        self.btn_eliminar.setEnabled(False)
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: #ffffff;
                border: 2px solid #d32f2f;
                border-radius: 18px;
                padding: 0px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #b71c1c;
                border: 2px solid #b71c1c;
            }
            QPushButton:disabled {
                background-color: #f3c6c6;
                border: 2px solid #f3c6c6;
                color: #ffffff;
            }
        """)
        pixmap_btn = cargar_pixmap_svg("iconobasura", 14)
        if pixmap_btn:
            icono_btn = QIcon()
            icono_btn.addPixmap(pixmap_btn, QIcon.Mode.Normal)
            icono_btn.addPixmap(pixmap_btn, QIcon.Mode.Disabled)
            self.btn_eliminar.setIcon(icono_btn)
            self.btn_eliminar.setIconSize(QSize(14, 14))
        self.btn_eliminar.clicked.connect(self._ejecutar_eliminacion)

        fila_botones.addStretch()
        fila_botones.addWidget(self.btn_cancelar)
        fila_botones.addWidget(self.btn_eliminar)
        layout.addLayout(fila_botones)

    def _actualizar_estado_boton(self, marcado):
        self.btn_eliminar.setEnabled(bool(marcado) and not self.tiene_trabajadores)

    def _ejecutar_eliminacion(self):
        if self.tiene_trabajadores or not self.chk_confirmar.isChecked():
            return

        # Revalidación final antes de ejecutar el DELETE en la base de datos
        if self._contar_trabajadores_vinculados() > 0:
            self.tiene_trabajadores = True
            self.chk_confirmar.setChecked(False)
            self.chk_confirmar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)
            self.lbl_error.setText(
                "No se puede eliminar este centro porque tiene trabajadores asignados."
            )
            self.lbl_error.show()
            return

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if not conexion:
                self.lbl_error.setText("No se pudo establecer conexión con la base de datos.")
                self.lbl_error.show()
                return

            cursor = conexion.cursor()
            cursor.execute(
                "DELETE FROM centros_votacion WHERE id_centro_votacion = %s",
                (self.id_centro,)
            )
            conexion.commit()
            cursor.close()
            self.eliminado = True
            self.accept()
        except Exception as e:
            try:
                conexion.rollback()
            except Exception:
                pass
            codigo = getattr(e, "errno", None)
            if codigo == 1451 or "foreign key" in str(e).lower():
                self.lbl_error.setText(
                    "No se puede eliminar este centro porque tiene trabajadores u otros registros asociados."
                )
            else:
                self.lbl_error.setText(f"Error al eliminar el centro de votación: {e}")
            self.lbl_error.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ejemplo = {
        "id_centro_votacion": 1,
        "nombre_centro": "U.E.N. Francisco Isnardi",
        "parroquia": "Las Cocuizas",
        "municipio": "Maturín",
        "estado": "Monagas",
        "direccion_centro": "Sector Los Cortijos, Av. Principal",
        "total_trabajadores": 0,
    }
    dlg = VentanaEliminarCentro(ejemplo)
    dlg.exec()
    sys.exit(0)