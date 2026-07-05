import paho.mqtt.client as mqtt
import json
import asyncio

from classes.MainWindow import MainWindow
from proto import sensors_pb2 as pb

async def subscribe(window: MainWindow) -> None:

    def on_connect(client: mqtt.Client, userdata: None, flags: None, reason_code: int, properties: None):
        print(f"Reading from broker with code: {reason_code}")
        client.subscribe("#")

    def on_message(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage):
        topic = msg.topic
        print(f"Received message on topic '{topic}': {msg.payload}")

        if topic == "iot/status/rpi4":
            status: dict = json.loads(msg.payload)
            timestamp = status.get("timestamp")
            status_value = status.get("status")
            window.emit_status_signal(timestamp, status_value)
        
        elif topic.startswith("iot/rpi4/"):
            envelope = pb.SensorEnvelope()
            envelope.ParseFromString(msg.payload)

            if topic == "iot/rpi4/accel":
                accel = envelope.payload
                window.emit_accel_signal(accel.timestamp_ms, accel.ax, accel.ay, accel.az)
            
            elif topic == "iot/rpi4/temp":
                temp = envelope.payload
                window.emit_temp_signal(temp.timestamp_ms, temp.temperature)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    while window.is_alive():
        try:
            client.connect("192.168.10.1", 1883, 60)
            client.loop_start()

            await window.wait_for_close()

        except Exception as e:
            print(f"Error occurred: {e}")

        finally:
            client.loop_stop()
            client.disconnect()
            await asyncio.sleep(5)

async def update_status(window: MainWindow) -> None:
    while window.is_alive():
        window.emit_update_status_signal()
        await asyncio.sleep(1)
