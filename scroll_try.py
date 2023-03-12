import sys
import os
import re
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap, QPalette, QImage, QColor, QBrush, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit, QScrollArea, QSizePolicy
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QColorDialog
from PyQt5.QtGui import QColor



#배경삭제 + RGBA png 로 output (alpha channel 0)
#equirectangular
#픽셀값 + 년도 선택
#Gaussian Blur 0.3, glow 효과까지 output. 가능하면 toggle.
#
class ColorPalette(QWidget):
    def __init__(self):
        super().__init__()

        # Create a grid layout for the color palette
        layout = QGridLayout()
        self.setLayout(layout)

        # Define the colors for the palette
        colors = [(255, 255, 255), (0, 0, 0), (128, 128, 128), (192, 192, 192), (255, 0, 0), (128, 0, 0), (255, 255, 0), (128, 128, 0), (0, 255, 0), (0, 128, 0), (0, 255, 255), (0, 128, 128), (0, 0, 255), (0, 0, 128), (255, 0, 255), (128, 0, 128), (255, 192, 203), (255, 255, 224), (138, 43, 226), (123, 104, 238), (255, 228, 225), (238, 130, 238), (127, 255, 212), (176, 196, 222), (255, 99, 71), (218, 112, 214), (255, 140, 0), (218, 165, 32), (255, 165, 0), (255, 215, 0)]
        # Add a button for each color to the grid layout
        for i, color in enumerate(colors):
            button = QPushButton()
            button.setFixedSize(50, 50)
            button.setStyleSheet("background-color: rgb({0}, {1}, {2});".format(*color))
            layout.addWidget(button, 0, i)

        # Set the size policy of the color palette widget to fixed
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create a horizontal layout for the main windows
        hlayout = QHBoxLayout()

        # Create the first main window
        self.window1 = QListWidget()
        window1_layout = QVBoxLayout()
        self.window1.setLayout(window1_layout)

        # Get a list of all files in the maps folder
        folder_path = "./maps"
        files = os.listdir(folder_path)

        # Add each file to the file list widget
        for file in sorted(files, key=self.sort_function):
            if file.endswith(".png") and os.path.isfile(os.path.join(folder_path, file)):
                item = QListWidgetItem(file)
                self.window1.addItem(item)

        # Connect the itemSelectionChanged signal of the list widget to a custom method
        self.window1.itemSelectionChanged.connect(self.update_window2)
        self.window1.setFixedSize(200, 1000)
        # Create a search widget
        search_widget = QLineEdit()
        search_widget.setPlaceholderText("Search")
        search_widget.textChanged.connect(self.filter_window1)

        # Add the list widget and search widget to a vertical layout
        self.color_palette = ColorPalette()
        # self.color_palette.clicked.connect(self.open_color_dialog)
        self.color = QColor("red")

        # Add the main windows and color palette to the main widget
        vlayout = QVBoxLayout()
        # vlayout.addWidget(color_palette)
        vlayout.addWidget(search_widget)
        vlayout.addWidget(self.window1)
        vwidget = QWidget()
        vwidget.setLayout(vlayout)
        vwidget.setFixedSize(200, 1000)




        # Create the second main window
        vlayout2 = QVBoxLayout()
        self.window2 = QLabel()
        self.window2.setAlignment(Qt.AlignCenter)
        self.window2.setStyleSheet("border: 1px solid red;")
        self.window2.installEventFilter(self)

        # Wrap the label inside a scroll area
        scroll_area2 = QScrollArea()
        scroll_area2.setWidgetResizable(True)
        scroll_area2.setWidget(self.window2)
        scroll_area2.setFixedSize(805, 805)
        vlayout2.addWidget(scroll_area2)
        # vlayout2.addWidget(self.color_palette)
        vwidget2 = QWidget()
        vwidget2.setLayout(vlayout2)
        # self.scale_factor = 1.0

        # Create the third main window
        self.window3 = QLabel()
        self.window3.setAlignment(Qt.AlignCenter)
        self.window3.setStyleSheet("border: 1px solid green;")
        self.window3.setFixedSize(800, 800)


        # Get the file path of the selected item
        file_path = "background.png"
        image = QImage(file_path)
        # Load the image using QPixmap and set it as the pixmap of the label
        self.original_pixmap3 = QPixmap.fromImage(image)

        self.scale_factor3 = 0.1953125
        scaled_pixmap = self.original_pixmap3.scaled(
            self.scale_factor3 * self.original_pixmap3.size(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.window3.setPixmap(scaled_pixmap)
        self.window3.adjustSize()  # Make sure the label is resized to fit the pixmap

        # self.window3 = QWidget()
        # self.window3_layout = QVBoxLayout()
        # self.window3_layout.addWidget(QLabel("Window 3"))
        # self.window3.setLayout(self.window3_layout)
        # self.window3.setStyleSheet("border: 1px solid green;")
        # self.window3.setFixedSize(800, 800)

        # Add the main windows to the main widget
        hlayout.addWidget(vwidget)
        hlayout.addWidget(vwidget2)
        hlayout.addWidget(self.window3)
        main_widget.setLayout(hlayout)

    def sort_function(self, file):
        if "BC" in file:
            year = -1*int(file.replace("BC","").replace(".png",""))
        else:
            year = int(file.replace("Year_AD", "").replace(".png", ""))
        return year

    def filter_window1(self, text):
        # Loop through the items in the list widget
        for i in range(self.window1.count()):
            item = self.window1.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def mouseDoubleClickEvent(self, event):
        # Open a QColorDialog to select a color

        if event.modifiers() != Qt.AltModifier:
            color = QColorDialog.getColor(self.color, self)

            if color.isValid():
                # Update the color and repaint the widget
                self.color = color
                self.update()

    def open_color_dialog(self):
        # Open the color dialog and get the selected color
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color

    def update_window2(self):
        # Get the selected item from the list widget
        selected_item = self.window1.currentItem()

        if selected_item is not None:
            # Get the file path of the selected item
            file_path = os.path.join("./maps", selected_item.text())
            image = QImage(file_path)
            # Load the image using QPixmap and set it as the pixmap of the label
            self.original_pixmap = QPixmap.fromImage(image)

            self.scale_factor = 0.1953125
            scaled_pixmap = self.original_pixmap.scaled(
                self.scale_factor * self.original_pixmap.size(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.window2.setPixmap(scaled_pixmap)
            self.window2.adjustSize()  # Make sure the label is resized to fit the pixmap

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.scale_factor *= 1.2
            scaled_pixmap = self.original_pixmap.scaled(
                self.scale_factor * self.original_pixmap.size(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.window2.setPixmap(scaled_pixmap)
            self.window2.adjustSize()  # Make sure the label is resized to fit the pixmap

        if event.key() == Qt.Key_W:
            self.scale_factor *= 0.8
            scaled_pixmap = self.original_pixmap.scaled(
                self.scale_factor * self.original_pixmap.size(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.window2.setPixmap(scaled_pixmap)
            self.window2.adjustSize()  # Make sure the label is resized to fit the pixmap

    def eventFilter(self, obj, event):
        if obj == self.window2 and event.type() == QEvent.MouseButtonPress and event.modifiers() == Qt.AltModifier:
            print("this was received")
            # Get the color of the selected pixel
            x = int(event.pos().x() / self.scale_factor)
            y = int(event.pos().y() / self.scale_factor)
            color = self.original_pixmap.toImage().pixelColor(x, y)

            # Create a new pixmap for the selected pixels

            # painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
            # painter.setBrush(QBrush(color))

            np_array = np.zeros((4096,4096))

            # Find all the adjacent pixels with the same color using an iterative flood fill algorithm
            image = self.original_pixmap.toImage()
            # new_color = QColor(Qt.green)  # Choose a new color that is unlikely to appear in the image
            # explored = {}
            print(x,y)
            print("xy")
            stack = [(x, y)]
            counter=0
            to_draw = []
            while stack:

                x, y = stack.pop()
                counter+=1
                if np_array[x][y] == 1:
                    continue
                np_array[x][y] = 1
                # print(counter)
                # print(x,y)
                if not self.check_pixel(image, x, y, color):
                    # print("out1")
                    continue

                to_draw.append([x,y])


                # new_pixmap.setPixelColor(x, y, new_color)
                if np_array[x+1, y] == 0:
                    stack.append((x + 1, y))
                if np_array[x-1, y] == 0:
                    stack.append((x - 1, y))
                if np_array[x, y+1] == 0:
                    stack.append((x, y + 1))
                if np_array[x, y-1] == 0:
                    stack.append((x, y - 1))

            # adjacent_pixels = [(i, j) for i in range(image.width()) for j in range(image.height()) if
            #                    image.pixelColor(i, j) == new_color]

            # Highlight the adjacent pixels with the same color
            # for pixel in adjacent_pixels:
            #     painter.drawRect(pixel[0], pixel[1], 1, 1)


            # print(explored.keys)
            # painter.end()

            # Set the new pixmap as the pixmap of window3
            # self.window3.setPixmap(new_pixmap)
        # print("we're safe so far")
        # new_pixmap = QPixmap(self.original_pixmap.size())
        # new_pixmap.fill(QColor("transparent"))
            print("hi?")
            painter = QPainter(self.original_pixmap3)
            painter.setPen(QPen(self.color, 1))
            painter.setBrush(QBrush(self.color))
            print("bad?")
            for x,y in to_draw:
                print("trying to draw: ", x,y)
                painter.drawPoint(x,y)
            painter.end()
            self.window3.setPixmap(self.original_pixmap3.scaled(
            self.scale_factor3 * self.original_pixmap3.size(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation))
            print("painting ended")
        return super().eventFilter(obj, event)

    def check_pixel(self, image, x, y, color):
        if x < 1 or x >= image.width() -1 or y < 1 or y >= image.height() - 1:
            return False
        return image.pixelColor(x, y) == color


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Studio Pirates Mercator")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())