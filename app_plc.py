import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
import plc


thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "donsky!"
socketio = SocketIO(app, cors_allowed_origins="*")

"""
Background Thread
"""


def background_thread():
    while True:
        #temperature, humidity = dht22_module.get_sensor_readings(),
        temperature = plc.deger_cek(0,0)
        humidity = plc.deger_cek(4,0)
        sensor_readings = {
            "temperature": temperature,
            "humidity": humidity,
        }
        sensor_json = json.dumps(sensor_readings)

        socketio.emit("updateSensorData", sensor_json)
        socketio.sleep(2)
 

"""
Serve root index file
"""


@app.route("/")
def index():
    return render_template("index.html")


"""
Decorator for connect
"""


@socketio.on("connect")
def connect():
    global thread
    print("Client connected")

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
            


"""
Decorator for disconnect
"""


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)


if __name__ == "__main__":
    socketio.run(app, port=5000, host="0.0.0.0", debug=True)
