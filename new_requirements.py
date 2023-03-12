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
        self.window1.setFixedSize(200, 700)
        # self.window1.installEventFilter(self)
        # Create a search widget
        search_widget = QLineEdit()
        search_widget.setPlaceholderText("Search")
        search_widget.textChanged.connect(self.filter_window1)

        # Add the list widget and search widget to a vertical layout
        # self.color_palette = ColorPalette()
        # self.color_palette.clicked.connect(self.open_color_dialog)
        self.color = QColor("red")

        self.selected_years = QListWidget()
        self.selected_years.setFixedSize(200,200)
        self.selected_years.itemClicked.connect(self.remove_item)

        # Add the main windows and color palette to the main widget
        vlayout = QVBoxLayout()
        vlayout.addWidget(search_widget)
        vlayout.addWidget(self.window1)
        vlayout.addWidget(self.selected_years)
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



        #
        # vwidget2 = QWidget()
        # vwidget2.setLayout(vlayout2)

        # Create the third main window
        self.window3 = QLabel()
        self.window3.setAlignment(Qt.AlignCenter)
        self.window3.setStyleSheet("border: 1px solid green;")
        self.window3.setFixedSize(800, 800)
        blank_rgba = np.zeros((4096, 4096, 4), dtype=np.uint8)

        # Convert the NumPy array to a QImage
        qimage_rgba = QImage(blank_rgba.data, blank_rgba.shape[1], blank_rgba.shape[0], QImage.Format_RGBA8888)

        # Convert the QImage to a QPixmap
        self.qpixmap_rgba = QPixmap.fromImage(qimage_rgba)
        self.scale_factor3 = 0.1953125



        scaled_pixmap = self.qpixmap_rgba.scaled(
            self.scale_factor3 * self.qpixmap_rgba.size(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.window3.setPixmap(scaled_pixmap)
        self.window3.adjustSize()  # Make sure the label is resized to fit the pixmap

        hlayout_2_3 = QHBoxLayout()
        hlayout_2_3.addLayout(vlayout2)
        hlayout_2_3.addWidget(self.window3)

        self.color_code = QLabel()
        self.color_code.setAlignment(Qt.AlignCenter)
        self.color_code.setStyleSheet("border: 1px solid blue;")
        self.color_code.setFixedSize(1600, 150)

        final_vlayout = QVBoxLayout()
        final_vlayout.addLayout(hlayout_2_3)
        final_vlayout.addWidget(self.color_code)

        # Add the main windows to the main widget
        hlayout.addWidget(vwidget)
        hlayout.addLayout(final_vlayout)

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

    def remove_item(self, item):
        if QApplication.keyboardModifiers() == Qt.AltModifier:
            self.selected_years.takeItem(self.selected_years.row(item))

    def open_color_dialog(self):
        # Open the color dialog and get the selected color
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color

    def update_window2(self):
        # Get the selected item from the list widget
        selected_item = self.window1.currentItem()
        self.currentYear = selected_item.text()

        if selected_item is not None:
            # Get the file path of the selected item
            file_path = os.path.join("./maps", selected_item.text())

            if QApplication.keyboardModifiers() == Qt.AltModifier:
                item = QListWidgetItem(selected_item.text())
                self.selected_years.addItem(item)



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
        else:
            super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_E:
            print("here")

            item = QListWidgetItem(self.currentYear)
            self.selected_years.addItem(item)
            print("added and updated")
            return True
            # return super().eventFilter(obj, event)

        if obj == self.window2 and event.type() == QEvent.MouseButtonPress and event.modifiers() == Qt.AltModifier:
            print("this was received")
            # Get the color of the selected pixel
            x = int(event.pos().x() / self.scale_factor)
            y = int(event.pos().y() / self.scale_factor)
            color = self.original_pixmap.toImage().pixelColor(x, y)

            # Create a new pixmap for the selected pixels

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

            print("hi?")
            painter = QPainter(self.qpixmap_rgba)
            painter.setPen(QPen(self.color, 1))
            painter.setBrush(QBrush(self.color))
            for x,y in to_draw:
                painter.drawPoint(x,y)
            painter.end()
            self.window3.setPixmap(self.qpixmap_rgba.scaled(
            self.scale_factor3 * self.qpixmap_rgba.size(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation))
            print("painting ended")
            return True
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