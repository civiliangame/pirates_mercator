import sys
import os
import re
from PyQt5.QtCore import Qt, QEvent, QCoreApplication, pyqtSignal, QUrl
from PyQt5.QtGui import QPixmap, QPalette, QImage, QColor, QBrush, QPainter, QPen, QDesktopServices
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit, QScrollArea, QSizePolicy, QCheckBox
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QColorDialog
from PyQt5.QtGui import QColor
from datetime import datetime
from PIL import Image, ImageFilter
class MyVBoxLayout(QVBoxLayout):

    mySignal = pyqtSignal(object, object)
    def __init__(self, x):
        super().__init__(x)

    def delete_signal(self, x, y):
        self.mySignal.emit(x,y)


class MyHBoxLayout(QHBoxLayout):
    # mySignal = pyqtSignal(str)
    mySignal = pyqtSignal(object, object)
    def __init__(self, x):
        super().__init__(x)

    def delete_signal(self, x, y):
        self.mySignal.emit(x,y)

#배경삭제 + RGBA png 로 output (alpha channel 0)
#equirectangular
#픽셀값 + 년도 선택
#Gaussian Blur 0.3, glow 효과까지 output. 가능하면 toggle.
#
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # widgetRemoved = pyqtSignal(QWidget)
        # Create a main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.radius = 0.3


        self.gaussian = False
        self.equi = False
        self.glow = False
        self.bruteforce = False
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
        self.color_change_queue = []

        self.selected_years = QListWidget()
        self.selected_years.setFixedSize(200,200)
        self.selected_years.itemClicked.connect(self.remove_item_from_selected_years)



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
        # self.window2

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


        self.color_code_widget = QWidget()
        self.color_code_widget.setStyleSheet("border: 1px solid blue;")
        self.color_code_widget.setFixedSize(1300, 150)
        self.color_code_widget.installEventFilter(self)
        self.color_code = MyHBoxLayout(self.color_code_widget)
        self.color_code.setAlignment(Qt.AlignLeft)



        self.checkboxes = QVBoxLayout()
        self.gaussian_checkbox = QCheckBox('Gaussian Blur?', self)
        self.gaussian_checkbox.stateChanged.connect(self.gaussian_checkboxClicked)

        self.equi_checkbox = QCheckBox('Equirectangular?', self)
        self.equi_checkbox.stateChanged.connect(self.equi_checkboxClicked)

        self.glow_checkbox = QCheckBox('Glow?', self)
        self.glow_checkbox.stateChanged.connect(self.glow_checkboxClicked)

        self.bruteforce_checkbox = QCheckBox('Brute Force?', self)
        self.bruteforce_checkbox.stateChanged.connect(self.brute_forceClicked)


        self.checkboxes.addWidget(self.gaussian_checkbox)
        self.checkboxes.addWidget(self.equi_checkbox)
        self.checkboxes.addWidget(self.glow_checkbox)
        self.checkboxes.addWidget(self.bruteforce_checkbox)



        self.render_button = QPushButton("Click to Render")
        self.render_button.clicked.connect(self.render_images)
        self.bottoms = QHBoxLayout()
        self.bottoms.addWidget(self.color_code_widget)
        self.bottoms.addLayout(self.checkboxes)
        self.bottoms.addWidget(self.render_button)

        print(self.color_code.mySignal)

        # def gaussian_checkboxClicked():
        # def equi_checkboxClicked():
        # def glow_checkboxClicked():
        # def render_images()


        # self.color_code.mySignal.connect(lambda x,y: self.update_color_list(x,y))
        # self.color_code_widget.(self.remove_item_from_selected_years)
        # self.color_code.




        final_vlayout = QVBoxLayout()
        final_vlayout.addLayout(hlayout_2_3)
        final_vlayout.addLayout(self.bottoms)

        # Add the main windows to the main widget
        hlayout.addWidget(vwidget)
        hlayout.addLayout(final_vlayout)

        main_widget.setLayout(hlayout)

    def mercator_to_equirectangular(self, x, y):
        longitude = (x / 4096.0) * 360.0 - 180.0
        latitude = ((y / 2048.0) * 180.0) - 90.0
        return (longitude, latitude)


    def render_images(self):
        years_to_render = [self.selected_years.item(i).text() for i in range(self.selected_years.count())]
        now = datetime.now()
        nowtime = now.strftime("%m_%d_%H_%M_%Y")
        folder_name = os.path.join("results", nowtime)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Created directory {folder_name}")




        for input_color, output_color, in_x, in_y, year in self.color_change_queue:
            print("check this out", input_color, output_color, in_x, in_y, year)
            max_area = {}
            np_array = np.zeros((4096, 4096))
            stack = [(in_x, in_y)]
            file_name = os.path.join("maps", year)
            print(file_name)
            original_image = QImage(file_name)
            print(original_image)
            print(original_image.size())
            # original_image = QPixmap.fromImage(original_image)
            while stack:
                x, y = stack.pop()
                if np_array[x][y] == 1:
                    continue
                np_array[x][y] = 1
                if not self.check_pixel(original_image, x, y, input_color):
                    # print("exiting here for some reason")
                    # print("out1")
                    continue
                max_area["%s,%s" % (x, y)] = 1
                # print("adding", x, y)
                # new_pixmap.setPixelColor(x, y, new_color)
                if np_array[x + 1, y] == 0:
                    stack.append((x + 1, y))
                if np_array[x - 1, y] == 0:
                    stack.append((x - 1, y))
                if np_array[x, y + 1] == 0:
                    stack.append((x, y + 1))
                if np_array[x, y - 1] == 0:
                    stack.append((x, y - 1))


            # print(max_area.keys())


            print("Part 1 done")

            for yl in years_to_render:



                print(yl)
                print("11111111")
                print(years_to_render)
                print("22222222222")
                compare_file = os.path.join("maps", yl)
                save_file = os.path.join(folder_name, yl)
                new_year_image = QImage(compare_file)
                print(new_year_image)
                print(new_year_image.size())
                print("----------------------")
                # new_year_image = QPixmap.fromImage(new_year_image)
                to_draw = []

                if self.bruteforce:
                    print("lmfao screw efficiency")
                    for y in range(4096):
                        for x in range(4096):
                            if self.check_pixel(new_year_image, x, y, input_color):
                                to_draw.append([x,y])
                else:
                    for key in max_area.keys():
                        x,y = int(key.split(",")[0]), int(key.split(",")[1])
                        # print("here safe", x,y)
                        if self.check_pixel(new_year_image, x, y, input_color):
                            stack_x, stack_y = x,y
                            print("stack x,y = ", x,y)
                            break

                    stack = [(stack_x, stack_y)]
                    np_array = np.zeros((4096, 4096))
                    while stack:
                        x, y = stack.pop()
                        if np_array[x][y] == 1:
                            continue
                        np_array[x][y] = 1
                        if not self.check_pixel(new_year_image, x, y, input_color):
                            continue

                        to_draw.append([x, y])
                        max_area["%s,%s" % (x, y)] = 1
                        # new_pixmap.setPixelColor(x, y, new_color)
                        if np_array[x + 1, y] == 0:
                            stack.append((x + 1, y))
                        if np_array[x - 1, y] == 0:
                            stack.append((x - 1, y))
                        if np_array[x, y + 1] == 0:
                            stack.append((x, y + 1))
                        if np_array[x, y - 1] == 0:
                            stack.append((x, y - 1))



                if not os.path.isfile(save_file):
                    blank_rgba = np.zeros((4096, 4096, 4), dtype=np.uint8)
                    rgba = QImage(blank_rgba.data, blank_rgba.shape[1], blank_rgba.shape[0],
                                         QImage.Format_RGBA8888)
                else:
                    rgba = QImage(save_file)
                painter = QPainter(rgba)
                painter.setPen(QPen(output_color, 1))
                painter.setBrush(QBrush(output_color))
                print("to draw", len(to_draw))
                for x, y in to_draw:
                    painter.drawPoint(x, y)
                print("points all drawn")
                painter.end()
                rgba.save(save_file, "png")





        if self.window3.pixmap() !=None:
            rgba = self.window3.pixmap().toImage()
            save_file = os.path.join(folder_name, "custom.png")
            rgba.save(save_file, "png")


        all_saved_files = os.listdir(folder_name)
        for file in all_saved_files:
            rgba_file = Image.open(os.path.join(folder_name, file))


            if self.gaussian:
                rgba_file = rgba_file.filter(ImageFilter.GaussianBlur(radius=self.radius))
                print("made into gaussian")


            if self.equi:
                print("making mercator into equirectangular...", file)
                # load the Mercator projection image

                # create a new equirectangular projection image with a resolution of 4096x2048 and RGBA format
                equirectangular_image = Image.new('RGBA', (4096, 2048), (0, 0, 0, 0))

                # calculate the pixel size of each degree of longitude and latitude
                pixel_size_x = 4096 / 360.0
                pixel_size_y = 2048 / 180.0

                # iterate through each pixel in the equirectangular image
                for y in range(2048):
                    for x in range(4096):
                        # calculate the longitude and latitude of the current pixel
                        longitude = (x / pixel_size_x) - 180.0
                        latitude = 90.0 - (y / pixel_size_y)

                        # calculate the corresponding pixel in the Mercator projection image
                        mercator_x = int((longitude + 180.0) / 360.0 * 4096.0)
                        mercator_y = int((90.0 - latitude) / 180.0 * 4096.0)

                        # get the color of the pixel from the Mercator projection image
                        color = rgba_file.getpixel((mercator_x, mercator_y))

                        # set the color of the current pixel in the equirectangular projection image
                        equirectangular_image.putpixel((x, y), color)

                # save the equirectangular projection image to a file
                rgba_file = equirectangular_image


            rgba_file.save(os.path.join(folder_name, file), "png")

        all_saved_files = os.listdir(folder_name)
        for file_path in all_saved_files:
            url = QUrl.fromLocalFile(os.path.join(folder_name, file_path))
            QDesktopServices.openUrl(url)
    def gaussian_checkboxClicked(self, state):
        if state==Qt.Checked:
            self.gaussian = True
        else:
            self.gaussian = False


    def equi_checkboxClicked(self, state):
        if state==Qt.Checked:
            self.equi = True
        else:
            self.equi = False


    def glow_checkboxClicked(self, state):
        if state==Qt.Checked:
            self.glow = True
        else:
            self.glow = False

    def brute_forceClicked(self, state):
        if state==Qt.Checked:
            self.bruteforce = True
        else:
            self.bruteforce = False

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



    def remove_item_from_selected_years(self, item):
        if QApplication.keyboardModifiers() == Qt.AltModifier:
            self.selected_years.takeItem(self.selected_years.row(item))
            return True


    #

    def open_color_dialog(self):
        # Open the color dialog and get the selected color
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color

    def update_color_list(self, layout, color_code_index):
        for i in range(self.color_code.count()):
            if self.color_code.itemAt(i) == layout:
                self.color_change_queue.pop(i)
                self.color_code.removeItem(layout)
                return True

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



    # Add an event listener to the second label in the layout
    # def add_event_listener_to_layout(self, layout):
    #     label1 = layout.itemAt(0).widget()
    #     label1.mousePressEvent = self.handle_label_click



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

        if event.key() == Qt.Key_R:
            print("ready to go!!!!")

        else:
            super().keyPressEvent(event)


    def eventFilter(self, obj, event):

        # if obj != QMainWindow and isinstance(obj, QLabel):
        #     if obj.text() == "change":
        #         if event.type() == QEvent.MouseButtonPress and event.modifiers() == Qt.AltModifier:
        #             for i in range(self.color_code.count()):
        #                 layout = self.color_code.itemAt(i)
        #                 if layout.itemAt(1).widget() == obj:
        #                     print("found: ", i)
        #                     color_code_index = i
        #                     break
        #             self.update_color_list(layout, color_code_index)
        #
        #             print("index", color_code_index)
        #             if color_code_index is not None and color_code_index < self.color_code.count():
        #                 item = self.color_code.itemAt(color_code_index)
        #                 if item is not None:
        #                     item.widget().deleteLater()
        #                     self.color_code.removeItem(item)
        #                     print("deleting", item, "length of color_queue:", len(self.color_code))
        #                     self.color_change_queue.pop(color_code_index)
        #                     # self.color_code_widget.
        #                     QCoreApplication.processEvents()
        # #             return True

        # ...

        # return super().eventFilter(obj, event)

        if obj == self.window2:
            if event.type() == QEvent.MouseButtonDblClick and event.modifiers() != Qt.AltModifier:
                color = QColorDialog.getColor(self.color, self)
                self.color = color
                if color.isValid():
                    output_color = color
                    x = int(event.pos().x() / self.scale_factor)
                    y = int(event.pos().y() / self.scale_factor)
                    input_color = self.original_pixmap.toImage().pixelColor(x, y)
                    colorLayout = QVBoxLayout()

                    label1 = QLabel()
                    label2 = QLabel()
                    label2.setText("change")

                    label1.setFixedSize(50,50)
                    label2.setFixedSize(50,50)
                    label1.setStyleSheet(f"background-color: {input_color.name()};")
                    label2.setStyleSheet(f"background-color: {output_color.name()};")
                    colorLayout.addWidget(label1)
                    colorLayout.addWidget(label2)
                    # colorLayout.destroyed.connect()
                    label2.installEventFilter(self)
                    self.color_code.addLayout(colorLayout)


                    # colorLayout.installEventFilter(self)
                    # print("appending: ", [input_color, output_color, x, y, self.currentYear])
                    self.color_change_queue.append([input_color, output_color, x, y, self.currentYear])
                    return True





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
            # print("type here:", type(image))
            # new_color = QColor(Qt.green)  # Choose a new color that is unlikely to appear in the image
            # explored = {}
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

            # print("hi?")
            painter = QPainter(self.qpixmap_rgba)
            painter.setPen(QPen(self.color, 1))
            painter.setBrush(QBrush(self.color))
            for x,y in to_draw:
                painter.drawPoint(x,y)
            painter.end()
            self.window3.setPixmap(self.qpixmap_rgba.scaled(
            self.scale_factor3 * self.qpixmap_rgba.size(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # print("painting ended")
            return True
        return super().eventFilter(obj, event)

    def check_pixel(self, image, x, y, color):

        # print(x,y,image.width(), image.height())
        if x < 1 or x >= image.width() -1 or y < 1 or y >= image.height() - 1:
            # print("exiting here????")
            return False
        # print("pixelcolor", image.pixelColor(x,y), type(image.pixelColor(x,y)))
        # print("color", color, type(color))


        return image.pixelColor(x, y) == color


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Studio Pirates Mercator")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())