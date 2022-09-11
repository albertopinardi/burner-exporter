from prometheus_client import start_http_server, Summary, Gauge
import time
import RPi.GPIO as GPIO
import logging
import signal
import sys
from w1thermsensor import W1ThermSensor, Sensor

BURNER_TIME = Summary('burner_seconds', 'Time spent burning and power cycling since last reset')
OUTDOOR_TEMP = Gauge('outdoor_temperature','Outdoor Temperature near the house at 2.5mt from the ground')
OUTDOOR_HWID = "3c01f0961f04"
BOILER_TEMP = Gauge('boiler_temperature','Boiler water Temperature As-Is')
BOILER_HWID = "3c01f09606e5"
BUTTON_GPIO = 16


def setup_logger():
    """Setup the logger"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


@BURNER_TIME.time()
def burner_on(*args):
    """Control how long the burner is on"""
    logger.debug(f"Function Called: {args}")
    start = time.perf_counter_ns()
    while GPIO.input(BUTTON_GPIO) is GPIO.LOW:
        time.sleep(1)
    stop = time.perf_counter_ns()
    duration = stop - start
    logger.debug(f"Burner on for {duration / 1e9 } seconds")


def gather_temperature(sensor_id, *args):
    """Read temperature from Sensors"""
    logger.debug(f"gather_temperature called: {args}")
    # Issue the conv_temp command
    sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=sensor_id)
    temperature_in_celsius = sensor.get_temperature()
    # return all values from the bus
    return temperature_in_celsius


def signal_handler(sig, frame):
    """Handle the SIGINT signal"""
    logger.info("Shutting down")
    GPIO.cleanup()
    sys.exit(0)


if __name__ == '__main__':
    logger = setup_logger()
    logger.debug("Starting up the server")
    start_http_server(8000)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    logger.debug("Add event detector")
    signal.signal(signal.SIGINT, signal_handler)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.RISING, callback=burner_on, bouncetime=1000)
    while True:
        BOILER_TEMP.set(gather_temperature(BOILER_HWID))
        OUTDOOR_TEMP.set(gather_temperature(OUTDOOR_HWID))
        time.sleep(5)
