import sys
import os
import re
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit, QScrollArea, QSizePolicy


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







        # Create a search widget
        search_widget = QLineEdit()
        search_widget.setPlaceholderText("Search")
        search_widget.textChanged.connect(self.filter_window1)

        # Add the list widget and search widget to a vertical layout
        vlayout = QVBoxLayout()
        vlayout.addWidget(search_widget)
        vlayout.addWidget(self.window1)



        # Create the second main window
        self.window2 = QLabel()
        self.window2.setAlignment(Qt.AlignCenter)
        self.window2.setStyleSheet("border: 1px solid red;")
        self.window2.setFocusPolicy(Qt.StrongFocus)
        # self.window2.setScaledContents(True)


        self.scale_factor = 1.0




        # self.scroll_area2 = QScrollArea()
        # self.scroll_area2.setWidgetResizable(True)
        #
        # self.widget2=QWidget()
        # self.scroll_area2.setWidget(self.widget2)
        # self.window2layout = QVBoxLayout(self.widget2)
        # self.window2layout.addWidget(self.window2)

        # self.setCentralWidget(self.scroll_area2)



        # self.scrollArea.setVisible(True)
        # self.scrollArea.setBackgroundRole(QPalette.Dark)
        # self.scrollArea.setWidget(self.window2)
        # self.window2.resize(800,800)

        # Create the third main window
        self.window3 = QWidget()
        self.window3_layout = QVBoxLayout()
        self.window3_layout.addWidget(QLabel("Window 3"))
        self.window3.setLayout(self.window3_layout)
        self.window3.setStyleSheet("border: 1px solid green;")


        # Set the allowed areas for the main windows
        self.window1.setFixedSize(200, 1000)
        self.window2.setFixedSize(800, 800)
        self.window3.setFixedSize(800, 800)

        # Add the main windows to the main widget
        hlayout.addLayout(vlayout)
        hlayout.addWidget(self.window2)
        hlayout.addWidget(self.window3)
        main_widget.setLayout(hlayout)
        # self.setCentralWidget(self.scroll_area2)
        #self.setFocus()

    def sort_function(self, file):

        if "BC" in file:
            year = -1*int(file.replace("BC","").replace(".png",""))
        else:
            year = int(file.replace("Year_AD", "").replace(".png", ""))
        ##self.setFocus()
        return year

    def filter_window1(self, text):
        # Loop through the items in the list widget
        for i in range(self.window1.count()):
            item = self.window1.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
        ##self.setFocus()

    def update_window2(self):
        # Get the selected item from the list widget
        selected_item = self.window1.currentItem()

        if selected_item is not None:
            # Get the file path of the selected item
            file_path = os.path.join("./maps", selected_item.text())

            # Load the image using QPixmap and set it as the pixmap of the label
            pixmap = QPixmap(file_path)
            self.window2.setPixmap(pixmap.scaled(self.window2.width(), self.window2.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # self.window2.setPixmap(pixmap.scaled(self.window2.width(), self.window2.height()))
            # self.window2.
        ##self.setFocus()




    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            print("hi")
            self.window2.setPixmap(self.window2.pixmap().scaled(1.1*self.window2.pixmap().size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # self.scroll_area2
            # print("doing1")
            # pixmap = self.window2.pixmap()
            # width = pixmap.width()*1.1
            # height = pixmap.height()*1.1
            # self.window2.setPixmap(pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # self.scroll_area2.setMinimumSize(width, height)
            # self.scroll_area2.updateGeometry()
            # self.window2.update()
            # print("doing2")

            # # Increase the scale factor by 0.1
            # print("I hear you")
            # self.scale_factor += 0.1
            #
            # print(self.scale_factor)
            #
            # # Get the current pixmap from window2
            # pixmap = self.window2.pixmap()
            #
            # if pixmap is not None:
            #     # Scale the pixmap using the new scale factor
            #
            #     scaled_pixmap = pixmap.scaled(
            #         pixmap.width() * self.scale_factor,
            #         pixmap.height() * self.scale_factor,
            #         Qt.KeepAspectRatio,
            #         Qt.SmoothTransformation
            #     )
            #
            #     print(pixmap.width())
            #     # Set the scaled pixmap as the pixmap of window2
            #     self.window2.setPixmap(scaled_pixmap)
            #     # self.window2.update()

        if event.key() == Qt.Key_W:
            # Increase the scale factor by 0.1
            self.scale_factor -= 0.1

            # Get the current pixmap from window2
            pixmap = self.window2.pixmap()

            if pixmap is not None:
                # Scale the pixmap using the new scale factor
                scaled_pixmap = pixmap.scaled(
                    pixmap.width() * self.scale_factor,
                    pixmap.height() * self.scale_factor,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                # Set the scaled pixmap as the pixmap of window2
                self.window2.setPixmap(scaled_pixmap)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

