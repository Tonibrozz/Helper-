import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мой Браузер")
        self.setGeometry(100, 100, 1200, 800)

        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://www.google.com"))
        self.setCentralWidget(self.browser)

app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())
