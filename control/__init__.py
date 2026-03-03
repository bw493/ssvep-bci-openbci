"""
Control module for SSVEP BCI pipeline

Includes:
- Arduino serial communication
- Bionic hand control commands
- Simulation mode for testing
"""

from .arduino_control import ArduinoController, send_bci_command

__all__ = [
    'ArduinoController',
    'send_bci_command'
]
