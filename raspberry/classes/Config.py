import json

class Config:

    __FILE_PATH = "config.json"
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
        self.__config = {}
        self.read_config()

    def get_wifi_ssid(self) -> str: return self.__config.get("wifi_ssid", "IoT_Grupo1")

    def get_wifi_password(self) -> str: return self.__config.get("wifi_password", "password1234")

    def get_mqtt_broker_uri(self) -> str: return self.__config.get("mqtt_broker_uri", "mqtt://192.168.10.1:1883")

    def __get_sensors_config(self) -> dict[str, dict[str]]: return self.__config.get("sensors", self.__DEFAULT_CONFIG.get("sensors"))

    def get_sensors_accel_config(self) -> dict[str]: return self.__get_sensors_config().get("accel", self.__DEFAULT_CONFIG["sensors"]["accel"])

    def get_sensors_temp_config(self) -> dict[str]: return self.__get_sensors_config().get("temp", self.__DEFAULT_CONFIG["sensors"]["temp"])

    def save_config(self, sensors_config: dict) -> None:
        self.__config["sensors"] = sensors_config
        with open(self.__FILE_PATH, "w") as f:
            json.dump(self.__config, f, indent=4)

    def reset_to_default(self) -> None:
        self.__config = self.__DEFAULT_CONFIG.copy()
        with open(self.__FILE_PATH, "w") as f:
            json.dump(self.__config, f, indent=4)

    def read_config(self) -> dict:
        try:
            with open(self.__FILE_PATH, "r") as f:
                config = json.load(f)

        except:
            config = self.__DEFAULT_CONFIG
            with open(self.__FILE_PATH, "w") as f:
                json.dump(config, f, indent=4)
        self.__config = config
