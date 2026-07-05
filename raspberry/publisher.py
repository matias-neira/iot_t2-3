import paho.mqtt.client as mqtt
import asyncio

from utils.tasks import accel_task, temp_task, status_task, print_messages_by_topic, update_tasks

async def publisher(event: asyncio.Event) -> None:

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Publishing in broker with code: {reason_code}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect("192.168.10.1", 1883, 60)
    client.loop_start()

    try:
        await asyncio.gather(
            update_tasks(event),
            accel_task(client),
            temp_task(client),
            status_task(client),
            print_messages_by_topic()            
        )
    
    except KeyboardInterrupt:
        print("Publisher interrupted. Stopping...")
