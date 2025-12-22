#!/usr/bin/env python

from abc import ABC, abstractmethod

from queue import Queue, Empty
from threading import Thread, Timer

import enum
from enum import Enum

import time
import logging

_logger = logging.getLogger(__name__)

class DoorCommand(Enum):
    CANCEL = enum.auto()
    ACTUATE = enum.auto()
    RELEASE = enum.auto()

class DoorControllerInterface(ABC):
    @abstractmethod
    def actuate(self, release_after: float = None) -> None:
        pass

    @abstractmethod
    def release(self) -> None:
        pass

    @abstractmethod
    def is_actuated(self) -> bool:
        pass

class VirtualDoorController(DoorControllerInterface):
    def __init__(self):
        self.actuated: bool = False
        self.delayed_releaser = Timer(1.0, self.release)

    def actuate(self, release_after: float = None) -> None:
        self.actuated = True
        _logger.info("MOCK: Door actuated")
        if release_after is not None and release_after > 0.0:
            self.delayed_releaser.cancel()
            self.delayed_releaser = Timer(release_after, lambda: self.release())
            self.delayed_releaser.start()
        else:
            self.delayed_releaser.cancel()

    def release(self):
        _logger.info("MOCK: Door released")
        self.actuated = False
        self.delayed_releaser.cancel()

    def is_actuated(self) -> bool:
        return self.actuated

class DoorController(DoorControllerInterface):
    def __init__(self, gpio_bcm_pin: int = 18):
        import RPi.GPIO as GPIO
        self.gpio_bcm_pin = gpio_bcm_pin
        self.actuated = False

        self.command_queue = Queue()
        self.thread = Thread(target=self.thread_worker, daemon=True)
        self.thread.start()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_bcm_pin, GPIO.OUT)
        GPIO.output(self.gpio_bcm_pin, GPIO.HIGH)

        self.delayed_releaser = Timer(1.0, self.release)

    def thread_worker(self):
        import RPi.GPIO as GPIO
        while True:
            command = self.command_queue.get()
            if command == DoorCommand.CANCEL:
                break
            if command == DoorCommand.ACTUATE:
                GPIO.output(self.gpio_bcm_pin, GPIO.LOW)
                self.actuated = True
                _logger.info("SERVICED: Door ACTUATE")
            if command == DoorCommand.RELEASE:
                GPIO.output(self.gpio_bcm_pin, GPIO.HIGH)
                self.actuated = False
                _logger.info("SERVICED: Door RELEASE")

    def __del__(self):
        self.thread.join()

    def actuate(self, release_after: float = None):
        _logger.info(f"ENQUEUED: Door Actuation - release_after={release_after}")

        self.command_queue.put(DoorCommand.ACTUATE)
        if release_after is not None and release_after > 0.0:
            self.delayed_releaser.cancel()
            self.delayed_releaser = Timer(release_after, lambda: self.command_queue.put(DoorCommand.RELEASE))
            self.delayed_releaser.start()
        else:
            self.delayed_releaser.cancel()

    def release(self):
        self.command_queue.put(DoorCommand.RELEASE)
        self.delayed_releaser.cancel()

    def is_actuated(self) -> bool:
        return self.actuated

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    _logger.info("Doorman Demo!")
    door = DoorController()

    try:
        while True:
            prompt = input(f"Choice of inputs: {DoorCommand.__members__.keys()} - ")
            try:
                command = getattr(DoorCommand, prompt.strip())
            except AttributeError:
                _logger.info(f"Command '{prompt}' was not recognized.")
                continue
            if command == DoorCommand.CANCEL:
                break
            if command == DoorCommand.ACTUATE:
                door.actuate(3.0)
            if command == DoorCommand.RELEASE:
                door.release()
    except KeyboardInterrupt:
        _logger.info("Ctrl+C caught - exiting.")
        pass

    _logger.info("Exited.")

if __name__ == "__main__":
    main()
