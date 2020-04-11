from PyQt4.QtGui import QApplication
import sys
import qdarkstyle
from Controlers.principal import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    form.show()
    app.exec_()