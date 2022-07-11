from random import random
from prometheus_client import start_http_server, Summary
import time
import logging
import sys

BURNER_CYCLES = Summary('fake_burner_cycles', 'Time spent burning and power cycling since last reset')


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


@BURNER_CYCLES.time()
def burner_on(*args):
    logger.debug(f"Function Called: {args}")
    start = time.perf_counter_ns()
    time.sleep(random()*100)
    stop = time.perf_counter_ns()
    duration = stop - start
    logger.info(f"Burner on for {duration / 1e9 } seconds")
    time.sleep(random()*100)


if __name__ == '__main__':
    logger = setup_logger()
    # Start up the server to expose the metrics.
    logger.debug("Starting up the server")
    start_http_server(8000)
    logger.debug("Add event detector")
    while True:
        burner_on()
