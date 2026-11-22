"""Interfaz visual del centro de reportes. Requiere PyQt6.

Clase principal: VentanaReportes(QWidget). Los datos son ilustrativos y los
filtros/exportaciones son visuales en esta primera etapa.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox)


class VentanaReportes(QWidget):
    AZUL = '#2563EB'
    REPORTES = [
        ('Resumen general', 'Indicadores principales del sistema', '▦'),
        ('Trabajadores', 'Listado y estado del personal', '♙'),
        ('Usuarios', 'Cuentas, roles y actividad', '◎'),
        ('Operativas', 'Registro de novedades operativas', '▤'),
        ('Asistencia', 'Control de asistencia y participación', '◷'),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('VentanaReportes')
        self.setWindowTitle('Centro de reportes')
        self.setMinimumSize(980, 650)
        self._reporte_actual = 'Resumen general'
        self._crear_ui()
        self._estilos()
        self._seleccionar_reporte('Resumen general')

    def _crear_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 24)
        root.setSpacing(18)

        top = QHBoxLayout()
        titlebox = QVBoxLayout()
        title = QLabel('Centro de reportes'); title.setObjectName('tituloPrincipal')
        subtitle = QLabel('Consulta, visualiza y prepara los informes de tu institución.'); subtitle.setObjectName('secundario')
        titlebox.addWidget(title); titlebox.addWidget(subtitle)
        top.addLayout(titlebox); top.addStretch()
        tag = QLabel('REPORTES'); tag.setObjectName('tag'); top.addWidget(tag)
        root.addLayout(top)

        body = QHBoxLayout(); body.setSpacing(18); root.addLayout(body, 1)
        left = QFrame(); left.setObjectName('panel'); left.setFixedWidth(258)
        ll = QVBoxLayout(left); ll.setContentsMargins(16, 18, 16, 16); ll.setSpacing(10)
        section = QLabel('TIPO DE REPORTE'); section.setObjectName('seccion'); ll.addWidget(section)
        helptext = QLabel('Selecciona el informe que deseas consultar.'); helptext.setObjectName('secundario'); helptext.setWordWrap(True); ll.addWidget(helptext)
        self.report_buttons = {}
        for name, desc, symbol in self.REPORTES:
            b = QPushButton(); b.setObjectName('tipoReporte'); b.setCheckable(True); b.setCursor(Qt.CursorShape.PointingHandCursor); b.setMinimumHeight(66)
            line = QHBoxLayout(); line.setContentsMargins(0, 0, 0, 0); line.setSpacing(10)
            ico = QLabel(symbol); ico.setObjectName('icono'); ico.setFixedSize(34, 34); ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            texts = QVBoxLayout(); texts.setSpacing(3)
            n = QLabel(name); n.setObjectName('nombreReporte')
            d = QLabel(desc); d.setObjectName('descripcionReporte'); d.setWordWrap(True)
            texts.addWidget(n); texts.addWidget(d); line.addWidget(ico); line.addLayout(texts, 1); b.setLayout(line)
            b.clicked.connect(lambda checked=False, value=name: self._seleccionar_reporte(value))
            ll.addWidget(b); self.report_buttons[name] = b
        ll.addStretch()
        note = QLabel('Los datos se mostrarán según el tipo de informe y los filtros seleccionados.'); note.setObjectName('nota'); note.setWordWrap(True); ll.addWidget(note)
        body.addWidget(left)

        right = QFrame(); right.setObjectName('panel'); rl = QVBoxLayout(right)
        rl.setContentsMargins(20, 18, 20, 18); rl.setSpacing(14)
        head = QHBoxLayout(); names = QVBoxLayout()
        self.report_title = QLabel('Resumen general'); self.report_title.setObjectName('tituloReporte')
        self.report_subtitle = QLabel('Vista previa del informe'); self.report_subtitle.setObjectName('secundario')
        names.addWidget(self.report_title); names.addWidget(self.report_subtitle); head.addLayout(names); head.addStretch()
        previewtag = QLabel('VISTA PREVIA'); previewtag.setObjectName('tag'); head.addWidget(previewtag)
        rl.addLayout(head)

        filters = QFrame(); filters.setObjectName('filtros'); fl = QHBoxLayout(filters); fl.setContentsMargins(12, 10, 12, 10); fl.setSpacing(9)
        def filter_label(text):
            x = QLabel(text); x.setObjectName('labelFiltro'); return x
        self.periodo = QComboBox(); self.periodo.addItems(['Este mes', 'Últimos 30 días', 'Este año', 'Personalizado']); self.periodo.setMinimumWidth(145)
        self.desde = QDateEdit(); self.desde.setCalendarPopup(True); self.desde.setDisplayFormat('dd/MM/yyyy'); self.desde.setDate(self.desde.date().addMonths(-1))
        self.hasta = QDateEdit(); self.hasta.setCalendarPopup(True); self.hasta.setDisplayFormat('dd/MM/yyyy')
        apply = QPushButton('Aplicar filtros'); apply.setObjectName('secundarioBtn'); apply.clicked.connect(self._aplicar_filtros)
        fl.addWidget(filter_label('Periodo')); fl.addWidget(self.periodo); fl.addWidget(filter_label('Desde')); fl.addWidget(self.desde); fl.addWidget(filter_label('Hasta')); fl.addWidget(self.hasta); fl.addStretch(); fl.addWidget(apply)
        rl.addWidget(filters)

        metrics = QGridLayout(); metrics.setHorizontalSpacing(12); self.metric_labels = []
        for i in range(3):
            card = QFrame(); card.setObjectName('metricCard'); cl = QVBoxLayout(card); cl.setContentsMargins(14, 10, 14, 10); cl.setSpacing(3)
            a = QLabel(); a.setObjectName('metricLabel'); v = QLabel(); v.setObjectName('metricValue'); d = QLabel(); d.setObjectName('metricDetail')
            cl.addWidget(a); cl.addWidget(v); cl.addWidget(d); metrics.addWidget(card, 0, i); self.metric_labels.append((a, v, d))
        rl.addLayout(metrics)

        tablehead = QHBoxLayout(); section2 = QLabel('Detalle del reporte'); section2.setObjectName('seccion'); tablehead.addWidget(section2); tablehead.addStretch()
        self.total = QLabel('128 registros'); self.total.setObjectName('secundario'); tablehead.addWidget(self.total); rl.addLayout(tablehead)
        self.table = QTableWidget(5, 4); self.table.setObjectName('tabla'); self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True); self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.table.setShowGrid(False)
        for col in (0, 1): self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        for col in (2, 3): self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(42); rl.addWidget(self.table, 1)

        footer = QHBoxLayout(); footnote = QLabel('La información de esta pantalla es una vista previa.'); footnote.setObjectName('secundario'); footer.addWidget(footnote); footer.addStretch()
        for text, obj in [('PDF', 'exportPdf'), ('Word', 'exportBtn'), ('Excel', 'exportBtn')]:
            b = QPushButton(text); b.setObjectName(obj); b.setMinimumHeight(38); b.setCursor(Qt.CursorShape.PointingHandCursor); b.clicked.connect(self._exportacion_pendiente); footer.addWidget(b)
        rl.addLayout(footer); body.addWidget(right, 1)

    def _estilos(self):
        self.setStyleSheet('''
        QWidget#VentanaReportes { background:#F4F6FA; color:#172033; font-family:"Segoe UI"; font-size:9pt; }
        QLabel#tituloPrincipal { font-size:22pt; font-weight:700; color:#172033; }
        QLabel#tituloReporte { font-size:15pt; font-weight:700; color:#172033; }
        QLabel#secundario, QLabel#metricDetail { color:#718096; font-size:8pt; }
        QLabel#seccion { color:#344054; font-size:8pt; font-weight:700; }
        QLabel#tag { background:#EAF1FF; color:#1E40AF; border-radius:9px; padding:7px 10px; font-weight:700; }
        QFrame#panel { background:white; border:1px solid #E5EAF1; border-radius:13px; }
        QPushButton#tipoReporte { background:transparent; border:1px solid transparent; border-radius:9px; text-align:left; padding:8px; }
        QPushButton#tipoReporte:hover { background:#F6F8FC; border-color:#E5EAF1; }
        QPushButton#tipoReporte:checked { background:#EEF4FF; border:1px solid #C9D9FF; }
        QLabel#icono { background:#F0F4FA; color:#52627A; border-radius:9px; font-size:16pt; font-weight:600; }
        QLabel#nombreReporte { color:#172033; font-weight:650; }
        QLabel#descripcionReporte { color:#718096; font-size:7.5pt; }
        QLabel#nota { background:#F7F9FC; color:#718096; border-radius:8px; padding:10px; font-size:8pt; }
        QFrame#filtros { background:#F8FAFD; border:1px solid #E5EAF1; border-radius:9px; }
        QLabel#labelFiltro { color:#52627A; font-size:8pt; font-weight:600; }
        QComboBox, QDateEdit { background:white; color:#172033; border:1px solid #DCE3ED; border-radius:7px; padding:7px 9px; min-height:19px; }
        QPushButton#secundarioBtn, QPushButton#exportBtn { background:white; color:#344054; border:1px solid #DCE3ED; border-radius:7px; padding:8px 12px; font-weight:600; }
        QPushButton#secundarioBtn:hover, QPushButton#exportBtn:hover { background:#F3F6FB; }
        QFrame#metricCard { background:#FBFCFE; border:1px solid #E5EAF1; border-radius:9px; }
        QLabel#metricLabel { color:#718096; font-size:7.5pt; font-weight:700; }
        QLabel#metricValue { color:#172033; font-size:19pt; font-weight:700; }
        QTableWidget#tabla { background:white; alternate-background-color:#FAFBFD; border:1px solid #E5EAF1; border-radius:8px; color:#344054; padding:3px; font-size:8.5pt; }
        QTableWidget#tabla::item { padding-left:9px; border:none; }
        QTableWidget#tabla::item:selected { background:#EAF1FF; color:#172033; }
        QHeaderView::section { background:#F5F7FA; color:#667085; border:none; border-bottom:1px solid #E5EAF1; padding:10px 8px; font-size:8pt; font-weight:700; }
        QPushButton#exportPdf { background:#2563EB; color:white; border:none; border-radius:7px; padding:8px 14px; font-weight:650; }
        QPushButton#exportPdf:hover { background:#1E40AF; }
        ''')

    def _seleccionar_reporte(self, nombre):
        self._reporte_actual = nombre
        for key, button in self.report_buttons.items(): button.setChecked(key == nombre)
        self.report_title.setText(nombre)
        self.report_subtitle.setText(f'Vista previa · {nombre.lower()} · Datos ilustrativos')
        data = {
            'Resumen general': (['REGISTROS','ACTIVOS','INACTIVOS'], ['128','96','32'], ['En el periodo','Elementos vigentes','Elementos no vigentes'], ['Nombre','Categoría','Fecha','Estado'], [('Ana Martínez','Personal','18/11/2026','Activo'),('Carlos Pérez','Usuario','17/11/2026','Activo'),('María González','Personal','15/11/2026','Inactivo'),('Luis Rodríguez','Operativa','12/11/2026','Activo'),('Sofía Herrera','Usuario','10/11/2026','Activo')]),
            'Trabajadores': (['TRABAJADORES','ACTIVOS','RETIRADOS'], ['48','42','6'], ['Total registrado','Personal activo','Personal retirado'], ['Trabajador','Área','Fecha de ingreso','Estado'], [('Ana Martínez','Administración','03/02/2024','Activo'),('Carlos Pérez','Docencia','14/05/2023','Activo'),('María González','Servicios','21/08/2021','Retirado'),('Luis Rodríguez','Docencia','09/01/2025','Activo'),('Sofía Herrera','Administración','11/03/2022','Activo')]),
            'Usuarios': (['USUARIOS','ACTIVOS','BLOQUEADOS'], ['24','21','3'], ['Cuentas registradas','Cuentas habilitadas','Cuentas bloqueadas'], ['Usuario','Rol','Último acceso','Estado'], [('aperez','Administrador','18/11/2026','Activo'),('mlopez','Operador','17/11/2026','Activo'),('cgarcia','Consulta','14/11/2026','Activo'),('lrojas','Operador','08/11/2026','Bloqueado'),('sherrera','Consulta','02/11/2026','Activo')]),
            'Operativas': (['NOVEDADES','PENDIENTES','FINALIZADAS'], ['36','8','28'], ['Registradas','Por atender','Resueltas'], ['Descripción','Responsable','Fecha','Estado'], [('Revisión de equipos','A. Martínez','18/11/2026','Pendiente'),('Incidencia de aula','C. Pérez','17/11/2026','Finalizada'),('Mantenimiento','L. Rodríguez','16/11/2026','Finalizada'),('Solicitud de apoyo','M. González','13/11/2026','Pendiente'),('Control de inventario','S. Herrera','11/11/2026','Finalizada')]),
            'Asistencia': (['REGISTROS','PRESENTES','AUSENCIAS'], ['320','296','24'], ['Marcas registradas','Asistencias','Inasistencias'], ['Nombre','Grupo','Fecha','Estado'], [('Ana Martínez','Grupo A','18/11/2026','Presente'),('Carlos Pérez','Grupo B','18/11/2026','Presente'),('María González','Grupo A','17/11/2026','Ausente'),('Luis Rodríguez','Grupo C','17/11/2026','Presente'),('Sofía Herrera','Grupo B','16/11/2026','Presente')]),
        }
        labels, values, details, headers, rows = data[nombre]
        for i, (a,v,d) in enumerate(self.metric_labels): a.setText(labels[i]); v.setText(values[i]); d.setText(details[i])
        self.table.clear(); self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(headers); self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem(value)
                if c == 3: item.setForeground(Qt.GlobalColor.darkGreen if value in ('Activo','Presente','Finalizada') else Qt.GlobalColor.darkGray)
                self.table.setItem(r,c,item)
        self.total.setText(f'{values[0]} registros')

    def _aplicar_filtros(self):
        self.report_subtitle.setText(f'Vista previa · {self._reporte_actual.lower()} · Filtros seleccionados')

    def _exportacion_pendiente(self):
        QMessageBox.information(self, 'Exportación', 'La interfaz de exportación está preparada. La generación de archivos PDF, Word y Excel se incorporará en la siguiente etapa.')
