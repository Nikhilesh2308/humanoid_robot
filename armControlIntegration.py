#controlling the motors with enabling signal from another raspberry pi
from gpiozero import OutputDevice
import threading
import time
import socket
import json

class StepperMotor:
    def __init__(self, pin1, pin2, pin3, pin4, enable_pin):
        """
        Initialize stepper motor with 4 GPIO pins and an enable pin
        """
        self.pins = [
            OutputDevice(pin1),
            OutputDevice(pin2),
            OutputDevice(pin3),
            OutputDevice(pin4)
        ]
        
        # Enable pin to control power to the motor
        self.enable_pin = OutputDevice(enable_pin, active_high=False)  # Active low enable
        
        # Motor specifications
        self.DEG_PER_STEP = 1.8
        self.STEPS_PER_REVOLUTION = int(360 / self.DEG_PER_STEP)
        
        # Initially disable the motor
        self.disable()
    
    def enable(self):
        """
        Enable the motor (provide power)
        """
        self.enable_pin.on()  # For active low enable pin, on() means enable
        time.sleep(0.01)  # Short delay to ensure the enable takes effect
    
    def disable(self):
        """
        Disable the motor (cut power)
        """
        self.enable_pin.off()  # For active low enable pin, off() means disable
    
    def _step_sequence(self):
        """
        Define full-step sequence
        """
        return [
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1)
        ]
    
    def rotate(self, angle, direction='clockwise', delay=0.01):
        """
        Rotate the stepper motor to a specific angle
        
        :param angle: Degrees to rotate
        :param direction: 'clockwise' or 'counterclockwise'
        :param delay: Time between steps
        """
        # Enable the motor before rotation
        self.enable()
        
        # Calculate number of steps
        sequence = self._step_sequence()
        steps = int((angle / 360) * self.STEPS_PER_REVOLUTION * (len(sequence)))
        
        # Determine sequence direction
        if direction == 'counterclockwise':
            sequence = list(reversed(sequence))
        
        # Perform rotation
        for _ in range(steps):
            for step in sequence:
                for i, value in enumerate(step):
                    if value:
                        self.pins[i].on()
                    else:
                        self.pins[i].off()
                time.sleep(delay)
        
        # Ensure all pins are off after rotation
        for pin in self.pins:
            pin.off()
            
        # Disable the motor after rotation to save power
        self.disable()

def rotate_motor(motor, angle, direction):
    """
    Helper function for threading motor rotation
    """
    motor.rotate(angle, direction)

class MotorController:
    def __init__(self, host='0.0.0.0', port=5000):
        """
        Initialize the motor controller server to receive signals
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
        # Initialize motors with enable pins
        # First motor pins + enable pin
        self.motor1 = StepperMotor(23, 24, 27, 22, 18)# last pin is enable pin  
        # Second motor pins + enable pin
        self.motor2 = StepperMotor(5, 6, 16, 17, 12)    
    4 
    def start_server(self):
        """
        Start the server to listen for incoming signals
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"Server started on {self.host}:{self.port}")
        print("Waiting for signals from the remote Raspberry Pi...")
        
        try:
            while self.running:
                client_socket, address = self.server_socket.accept()
                print(f"Connected to client at {address}")
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def handle_client(self, client_socket):
        """
        Handle communication with a connected client
        """
        try:
            while True:
                # Receive data from the client
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Process the received command
                self.process_command(data)
                
                # Send acknowledgment
                client_socket.send(b'{"status": "ok"}')
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def process_command(self, data):
        """
        Process the command received from the remote Raspberry Pi
        """
        try:
            command = json.loads(data.decode('utf-8'))
            
            # Extract command parameters
            action = command.get('action')
            
            if action == 'rotate':
                motor_id = command.get('motor', 'both')
                angle = command.get('angle', 0)
                direction = command.get('direction', 'clockwise')
                
                print(f"Rotating motor {motor_id} {angle} degrees {direction}")
                
                if motor_id == 'both':
                    # Create threads for simultaneous rotation
                    thread1 = threading.Thread(target=rotate_motor, args=(self.motor1, angle, direction))
                    thread2 = threading.Thread(target=rotate_motor, args=(self.motor2, angle, direction))
                    
                    thread1.start()
                    thread2.start()
                    
                    thread1.join()
                    thread2.join()
                    
                elif motor_id == '1':
                    self.motor1.rotate(angle, direction)
                    
                elif motor_id == '2':
                    self.motor2.rotate(angle, direction)
            
            elif action == 'enable':
                motor_id = command.get('motor', 'both')
                
                if motor_id == 'both':
                    self.motor1.enable()
                    self.motor2.enable()
                    print("Both motors enabled")
                elif motor_id == '1':
                    self.motor1.enable()
                    print("Motor 1 enabled")
                elif motor_id == '2':
                    self.motor2.enable()
                    print("Motor 2 enabled")
            
            elif action == 'disable':
                motor_id = command.get('motor', 'both')
                
                if motor_id == 'both':
                    self.motor1.disable()
                    self.motor2.disable()
                    print("Both motors disabled")
                elif motor_id == '1':
                    self.motor1.disable()
                    print("Motor 1 disabled")
                elif motor_id == '2':
                    self.motor2.disable()
                    print("Motor 2 disabled")
                    
            elif action == 'pattern':
                pattern_type = command.get('type', 'default')
                
                if pattern_type == 'default':
                    self._run_default_pattern()
                elif pattern_type == 'alternate':
                    self._run_alternate_pattern()
            
            print("Command execution completed")
            
        except json.JSONDecodeError:
            print("Error: Invalid JSON command received")
        except Exception as e:
            print(f"Error processing command: {e}")
    
    def _run_default_pattern(self):
        """
        Run the default motor pattern
        """
        # Rotate both motors 70 degrees
        print("Running default pattern: Rotating both motors 70 degrees")
        
        thread1 = threading.Thread(target=rotate_motor, args=(self.motor1, 5, 'clockwise'))
        thread2 = threading.Thread(target=rotate_motor, args=(self.motor2, 5, 'counterclockwise'))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Pause for 1 second
        print("Pausing for 1 second")
        time.sleep(1)
        
        # Return both motors to starting position
        print("Returning motors to starting position")
        thread1 = threading.Thread(target=rotate_motor, args=(self.motor1, 5, 'counterclockwise'))
        thread2 = threading.Thread(target=rotate_motor, args=(self.motor2, 5, 'clockwise'))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
    
    def _run_alternate_pattern(self):
        """
        Run an alternate motor pattern
        """
        # First motor rotates
        print("Running alternate pattern: Motor 1 rotates")
        self.motor1.rotate(90, 'clockwise')
        
        # Pause briefly
        time.sleep(0.5)
        
        # Then second motor rotates
        print("Motor 2 rotates")
        self.motor2.rotate(90, 'clockwise')
        
        # Pause
        time.sleep(1)
        
        # Both return together
        print("Both motors return together")
        thread1 = threading.Thread(target=rotate_motor, args=(self.motor1, 5, 'counterclockwise'))
        thread2 = threading.Thread(target=rotate_motor, args=(self.motor2, 5, 'counterclockwise'))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()

def main():
    try:
        # Create and start the motor controller
        controller = MotorController()
        controller.start_server()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
