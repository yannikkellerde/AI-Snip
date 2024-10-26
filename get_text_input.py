import sys
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PyQt6.QtCore import Qt


class TextInputCapture(QWidget):
    def __init__(self, callback=None):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Enter API Key")
        self.setGeometry(100, 100, 300, 100)

        # Set up layout
        layout = QVBoxLayout()

        description_label = QLabel("Enter your OpenAI API key:")

        # Create a QLineEdit widget
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter some text here")

        # Create a button
        self.button = QPushButton("Submit", self)
        self.button.clicked.connect(self.get_text)

        # Add widgets to layout
        layout.addWidget(description_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.button)
        self.callback = callback

        # Set central widget
        self.setLayout(layout)

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event.key() == Qt.Key.Key_Return:
            self.get_text()

    def get_text(self):
        # Capture text from QLineEdit and store it in a variable
        user_text = self.input_field.text()
        if self.callback is not None:
            self.callback(user_text)
        self.close()
        # Now you can use the variable user_text as needed


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextInputCapture()
    window.show()
    sys.exit(app.exec())
