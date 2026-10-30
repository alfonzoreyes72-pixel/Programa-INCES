import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# Cambiamos QMainWindow por QWidget para que actúe como un panel incrustable
class VentanaPerfil(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal del panel de perfil
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Etiqueta de bienvenida que ya tenías
        label = QLabel("Bienvenido a la Ventana de Perfil")
        label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333333;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPerfil()
    ventana.show()
    sys.exit(app.exec_())