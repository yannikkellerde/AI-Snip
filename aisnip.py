import sys
import os
from datetime import datetime
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import (
    QPainter,
    QPen,
    QPixmap,
    QScreen,
    QColor,
    QKeySequence,
    QIcon,
    QAction,
    QShortcut,
)
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QFileDialog,
    QMainWindow,
    QMenu,
    QSystemTrayIcon,
)
from util import (
    local_image_to_data_url,
    resource_path
)
from model_wrapper import ModelWrapper
from config import Config
from speech_bubble import SpeechBubbleWidget
from write_text import TextInputWidget
from get_text_input import TextInputCapture
import pyperclip
import time
if os.name == "nt":
    import keyboard

basepath = os.path.abspath(os.path.dirname(sys.executable)) if getattr(sys, "frozen", False) else os.path.abspath(os.path.dirname(__file__))


class SnippingTool(QMainWindow):
    def __init__(self, model: ModelWrapper, config:Config):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowOpacity(0.2)

        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

        self.save_folder = os.path.expanduser("~/Pictures/snips")
        os.makedirs(self.save_folder, exist_ok=True)

        self.begin = None
        self.end = None
        self.clippy_enabled = True
        self.clipboard_enabled = False
        self.stream = config.stream
        self.snip_config = config

        self.model = model

    def set_model(self, model: ModelWrapper):
        self.model = model

    def showFullScreen(self) -> None:
        super().showFullScreen()
        self.begin = self.end = None
        self.clippy_enabled = True
        self.clipboard_enabled = False
        text_widget.current_text = "Please explain the contents of this image concisely."
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the overlay with opacity
        overlay_color = QColor(0, 0, 0, 128)  # Semi-transparent black
        painter.fillRect(self.rect(), overlay_color)

        # If we have a selection, cut it out to reveal the screen content
        if self.begin and self.end:
            rect = QRect(self.begin, self.end)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)

            # Draw a red border around the selection
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceOver
            )
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
            painter.drawRect(rect)

    def get_ai_complete(self, img_path):
        if self.snip_config.llm_provider == "ollama":
            data_url = img_path
        else:
            data_url = local_image_to_data_url(img_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_widget.current_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                        },
                    },
                ],
            }
        ]
        if self.model is None:
            reply = """Got no API key. Either set the OPENAI_API_KEY environment variable
            or restart AI Snip and enter your key."""
        else:
            if self.stream and self.clippy_enabled and not self.clipboard_enabled:
                reply = self.model.stream_complete(messages)
            else:
                reply = self.model.complete(messages)

        return reply

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        file_path = self.capture()
        self.begin = self.end = None
        if file_path is not None:
            self.close()
            if text_widget.isVisible():
                text_widget.close()
            reply = self.get_ai_complete(file_path)
            if self.clipboard_enabled:
                pyperclip.copy(reply)
            speech_bubble.reset(reply)
            if self.clippy_enabled:
                if not speech_bubble.isVisible():
                    speech_bubble.show()
            elif os.name == "posix":
                sys.exit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_Q:
            self.close()
            text_widget.close()
            if os.name == "posix":
                sys.exit()

        if event.key() == Qt.Key.Key_C:
            self.clipboard_enabled = not self.clipboard_enabled

        if event.key() == Qt.Key.Key_D:
            self.clippy_enabled = not self.clippy_enabled

        if event.key() == Qt.Key.Key_E:
            text_widget.change_text(
                "Translate this text to English. Only respond with the translated text."
            )
            self.clipboard_enabled = True
            if not text_widget.isVisible():
                text_widget.show()

        if event.key() == Qt.Key.Key_T:
            text_widget.change_text("")
            if not text_widget.isVisible():
                text_widget.show()

        if event.key() == Qt.Key.Key_L:
            self.clippy_enabled = False
            self.clipboard_enabled = True
            text_widget.change_text(
                "Give me the latex code that generates this image. Only respond with the core code without wrappers or the document environment."
            )
            if not text_widget.isVisible():
                text_widget.show()

    def capture(self):
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        if x2 - x1 + y2 - y1 < 6:
            return None
        rect = QRect(x1, y1, x2 - x1, y2 - y1)

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(
            0, rect.x(), rect.y(), rect.width(), rect.height()
        )

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(self.save_folder, f"{now}.png")
        screenshot.save(file_path)
        return file_path


def store_api_key(api_key):
    config.api_key = api_key
    config.save_to_yaml(cfg_path)
    return api_key


app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

cfg_path = os.path.join(basepath, "config.yml")
if os.path.exists(cfg_path):
    config = Config.load_from_yaml(cfg_path)
else:
    config = Config()

def tex_callback(x):
    window.set_model(OpenAIModelWrapper(api_key=store_api_key(x)))
    if os.name == "posix":
        window.showFullScreen()

if config.llm_provider == "ollama":
    from ollama_model_wrapper import OllamaModelWrapper
    model = OllamaModelWrapper(config)
else:
    api_key = os.environ.get("OPENAI_API_KEY", config.api_key) if config.llm_provider == "openai" else os.environ.get("AZURE_OPENAI_API_KEY", config.api_key)
    if api_key is None:
        model = None
    else:
        if config.llm_provider == "openai":
            from openai_model_wrapper import OpenAIModelWrapper
            model = OpenAIModelWrapper(api_key=api_key, model_name=config.model_name)
        elif config.llm_provider == "azure":
            from openai_model_wrapper import AzureModelWrapper
            model = AzureModelWrapper(api_key=api_key, model_name=config.model_name)

window = SnippingTool(model, config)
speech_bubble = SpeechBubbleWidget()
text_widget = TextInputWidget()


if model is None:
    text_cap = TextInputCapture(
        tex_callback
    )
    text_cap.show()

elif os.name == "posix":
    window.showFullScreen()
    
def on_tray_icon_activated(reason):
    if reason == QSystemTrayIcon.ActivationReason.Trigger:
        window.showFullScreen()

if os.name == "nt":
    tray_icon = QSystemTrayIcon(QIcon(resource_path("clippy.png")))
    tray_icon.setToolTip("AI Snip tool")

    tray_menu = QMenu()
    show_action = QAction("AI Snip (CTRL + SHIFT + A)")
    response_action = QAction("Show AI response")
    text_write_action = QAction("Show text input")
    quit_action = QAction("Quit")
    show_action.triggered.connect(window.showFullScreen)
    response_action.triggered.connect(speech_bubble.show)
    text_write_action.triggered.connect(text_widget.show)
    quit_action.triggered.connect(app.quit)

    tray_menu.addAction(show_action)
    tray_menu.addAction(response_action)
    tray_menu.addAction(quit_action)
    tray_icon.setContextMenu(tray_menu)
    tray_icon.activated.connect(on_tray_icon_activated)

    tray_icon.show()

    keyboard.add_hotkey("CTRL + SHIFT + A", show_action.trigger)

    window.showFullScreen()
    window.close()

sys.exit(app.exec())
