import math
import random
import time
import json

import proto.sensors_pb2 as pb

_ACCEL_RANGE_G = 16.0
_ATTENUATION = .7
_TEMP_MIN = 20.0
_TEMP_MAX = 30.0

_phase = .0
_temp = 25.0

def _timestamp_ms() -> int:
	return time.monotonic_ns() // 1_000_000

def simulate_accel() -> str:
    global _phase
    
    _phase += 0.01
    main_val = _ACCEL_RANGE_G * math.sin(_phase) + random.random() - .5
    accel = pb.AccelSample()
    accel.timestamp_ms = _timestamp_ms()
    accel.ax = main_val
    accel.ay = main_val * _ATTENUATION + (random.random() - .5) * .5
    accel.az = main_val * _ATTENUATION + (random.random() - .5) * .5
    envelope = pb.SensorEnvelope()
    envelope.source_id = "rpi4"
    envelope.accel.CopyFrom(accel)
    return envelope.SerializeToString()

def simulate_temp() -> str:
      global _temp
      
      delta = (random.random() - .5) * .4
      _temp += delta
      if _temp < _TEMP_MIN: _temp = _TEMP_MIN
      if _temp > _TEMP_MAX: _temp = _TEMP_MAX
      temp = pb.TempSample()
      temp.timestamp_ms = _timestamp_ms()
      temp.temperature = _temp
      envelope = pb.SensorEnvelope()
      envelope.source_id = "rpi4"
      envelope.temp.CopyFrom(temp)
      return envelope.SerializeToString()

def simulate_status() -> str:
      status = {
            "timestamp": _timestamp_ms(),
            "status": 0
      }
      return json.dumps(status).replace(" ", "")
