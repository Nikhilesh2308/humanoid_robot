#to send the data singal through ip address
import socket
import json
import time

class MotorSignalSender:
    def __init__(self, target_ip, target_port=5000):
        """
        Initialize the signal sender to control motors on another Raspberry Pi
        
        :param target_ip: IP address of the Raspberry Pi with motors
        :param target_port: Port the motor controller is listening on
        """
        self.target_ip = target_ip
        self.target_port = target_port
    
    def send_command(self, command):
        """
        Send a command to the motor controller
        
        :param command: Dictionary containing the command
        :return: True if successful, False otherwise
        """
        try:
            # Create a socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target_ip, self.target_port))
            
            # Convert command to JSON and send
            json_command = json.dumps(command).encode('utf-8')
            s.send(json_command)
            
            # Wait for acknowledgment
            response = s.recv(1024)
            
            # Close the connection
            s.close()
            
            # Parse the response
            response_data = json.loads(response.decode('utf-8'))
            return response_data.get('status') == 'ok'
            
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def rotate_motor(self, motor_id, angle, direction='clockwise'):
        """
        Send a command to rotate a specific motor
        
        :param motor_id: '1', '2', or 'both'
        :param angle: Angle in degrees
        :param direction: 'clockwise' or 'counterclockwise'
        :return: True if successful, False otherwise
        """
        command = {
            'action': 'rotate',
            'motor': motor_id,
            'angle': angle,
            'direction': direction
        }
        return self.send_command(command)
    
    def enable_motor(self, motor_id='both'):
        """
        Send a command to enable a specific motor
        
        :param motor_id: '1', '2', or 'both'
        :return: True if successful, False otherwise
        """
        command = {
            'action': 'enable',
            'motor': motor_id
        }
        return self.send_command(command)
    
    def disable_motor(self, motor_id='both'):
        """
        Send a command to disable a specific motor
        
        :param motor_id: '1', '2', or 'both'
        :return: True if successful, False otherwise
        """
        command = {
            'action': 'disable',
            'motor': motor_id
        }
        return self.send_command(command)
    
    def run_pattern(self, pattern_type='default'):
        """
        Send a command to run a predefined pattern
        
        :param pattern_type: 'default' or 'alternate'
        :return: True if successful, False otherwise
        """
        command = {
            'action': 'pattern',
            'type': pattern_type
        }
        return self.send_command(command)

def main():
    # Replace with the actual IP address of your motor controller Raspberry Pi
    MOTOR_CONTROLLER_IP = '000.00.00.0'  # Example IP - use the actual IP
    
    # Create the signal sender
    sender = MotorSignalSender(MOTOR_CONTROLLER_IP)
    
    # Example sequences
    try:
        print("Sending commands to control motors")
        
        # Enable both motors
        print("Enabling motors...")
        if sender.enable_motor('both'):
            print("Motors enabled successfully")
        else:
            print("Failed to enable motors")
        
        # Wait 1 second
        time.sleep(1)
        
        # Run the default pattern
        print("Running default pattern...")
        if sender.run_pattern('default'):
            print("Default pattern executed successfully")
        else:
            print("Failed to execute default pattern")
        
        # Wait 3 seconds
        time.sleep(3)
        
        # Rotate just the first motor
        print("Rotating motor 1...")
        if sender.rotate_motor('1', 90, 'clockwise'):
            print("Motor 1 rotated successfully")
        else:
            print("Failed to rotate motor 1")
        
        # Wait 2 seconds
        time.sleep(2)
        
        # Rotate just the second motor in the opposite direction
        print("Rotating motor 2...")
        if sender.rotate_motor('2', 90, 'counterclockwise'):
            print("Motor 2 rotated successfully")
        else:
            print("Failed to rotate motor 2")
        
        # Wait 2 seconds
        time.sleep(2)
        
        # Run the alternate pattern
        print("Running alternate pattern...")
        if sender.run_pattern('alternate'):
            print("Alternate pattern executed successfully")
        else:
            print("Failed to execute alternate pattern")
        
        # Wait 2 seconds
        time.sleep(2)
        
        # Disable motors to save power
        print("Disabling motors...")
        if sender.disable_motor('both'):
            print("Motors disabled successfully")
        else:
            print("Failed to disable motors")
            
    except KeyboardInterrupt:
        print("Program interrupted by user")
        # Make sure to disable motors on interrupt
        sender.disable_motor('both')
    except Exception as e:
        print(f"An error occurred: {e}")
        # Make sure to disable motors on error
        sender.disable_motor('both')

if __name__ == "__main__":
    main()
