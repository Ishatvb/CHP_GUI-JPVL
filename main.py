import sys
import numpy as np
import random
import serial
import time
import csv
from datetime import datetime
import RPi.GPIO as GPIO
from PyQt5.QtCore import QTimer, QFile, QTextStream
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton
import pyqtgraph as pg
from sidebar_ui import Ui_MainWindow  # Import the generated UI module

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.icon_only_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.home_btn_2.setChecked(True)

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

        # Replace frames with plot widgets
        self.ui.frame.setLayout(QVBoxLayout())
        self.ui.frame.layout().addWidget(self.graph_hopper)

        self.ui.frame_4.setLayout(QVBoxLayout())
        self.ui.frame_4.layout().addWidget(self.graph_head)

        self.ui.frame_6.setLayout(QVBoxLayout())
        self.ui.frame_6.layout().addWidget(self.graph_tail)

        # Setup timer for updating the plots
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # Update every second

        self.connect_signals()

        # Initialize serial connections
        #self.ser0 = serial.Serial('/dev/ttyAMA0', 115200)
        #self.ser1 = serial.Serial('/dev/ttyAMA3', 115200, timeout=3)
        #self.ser2 = serial.Serial('/dev/ttyAMA4', 115200, timeout=3)

    def connect_signals(self):
        self.ui.home_btn_1.toggled.connect(self.on_home_btn_1_toggled)
        self.ui.home_btn_2.toggled.connect(self.on_home_btn_2_toggled)
        self.ui.dashboard_btn_1.toggled.connect(self.on_dashboard_btn_1_toggled)
        self.ui.dashboard_btn_2.toggled.connect(self.on_dashboard_btn_2_toggled)
        self.ui.orders_btn_1.toggled.connect(self.on_orders_btn_1_toggled)
        self.ui.orders_btn_2.toggled.connect(self.on_orders_btn_2_toggled)
        self.ui.products_btn_1.toggled.connect(self.on_products_btn_1_toggled)
        self.ui.products_btn_2.toggled.connect(self.on_products_btn_2_toggled)
        self.ui.customers_btn_1.toggled.connect(self.on_customers_btn_1_toggled)
        self.ui.customers_btn_2.toggled.connect(self.on_customers_btn_2_toggled)
        self.ui.search_btn.clicked.connect(self.on_search_btn_clicked)
        self.ui.user_btn.clicked.connect(self.on_user_btn_clicked)
        self.ui.stackedWidget.currentChanged.connect(self.on_stackedWidget_currentChanged)

    def parse_lidar_data(self, data):
        if data[0] == 0x59 and data[1] == 0x59:
            distance = (data[3] << 8) | data[2]
            return distance / 100.0
        else:
            print("Invalid frame header")
            return None

    def read_sensor_data(self):
        # Read LiDAR data
        self.ser0.reset_input_buffer()
        self.ser1.reset_input_buffer()
        self.ser2.reset_input_buffer()
        data0 = self.ser0.read(9)
        data1 = self.ser1.read(9)
        data2 = self.ser2.read(9)

        luna_distance_1 = self.parse_lidar_data(data0)
        luna_distance_2 = self.parse_lidar_data(data1)
        luna_distance_3 = self.parse_lidar_data(data2)

        if luna_distance_1 is not None and luna_distance_2 is not None and luna_distance_3 is not None:
            print("Luna Distance_Hopper:", luna_distance_1 * 100, "cm")
            print("Luna Distance_Head:", luna_distance_2 * 100, "cm")
            print("Luna Distance_Tail:", luna_distance_3 * 100, "cm")

            return luna_distance_1 * 100, luna_distance_2 * 100, luna_distance_3 * 100
        else:
            return 0, 0, 0  # Return 0 if any distance is None

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

        # Update plots
        self.graph_hopper.plotItem.clear()
        self.graph_hopper.plotItem.plot(self.x, self.sensor_data_hopper, pen='r')

        self.graph_head.plotItem.clear()
        self.graph_head.plotItem.plot(self.x, self.sensor_data_head, pen='g')

        self.graph_tail.plotItem.clear()
        self.graph_tail.plotItem.plot(self.x, self.sensor_data_tail, pen='b')

        # Update labels with the latest sensor readings
        self.ui.label_5.setText(f'Hopper: {hopper:.2f}')
        self.ui.label_12.setText(f'Head: {head:.2f}')
        self.ui.label_14.setText(f'Tail: {tail:.2f}')

    # Functions for changing page
    def on_search_btn_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(5)
        search_text = self.ui.search_input.text().strip()
        if search_text:
            self.ui.label_9.setText(search_text)

    def on_user_btn_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(6)

    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.icon_only_widget.findChildren(QPushButton) \
                   + self.ui.full_menu_widget.findChildren(QPushButton)

        for btn in btn_list:
            if index in [5, 6]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)

    def on_home_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_home_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_dashboard_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_dashboard_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_orders_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def on_orders_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def on_products_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def on_products_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def on_customers_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    def on_customers_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    def closeEvent(self, event):
        # Clean up serial connections
        self.ser0.close()
        self.ser1.close()
        self.ser2.close()
        GPIO.cleanup()
        event.accept()

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
