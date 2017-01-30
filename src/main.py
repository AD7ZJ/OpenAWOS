import serial
from ws425 import *
import lcd

class WindSample:
    """One wind speed measurement"""
    
    def __init__(self):
        """Constructor"""
    

def main():
    print ("Starting OpenAWOS...")
    
    
    port = serial.Serial(baudrate=2400, port='/dev/ttyUSB0', timeout=5) # /dev/ttyAMA0
    lcdDev = lcd.I2CLcd()
    anemometer = Ws425()

    lcdDev.WriteString("AZ86 Wind      ", lcdDev.LCD_LINE_1)
    anemometer.Update()
    
    
    while (1):
        # poll serial port
        line = port.readline()
        print line 
        if (line):
            anemometer.Update(line)
            avgSpeed = anemometer.GetAvgSpeed()
            avgDir = anemometer.GetAvgDir()
            gust = anemometer.GetGust()
            print anemometer.checksum 
            print anemometer.CalcChecksum(line)

            windString = ""
            if (avgSpeed <= 2.0):
                windString = "Calm"
            elif (gust > 0):
                windString = "%03d@%02dG%d" % (avgSpeed, avgDir, gust)
            else:
                windString = "%03d@%02d" % (avgSpeed, avgDir) 
   
            print windString 
            lcdDev.WriteString(windString, lcdDev.LCD_LINE_2)
    
    
def CheckSquelch():
    return False
    
    
if __name__ == '__main__':
    main()
