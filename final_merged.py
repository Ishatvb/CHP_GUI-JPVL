import sys
import numpy as np
import random
import cv2
import serial 
import time
import csv
from datetime import datetime
import RPi.GPIO as GPIO
from PyQt5.QtCore import QTimer, QFile, QTextStream, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton, QLabel, QSizePolicy
import pyqtgraph as pg
from PyQt5.QtGui import QPixmap, QImage
from sidebar import Ui_MainWindow  
from video_player import VideoPlayer  
from Hopper_GUI import HopperWidget 

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
        
        self.label_head_main = QLabel(self.ui.label_23)
        
        self.label_tail_main = QLabel(self.ui.label_37)
        
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

        # Initialize and add VideoPlayer to label_55
        self.video_player = VideoPlayer()
        self.ui.label_55.setLayout(QVBoxLayout())
        self.ui.label_55.layout().addWidget(self.video_player)

        # Initialize HopperWidget
        self.hopper_widget = HopperWidget(self)
        self.ui.label_16.setLayout(QVBoxLayout())
        self.ui.label_16.layout().addWidget(self.hopper_widget)
        
        self.connect_signals()

        #Initialize serial connections
        self.ser0 = serial.Serial('/dev/ttyAMA0', 115200)
        self.ser1 = serial.Serial('/dev/ttyAMA3', 115200, timeout=3)
        self.ser2 = serial.Serial('/dev/ttyAMA4', 115200, timeout=3)

        # Initialize CSV file
        self.csvfile = open('Experiment_1.csv', 'a', newline='')
        self.fieldnames = ['Date', 'Current_Time', 'Luna_Distance_Hopper', 'Luna_Distance_Head', 'Luna_Distance_Tail', 'Spilage']
        self.writer = csv.DictWriter(self.csvfile, fieldnames=self.fieldnames)
        if self.csvfile.tell() == 0:
            self.writer.writeheader()
        
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

    def parse_lidar_data(data):
    #print(data[1])
        if data[0] == 0x59 and data[1] == 0x59:
            distance = (data[3] << 8) | data[2]
            return distance / 100.0
        else:
            print("Invalid frame header")
            return None

    def read_sensor_data(self):
        # Simulate reading new data from sensors
        # hopper_data = random.uniform(4, 9)  # Simulate hopper data
        # head_data = random.uniform(3, 6)    # Simulate head data
        # tail_data = random.uniform(3, 6)    # Simulate tail data
        # return hopper_data, head_data, tail_data

        self.ser0.reset_input_buffer()
        self.ser1.reset_input_buffer()
        self.ser2.reset_input_buffer()
        data0 = self.ser0.read(9)
        data1 = self.ser1.read(9)
        data2 = self.ser2.read(9)

        hopper_data = self.parse_lidar_data(data0)
        head_data = self.parse_lidar_data(data1)
        tail_data = self.parse_lidar_data(data2)

        if hopper_data is not None and head_data is not None and tail_data is not None:
            print("Luna Distance_Hopper:", hopper_data * 100, "cm")
            print("Luna Distance_Head:", head_data * 100, "cm")
            print("Luna Distance_Tail:", tail_data * 100, "cm")

            return hopper_data * 100, head_data * 100, tail_data * 100
        else:
            return 0, 0, 0  # Return 0 if any distance is None

    def update(self):
        # Read new sensor data
        hopper, head, tail = self.read_sensor_data()

        # Update coal level in the HopperWidget
        coal_percentage = (9 - hopper) * 10  # Convert hopper data to percentage
        self.hopper_widget.set_coal_level(coal_percentage)

        # Shift data and update plots (existing code follows)
        self.sensor_data_hopper = np.roll(self.sensor_data_hopper, -1)
        self.sensor_data_hopper[-1] = hopper

        # Shift data to the left and append new data
        self.sensor_data_hopper = np.roll(self.sensor_data_hopper, -1)
        self.sensor_data_head = np.roll(self.sensor_data_head, -1)
        self.sensor_data_tail = np.roll(self.sensor_data_tail, -1)
        
        self.sensor_data_hopper[-1] = hopper
        self.sensor_data_head[-1] = head
        self.sensor_data_tail[-1] = tail
        
        # Determine plot color based on the latest value
        hopper_color = self.get_color_hopper(hopper)
        head_color = self.get_color_head(head)
        tail_color = self.get_color_tail(tail)
        
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

        # Write data to CSV file
        self.write_to_csv(hopper, head, tail)

        # Display current status based on the sensor readings
        status = self.get_status(hopper, head, tail)
        self.ui.label_57.setText(status)

        # Determine the background color for label_55 based on status
        color_map = {
            "STOP THE BELT": "red",
            "Normal Operation": "green",
            "Alert: Coal Present Between Head and Tail, Hopper Empty": "yellow",
            "Alert: Coal Present Between Head and Tail": "yellow",
            "Alert: Coal on Conveyor Belt, Hopper Empty": "yellow",
            "Alert: Possible Hopper Jam": "yellow",
            "Alert: Possible Hopper Jam with Coal Between Head and Tail": "yellow"
        }

        color = color_map.get(status, "white")  # Default to white if status is not found
        self.ui.label_55.setStyleSheet(f"background-color: {color};")

        # Update the VideoPlayer component or other elements if needed
        self.video_player.update()  # Assuming VideoPlayer has an update method


    # Method to update a plot
    def update_plot(self, plot_widget, data, color):
        plot_widget.plotItem.clear()
        plot_widget.plotItem.plot(self.x, data, pen=color)

    def get_color_hopper(self, value):
        if value > 8:
            return 'r'
        elif value > 5:
            return 'y'
        else:
            return 'g'
        
    def get_color_head(self, value):
        if value > 8:
            return 'r'
        elif value > 5:
            return 'y'
        else:
            return 'g'
        
    def get_color_tail(self, value):
        if value > 8:
            return 'r'
        elif value > 5:
            return 'y'
        else:
            return 'g'
        
    def write_to_csv(self, hopper, head, tail):
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            self.writer.writerow({
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Current_Time': current_time,
                'Luna_Distance_Hopper': hopper,
                'Luna_Distance_Head': head,
                'Luna_Distance_Tail': tail,
                'Spilage': 0  # Placeholder for Spilage
            })
            self.csvfile.flush()
        except Exception as e:
            print(f"Error writing to CSV: {e}")

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



    def get_status(self, hopper, head, tail):
        # Define thresholds and ranges
        hopper_max, hopper_min = 9, 4
        head_max, head_min = 6, 3
        tail_max, tail_min = 6, 3

        # Define ranges for near-max and near-min values
        hopper_max_range = (hopper_max - 0.5, hopper_max + 0.5)
        hopper_min_range = (hopper_min - 0.5, hopper_min + 0.5)
        
        head_max_range = (head_max - 0.5, head_max + 0.5)
        head_min_range = (head_min - 0.5, head_min + 0.5)
        
        tail_max_range = (tail_max - 0.5, tail_max + 0.5)
        tail_min_range = (tail_min - 0.5, tail_min + 0.5)

        # Case 1: H = Max value, Hd = Max value, T = Max value
        if hopper_max_range[0] <= hopper <= hopper_max_range[1] and \
        head_max_range[0] <= head <= head_max_range[1] and \
        tail_max_range[0] <= tail <= tail_max_range[1]:
            return "STOP THE BELT"

        # Case 2: H = Max value, Hd = Max value, T = (less than max value and more than or equal to min value)
        elif hopper_max_range[0] <= hopper <= hopper_max_range[1] and \
            head_max_range[0] <= head <= head_max_range[1] and \
            tail_min_range[0] <= tail < tail_max_range[0]:
            return "Alert: Coal Present Between Head and Tail, Hopper Empty"

        # Case 3: H = Max value, Hd = (less than max value and more than or equal to min value), T = Max value
        elif hopper_max_range[0] <= hopper <= hopper_max_range[1] and \
            head_min_range[0] <= head < head_max_range[0] and \
            tail_max_range[0] <= tail <= tail_max_range[1]:
            return "Alert: Coal Present Between Head and Tail, Hopper Empty"

        # Case 4: H = Max value, Hd = (less than max value and more than or equal to min value), T = (less than max value and more than or equal to min value)
        elif hopper_max_range[0] <= hopper <= hopper_max_range[1] and \
            head_min_range[0] <= head < head_max_range[0] and \
            tail_min_range[0] <= tail < tail_max_range[0]:
            return "Alert: Coal on Conveyor Belt, Hopper Empty"

        # Case 5: H = (less than max value and more than or equal to min value), Hd = Max value, T = Max value
        elif hopper_min_range[0] <= hopper < hopper_max_range[1] and \
            head_max_range[0] <= head <= head_max_range[1] and \
            tail_max_range[0] <= tail <= tail_max_range[1]:
            return "Alert: Possible Hopper Jam"

        # Case 6: H = (less than max value and more than or equal to min value), Hd = Max value, T = (less than max value and more than or equal to min value)
        elif hopper_min_range[0] <= hopper < hopper_max_range[1] and \
            head_max_range[0] <= head <= head_max_range[1] and \
            tail_min_range[0] <= tail < tail_max_range[0]:
            return "Alert: Possible Hopper Jam with Coal Between Head and Tail"

        # Case 7: H = (less than max value and more than or equal to min value), Hd = (less than max value and more than or equal to min value), T = Max value
        elif hopper_min_range[0] <= hopper < hopper_max_range[1] and \
            head_min_range[0] <= head < head_max_range[1] and \
            tail_max_range[0] <= tail <= tail_max_range[1]:
            return "Alert: Coal Present Between Head and Tail"

        # Case 8: H = (less than max value and more than or equal to min value), Hd = (less than max value and more than or equal to min value), T = (less than max value and more than or equal to min value)
        elif hopper_min_range[0] <= hopper < hopper_max_range[1] and \
            head_min_range[0] <= head < head_max_range[1] and \
            tail_min_range[0] <= tail < tail_max_range[1]:
            return "Normal Operation"

    ## Function for searching
    def on_search_btn_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(6)
        search_text = self.ui.search_input.text().strip()
        if search_text:
            self.ui.label_9.setText(search_text)

    ## Function for changing page to user page
    def on_user_btn_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(7)

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

    def on_stackedWidget_currentChanged(self, index):
        if index == 0:
            # Update SCADA page elements
            self.update()

    def closeEvent(self, event):
        # Cleanup serial connections and CSV file on exit
        self.ser0.close()
        self.ser1.close()
        self.ser2.close()
        self.csvfile.close()
        self.capture_hopper.release()
        self.capture_head.release()
        self.capture_tail.release()
        super(MainWindow, self).closeEvent(event)

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