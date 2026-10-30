import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class VentanaOperativas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel("¡Bienvenido a la ventana de novedades operativas!")
        label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaOperativas()
    ventana.show()
    sys.exit(app.exec_())