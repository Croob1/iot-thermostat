import Adafruit_DHT
import time

SENSOR_TYPE = Adafruit_DHT.DHT11
GPIO_PIN_NUMBER = 4

if __name__ == "__main__" :
  start_time = time.time()
  humidity, temperature = Adafruit_DHT.read_retry(
    SENSOR_TYPE, 
    GPIO_PIN_NUMBER
  )
  end_time = time.time()

  print(f"Measured Temp={temperature}°C | Hum={humidity}%")
  print(f"Measurement took {end_time-start_time}s")
