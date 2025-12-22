import logging
import time

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

_logger = logging.getLogger(__name__)

def main() -> None:
    while True:
        _logger.info(f"Here {time.time()}")
        time.sleep(1)

