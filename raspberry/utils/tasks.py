import asyncio
from paho.mqtt.client import Client

from classes.Config import Config
from utils.data import simulate_accel, simulate_temp, simulate_status

_accel_messages_amount = 0
_temp_messages_amount = 0
_status_messages_amount = 0

_accel_qos = 0
_temp_qos = 1

_enabled_accel = asyncio.Event()
_enabled_temp = asyncio.Event()

async def update_tasks(event: asyncio.Event) -> None:
    global  _accel_qos, _temp_qos

    config = Config()

    while True:
        accel_config = config.get_sensors_accel_config()
        temp_config = config.get_sensors_temp_config()

        if accel_config.get("enabled", True):
            _enabled_accel.set()
        else:
            _enabled_accel.clear()

        if temp_config.get("enabled", True):
            _enabled_temp.set()
        else:
            _enabled_temp.clear()

        _accel_qos = accel_config.get("qos", 0)
        _temp_qos = temp_config.get("qos", 1)

        await event.wait()
        print("Configuration updated. Reloading...")
        event.clear()
        config.read_config()

async def accel_task(client: Client) -> None:
    global _accel_messages_amount

    while True:
        await _enabled_accel.wait()
        msg_bytes = simulate_accel()

        client.publish("iot/rpi4/accel", msg_bytes, qos=_accel_qos)

        _accel_messages_amount += 1
        await asyncio.sleep(.02)

async def temp_task(client: Client) -> None:
    global _temp_messages_amount

    while True:
        await _enabled_temp.wait()
        msg_bytes = simulate_temp()

        client.publish("iot/rpi4/temp", msg_bytes, qos=_temp_qos)

        _temp_messages_amount += 1
        await asyncio.sleep(15)

async def status_task(client: Client) -> None:
    global _status_messages_amount

    while True:
        msg_bytes = simulate_status()

        client.publish("iot/status/rpi4", msg_bytes, qos=1)

        _status_messages_amount += 1
        await asyncio.sleep(.1)

async def print_messages_by_topic() -> None:
    while True:
        await asyncio.sleep(10)
        print(
            "=========================\n",
            f"Accel messages: {_accel_messages_amount}\n",
            f"Temp messages: {_temp_messages_amount}\n",
            f"Status messages: {_status_messages_amount}\n"
        )
