# app.py
from flask import Flask, render_template_string
from flask_socketio import SocketIO
from gpiozero import Motor
import eventlet
import logging

# Enable eventlet monkey patching for better async with gpiozero + flask-socketio
eventlet.monkey_patch()

app = Flask(__name__)

# Enable SocketIO logging for debugging protocol issues
socketio = SocketIO(app, logger=True, engineio_logger=True)

# Configure Flask app logger to show debug logs
logging.basicConfig(level=logging.DEBUG)

# Define motors for your GPIO configuration
right_motor = Motor(forward=17, backward=27, enable=12)
left_motor = Motor(forward=23, backward=22, enable=13)

# Inline HTML with debugging info and joystick
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Robot Joystick Web Control</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://yoannmoinet.github.io/nipplejs/dist/nipplejs.min.js"></script>
    <style>
        body { background:#181818; color:#fff; text-align:center; font-family:sans-serif; }
        #joystick { width:220px; height:220px; margin:40px auto; background:#282828; border-radius:10px; }
        #status { margin-top: 10px; font-size: 14px; color: #6f6; }
        #debug { margin-top:20px; text-align:left; max-width:600px; margin-left:auto; margin-right:auto;
                 background:#222; padding:10px; font-family: monospace; height:120px; overflow:auto; border-radius:5px; }
    </style>
</head>
<body>
    <h2>Raspberry Pi Robot Joystick</h2>
    <div id="joystick"></div>
    <p>Move the joystick to drive the robot.<br>Release to stop.</p>
    <div id="status">Status: <span id="connStatus">Connecting...</span></div>
    <div id="debug"></div>
    <script>
        const debugEl = document.getElementById("debug");
        function logDebug(msg) {
            console.log(msg);
            debugEl.textContent += msg + "\\n";
            debugEl.scrollTop = debugEl.scrollHeight;
        }

        var socket = io();

        socket.on('connect', function() {
            document.getElementById("connStatus").textContent = "Connected!";
            logDebug("Socket connected.");
        });

        socket.on('disconnect', function() {
            document.getElementById("connStatus").textContent = "Disconnected!";
            logDebug("Socket disconnected.");
        });

        socket.on('connect_error', function(err) {
            document.getElementById("connStatus").textContent = "Connect Error!";
            logDebug("Connection error: " + err);
        });

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
            var y = -(data.vector.y || 0); // invert y axis for natural forward/back
            socket.emit('joystick', { x: x, y: y });
            logDebug(`Joystick moved: x=${x.toFixed(2)}, y=${y.toFixed(2)}`);
        });

        joystick.on("end", function() {
            socket.emit('joystick', { x: 0, y: 0 });
            logDebug("Joystick released: stopping motors");
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
    try:
        x = float(data.get('x', 0))
        y = float(data.get('y', 0))

        # Mixing for tank drive: left  = y + x, right = y - x
        left = max(min(y + x, 1), -1)
        right = max(min(y - x, 1), -1)

        set_motor(left_motor, left)
        set_motor(right_motor, right)

        app.logger.debug(f"Joystick data received: x={x:.3f}, y={y:.3f} -> left={left:.3f}, right={right:.3f}")
    except Exception as e:
        app.logger.error(f"Error handling joystick input: {e}", exc_info=True)

@socketio.on_error_default
def default_error_handler(e):
    app.logger.error(f"SocketIO error: {e}", exc_info=True)

if __name__ == '__main__':
    # Run with debug=True if you want auto-reload and Flask debugger (not recommended with eventlet)
    # Use eventlet for asynchronous socket handling
    socketio.run(app, host='0.0.0.0', port=5000)
