import json

class Config:

    __FILE_PATH = "raspberry/config.json"
    __DEFAULT_CONFIG = {
        "wifi_ssid": "IoT_Grupo1",
        "wifi_password": "password1234",
        "mqtt_broker_uri": "mqtt://192.168.10.1:1883",
        "sensors": {
            "accel": {
                "enabled": True,
                "qos": 0,
                "rate_hz": 50
            },
            "temp": {
                "enabled": True,
                "qos": 1,
                "rate_hz": 0.067
            }
        }
    }

    def __init__(self) -> None:
        try:
            with open(self.__FILE_PATH, "r") as f:
                config = json.load(f)

        except:
            config = self.__DEFAULT_CONFIG
            with open(self.__FILE_PATH, "w") as f:
                json.dump(config, f, indent=4)
        self.__config = config

    def get_wifi_ssid(self) -> str: return self.__config.get("wifi_ssid", "IoT_Grupo1")

    def get_wifi_password(self) -> str: return self.__config.get("wifi_password", "password1234")

    def get_mqtt_broker_uri(self) -> str: return self.__config.get("mqtt_broker_uri", "mqtt://192.168.10.1:1883")

    def get_sensors_config(self) -> dict[str, dict[str]]: return self.__config.get("sensors", self.__DEFAULT_CONFIG.get("sensors"))

    def save_config(self, sensors_config: dict) -> None:
        self.__config["sensors"] = sensors_config
        with open(self.__FILE_PATH, "w") as f:
            json.dump(self.__config, f, indent=4)

    def reset_to_default(self) -> None:
        self.__config = self.__DEFAULT_CONFIG.copy()
        with open(self.__FILE_PATH, "w") as f:
            json.dump(self.__config, f, indent=4)
