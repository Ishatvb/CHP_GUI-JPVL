import sys
import random
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QTimer
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication


class HopperWidget(QWidget):
    def __init__(self, parent=None):
        super(HopperWidget, self).__init__(parent)
        self._coal_level = 0  # Coal level as a percentage (0% to 100%)
        self.animation = QPropertyAnimation(self, b"coal_level")
        self.animation.setDuration(1000)  # Duration of the animation (1 second)

    @pyqtProperty(int)
    def coal_level(self):
        return self._coal_level

    @coal_level.setter
    def coal_level(self, value):
        self._coal_level = value
        self.update()  # Trigger a repaint when the value changes

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define the hopper dimensions
        hopper_width = self.width() // 2
        hopper_height = self.height() - 50  # Padding at the bottom

        # Calculate the current coal level height based on the percentage
        coal_height = int(hopper_height * (self._coal_level / 100))

        # Draw the hopper (a rectangle)
        hopper_x = (self.width() - hopper_width) // 2
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(150, 150, 150))  # Grey color for the hopper
        painter.drawRect(hopper_x, 0, hopper_width, hopper_height)

        # Draw the coal level (a black rectangle)
        painter.setBrush(QColor(0, 0, 0))  # Black color for coal
        painter.drawRect(hopper_x, hopper_height - coal_height, hopper_width, coal_height)

    def set_coal_level(self, level):
        # Animate the coal level smoothly to the new value
        self.animation.stop()
        self.animation.setStartValue(self._coal_level)
        self.animation.setEndValue(level)
        self.animation.start()


class HopperStatusApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hopper Status GUI")
        self.resize(400, 500)

        # Layout setup
        layout = QVBoxLayout()
        self.hopper_widget = HopperWidget(self)
        layout.addWidget(self.hopper_widget)
        self.setLayout(layout)

        # Timer to simulate random LIDAR readings
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.generate_random_reading)
        self.timer.start(2000)  # Update reading every 2 seconds

    def generate_random_reading(self):
        # Simulate random LIDAR readings (1 to 10)
        reading = random.randint(1, 10)  # Random value between 1 and 10

        # Convert the reading to percentage (1 is full, 10 is empty)
        # The formula maps 1-10 range to a 100% scale (100% full, 0% empty)
        percentage = (10 - reading) * 10

        # Set the new coal level in the GUI (trigger the animation)
        self.hopper_widget.set_coal_level(percentage)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HopperStatusApp()
    window.show()
    sys.exit(app.exec_())
