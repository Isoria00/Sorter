from flask import Flask, render_template, jsonify, Response
from picamera2 import Picamera2
import cv2
import time
import numpy as np
from gpiozero import LED, Servo, DistanceSensor
import threading
import atexit
import pigpio


app = Flask(__name__)

def cleanup():
    led.close()
    servo.close()
    sensor.close()
    if pi.connected:
        pi.stop()

atexit.register(cleanup)



# Clean up and pigpio setup
pi = pigpio.pi()

# GPIO setup
TRIG = 21  # ultrasonic trigger
ECHO = 20  # ultrasonic echo
SERVO_PIN = 16  # servo control
LED_PIN = 17  # green led

# Hardware setup
led = LED(LED_PIN)
servo = Servo(SERVO_PIN)  # might need calibration
sensor = DistanceSensor(echo=ECHO, trigger=TRIG)


sorts = 0
system_status = "OFF"
picam2 = None  # Camera is not initialized at startup
sorter_thread = None
stop_sorter = threading.Event()






def sorter_loop():
    global sorts
    print("Sorter thread started")
    led.on()
    servo.value = 0
    try:
        while not stop_sorter.is_set():
            dist = sensor.distance
            print(f"Distance: {dist}")
            if dist < 0.1:
                print("Object detected! Moving servo")
                sorts += 1
                servo.value = 1
                time.sleep(0.5)
                servo.value = 0
                time.sleep(0.5)
            else:
                time.sleep(0.05)
    finally:
        led.off()
        servo.value = 0
        print("Sorter thread stopped")



@app.route('/get_sorts')
def get_sorts():
    return jsonify({'sorts': sorts})





def init_camera():
    global picam2
    if picam2 is None:
        try:
            picam2 = Picamera2()
            picam2.preview_configuration.main.size = (640, 480)
            picam2.preview_configuration.main.format = "RGB888"
            picam2.configure("preview")
            picam2.start()
            time.sleep(1)  # Let camera warm up
        except Exception as e:
            print("Failed to initialize camera:", e)
            picam2 = None

def gen_frames():
    init_camera()
    if not picam2:
        while True:
            # Send black frame or error message frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, 'Camera Error', (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.2)
    else:
        while True:
            frame = picam2.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def dashboard():
    return render_template('dashboard.html', sorts=sorts, system_status=system_status)

@app.route('/start', methods=['POST', 'GET'])
def start():
    global system_status, sorter_thread, stop_sorter

    if system_status == "OFF":
        system_status = "ON"
        led.on()
        stop_sorter.clear()
        sorter_thread = threading.Thread(target=sorter_loop)
        sorter_thread.start()
    else:
        system_status = "OFF"
        stop_sorter.set()
        if sorter_thread:
            sorter_thread.join()
            sorter_thread = None

    return jsonify({'system_status': system_status})
    



@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
