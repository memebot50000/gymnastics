import os
import time
import threading
from flask import Flask, Response, render_template_string, request
from gpiozero import Motor
import pygame  # <--- add pygame import

app = Flask(__name__)

# Motor Initialization
right_motor = Motor(forward=17, backward=27, enable=12)
left_motor = Motor(forward=23, backward=22, enable=13)

# Motor control state
current_throttle = 0.0
current_steering = 0.0
MOTOR_UPDATE_INTERVAL = 0.05  # seconds

# Deadzone logic
DEAD_ZONE = 0.2  # 20% dead zone
def apply_dead_zone(value, dead_zone):
    if abs(value) < dead_zone:
        return 0
    return (value - dead_zone * (1 if value > 0 else -1)) / (1 - dead_zone)

# Motor arming state
motors_armed = False
motors_armed_lock = threading.Lock()

# Global running flag for threads
running = True

# --- Setup for positive speech ---
numberOfThings = 3
positiveThings = []
for r in range(0, numberOfThings):
    positiveThings.append("thing" + str(r) + ".mp3")  # Your mp3 filenames here

def sayPositiveThings():
    """Play a random positive mp3 sound."""
    try:
        sound = pygame.mixer.Sound(random.choice(positiveThings))
        sound.play()
        # Wait for the sound to finish playing
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
    except Exception as e:
        print(f"Error playing sound: {e}")

def positive_speech_loop():
    """Loop that says positive things every 10 minutes."""
    while running:
        # Wait 10 minutes (600 seconds)
        time.sleep(600)
        sayPositiveThings()

# --- Utility Functions ---

def cleanup():
    global running
    running = False
    print("Stopping motors")
    try:
        left_motor.stop()
    except Exception:
        pass
    try:
        right_motor.stop()
    except Exception:
        pass
    # Quit pygame mixer on cleanup
    try:
        pygame.mixer.quit()
    except Exception:
        pass
    print("Cleanup complete")

# --- Threads ---
def motor_control_loop():
    global current_throttle, current_steering, motors_armed
    while running:
        with motors_armed_lock:
            armed = motors_armed
        if not armed:
            left_motor.stop()
            right_motor.stop()
            time.sleep(MOTOR_UPDATE_INTERVAL)
            continue
        # Map joystick values to motor speeds
        throttle = current_throttle  # -1 to 1
        steering = current_steering  # -1 to 1
        left_speed = throttle + steering
        right_speed = throttle - steering
        left_speed = max(-1, min(1, left_speed))
        right_speed = max(-1, min(1, right_speed))
        if left_speed > 0:
            left_motor.forward(left_speed)
        elif left_speed < 0:
            left_motor.backward(-left_speed)
        else:
            left_motor.stop()
        if right_speed > 0:
            right_motor.forward(right_speed)
        elif right_speed < 0:
            right_motor.backward(-right_speed)
        else:
            right_motor.stop()
        time.sleep(MOTOR_UPDATE_INTERVAL)

# --- Flask Endpoints ---
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Robot Control Panel</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.0/nipplejs.min.js"></script>
        <style>
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
                background: #181a20;
                color: #f5f6fa;
                font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
                overflow: hidden;
            }
            body {
                display: flex;
                flex-direction: column;
                height: 100vh;
                width: 100vw;
            }
            #main-content {
                flex: 1 1 auto;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                width: 100vw;
                overflow: hidden;
            }
            #joystick-container {
                z-index: 3;
                width: 140px;
                height: 140px;
                background: rgba(24,26,32,0.85);
                border-radius: 18px;
                box-shadow: 0 4px 32px 0 #000a;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            #joystick {
                width: 120px;
                height: 120px;
                position: relative;
            }
            #arm-switch-container {
                margin-top: 20px;
                display: flex;
                align-items: center;
                gap: 16px;
            }
            .switch {
                position: relative;
                display: inline-block;
                width: 60px;
                height: 34px;
            }
            .switch input {display:none;}
            .slider {
                position: absolute;
                cursor: pointer;
                top: 0; left: 0; right: 0; bottom: 0;
                background: #232a3a;
                border-radius: 34px;
                transition: .4s;
            }
            .slider:before {
                position: absolute;
                content: "";
                height: 26px;
                width: 26px;
                left: 4px;
                bottom: 4px;
                background: #f5f6fa;
                border-radius: 50%;
                transition: .4s;
                box-shadow: 0 2px 8px 0 #0006;
            }
            input:checked + .slider {
                background: linear-gradient(90deg, #4e8cff 0%, #1e3c72 100%);
            }
            input:checked + .slider:before {
                transform: translateX(26px);
                background: #4e8cff;
            }
            #arm-label {
                font-size: 1.1rem;
                font-weight: 500;
                letter-spacing: 0.04em;
            }
        </style>
    </head>
    <body>
        <div id="main-content">
            <div id="joystick-container">
                <div id="joystick"></div>
            </div>
            <div id="arm-switch-container">
                <label class="switch">
                  <input type="checkbox" id="arm-switch">
                  <span class="slider"></span>
                </label>
                <span id="arm-label">Motors Disarmed</span>
            </div>
        </div>
        <script>
            var throttle = 0.0;
            var steering = 0.0;
            var joystick = nipplejs.create({
                zone: document.getElementById('joystick'),
                mode: 'static',
                position: {left: '50%', top: '50%'},
                color: '#4e8cff',
                size: 120
            });
            function sendJoystick(throttle, steering) {
                $.post('/joystick', {throttle: throttle, steering: steering});
            }
            joystick.on('move', function(evt, data) {
                if (data && data.distance) {
                    var angle = data.angle ? data.angle.radian : 0;
                    var dist = Math.min(data.distance, 50);
                    var norm = dist / 50;
                    var x = Math.cos(angle) * norm;
                    var y = Math.sin(angle) * norm;
                    sendJoystick(-y, x);  // throttle inverted Y, steering X
                }
            });
            joystick.on('end', function() {
                sendJoystick(0, 0);
            });
            var armSwitch = document.getElementById('arm-switch');
            var armLabel = document.getElementById('arm-label');
            function setArmState(armed) {
                $.post('/arm', {state: armed ? 'true' : 'false'});
                armLabel.textContent = armed ? 'Motors Armed' : 'Motors Disarmed';
                if (armed) {
                    armLabel.style.color = '#4e8cff';
                } else {
                    armLabel.style.color = '#f5f6fa';
                }
            }
            armSwitch.addEventListener('change', function() {
                setArmState(armSwitch.checked);
            });
            // Initialize arm state as disarmed
            setArmState(false);
        </script>
    </body>
    </html>
    ''')

@app.route('/joystick', methods=['POST'])
def joystick():
    global current_throttle, current_steering
    try:
        throttle = float(request.form.get('throttle', 0.0))
        steering = float(request.form.get('steering', 0.0))
        current_throttle = max(-1, min(1, apply_dead_zone(throttle, DEAD_ZONE)))
        current_steering = max(-1, min(1, apply_dead_zone(steering, DEAD_ZONE)))
    except Exception:
        current_throttle = 0.0
        current_steering = 0.0
    return 'OK'

@app.route('/arm', methods=['POST'])
def arm():
    global motors_armed
    state = request.form.get('state')
    with motors_armed_lock:
        motors_armed = (state == 'true')
    return 'OK'

@app.route('/shutdown', methods=['POST'])
def shutdown():
    cleanup()
    os._exit(0)

if __name__ == '__main__':
    try:
        # Initialize pygame mixer once before threads start
        pygame.mixer.init()

        print("Initializing motors and starting motor control and positive speech loops")

        motor_thread = threading.Thread(target=motor_control_loop, daemon=True)
        motor_thread.start()

        positive_speech_thread = threading.Thread(target=positive_speech_loop, daemon=True)
        positive_speech_thread.start()

        print("Threads started, starting Flask app")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
    finally:
        cleanup()
