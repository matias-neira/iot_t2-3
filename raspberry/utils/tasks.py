import time
from paho.mqtt.client import Client

from utils.data import simulate_accel, simulate_temp, simulate_status

_accel_messages_amount = 0
_temp_messages_amount = 0
_status_messages_amount = 0

async def accel_task(client: Client, enabled: bool, qos: int) -> None:
    global _accel_messages_amount

    while enabled:
        msg_bytes = simulate_accel()

        client.publish("iot/rpi4/accel", msg_bytes, qos=qos)

        _accel_messages_amount += 1
        time.sleep(.02)

async def temp_task(client: Client, enabled: bool, qos: int) -> None:
    global _temp_messages_amount

    while enabled:
        msg_bytes = simulate_temp()

        client.publish("iot/rpi4/temp", msg_bytes, qos=qos)

        _temp_messages_amount += 1
        time.sleep(15)

async def status_task(client: Client) -> None:
    global _status_messages_amount

    while True:
        msg_bytes = simulate_status()

        client.publish("iot/status/rpi4", msg_bytes, qos=1)

        _status_messages_amount += 1
        time.sleep(.1)

async def print_messages_by_topic() -> None:
    while True:
        print(
            "====================\n",
            f"Accel messages: {_accel_messages_amount}\n",
            f"Temp messages: {_temp_messages_amount}\n",
            f"Status messages: {_status_messages_amount}\n"
        )
        time.sleep(10)
