from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QWheelEvent
from PyQt5.QtCore import Qt
import sys


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Create widget for scroll area
        self.widget = QWidget()
        self.scroll_area.setWidget(self.widget)

        # Create layout for widget
        self.layout = QVBoxLayout(self.widget)

        # Load image
        self.image = QPixmap("background.png")
        self.zoom_factor = 1.0

        # Create label and add to layout
        self.label = QLabel()
        self.label.setPixmap(self.image)
        self.layout.addWidget(self.label)

        # Set scroll area as central widget
        self.setCentralWidget(self.scroll_area)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            # Zoom in with the "q" key
            self.zoom_factor *= 1.1
            self.label.setPixmap(self.image.scaled(self.zoom_factor * self.image.size()))

        elif event.key() == Qt.Key_W:
            # Zoom out with the "w" key
            self.zoom_factor /= 1.1
            self.label.setPixmap(self.image.scaled(self.zoom_factor * self.image.size()))

        elif event.key() == Qt.Key_Left:
            # Scroll left with the left arrow key
            self.scroll_area.horizontalScrollBar().setValue(self.scroll_area.horizontalScrollBar().value() - 10)

        elif event.key() == Qt.Key_Right:
            # Scroll right with the right arrow key
            self.scroll_area.horizontalScrollBar().setValue(self.scroll_area.horizontalScrollBar().value() + 10)

        elif event.key() == Qt.Key_Up:
            # Scroll up with the up arrow key
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().value() - 10)

        elif event.key() == Qt.Key_Down:
            # Scroll down with the down arrow key
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().value() + 10)

    def wheelEvent(self, event: QWheelEvent):
        # Zoom in or out with Ctrl+Scroll
        if event.modifiers() == Qt.ControlModifier:
            num_steps = event.angleDelta().y() / 120
            self.zoom_factor *= 1.1 ** num_steps
            self.label.setPixmap(self.image.scaled(self.zoom_factor * self.image.size()))

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
