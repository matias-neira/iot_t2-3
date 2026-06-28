import paho.mqtt.client as mqtt
import asyncio

from classes.Config import Config
from utils.tasks import accel_task, temp_task, status_task, print_messages_by_topic

async def publisher(event: asyncio.Event) -> None:
    
    #count = [0, 0, 0]

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected to broker with code: {reason_code}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect("127.0.0.1", 1883, 60)
    client.loop_start()

    while True:
        config = Config()
        accel_config = config.get_sensors_accel_config()
        temp_config = config.get_sensors_temp_config()
        accel_enabled = accel_config.get("enabled", True)
        temp_enabled = temp_config.get("enabled", True)
        accel_qos = accel_config.get("qos", 0)
        temp_qos = temp_config.get("qos", 1)


        tasks = asyncio.gather(
            accel_task(client, accel_enabled, accel_qos),
            temp_task(client, temp_enabled, temp_qos),
            status_task(client),
            print_messages_by_topic()
        )

        await event.wait()
        event.clear()
