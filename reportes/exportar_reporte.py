import sys
import os
import re
import zipfile
import tempfile
import unicodedata
from datetime import datetime
from html import escape
from pathlib import Path
from xml.sax.saxutils import escape as escapar_xml

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QFrame,
    QLineEdit, QComboBox, QListView, QPushButton, QLabel, QCheckBox,
    QButtonGroup, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QRectF, QSizeF, QMarginsF, QUrl, QStandardPaths, QPointF
from PyQt6.QtGui import (
    QPalette, QColor, QPixmap, QPainter, QPen, QPolygonF, QFont, QImage,
    QTextDocument, QPdfWriter, QPageSize, QPageLayout, QDesktopServices
)


# ==================== RUTAS AUTOCALCULABLES ====================
# Las imágenes viven en la carpeta 'imagenes' de la raíz del proyecto (junto a ventana_principal.py).
# La ruta se calcula a partir de la ubicación de este archivo, así funciona en cualquier computadora.
_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
CARPETAS_IMAGENES = [
    os.path.join(_DIRECTORIO, '..', 'imagenes'),
    os.path.join(_DIRECTORIO, 'imagenes'),
]


def _clave_nombre(texto):
    """'logo inces.png' -> 'logoinces' (ignora signos, espacios y mayúsculas)"""
    return re.sub(r"[^a-z0-9]", "", os.path.splitext(str(texto))[0].lower())


def buscar_imagen(clave, extensiones=(".png", ".jpg", ".jpeg")):
    for carpeta in CARPETAS_IMAGENES:
        carpeta = os.path.abspath(carpeta)
        if not os.path.isdir(carpeta):
            continue
        for archivo in os.listdir(carpeta):
            if archivo.lower().endswith(extensiones) and _clave_nombre(archivo) == clave:
                return os.path.join(carpeta, archivo)
    return None


# ==================== UTILIDADES ====================
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
    """Dibuja la flecha de las listas desplegables y la guarda como imagen temporal"""
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


def nombre_seguro(texto):
    """'Reporte de novedades · nov 2026' -> 'reporte_de_novedades_nov_2026' (para el nombre del archivo)"""
    texto = unicodedata.normalize("NFD", str(texto))
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn").lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto).strip("_")
    return texto[:60] or "reporte"


def _limpiar_texto_xml(texto):
    """Quita los caracteres de control que Excel no admite"""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(texto))


# ==================== EXPORTAR A EXCEL (sin librerías externas) ====================
def _letra_columna(n):
    """1 -> A, 27 -> AA"""
    letras = ""
    while n > 0:
        n, resto = divmod(n - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


def _celda(columna, fila, texto, estilo=0):
    texto = _limpiar_texto_xml(texto)
    if texto == "":
        return ""
    return (f'<c r="{_letra_columna(columna)}{fila}" t="inlineStr" s="{estilo}">'
            f'<is><t xml:space="preserve">{escapar_xml(texto)}</t></is></c>')


def _hoja_reporte(titulo, subtitulo, encabezados, filas):
    fila_encabezado = 4
    filas_xml = [
        f'<row r="1">{_celda(1, 1, titulo, 2)}</row>',
        f'<row r="2">{_celda(1, 2, subtitulo, 3)}</row>',
    ]
    celdas = "".join(_celda(i + 1, fila_encabezado, h, 1) for i, h in enumerate(encabezados))
    filas_xml.append(f'<row r="{fila_encabezado}" ht="22" customHeight="1">{celdas}</row>')

    anchos = [len(str(h)) + 2 for h in encabezados]
    for numero, fila in enumerate(filas, start=fila_encabezado + 1):
        celdas = []
        for i, valor in enumerate(fila):
            celdas.append(_celda(i + 1, numero, valor))
            if i < len(anchos):
                anchos[i] = max(anchos[i], min(len(str(valor)), 60) + 2)
        filas_xml.append(f'<row r="{numero}">{"".join(celdas)}</row>')

    columnas = "".join(
        f'<col min="{i + 1}" max="{i + 1}" width="{min(max(ancho, 10), 60)}" customWidth="1"/>'
        for i, ancho in enumerate(anchos)
    )
    ultima_columna = _letra_columna(max(len(encabezados), 1))
    ultima_fila = fila_encabezado + len(filas)
    autofiltro = f'<autoFilter ref="A{fila_encabezado}:{ultima_columna}{ultima_fila}"/>' if filas else ""

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0">'
        f'<pane ySplit="{fila_encabezado}" topLeftCell="A{fila_encabezado + 1}" activePane="bottomLeft" state="frozen"/>'
        '<selection pane="bottomLeft"/></sheetView></sheetViews>'
        f'<cols>{columnas}</cols>'
        f'<sheetData>{"".join(filas_xml)}</sheetData>'
        f'{autofiltro}'
        '</worksheet>'
    )


def _hoja_filtros(titulo, filtros):
    filas_xml = [f'<row r="1">{_celda(1, 1, titulo, 2)}</row>']
    for numero, (etiqueta, valor) in enumerate(filtros, start=3):
        filas_xml.append(f'<row r="{numero}">{_celda(1, numero, etiqueta, 1)}{_celda(2, numero, valor)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<cols><col min="1" max="1" width="28" customWidth="1"/><col min="2" max="2" width="50" customWidth="1"/></cols>'
        f'<sheetData>{"".join(filas_xml)}</sheetData>'
        '</worksheet>'
    )


ESTILOS_XLSX = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<fonts count="4">'
    '<font><sz val="11"/><name val="Calibri"/></font>'
    '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>'
    '<font><b/><sz val="14"/><color rgb="FF163E7A"/><name val="Calibri"/></font>'
    '<font><sz val="10"/><color rgb="FF777777"/><name val="Calibri"/></font>'
    '</fonts>'
    '<fills count="3">'
    '<fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FF163E7A"/><bgColor indexed="64"/></patternFill></fill>'
    '</fills>'
    '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="4">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1">'
    '<alignment horizontal="left" vertical="center"/></xf>'
    '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
    '<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
    '</cellXfs>'
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    '</styleSheet>'
)


def exportar_excel(ruta, datos, titulo, incluir_filtros=True):
    """Crea un archivo .xlsx con el reporte (encabezado azul, filtros activos, panel fijo y hoja de filtros)"""
    fecha = datos.get("fecha_generacion") or datetime.now()
    filas = datos["filas"]
    subtitulo = f"Generado el {fecha:%d/%m/%Y %H:%M} · {len(filas)} registro" + ("" if len(filas) == 1 else "s")

    hojas = [("Reporte", _hoja_reporte(titulo, subtitulo, datos["encabezados"], filas))]
    if incluir_filtros and datos.get("filtros"):
        hojas.append(("Filtros", _hoja_filtros("Filtros aplicados", datos["filtros"])))

    tipos_hojas = "".join(
        f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for i in range(1, len(hojas) + 1)
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        f'{tipos_hojas}'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '</Types>'
    )
    rels_raiz = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/></Relationships>'
    )
    hojas_libro = "".join(
        f'<sheet name="{escapar_xml(nombre)}" sheetId="{i}" r:id="rId{i}"/>'
        for i, (nombre, _) in enumerate(hojas, start=1)
    )
    libro = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets>{hojas_libro}</sheets></workbook>'
    )
    relaciones_hojas = "".join(
        f'<Relationship Id="rId{i}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{i}.xml"/>'
        for i in range(1, len(hojas) + 1)
    )
    rels_libro = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'{relaciones_hojas}'
        f'<Relationship Id="rId{len(hojas) + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/></Relationships>'
    )

    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as zip_xlsx:
        zip_xlsx.writestr("[Content_Types].xml", content_types)
        zip_xlsx.writestr("_rels/.rels", rels_raiz)
        zip_xlsx.writestr("xl/workbook.xml", libro)
        zip_xlsx.writestr("xl/_rels/workbook.xml.rels", rels_libro)
        zip_xlsx.writestr("xl/styles.xml", ESTILOS_XLSX)
        for i, (_, contenido) in enumerate(hojas, start=1):
            zip_xlsx.writestr(f"xl/worksheets/sheet{i}.xml", contenido)


# ==================== EXPORTAR A PDF (con las herramientas de Qt, sin instalar nada) ====================
def _html_reporte(datos, incluir_filtros):
    """Tabla del reporte en HTML sencillo, que Qt dibuja y reparte en páginas"""
    encabezados = datos["encabezados"]
    filas = datos["filas"]
    pt = 8 if len(encabezados) <= 8 else (7 if len(encabezados) <= 11 else 6)

    partes = [f'<html><body style="font-family: Arial; font-size: {pt}pt; color: #333333;">']
    total = len(filas)
    resumen = f"{total} registro" + ("" if total == 1 else "s")
    partes.append(f'<p style="font-size: {pt + 1}pt; color: #555555;"><b>{resumen}</b></p>')

    if incluir_filtros and datos.get("filtros"):
        texto = " &nbsp;·&nbsp; ".join(f"<b>{escape(str(e))}:</b> {escape(str(v))}" for e, v in datos["filtros"])
        partes.append(f'<p style="font-size: {pt}pt;">Filtros aplicados: {texto}</p>')

    partes.append('<table width="100%" cellspacing="0" cellpadding="3"><thead><tr>')
    for h in encabezados:
        partes.append(
            f'<th align="left" style="background-color:#163e7a; color:#ffffff; font-size:{pt}pt;">{escape(str(h))}</th>'
        )
    partes.append('</tr></thead><tbody>')

    for numero, fila in enumerate(filas):
        fondo = "#f4f6f9" if numero % 2 else "#ffffff"
        partes.append("<tr>")
        for valor in fila:
            partes.append(f'<td style="background-color:{fondo}; font-size:{pt}pt;">{escape(str(valor))}</td>')
        partes.append("</tr>")
    partes.append("</tbody></table></body></html>")
    return "".join(partes)


def exportar_pdf(ruta, datos, titulo, horizontal=True, oficio=False,
                 incluir_logo=True, incluir_filtros=True, numerar_paginas=True):
    """Crea un PDF con logo, título, tabla repartida en páginas (con el encabezado repetido) y numeración"""
    fecha = datos.get("fecha_generacion") or datetime.now()

    writer = QPdfWriter(ruta)
    writer.setResolution(300)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.Legal if oficio else QPageSize.PageSizeId.Letter))
    writer.setPageOrientation(QPageLayout.Orientation.Landscape if horizontal else QPageLayout.Orientation.Portrait)
    writer.setPageMargins(QMarginsF(12, 12, 12, 10), QPageLayout.Unit.Millimeter)
    writer.setTitle(titulo)
    writer.setCreator("Sistema INCES")

    mm = writer.resolution() / 25.4
    ancho = writer.width()
    alto = writer.height()
    alto_encabezado = int(20 * mm)
    alto_pie = int(9 * mm)

    # Documento con la tabla; se mide con la resolución del PDF
    documento = QTextDocument()
    documento.documentLayout().setPaintDevice(writer)
    documento.setDocumentMargin(0)
    documento.setHtml(_html_reporte(datos, incluir_filtros))
    alto_contenido = alto - alto_encabezado - alto_pie
    documento.setPageSize(QSizeF(ancho, alto_contenido))
    paginas = max(1, documento.pageCount())

    # Logo (se busca el logo a color; el del menú lateral es blanco y no se vería en una hoja blanca)
    logo = None
    if incluir_logo:
        ruta_logo = buscar_imagen("logoinces")
        if ruta_logo:
            imagen = QImage(ruta_logo)
            if not imagen.isNull():
                logo = imagen

    painter = QPainter(writer)
    try:
        for pagina in range(paginas):
            if pagina > 0:
                writer.newPage()

            # --- Encabezado ---
            x = 0
            if logo is not None:
                alto_logo = 14 * mm
                ancho_logo = alto_logo * logo.width() / logo.height()
                painter.drawImage(QRectF(0, 0, ancho_logo, alto_logo), logo)
                x = ancho_logo + 4 * mm

            painter.setPen(QColor("#163e7a"))
            fuente = QFont("Arial", 14)
            fuente.setBold(True)
            painter.setFont(fuente)
            painter.drawText(QRectF(x, 0, ancho - x, 9 * mm),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, titulo)

            painter.setPen(QColor("#555555"))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(QRectF(x, 9 * mm, ancho - x, 5 * mm),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "INCES · Sede Monagas")
            painter.drawText(QRectF(0, 0, ancho, 5 * mm),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
                             f"Generado el {fecha:%d/%m/%Y %H:%M}")

            lapiz = QPen(QColor("#163e7a"))
            lapiz.setWidthF(0.4 * mm)
            painter.setPen(lapiz)
            painter.drawLine(QPointF(0, 17 * mm), QPointF(ancho, 17 * mm))

            # --- Contenido (la parte del documento que corresponde a esta página) ---
            painter.save()
            painter.translate(0, alto_encabezado - pagina * alto_contenido)
            documento.drawContents(painter, QRectF(0, pagina * alto_contenido, ancho, alto_contenido))
            painter.restore()

            # --- Pie de página ---
            if numerar_paginas:
                painter.setPen(QColor("#777777"))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(QRectF(0, alto - alto_pie, ancho, alto_pie),
                                 Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                                 f"Página {pagina + 1} de {paginas}")
    finally:
        painter.end()


# ==================== VENTANA ====================
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
    QComboBox:disabled {
        background-color: #f0f0f0;
        color: #aaaaaa;
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
        font-size: 13px;
        color: #333333;
        background: transparent;
    }
    QCheckBox:disabled {
        color: #aaaaaa;
    }
"""

ESTILO_SEGMENTO = """
    QPushButton {
        background-color: #ffffff;
        color: #163e7a;
        border: 2px solid #163e7a;
        border-radius: 18px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #eef2f7; }
    QPushButton:checked { background-color: #163e7a; color: #ffffff; }
"""


class VentanaExportarReporte(QDialog):
    """
    Ventana modal para exportar un reporte a PDF o Excel.

    'datos' es un diccionario con:
      - titulo: título sugerido del reporte
      - encabezados: lista con los nombres de las columnas
      - filas: lista de listas con los valores (texto)
      - filtros: lista de (etiqueta, valor) con los filtros aplicados
      - fecha_generacion: datetime del momento en que se generó (opcional)
    """

    def __init__(self, datos, formato="pdf", parent=None):
        super().__init__(parent)

        self.datos = datos
        self.ruta_exportada = None

        self.setWindowTitle("Exportar reporte")
        self.setFixedSize(500, 640)
        self.setPalette(paleta_clara())
        self.setStyleSheet(ESTILO_VENTANA.replace("__FLECHA__", crear_icono_flecha()))

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        lbl_titulo = QLabel("Exportar reporte")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c2c2c; background: transparent;")
        layout_principal.addWidget(lbl_titulo)

        card = QFrame()
        card.setObjectName("cardContenedor")
        card.setStyleSheet("QFrame#cardContenedor { background-color: #ffffff; border-radius: 15px; }")
        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(20, 18, 20, 18)
        layout_card.setSpacing(14)

        total_filas = len(datos["filas"])
        total_columnas = len(datos["encabezados"])
        lbl_resumen = QLabel(f"{total_filas} registro" + ("" if total_filas == 1 else "s")
                             + f" · {total_columnas} columna" + ("" if total_columnas == 1 else "s"))
        lbl_resumen.setStyleSheet("font-size: 12px; font-weight: bold; color: #777777; background: transparent;")
        layout_card.addWidget(lbl_resumen)

        # ---------- Formato ----------
        lbl_formato = QLabel("Formato")
        layout_card.addWidget(lbl_formato)

        fila_formato = QHBoxLayout()
        fila_formato.setSpacing(10)
        self.btn_pdf = QPushButton("PDF")
        self.btn_excel = QPushButton("Excel")
        self.grupo_formato = QButtonGroup(self)
        self.grupo_formato.setExclusive(True)
        for boton in (self.btn_pdf, self.btn_excel):
            boton.setCheckable(True)
            boton.setFixedHeight(36)
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.setStyleSheet(ESTILO_SEGMENTO)
            self.grupo_formato.addButton(boton)
            fila_formato.addWidget(boton, stretch=1)
        layout_card.addLayout(fila_formato)

        # ---------- Opciones ----------
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.cmb_orientacion = QComboBox()
        self.cmb_orientacion.setView(QListView())
        self.cmb_orientacion.setFixedHeight(36)
        self.cmb_orientacion.addItem("Horizontal", True)
        self.cmb_orientacion.addItem("Vertical", False)
        # Con muchas columnas conviene la hoja horizontal
        self.cmb_orientacion.setCurrentIndex(0 if total_columnas > 6 else 1)
        form.addRow("Orientación:", self.cmb_orientacion)

        self.cmb_tamano = QComboBox()
        self.cmb_tamano.setView(QListView())
        self.cmb_tamano.setFixedHeight(36)
        self.cmb_tamano.addItem("Carta", False)
        self.cmb_tamano.addItem("Oficio", True)
        form.addRow("Tamaño de hoja:", self.cmb_tamano)

        self.txt_titulo = QLineEdit(str(datos.get("titulo", "Reporte")))
        self.txt_titulo.setMaxLength(120)
        self.txt_titulo.setFixedHeight(36)
        form.addRow("Título:", self.txt_titulo)
        layout_card.addLayout(form)

        self.chk_logo = QCheckBox("Incluir el logo del INCES")
        self.chk_logo.setChecked(True)
        self.chk_filtros = QCheckBox("Incluir los filtros aplicados")
        self.chk_filtros.setChecked(True)
        self.chk_paginas = QCheckBox("Numerar las páginas")
        self.chk_paginas.setChecked(True)
        for chk in (self.chk_logo, self.chk_filtros, self.chk_paginas):
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            layout_card.addWidget(chk)

        self.lbl_nota = QLabel("")
        self.lbl_nota.setWordWrap(True)
        self.lbl_nota.setStyleSheet("font-size: 11px; font-weight: normal; color: #777777; background: transparent;")
        layout_card.addWidget(self.lbl_nota)

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

        self.btn_guardar = QPushButton("Guardar como…")
        self.btn_guardar.setFixedSize(150, 36)
        self.btn_guardar.setAutoDefault(False)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton { background-color: #163e7a; color: white; border-radius: 18px; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #235299; }
        """)
        self.btn_guardar.clicked.connect(self.guardar_como)
        layout_botones.addWidget(self.btn_guardar)

        layout_principal.addLayout(layout_botones)

        # Formato inicial y señales
        (self.btn_excel if formato == "excel" else self.btn_pdf).setChecked(True)
        self.grupo_formato.buttonClicked.connect(self.actualizar_opciones)
        self.actualizar_opciones()

    def formato_elegido(self):
        return "excel" if self.btn_excel.isChecked() else "pdf"

    def actualizar_opciones(self, *_):
        """Las opciones de hoja solo aplican al PDF; en Excel los filtros van en una segunda hoja"""
        es_pdf = self.formato_elegido() == "pdf"
        self.cmb_orientacion.setEnabled(es_pdf)
        self.cmb_tamano.setEnabled(es_pdf)
        self.chk_logo.setEnabled(es_pdf)
        self.chk_paginas.setEnabled(es_pdf)
        if es_pdf:
            self.lbl_nota.setText("El PDF repite el encabezado de la tabla en cada página.")
        else:
            self.lbl_nota.setText("El archivo de Excel incluye los filtros en una segunda hoja llamada «Filtros».")

    def guardar_como(self):
        formato = self.formato_elegido()
        extension = ".pdf" if formato == "pdf" else ".xlsx"
        filtro = "Documento PDF (*.pdf)" if formato == "pdf" else "Libro de Excel (*.xlsx)"

        titulo = self.txt_titulo.text().strip() or "Reporte"
        fecha = self.datos.get("fecha_generacion") or datetime.now()
        carpeta = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation) or os.path.expanduser("~")
        sugerido = os.path.join(carpeta, f"{nombre_seguro(titulo)}_{fecha:%Y%m%d}{extension}")

        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar reporte", sugerido, filtro)
        if not ruta:
            return
        if not ruta.lower().endswith(extension):
            ruta += extension

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            if formato == "pdf":
                exportar_pdf(
                    ruta, self.datos, titulo,
                    horizontal=bool(self.cmb_orientacion.currentData()),
                    oficio=bool(self.cmb_tamano.currentData()),
                    incluir_logo=self.chk_logo.isChecked(),
                    incluir_filtros=self.chk_filtros.isChecked(),
                    numerar_paginas=self.chk_paginas.isChecked(),
                )
            else:
                exportar_excel(ruta, self.datos, titulo, incluir_filtros=self.chk_filtros.isChecked())
        except PermissionError:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(
                self, "No se pudo guardar",
                "No se puede escribir en ese archivo. Si lo tienes abierto en otro programa, ciérralo "
                "e inténtalo de nuevo, o elige otro nombre."
            )
            return
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error al exportar", f"Ocurrió un error al crear el archivo:\n{e}")
            return
        QApplication.restoreOverrideCursor()

        self.ruta_exportada = ruta
        mensaje = QMessageBox(self)
        mensaje.setIcon(QMessageBox.Icon.Question)
        mensaje.setWindowTitle("Reporte exportado")
        mensaje.setText(f"El reporte se guardó en:\n{ruta}\n\n¿Deseas abrirlo ahora?")
        btn_si = mensaje.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        btn_no = mensaje.addButton("No", QMessageBox.ButtonRole.NoRole)
        mensaje.setDefaultButton(btn_si)
        mensaje.exec()

        if mensaje.clickedButton() == btn_si:
            QDesktopServices.openUrl(QUrl.fromLocalFile(ruta))
        self.accept()


if __name__ == "__main__":
    # Al ejecutar este archivo solo se abre con datos de prueba (nada se lee ni se escribe en la base de datos);
    # sirve para probar la exportación a PDF y a Excel por separado.
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(paleta_clara())
    datos_prueba = {
        "titulo": "Reporte de prueba",
        "encabezados": ["Trabajador", "Cédula", "Tipo", "Inicio", "Fin", "Estado"],
        "filas": [[f"Trabajador de prueba {i}", f"{10000000 + i * 137:,}".replace(",", "."), "Reposo médico",
                   "10 nov 2026", "Sin fecha de fin", "En curso"] for i in range(1, 61)],
        "filtros": [("Desde", "01/11/2026"), ("Hasta", "21/11/2026"), ("Tipo", "Todos los tipos")],
        "fecha_generacion": datetime.now(),
    }
    ventana = VentanaExportarReporte(datos_prueba)
    ventana.exec()
    sys.exit(0)