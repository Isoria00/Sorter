Sorter Dashboard (Raspberry Pi + Flask + GPIO)

This is a real-time object sorter system prototype using a Raspberry Pi, ultrasonic distance sensor, servo motor, LED indicator, and Arducam - all controlled through a sleek Flask Web dashboard.

Features:
  
  Live Object Sorting: Detecs nearby objects using an ultra sonic sensor and activates a servo-based sorting arm.

  Live Camera Feed: Stream real-time video from the Camera to your browser using OpenCV + Flask

  Status Indicator LED: LED shows when the sorter system is active

  Web Dashboard: Start/Stop the system, monitor status, and view total objects sorted all from the browser. 

  Threaded Sorting Logic: Sorting runs in a background thread so the Flask Server stays responsive

Hardware Used
  
  Component                    PIN
  Ultrasonic Sensor            Trig: GPIO 21, ECHO: GPIO 20
  Servo Motor                  GPIO 16
  Green LED                    GPIO 17
  Arducam                      DISP 1

Requirements:

  RaspberryPi5
  Python 3
  Flask
  gpiozero
  OpenCV
  numpy
  Picamera2

  



  
