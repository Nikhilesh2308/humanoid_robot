#source for contorlling robotic arms and head
from gpiozero import OutputDevice
import threading
import time

class StepperMotor:
    def __init__(self, pin1, pin2, pin3, pin4):
        """
        Initialize stepper motor with 4 GPIO pins
        """
        self.pins = [
            OutputDevice(pin1),
            OutputDevice(pin2),
            OutputDevice(pin3),
            OutputDevice(pin4)
        ]
        
        # Motor specifications
        self.DEG_PER_STEP = 1.8
        self.STEPS_PER_REVOLUTION = int(360 / self.DEG_PER_STEP)

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

def rotate_motor(motor, angle, direction):
    """
    Helper function for threading motor rotation
    """
    motor.rotate(angle, direction)

def main():
    try:
        # Initialize two stepper motors with GPIO pins
        motor1 = StepperMotor(23, 24, 27, 22)  # First motor pins
        motor2 = StepperMotor(5, 6, 16, 17)    # Second motor pins
        
        # Rotate both motors simultaneously
        print("Rotating both motors 70 degrees")
        
        # Create threads for simultaneous rotation
        thread1 = threading.Thread(target=rotate_motor, args=(motor1, 5, 'clockwise'))
        thread2 = threading.Thread(target=rotate_motor, args=(motor2, 5, 'counterclockwise'))
        
        # Start both threads
        thread1.start()
        thread2.start()
        
        # Wait for both threads to complete
        thread1.join()
        thread2.join()
        
        # Pause for 1 second
        print("Pausing for 5 second")
        time.sleep(5)
        
        # Return both motors to starting position
        print("Returning motors to starting position")
      #still working with the angle of arms for reference I kept with
      #note if you want keep the angle as degree then frst calibrate the angle with voltage output of the motors and with drivers
      
        thread1 = threading.Thread(target=rotate_motor, args=(motor1, 5, 'counterclockwise'))
        thread2 = threading.Thread(target=rotate_motor, args=(motor2, 5, 'clockwise')
        
        # Start return threads
        thread1.start()
        thread2.start()
        
        # Wait for both threads to complete
        thread1.join()
        thread2.join()
        
        print("Motors rotation complete")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    
