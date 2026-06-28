import time
import json
from paho.mqtt.client import Client

from .data import simulate_accel, simulate_temp, simulate_status

_accel_messages_amount = 0
_temp_messages_amount = 0
_status_messages_amount = 0

async def accel_task(client: Client, enabled: bool, qos: int) -> None:
    global _accel_messages_amount

    while enabled:
        accel = simulate_accel()
        msg_bytes = json.dumps(accel)

        client.publish("iot/rpi4/accel", msg_bytes, qos=qos)

        _accel_messages_amount += 1
        time.sleep(.02)

async def temp_task(client: Client, enabled: bool, qos: int) -> None:
    global _temp_messages_amount

    while enabled:
        temp = simulate_temp()
        msg_bytes = json.dumps(temp)

        client.publish("iot/rpi4/temp", msg_bytes, qos=qos)

        _temp_messages_amount += 1
        time.sleep(15)

async def status_task(client: Client) -> None:
    global _status_messages_amount

    while True:
        status = simulate_status()
        msg_bytes = json.dumps(status)

        client.publish("iot/status/rpi4", msg_bytes, qos=1)

        _status_messages_amount += 1
        time.sleep(.1)

async def print_messages_by_topic() -> None:
    while True:
        print(
            "====================", "\n",
            f"Accel messages: {_accel_messages_amount}", "\n",
            f"Temp messages: {_temp_messages_amount}", "\n",
            f"Status messages: {_status_messages_amount}"
        )
        time.sleep(10)
