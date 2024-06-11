import sys
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel
import pyqtgraph as pg
import random

class Window(QWidget):
    def __init__(self):
        super().__init__()
        
        # Fixed length for the data arrays
        self.data_length = 100
        
        # Initialize sensor data containers
        self.sensor_data_hopper = []
        self.sensor_data_head = []
        self.sensor_data_tail = []
        
        # Create the grid layout
        self.grid = QGridLayout()
        
        # Create plot widgets
        self.graph_hopper = pg.PlotWidget(self)
        self.graph_head = pg.PlotWidget(self)
        self.graph_tail = pg.PlotWidget(self)
        
        # Create labels for displaying sensor readings
        self.label_hopper = QLabel(self)
        self.label_head = QLabel(self)
        self.label_tail = QLabel(self)
        
        # Add widgets to the grid layout
        self.grid.addWidget(self.graph_hopper, 0, 0, 1, 1)
        self.grid.addWidget(self.label_hopper, 1, 0, 1, 1)
        self.grid.addWidget(self.graph_head, 0, 1, 1, 1)
        self.grid.addWidget(self.label_head, 1, 1, 1, 1)
        self.grid.addWidget(self.graph_tail, 0, 2, 1, 1)
        self.grid.addWidget(self.label_tail, 1, 2, 1, 1)
        
        self.setLayout(self.grid)
        
        # Setup timer for updating the plots
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # Update every second
        
        self.setGeometry(0, 0, 1500, 400)
        self.show()
    
    def read_sensor_data(self):
        # Simulate reading new data from sensors
        hopper_data = random.uniform(0, 10)  # Simulate hopper data
        head_data = random.uniform(0, 10)    # Simulate head data
        tail_data = random.uniform(0, 10)    # Simulate tail data
        return hopper_data, head_data, tail_data
    
    def update(self):
        # Read new sensor data
        hopper, head, tail = self.read_sensor_data()

        # Append new data to the sensor data lists
        self.sensor_data_hopper.append(hopper)
        self.sensor_data_head.append(head)
        self.sensor_data_tail.append(tail)
        
        # Limit the size of the data arrays
        if len(self.sensor_data_hopper) > self.data_length:
            self.sensor_data_hopper.pop(0)
        if len(self.sensor_data_head) > self.data_length:
            self.sensor_data_head.pop(0)
        if len(self.sensor_data_tail) > self.data_length:
            self.sensor_data_tail.pop(0)
        
        # Update plots
        self.graph_hopper.plotItem.clear()
        self.graph_hopper.plotItem.plot(self.sensor_data_hopper, pen='r')
        
        self.graph_head.plotItem.clear()
        self.graph_head.plotItem.plot(self.sensor_data_head, pen='g')
        
        self.graph_tail.plotItem.clear()
        self.graph_tail.plotItem.plot(self.sensor_data_tail, pen='b')
        
        # Update labels with the latest sensor readings
        self.label_hopper.setText(f'Hopper: {hopper:.2f}')
        self.label_head.setText(f'Head: {head:.2f}')
        self.label_tail.setText(f'Tail: {tail:.2f}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())
