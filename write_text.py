import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout
from PyQt6.QtGui import QFont, QFontMetrics


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget


class TextInputWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the main layout
        self.layout = QVBoxLayout()

        # Create the QLineEdit widget
        self.text_input = QLineEdit(self)
        font = QFont()
        font.setPointSize(14)  # Set font size to 14 (you can adjust this as needed)
        self.text_input.setFont(font)
        self.text_input.setPlaceholderText("Type here...")  # Placeholder text

        # Connect the input text change to a function if needed
        self.text_input.textChanged.connect(self.on_text_change)

        self.resize(400, 40)
        self.text_input.setFixedHeight(40)  # Set fixed height for QLineEdit

        # Add the QLineEdit to the layout
        self.layout.addWidget(self.text_input)

        # Set the layout to the main widget
        self.setLayout(self.layout)
        self.setWindowTitle("Write your prompt")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        screen_geometry = QApplication.primaryScreen().geometry()
        x = screen_geometry.width() // 2 - self.width() // 2
        y = screen_geometry.height() - self.height() - 20
        self.move(x, y)

        self.current_text = "Please explain the contents of this image concisely."

    def show(self, *args, **kwargs):
        super().show(*args, **kwargs)
        self.activateWindow()  # Brings the window to the front
        self.raise_()  # Ensures it is the topmost window

    def on_text_change(self, text):
        # Update current text
        self.current_text = text

        # Calculate the width of the text
        font_metrics = QFontMetrics(self.text_input.font())
        text_width = font_metrics.horizontalAdvance(text) + 20  # 20 for padding

        # Set a max width to prevent excessive growth
        #max_width = 600
        thing_width = max(300,text_width)
        self.text_input.setFixedWidth(thing_width)
        screen_geometry = QApplication.primaryScreen().geometry()
        x = screen_geometry.width() // 2 - thing_width // 2
        self.move(x, self.y())

    def change_text(self, text):
        # Set new text in the QLineEdit
        self.text_input.setText(text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_Q:
            self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextInputWidget()
    window.show()
    sys.exit(app.exec())
