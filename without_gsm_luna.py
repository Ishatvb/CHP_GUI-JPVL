import serial 
import time
import csv
from datetime import datetime
import RPi.GPIO as GPIO
# Luna Sensor Pins
#VCC 8 10 Ground

def parse_lidar_data(data):
    #print(data[1])
    if data[0] == 0x59 and data[1] == 0x59:
        distance = (data[3] << 8) | data[2]
        return distance / 100.0
    else:
        print("Invalid frame header")
        return None
def main():
    #ser0 = serial.Serial('/dev/ttyAMA0', 115200, timeout=3)
    #ser0.flushInput()
    ser0 = serial.Serial('/dev/ttyAMA0', 115200)
    ser1 = serial.Serial('/dev/ttyAMA3', 115200, timeout=3)
    ser2 = serial.Serial('/dev/ttyAMA4', 115200, timeout=3)
    #ser3 = serial.Serial('/dev/ttyAMA4', 115200, timeout=3)
    phone_number = '+918120194488' #********** change it to the phone number you want to send sms
    text_message = 'Hello Sir from raspberrypi and GSM'
    power_key = 6
    rec_buff = ''
    try:
        with open('Experiment_1.csv', 'a', newline='') as csvfile:
            fieldnames = ['Date', 'Current_Time','Luna_Distance_Hopper', 'Luna_Distance_Head','Luna_Distance_Tail','Spilage']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
              
            
            while True:
                
                time.sleep(1)
                ser0.reset_input_buffer()
                ser1.reset_input_buffer()
                ser2.reset_input_buffer()
                #ser3.reset_input_buffer()
                data0 = ser0.read(9)
                data1 = ser1.read(9)
                data2 = ser2.read(9)
            
                luna_distance_1 = parse_lidar_data(data0)
                luna_distance_2 = parse_lidar_data(data1)
                luna_distance_3 = parse_lidar_data(data2)
                
                
                if luna_distance_1 is not None and luna_distance_2 is not None and luna_distance_3 is not None:
                    print("Luna Distance_Hopper:", luna_distance_1 * 100, "cm")
                    print("Luna Distance_Head:", luna_distance_2 * 100, "cm")
                    print("Luna Distance_Tail:", luna_distance_3 * 100, "cm")

                    now = datetime.now()
                    current_date = now.strftime("%Y-%m-%d")
                    current_time = now.strftime("%H:%M:%S")
                    difference=luna_distance_3*100 - luna_distance_2*100
                   
                    if difference >=4.00:
                        spilage = difference
                    else:spilage= 0
                    writer.writerow({
                        'Date': current_date,
                        'Current_Time': current_time,
                        'Luna_Distance_Hopper': luna_distance_1 * 100,
                        'Luna_Distance_Head': luna_distance_2 * 100,
                        'Luna_Distance_Tail': luna_distance_3 * 100,
                        'Spilage':spilage,
                    })
                    
                    csvfile.flush()
                    
                    if luna_distance_1 < 0.05 or luna_distance_2 < 0.05:
                        print("Luna Distance is less than 5cm. Closing the file.")
                        break
    except KeyboardInterrupt:
        pass
    finally:
        ser0.close()
        ser1.close()
        ser2.close()
        GPIO.cleanup()

if __name__ == "__main__":
    main()