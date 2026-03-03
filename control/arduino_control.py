"""
Arduino control module for bionic hand actuation
Handles serial communication with Arduino for motor control
"""

import serial
import time
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import ARDUINO_PORT, ARDUINO_BAUDRATE, COMMANDS


class ArduinoController:
    """
    Controller for Arduino-based bionic hand
    
    Sends serial commands to control thumb and finger motors
    """
    
    def __init__(self, 
                 port: str = ARDUINO_PORT,
                 baudrate: int = ARDUINO_BAUDRATE,
                 timeout: float = 1.0,
                 simulation_mode: bool = False):
        """
        Initialize Arduino controller
        
        Parameters:
        -----------
        port : str
            Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
        baudrate : int
            Communication baudrate
        timeout : float
            Read timeout in seconds
        simulation_mode : bool
            If True, simulate commands without actual serial connection
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.simulation_mode = simulation_mode
        self.serial_connection = None
        self.is_connected = False
        
        if not simulation_mode:
            self.connect()
        else:
            print(f"Arduino Controller initialized in SIMULATION MODE")
            self.is_connected = True
    
    def connect(self) -> bool:
        """
        Establish serial connection with Arduino
        
        Returns:
        --------
        success : bool
            True if connection successful
        """
        try:
            print(f"Connecting to Arduino on {self.port}...")
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            # Wait for Arduino to reset
            time.sleep(2)
            
            self.is_connected = True
            print(f"✓ Connected to Arduino on {self.port}")
            return True
            
        except serial.SerialException as e:
            print(f"✗ Failed to connect to Arduino: {e}")
            print(f"  Make sure Arduino is connected to {self.port}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """
        Close serial connection
        """
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            print("Arduino connection closed")
    
    def send_command(self, command: str) -> bool:
        """
        Send command to Arduino
        
        Parameters:
        -----------
        command : str
            Command to send ('OPEN' or 'CLOSE')
            
        Returns:
        --------
        success : bool
            True if command sent successfully
        """
        if command not in COMMANDS:
            print(f"✗ Unknown command: {command}")
            return False
        
        cmd_byte = COMMANDS[command]
        
        if self.simulation_mode:
            print(f"[SIMULATION] Sending command: {command} ({cmd_byte})")
            return True
        
        if not self.is_connected:
            print("✗ Not connected to Arduino")
            return False
        
        try:
            self.serial_connection.write(cmd_byte)
            print(f"✓ Sent command: {command}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send command: {e}")
            return False
    
    def open_hand(self) -> bool:
        """
        Send OPEN command to bionic hand
        
        Returns:
        --------
        success : bool
        """
        return self.send_command('OPEN')
    
    def close_hand(self) -> bool:
        """
        Send CLOSE command to bionic hand
        
        Returns:
        --------
        success : bool
        """
        return self.send_command('CLOSE')
    
    def read_response(self, max_lines: int = 10) -> list:
        """
        Read response from Arduino (if any)
        
        Parameters:
        -----------
        max_lines : int
            Maximum number of lines to read
            
        Returns:
        --------
        responses : list
            List of response strings
        """
        if self.simulation_mode:
            return ["[SIMULATION] No response in simulation mode"]
        
        if not self.is_connected:
            return []
        
        responses = []
        try:
            while self.serial_connection.in_waiting > 0 and len(responses) < max_lines:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    responses.append(line)
                    print(f"Arduino: {line}")
        except Exception as e:
            print(f"Error reading response: {e}")
        
        return responses
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def send_bci_command(command: str, 
                     controller: Optional[ArduinoController] = None,
                     simulation: bool = True):
    """
    Send BCI classification result to Arduino
    
    Parameters:
    -----------
    command : str
        Classified command ('OPEN' or 'CLOSE')
    controller : ArduinoController, optional
        Existing controller instance
    simulation : bool
        Whether to use simulation mode
    """
    if controller is None:
        # Create temporary controller
        with ArduinoController(simulation_mode=simulation) as ctrl:
            ctrl.send_command(command)
    else:
        controller.send_command(command)


if __name__ == "__main__":
    print("Arduino Control Module")
    print("======================\n")
    
    # Test in simulation mode
    print("Testing in simulation mode...")
    with ArduinoController(simulation_mode=True) as ctrl:
        ctrl.open_hand()
        time.sleep(1)
        ctrl.close_hand()
    
    print("\nModule loaded successfully")
    print(f"Default port: {ARDUINO_PORT}")
    print(f"Default baudrate: {ARDUINO_BAUDRATE}")
    print(f"Available commands: {list(COMMANDS.keys())}")
