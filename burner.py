from prometheus_client import start_http_server, Summary
import time
import RPi.GPIO as GPIO
import logging
import signal
import sys


BURNER_TIME = Summary('burner_seconds', 'Time spent burning and power cycling since last reset')
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
    while True:
        GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=burner_on, bouncetime=500)
        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()
