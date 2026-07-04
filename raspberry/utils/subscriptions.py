import paho.mqtt.client as mqtt
import json

from classes.MainWindow import MainWindow
from proto import sensors_pb2 as pb

async def subscribe(window: MainWindow) -> None:

    def on_connect(client: mqtt.Client, userdata: None, flags: None, reason_code: int, properties: None):
        print(f"Connected to broker with code: {reason_code}")
        client.subscribe("#")

    def on_message(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage):
        topic = msg.topic
        print(f"Received message on topic '{topic}': {msg.payload}")

        if topic == "iot/status/rpi4":
            status = json.loads(msg.payload)
            timestamp = status.get("timestamp")
            status_value = status.get("status")
            window.emit_status_signal(timestamp, status_value)
        
        elif topic.startswith("iot/rpi4/"):
            envelope = pb.SensorEnvelope()
            envelope.ParseFromString(msg.payload)

            if topic == "iot/rpi4/accel":
                accel = envelope.accel
                window.emit_accel_signal(accel.timestamp, accel.ax, accel.ay, accel.az)
            
            elif topic == "iot/rpi4/temp":
                temp = envelope.temp
                window.emit_temp_signal(temp.timestamp, temp.temp)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect("127.0.0.1", 1883, 60)
            client.loop_forever()

        except Exception as e:
            print(f"Error occurred: {e}")

