import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess

class ProcessThread(QThread):
    output_signal = pyqtSignal(str)

    def run(self):
        # Example: Replace 'ping localhost -c 4' with your command
        process = subprocess.Popen(['ping', 'localhost'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="latin-1")

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.output_signal.emit(output.strip())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.startProcess()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Process Output')

    def startProcess(self):
        self.thread = ProcessThread()
        self.thread.output_signal.connect(self.updateOutput)
        self.thread.start()

    def updateOutput(self, text):
        self.list_widget.addItem(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())