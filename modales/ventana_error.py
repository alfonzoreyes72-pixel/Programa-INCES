import sys
from PyQt5.QtWidgets import (
    QApplication, QPushButton, QVBoxLayout, QDialog, QLabel, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class VentanaError(QDialog):  # Clase para la ventana modal
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuración de la ventana modal
        self.setWindowTitle("Error")  # Título de la ventana modal
        self.resize(350, 180)  # Tamaño compacto y proporcionado
        self.setModal(True)  # Hacer que la ventana sea modal
        self.setStyleSheet("background-color: white;")

        # QUITAMOS EL SÍMBOLO DE INTERROGACIÓN DE LA BARRA DE TÍTULO
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Crear un layout para organizar los widgets
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        # Etiqueta de texto
        self.etiqueta = QLabel("Usuario o contraseña incorrectos")
        self.etiqueta.setStyleSheet("""
                    QLabel {
                        font-size: 16px;
                        font-weight: bold;
                        color: #000000;
                        font-family: 'Arial', sans-serif;
                        background: transparent;
                        margin-bottom: 15px;
                    }
                """)
        self.etiqueta.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.etiqueta)

        # Botón para aceptar
        self.btn_aceptar = QPushButton("Aceptar") 
        self.btn_aceptar.setFixedSize(160, 40) 
        self.btn_aceptar.setStyleSheet( """
                    QPushButton {
                        background-color: #0833a2; /* Color de fondo */
                        color: white;               /* Color del texto */
                        border-radius: 20px;        /* El radio define la curvatura */
                        border: 2px solid #0833a2;  /* Borde opcional */
                        padding: 5px;               /* Separacion entre el texto y el borde del boton */
                        font-size: 16px;            /* Tamaño de la letra */
                        font-weight: bold;
                    }
            
                    QPushButton:hover {
                        background-color: #3150ff; /* Cambio de color al pasar el ratón */
                        border: 2px solid #3150ff;
                    }
                        """ )
        efecto_sombra = QGraphicsDropShadowEffect(self)
        efecto_sombra.setBlurRadius(20)
        efecto_sombra.setXOffset(5)
        efecto_sombra.setYOffset(5)
        efecto_sombra.setColor(QColor(0, 0, 0, 70))
        self.btn_aceptar.setGraphicsEffect(efecto_sombra)
        
        # Conectamos el botón al método de cierre
        self.btn_aceptar.clicked.connect(self.cerrar) 
        self.layout.addWidget(self.btn_aceptar, alignment=Qt.AlignCenter) # Centrado debajo del texto

    def cerrar(self):
        """Método para cerrar la ventana modal de error"""
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaError()
    ventana.show()
    sys.exit(app.exec_())