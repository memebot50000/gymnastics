# app.py
from flask import Flask, render_template_string
from flask_socketio import SocketIO
from gpiozero import Motor
import eventlet

app = Flask(__name__)
socketio = SocketIO(app)

# Define motors for your GPIO configuration
right_motor = Motor(forward=17, backward=27, enable=12)
left_motor = Motor(forward=23, backward=22, enable=13)

# Inline HTML for joystick and websocket control
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smilebot Control</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://yoannmoinet.github.io/nipplejs/dist/nipplejs.min.js"></script>
</head>
<body style="background:#181818;color:#fff;text-align:center;font-family:sans-serif;">
    <h2>Raspberry Pi Robot Joystick</h2>
    <div id="joystick" style="width:220px; height:220px; margin:40px auto;background:#282828;border-radius:10px;"></div>
    <p>Move the joystick to drive the robot.<br>Release to stop.</p>
    <script>
        var socket = io();
        var options = {
            zone: document.getElementById("joystick"),
            mode: "static",
            position: { left: "50%", top: "50%" },
            size: 180,
            color: "#40f040"
        };
        var joystick = nipplejs.create(options);

        joystick.on("move", function(evt, data) {
            var x = (data.vector.x || 0);
            var y = -(data.vector.y || 0); // Invert Y axis
            socket.emit('joystick', { x: x, y: y });
        });
        joystick.on("end", function() {
            socket.emit('joystick', { x: 0, y: 0 });
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

def set_motor(motor, value):
    if value > 0:
        motor.forward(min(1, value))
    elif value < 0:
        motor.backward(min(1, -value))
    else:
        motor.stop()

@socketio.on('joystick')
def handle_joystick(data):
    x = float(data.get('x', 0))
    y = float(data.get('y', 0))
    # Mixing for tank drive: left  = y + x, right = y - x
    left = max(min(y + x, 1), -1)
    right = max(min(y - x, 1), -1)
    set_motor(left_motor, left)
    set_motor(right_motor, right)

if __name__ == '__main__':
    # Use eventlet for SocketIO
    socketio.run(app, host='0.0.0.0', port=5000)
