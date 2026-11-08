import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QLabel, QScrollArea, QSizePolicy, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

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


class FilaTrabajador(QFrame):
    """Componente interactivo para cada fila de trabajador en la lista"""
    cliqueado = pyqtSignal(dict)

    def __init__(self, datos_trabajador, parent=None):
        super().__init__(parent)
        self.datos = datos_trabajador
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        
        self.setStyleSheet("""
            FilaTrabajador {
                background-color: transparent;
                border-radius: 10px;
                border-bottom: 1px solid #eaeaea;
            }
            FilaTrabajador:hover {
                background-color: #e8ebf0;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)

        self.lbl_nombre = QLabel(self.datos["nombre"])
        self.lbl_nombre.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; border: none; background: transparent;")
        
        self.lbl_cedula = QLabel(str(self.datos["cedula"]))
        self.lbl_cedula.setStyleSheet("font-size: 14px; font-weight: bold; color: #555555; border: none; background: transparent;")

        layout.addWidget(self.lbl_nombre)
        layout.addStretch()
        layout.addWidget(self.lbl_cedula)

    def mousePressEvent(self, event):
        self.cliqueado.emit(self.datos)
        super().mousePressEvent(event)


class VentanaTrabajadores(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.trabajador_seleccionado = None

        # Layout principal horizontal
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        # Contenedor izquierdo (Tarjetas superiores + Listado)
        self.contenedor_izq = QWidget()
        layout_izq = QVBoxLayout(self.contenedor_izq)
        layout_izq.setContentsMargins(0, 0, 0, 0)
        layout_izq.setSpacing(15)

        # =================================================================
        # 1. TRES TARJETAS DE WIDGETS SUPERIORES
        # =================================================================
        layout_tarjetas = QHBoxLayout()
        layout_tarjetas.setSpacing(15)

        self.card_total = self.crear_tarjeta_metrica("Total Trabajadores", "0", "#163e7a")
        self.card_fijo = self.crear_tarjeta_metrica("Contrato Fijo", "0", "#235299")
        self.card_temporal = self.crear_tarjeta_metrica("Contrato Temporal", "0", "#3b6ba3")

        layout_tarjetas.addWidget(self.card_total)
        layout_tarjetas.addWidget(self.card_fijo)
        layout_tarjetas.addWidget(self.card_temporal)
        layout_izq.addLayout(layout_tarjetas)

        # =================================================================
        # 2. PANEL PRINCIPAL DEL LISTADO
        # =================================================================
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
        self.btn_agregar.setFixedSize(105, 36)
        self.btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #163e7a;
                color: white;
                border-radius: 18px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #235299; }
        """)
        self.btn_agregar.clicked.connect(self.abrir_dialogo_agregar)
        controles_layout.addWidget(self.btn_agregar)

        self.btn_modificar = QPushButton("Modificar")
        self.btn_modificar.setFixedSize(105, 36)
        self.btn_modificar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_modificar.setStyleSheet("""
            QPushButton {
                background-color: #163e7a;
                color: white;
                border-radius: 18px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #235299; }
        """)
        self.btn_modificar.clicked.connect(self.abrir_dialogo_modificar)
        controles_layout.addWidget(self.btn_modificar)

        controles_layout.addStretch()

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("🔍 Buscar trabajador...")
        self.txt_buscar.setFixedSize(220, 36)
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

        # =================================================================
        # 3. TARJETA BLANCA LATERAL DE DETALLES
        # =================================================================
        self.panel_detalles = QFrame()
        self.panel_detalles.setObjectName("panelDetalles")
        self.panel_detalles.setFixedWidth(300)
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

        # Cargar datos reales desde la base de datos MySQL
        self.cargar_trabajadores_desde_bd()

    def crear_tarjeta_metrica(self, titulo, valor, color_borde):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 15px;
                border-left: 6px solid {color_borde};
                border-top: none;
                border-right: none;
                border-bottom: none;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; border: none; background: transparent;")
        
        lbl_val = QLabel(valor)
        lbl_val.setObjectName(f"val_{titulo}")
        lbl_val.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color_borde}; border: none; background: transparent;")
        
        layout.addWidget(lbl_tit)
        layout.addWidget(lbl_val)
        return card

    def cargar_trabajadores_desde_bd(self):
        """Carga los trabajadores directamente desde la base de datos MySQL"""
        # Limpiar filas anteriores (excepto el stretch final)
        while self.layout_filas.count() > 1:
            item = self.layout_filas.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            db = GestorBD()
            conexion = db.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                sql = """
                    SELECT 
                        t.cedula_trabajador AS cedula,
                        CONCAT(t.nombres, ' ', t.apellidos) AS nombre,
                        COALESCE(d.nombre_departamento, 'General') AS departamento,
                        COALESCE(el.descripcion_estado, 'Fijo') AS contrato,
                        t.telefono,
                        t.correo,
                        t.direccion
                    FROM trabajadores t
                    LEFT JOIN departamentos d ON t.id_departamento_fk = d.id_departamento
                    LEFT JOIN estados_laborales el ON t.id_estado_laboral_fk = el.id_estado_laboral
                """
                cursor.execute(sql)
                trabajadores = cursor.fetchall()
                cursor.close()

                for t in trabajadores:
                    fila = FilaTrabajador(t)
                    fila.cliqueado.connect(self.mostrar_detalles_trabajador)
                    self.layout_filas.insertWidget(self.layout_filas.count() - 1, fila)

                # Actualizar contador de métricas
                total = len(trabajadores)
                val_total = self.card_total.findChild(QLabel, "val_Total Trabajadores")
                if val_total:
                    val_total.setText(str(total))
        except Exception as e:
            print(f"Error al conectar con la base de datos para listar trabajadores: {e}")

    def mostrar_detalles_trabajador(self, datos):
        self.trabajador_seleccionado = datos
        nombre = datos['nombre']
        inicial = nombre[0].upper() if nombre else "?"
        
        self.lbl_avatar.setText(inicial)
        self.lbl_nombre_detalle.setText(nombre)

        texto = f"""
        <b>Cédula:</b> {datos['cedula']}<br><br>
        <b>Departamento:</b> {datos['departamento']}<br><br>
        <b>Tipo Contrato:</b> {datos['contrato']}<br><br>
        <b>Correo:</b> {datos.get('correo', 'N/D')}<br><br>
        <b>Teléfono:</b> {datos.get('telefono', 'N/D')}<br><br>
        <b>Dirección:</b> {datos.get('direccion', 'N/D')}
        """
        self.lbl_detalles_contenido.setText(texto)
        self.panel_detalles.show()

    def ocultar_detalles(self):
        self.trabajador_seleccionado = None
        self.panel_detalles.hide()

    def abrir_dialogo_agregar(self):
        """Abre la ventana modal de registro y actualiza la lista si se guarda"""
        dialogo = RegistroTrabajadores("Registrar Nuevo Trabajador", parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_trabajadores_desde_bd()

    def abrir_dialogo_modificar(self):
        """Abre la ventana modal para modificar al trabajador seleccionado"""
        if not self.trabajador_seleccionado:
            return
        dialogo = RegistroTrabajadores("Modificar Trabajador", datos=self.trabajador_seleccionado, parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_trabajadores_desde_bd()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaTrabajadores()
    ventana.resize(1050, 650)
    ventana.show()
    sys.exit(app.exec())