import sys
import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create a label to display the video frames
        self.label = QLabel(self)
        self.label.setScaledContents(True)  # Ensure video scales to fit label
        self.label.setMinimumSize(1, 1)  # Ensure QLabel resizes correctly
        self.label.setAlignment(Qt.AlignCenter)  # Center the image
        
        # Layout for the widget
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Open the video file
        self.cap = cv2.VideoCapture('images/scadav1.mp4')  # Replace with your video file path
        
        # Check if the video opened successfully
        if not self.cap.isOpened():
            print("Error opening video file")
            sys.exit()
        
        # Create a timer to trigger the display function
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(25)  # Trigger every 25 milliseconds (40 fps)

    def display_frame(self):
        # Read frame-by-frame
        ret, frame = self.cap.read()
        
        if ret:
            # Convert frame to RGB format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert frame to QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Display QImage in QLabel
            self.label.setPixmap(QPixmap.fromImage(q_image))
        else:
            # Reset video to the beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def closeEvent(self, event):
        # Release the video capture when closing the widget
        self.cap.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle('Video Player')
    player.show()
    sys.exit(app.exec_())
