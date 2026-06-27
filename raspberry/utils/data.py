import math
import random
import time

_ACCEL_RANGE_G = 16.0
_ATTENUATION = .7
_TEMP_MIN = 20.0
_TEMP_MAX = 30.0

_phase = .0
_temp = 25.0

def _timestamp_ms() -> int:
	return time.monotonic_ns() // 1_000_000

def simulate_accel() -> dict[str]:
    global _phase
    _phase += 0.01
    main_val = _ACCEL_RANGE_G * math.sin(_phase) + random.random() - .5
    return {
          "timestamp": _timestamp_ms(),
          "ax": main_val,
          "ay": main_val * _ATTENUATION + (random.random() - .5) * .5,
          "az": main_val * _ATTENUATION + (random.random() - .5) * .5
    }

def simulate_temp() -> dict[str]:
      global _temp
      delta = (random.random() - .5) * .4
      _temp += delta
      if _temp < _TEMP_MIN: _temp = _TEMP_MIN
      if _temp > _TEMP_MAX: _temp = _TEMP_MAX
      return {
            "timestamp": _timestamp_ms(),
            "temp": _temp
      }

def simulate_status() -> dict[str]:
      return {
            "timestamp": _timestamp_ms(),
            "status": 0
      }
