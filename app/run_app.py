import sys
import os

# Forzamos la ruta de Graphviz en el sistema para esta sesión
graphviz_path = r'C:\Program Files\Graphviz\bin'
os.environ["PATH"] += os.pathsep + graphviz_path

# Verificación interna opcional
print(f">> Sistema: Ruta Graphviz inyectada: {graphviz_path}")

from PySide6.QtWidgets import QApplication

from app.ui.main_flow.main_window import MainWindow
from app.ui.main_flow.styles import STYLE


def run():

    app = QApplication(sys.argv)

    app.setStyleSheet(STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()