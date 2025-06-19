# Sorter Dashboard (Raspberry Pi + Flask + GPIO)

This is a real-time object sorter system prototype using a Raspberry Pi, ultrasonic distance sensor, servo motor, LED indicator, and Arducam - all controlled through a sleek Flask Web dashboard.
➡ There is so much potential to this prototype — you can 3D print any arm and connect a belt to it to really start sorting at scale.

## Images:

![Screenshot 2025-06-19 133556](https://github.com/user-attachments/assets/302a41a2-721c-4c48-885c-c5e3a3682d15)

![Screenshot 2025-06-19 133647](https://github.com/user-attachments/assets/93b7e8b5-c53c-41af-b78b-5d61ba5ce42c)

![Screenshot 2025-06-19 133723](https://github.com/user-attachments/assets/bb392e2f-2ec6-4c0a-9509-148f8c45156c)

![Screenshot 2025-06-19 133811](https://github.com/user-attachments/assets/2d94ec2f-b0f2-48a9-9dc8-1b5a472759d0)

![Screenshot 2025-06-19 133543](https://github.com/user-attachments/assets/927d7fc3-f029-40d3-b0e0-e108e12ca349)

![Screenshot 2025-06-19 133447](https://github.com/user-attachments/assets/43418ad4-d622-405b-b44d-ac74df79c472)

![Screenshot 2025-06-19 133431](https://github.com/user-attachments/assets/65e50693-f5a0-4ca8-b3ab-437a9d6f1b47)

---

## Features:

- **Live Object Sorting**: Detects nearby objects using an ultra sonic sensor and activates a servo.
- **Live Camera Feed**: Stream real-time video from the Camera to your browser using OpenCV + Flask
- **Status Indicator LED**: LED shows when the sorter system is active
- **Web Dashboard**: Start/Stop the system, monitor status, and view total objects sorted all from the browser and in real time.
- **Threaded Sorting Logic**: Sorting runs in a background thread so the Flask Server stays responsive

---

## Hardware Used

Component
- Ultrasonic Sensor Trig: GPIO 21, ECHO: GPIO 20
- Servo Motor GPIO 16
- Green LED GPIO 17
- Arducam DISP 1
- Wires
- Resistors used to drop down from 5v to 3.3 to avoid pin damage from Ultrasonic Sensor I used 1k and 2k


---

## Requirements:

- RaspberryPi5  
- Python 3  
- Flask  
- gpiozero  
- OpenCV  
- numpy  
- Picamera2
