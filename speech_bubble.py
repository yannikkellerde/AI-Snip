from PyQt6.QtWidgets import QApplication, QWidget, QLabel
import sys
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QFontMetrics, QPainterPath, QPixmap
from functools import lru_cache
from util import resource_path


class SpeechBubbleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech Bubble")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        image_path = resource_path("full_clippy.png")

        # Create a QLabel widget to display the image
        self.label = QLabel(self)

        # Load the image and set it in the QLabel
        self.pixmap = QPixmap(image_path)

        scale_factor = 250 / self.pixmap.width()

        self.img_height = int(self.pixmap.height() * scale_factor)
        self.img_width = int(self.pixmap.width() * scale_factor)

    def reset(self, text):
        self.full_text = text
        self.displayed_text = ""
        self.char_index = 0
        self.opacity = 0.0

        bubble_width = 300 + max(0, min(300, (len(self.full_text) - 100) // 2))
        self.resize(bubble_width, 150)

        # Timer for the typewriter effect
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)
        self.timer.start(20)  # Adjust the interval as needed (milliseconds)

    def update_text(self):
        # Add one more character each time the timer fires
        if self.opacity > 0.25:
            if self.char_index < len(self.full_text):
                self.char_index += 1
                self.displayed_text = self.full_text[: self.char_index]
                self.update()  # Trigger a repaint
            elif self.opacity == 1.0:
                self.timer.stop()  # Stop timer when all characters are displayed
        if self.opacity < 1.0:
            self.opacity = min(1.0, self.opacity + 0.01)
            self.setWindowOpacity(self.opacity)

    @staticmethod
    def compute_height(text: str, metrics: QFontMetrics, max_width: int):
        # Split displayed_text into lines to fit within max_width
        words = [x for x in text.replace("\n", " \n ").split(" ") if x]
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if word == "\n":
                lines.append(current_line)
                current_line = ""
            elif metrics.horizontalAdvance(test_line) > max_width:
                lines.append(current_line)
                current_line = word  # Start a new line with the current word
            else:
                current_line = test_line  # Add word to the current line

        # Append the last line
        if current_line:
            lines.append(current_line)

        line_req = metrics.height() * len(lines)
        return lines, line_req

    def paintEvent(self, event):
        # Set the window location to the bottom right corner
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define bubble color and border
        bubble_color = QColor(252, 250, 207)
        border_color = QColor(0, 0, 0)

        # Set bubble rectangle size and position, convert to QRectF

        font = QFont("Tahoma", 12)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        max_width = self.rect().width() - 60  # Padding for text within bubble

        lines, line_req = self.compute_height(self.displayed_text, metrics, max_width)
        _, max_req = self.compute_height(self.full_text, metrics, max_width)
        diff = max_req - line_req

        total_height = max_req + 60 + self.img_height
        if self.rect().height() != total_height:
            self.resize(self.rect().width(), total_height)
            screen_geometry = QApplication.primaryScreen().geometry()
            x = screen_geometry.width() - self.width() - 20
            y = screen_geometry.height() - self.height() - 20
            self.move(x, y)

        painter.drawPixmap(
            QRect(
                self.rect().right() - self.img_width,
                self.rect().bottom() - self.img_height,
                self.img_width,
                self.img_height,
            ),
            self.pixmap,
        )

        bubble_rect = QRectF(
            self.rect().adjusted(20, 20 + diff, -20, -20 - self.img_height)
        )

        # Create a path for the bubble with the triangle pointer
        dummy_path = QPainterPath()
        dummy_path.addRoundedRect(bubble_rect, 20, 20)
        points = []
        for i in range(dummy_path.elementCount()):
            element = dummy_path.elementAt(i)
            points.append((element.x, element.y))

        # Add the pointer as part of the path to avoid the line
        pointer_top = QPointF(bubble_rect.right() - 110, bubble_rect.bottom())
        pointer_tip = QPointF(bubble_rect.right() - 110, bubble_rect.bottom() + 20)
        pointer_bottom = QPointF(bubble_rect.right() - 100, bubble_rect.bottom())

        path = QPainterPath()
        path.moveTo(QPointF(*points[0]))

        for point in points[:12]:
            path.lineTo(QPointF(*point))

        path.lineTo(pointer_bottom)
        path.lineTo(pointer_tip)
        path.lineTo(pointer_top)
        for point in points[12:]:
            path.lineTo(QPointF(*point))

        path.closeSubpath()

        # Draw the combined bubble and pointer shape
        painter.setBrush(bubble_color)
        painter.setPen(border_color)
        painter.drawPath(path)

        # Draw each line of text within the bubble
        painter.setPen(Qt.GlobalColor.black)
        y_offset = 10  # Vertical padding inside the bubble
        line_height = metrics.height()

        for i, line in enumerate(lines):
            painter.drawText(
                bubble_rect.adjusted(10, y_offset, 0, 0),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                line,
            )
            y_offset += line_height  # Move down for the next line

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_Q:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    text = """Hello! This is a seamless speech bubble.
It can contain multiple lines of text and will automatically wrap to fit within the bubble.
The bubble is also resizable based on the text content.
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."""
    window = SpeechBubbleWidget()
    window.show()
    window.reset(text)
    sys.exit(app.exec())
