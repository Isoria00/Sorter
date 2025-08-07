from flask import Flask, render_template, jsonify, Response
from picamera2 import Picamera2
import cv2
import time
import numpy as np
from gpiozero import LED, Button, Servo, DistanceSensor
import time
import threading
from signal import pause
import atexit
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio
import RPi.GPIO as GPIO
from datetime import datetime

app = Flask(__name__)

def cleanup():
    led.close()
    servo.close()
    sensor.close()


TRIG = 21  
ECHO = 20  
SERVO_PIN = 16  
LED_PIN = 17 


led = LED(LED_PIN)
servo = Servo(SERVO_PIN)  
sensor = DistanceSensor(echo=ECHO, trigger=TRIG)


sorts = 0
system_status = "OFF"  
sorter_thread = None
stop_sorter = threading.Event()

logs = []
speeds = {
    'Slow': .5,
    'Medium': .4,
    'Fast': .3,
    'Super Fast': .2,
    'Max': .1
}
current_speed = speeds['Medium']

servo.detach()

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (240, 180)}))
picam2.start()



def generate_video_stream():
    while True:
        frame = picam2.capture_array()

        height, width, _ = frame.shape

        rect_w, rect_h = width // 3, height // 3
        top_left = ((width - rect_w) // 2, (height - rect_h) // 2)
        bottom_right = (top_left[0] + rect_w, top_left[1] + rect_h)

        cv2.rectangle(frame, top_left, bottom_right, (0, 0, 255), 2)

        roi = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        avg_h = int(np.mean(hsv_roi[:, :, 0]))
        avg_s = int(np.mean(hsv_roi[:, :, 1]))
        avg_v = int(np.mean(hsv_roi[:, :, 2]))

        text = f"Avg HSV: H={avg_h} S={avg_s} V={avg_v}"

        
        target_h, target_s, target_v = 112, 245, 105
        tol_h, tol_s, tol_v = 10, 40, 40  
        
        def in_range(value, target, tol):
            lower = target - tol
            upper = target + tol
            if lower < 0:
                return value >= (180 + lower) or value <= upper  
            if upper > 180:
                return value >= lower or value <= (upper - 180) 
            return lower <= value <= upper

        h_match = in_range(avg_h, target_h, tol_h)
        s_match = (target_s - tol_s) <= avg_s <= (target_s + tol_s)
        v_match = (target_v - tol_v) <= avg_v <= (target_v + tol_v)

        if h_match and s_match and v_match:
            cv2.putText(frame, "Red detected!", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        cv2.putText(frame, text, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame_rgb)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')






@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def add_log(message):
    timestamp = datetime.now().strftime("%d/%B/%Y %I:%M:%S %p")
    full_message = f"{timestamp} - {message}"
    if len(logs) >= 1000:
        logs.pop(0)
    logs.append(full_message)

@app.route('/get_logs')
def get_logs():
    return jsonify(logs=logs)

@app.route('/logs')
def logs_page():
    return render_template('logs.html')

def sorter_loop():
    servo.detach()
    global sorts, current_speed
    print("Sorter Turned ON")
    add_log("Sorter Turned ON")
    led.on()
    
    try:
        while not stop_sorter.is_set():
            dist = sensor.distance
            if dist < 0.1:
                print("Object detected! Moving servo")
                add_log("Object Detected")
                sorts += 1
                servo.value = 1
                time.sleep(current_speed)
                servo.value = 0
                time.sleep(current_speed)
                servo.detach()
            
    finally:
        led.off()
        servo.value = 0
        print("Sorter thread stopped")
        add_log("Sorter Turned OFF")




@app.route('/get_sorts')
def get_sorts():
    return jsonify({'sorts': sorts})

@app.route('/')
def dashboard():
    return render_template('dashboard.html', sorts=sorts, system_status=system_status)

@app.route('/settings')
def settings_page():
    return render_template(
        'settings.html', 
        speed = current_speed,
        speeds = speeds.keys()
        
        
        )

@app.route('/set_speed/<level>')
def set_speed(level):
    global current_speed
    if level in speeds:
        current_speed = speeds[level]
        add_log(f"Speed set to {level}")
        return jsonify({'status': 'ok', 'speed': level})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid speed'}), 400


@app.route('/start', methods=['POST', 'GET'])
def start():
    global system_status, sorter_thread, stop_sorter

    if system_status == "OFF":
        system_status = "ON"
        led.on()
        stop_sorter.clear()
        sorter_thread = threading.Thread(target=sorter_loop)
        sorter_thread.start()
        servo.detach()
        
    else:
        system_status = "OFF"
        stop_sorter.set()
        if sorter_thread:
            sorter_thread.join()
            sorter_thread = None
            servo.detach()
            

    return jsonify({'system_status': system_status})
    



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
