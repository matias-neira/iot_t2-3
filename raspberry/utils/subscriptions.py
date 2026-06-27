import paho.mqtt.client as mqtt

from classes.MainWindow import MainWindow

async def subscribe(window: MainWindow) -> None:

    def on_connect(client: mqtt.Client, userdata: None, flags: None, reason_code: int, properties: None):
        print(f"Connected to broker with code: {reason_code}")
        client.subscribe("iot/rpi4/+")
        client.subscribe("iot/status/rpi4")

    def on_message(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage):
        temperature = int.from_bytes(msg.payload[:4], byteorder="little")
        window.update_temperature(temperature)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect("127.0.0.1", 1883, 60)
            client.loop_forever()

        except Exception as e:
            print(f"Error occurred: {e}")

