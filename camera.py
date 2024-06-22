import sys
import numpy as np
import random
import cv2
from PyQt5.QtCore import QTimer, QFile, QTextStream, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton, QLabel, QSizePolicy
import pyqtgraph as pg
from PyQt5.QtGui import QPixmap, QImage
from sidebar_ui import Ui_MainWindow  # Import the generated UI module

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.icon_only_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.scada_btn_2.setChecked(True)

        # Fixed length for the data arrays
        self.data_length = 100
        
        # Initialize sensor data containers
        self.sensor_data_hopper = np.zeros(self.data_length)
        self.sensor_data_head = np.zeros(self.data_length)
        self.sensor_data_tail = np.zeros(self.data_length)
        
        # Initialize x-axis values
        self.x = np.arange(self.data_length)
        
        # Create plot widgets
        self.graph_hopper = pg.PlotWidget()
        self.graph_head = pg.PlotWidget()
        self.graph_tail = pg.PlotWidget()

         # Create additional plot widgets for labels
        self.graph_hopper_label = pg.PlotWidget()
        self.graph_head_label = pg.PlotWidget()
        self.graph_tail_label = pg.PlotWidget()
        
        # Replace frames and labels with plot widgets
        self.ui.frame.setLayout(QVBoxLayout())
        self.ui.frame.layout().addWidget(self.graph_hopper)

        self.ui.label_30.setLayout(QVBoxLayout())
        self.ui.label_30.layout().addWidget(self.graph_hopper_label)
        
        self.ui.frame_4.setLayout(QVBoxLayout())
        self.ui.frame_4.layout().addWidget(self.graph_head)

        self.ui.label_31.setLayout(QVBoxLayout())
        self.ui.label_31.layout().addWidget(self.graph_head_label)
        
        self.ui.frame_6.setLayout(QVBoxLayout())
        self.ui.frame_6.layout().addWidget(self.graph_tail)

        self.ui.label_40.setLayout(QVBoxLayout())
        self.ui.label_40.layout().addWidget(self.graph_tail_label)
        
        # Initialize QLabel widgets for live streaming
        self.label_hopper_main = QLabel(self.ui.label_15)
        
        self.label_head_main = QLabel(self.ui.label_17)
        
        self.label_tail_main = QLabel(self.ui.label_19)
        
        # Ensure QLabel widgets expand to fill the frames
        self.label_hopper_main.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_hopper_main.setAlignment(Qt.AlignCenter)

        self.label_head_main.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_head_main.setAlignment(Qt.AlignCenter)

        self.label_tail_main.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_tail_main.setAlignment(Qt.AlignCenter)

        # Start video capture
        self.capture_hopper = cv2.VideoCapture(0)  # Change the argument to the camera index if needed
        self.capture_head = cv2.VideoCapture(1)  # Change the argument to the camera index if needed
        self.capture_tail = cv2.VideoCapture(2)  # Change the argument to the camera index if needed

        # Set up QTimer for updating video frames
        self.timer_video = QTimer()
        self.timer_video.timeout.connect(self.update_video)
        self.timer_video.start(100)  # Update video frames every 100 milliseconds

        # Setup timer for updating the plots
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # Update every second

        self.connect_signals()
        
    def connect_signals(self):
        self.ui.scada_btn_1.toggled.connect(self.on_scada_btn_1_toggled)
        self.ui.scada_btn_2.toggled.connect(self.on_scada_btn_2_toggled)
        self.ui.luna_btn_1.toggled.connect(self.on_luna_btn_1_toggled)
        self.ui.luna_btn_2.toggled.connect(self.on_luna_btn_2_toggled)
        self.ui.hopper_btn_1.toggled.connect(self.on_hopper_btn_1_toggled)
        self.ui.hopper_btn_2.toggled.connect(self.on_hopper_btn_2_toggled)
        self.ui.head_btn_1.toggled.connect(self.on_head_btn_1_toggled)
        self.ui.head_btn_2.toggled.connect(self.on_head_btn_2_toggled)
        self.ui.tail_btn_1.toggled.connect(self.on_tail_btn_1_toggled)
        self.ui.tail_btn_2.toggled.connect(self.on_tail_btn_2_toggled)
        self.ui.search_btn.clicked.connect(self.on_search_btn_clicked)
        self.ui.user_btn.clicked.connect(self.on_user_btn_clicked)
        self.ui.search_btn.clicked.connect(self.on_search_btn_clicked)
        self.ui.user_btn.clicked.connect(self.on_user_btn_clicked)
        self.ui.stackedWidget.currentChanged.connect(self.on_stackedWidget_currentChanged)

    def read_sensor_data(self):
        # Simulate reading new data from sensors
        hopper_data = random.uniform(0, 10)  # Simulate hopper data
        head_data = random.uniform(0, 10)    # Simulate head data
        tail_data = random.uniform(0, 10)    # Simulate tail data
        return hopper_data, head_data, tail_data

    def update(self):
        # Read new sensor data
        hopper, head, tail = self.read_sensor_data()

        # Shift data to the left and append new data
        self.sensor_data_hopper = np.roll(self.sensor_data_hopper, -1)
        self.sensor_data_head = np.roll(self.sensor_data_head, -1)
        self.sensor_data_tail = np.roll(self.sensor_data_tail, -1)
        
        self.sensor_data_hopper[-1] = hopper
        self.sensor_data_head[-1] = head
        self.sensor_data_tail[-1] = tail
        
        # Determine plot color based on the latest value
        hopper_color = self.get_color(hopper)
        head_color = self.get_color(head)
        tail_color = self.get_color(tail)
        
        # Update plots
        self.update_plot(self.graph_hopper, self.sensor_data_hopper, hopper_color)
        self.update_plot(self.graph_hopper_label, self.sensor_data_hopper, hopper_color)

        self.update_plot(self.graph_head, self.sensor_data_head, head_color)
        self.update_plot(self.graph_head_label, self.sensor_data_head, head_color)

        self.update_plot(self.graph_tail, self.sensor_data_tail, tail_color)
        self.update_plot(self.graph_tail_label, self.sensor_data_tail, tail_color)

        # Update labels with the latest sensor readings
        self.ui.label_5.setText(f'Hopper: {hopper:.2f}')
        self.ui.label_53.setText(f'Hopper: {hopper:.2f}')

        self.ui.label_12.setText(f'Head: {head:.2f}')
        self.ui.label_52.setText(f'Head: {head:.2f}')

        self.ui.label_14.setText(f'Tail: {tail:.2f}')
        self.ui.label_54.setText(f'Tail: {tail:.2f}')

    # Method to update a plot
    def update_plot(self, plot_widget, data, color):
        plot_widget.plotItem.clear()
        plot_widget.plotItem.plot(self.x, data, pen=color)

    def update_video(self):
        # Read frames from cameras
        ret_hopper, frame_hopper = self.capture_hopper.read()
        ret_head, frame_head = self.capture_head.read()
        ret_tail, frame_tail = self.capture_tail.read()

        if ret_hopper:
            # Convert the frame to RGB format
            frame_hopper = cv2.cvtColor(frame_hopper, cv2.COLOR_BGR2RGB)
            # Convert the frame to QImage
            img_hopper = QImage(frame_hopper.data, frame_hopper.shape[1], frame_hopper.shape[0], QImage.Format_RGB888)
            # Set the QImage to the QLabel
            self.label_hopper_main.setPixmap(QPixmap.fromImage(img_hopper))

        if ret_head:
            # Convert the frame to RGB format
            frame_head = cv2.cvtColor(frame_head, cv2.COLOR_BGR2RGB)
            # Convert the frame to QImage
            img_head = QImage(frame_head.data, frame_head.shape[1], frame_head.shape[0], QImage.Format_RGB888)
            # Set the QImage to the QLabel
            self.label_head_main.setPixmap(QPixmap.fromImage(img_head))

        if ret_tail:
            # Convert the frame to RGB format
            frame_tail = cv2.cvtColor(frame_tail, cv2.COLOR_BGR2RGB)
            # Convert the frame to QImage
            img_tail = QImage(frame_tail.data, frame_tail.shape[1], frame_tail.shape[0], QImage.Format_RGB888)
            # Set the QImage to the QLabel
            self.label_tail_main.setPixmap(QPixmap.fromImage(img_tail))

    def get_color(self, value):
        if value > 8:
            return 'r'
        elif value > 5:
            return 'y'
        else:
            return 'g'

    ## Function for searching
    def on_search_btn_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(5)
        search_text = self.ui.search_input.text().strip()
        if search_text:
            self.ui.label_9.setText(search_text)

    ## Function for changing page to user page
    def on_user_btn_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(6)

    ## Change QPushButton Checkable status when stackedWidget index changed
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.icon_only_widget.findChildren(QPushButton) \
                    + self.ui.full_menu_widget.findChildren(QPushButton)
        
        for btn in btn_list:
            if index in [5, 6]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)
            
    ## functions for changing menu page
    def on_scada_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)
    
    def on_scada_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_luna_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_luna_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_hopper_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def on_hopper_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def on_head_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def on_head_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def on_tail_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    def on_tail_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    def on_power_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(5)

    def on_power_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(5)

    def on_history_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(8)

    def on_history_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(8)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load style file
    style_file = QFile("style.qss")
    style_file.open(QFile.ReadOnly | QFile.Text)
    style_stream = QTextStream(style_file)
    app.setStyleSheet(style_stream.readAll())

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
