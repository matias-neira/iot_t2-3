# Tarea 2-3 – Diseño de Sistemas IoT
Universidad de Chile – DCC  
Profesor: Luciano Radrigán F.  
Ayudante: Lucas Llort  
Grupo: 
- Matías Neira

**Demostración en video:** https://drive.google.com/file/d/1Wst2ql_CXg_fWsrSN2SU_fb23bBw7p8S/view?usp=sharing

**Aclaraciones**
- La tarea la realicé solo, ya que mi compañero no ha contestado mis mensajes en 3 semanas.
- En la demostración se utilizo la rama PyQt6, debido a que la raspberry pi 5 tenía problemas instalando PyQt5, en esta rama (main) se encuentra la versión con PyQt5

## 1 Descripción de la Arquitectura del Sistema

El sistema está compuesto por:

- **Raspberry Pi 5**: actúa como punto de acceso Wi‑Fi (AP), servidor DHCP, broker MQTT (Mosquitto), publicador de datos simulados y aloja la interfaz gráfica (PyQt5).
- **ESP32**: suscriptor MQTT que se conecta a la red Wi‑Fi de la Raspberry Pi, recibe los mensajes publicados y los imprime en pantalla.

## 2 Instrucciones de instalación del AP, DHCP y Mosquitto
### 2.1 Hostapd
```bash
sudo hostapd /raspberry/network/hostapd.conf
```

### 2.2 Dnsmasq
```bash
sudo dnsmasq -C /raspberry/network/dnsmasq.conf -d
```

### 2.3 Mosquitto
```bash
sudo mosquitto -c /raspberry/network/mosquitto.conf
```

## 3 Comandos para generar el código Protobuf (Python y nanopb)
### 3.1 Python
```bash
protoc --python_out=raspberry/proto proto/sensors.proto
```

### 3.2 Nanopb
```bash
protoc -opacket.pb proto/sensors.proto
nanopb_generator packet.pb
```

**Nota:** El archivo `packet.pb.c` generado por nanopb debe ser copiado a la carpeta `esp32-sub/main/proto` para que el ESP32 pueda compilar correctamente. 

## 4 Instrucciones de compilación y ejecucióin del ESP32
```bash
idf.py set-target esp32
idf.py flash
idf.py monitor
```

## 5 Instrucciones de compilación y ejecución de la interfaz gráfica
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd raspberry
python3 main.py
```

## 6 Red Wifi
SSID: IoT_Grupo1
Password: password1234
