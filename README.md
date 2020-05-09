# TSD305 Python Library
## Adapted from [Raspberry Pi Weather Shield Python](https://github.com/TEConnectivity/piweathershield-python)
This is a python library (file?) adapted from the official Weather Shield repo. The original library was having difficulties reading object temperature so I read the datasheet and reprogrammed the library to correctly output ambient temperature and object temperature. Feel free to use this however you need.
# Example Usage
```python
from tsd305 import TSD305
sensor = TSD305(1) #i2c device 1 for newer raspberry pi's
amb_temp, obj_temp = sensor.read_temperature_and_object_temperature()
```