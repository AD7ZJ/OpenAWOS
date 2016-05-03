import serial
from ws425 import *

class WindSample:
    """One wind speed measurement"""
    
    def __init__(self):
        """Constructor"""
    

def main():
    print ("Starting OpenAWOS...")
    
    
    port = serial.Serial(baudrate=19200, port='/dev/ttyUSB0', timeout=5) # /dev/ttyAMA0

    
    anemometer = Ws425()
    anemometer.Update()
    
    
    while (1):
        # poll serial port
        line = port.readline()
        
        if (line):
            anemometer.Update(line)
    
    
    
    
    
    
    
def CheckSquelch():
    return False
    
    
if __name__ == '__main__':
    main()