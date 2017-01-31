import serial
import time
import kiss
import aprs
from ws425 import *
import lcd


ws425SerialPort = "/dev/ttyUSB0"
tncSerialPort = "/dev/ttyAMA0"
now = 0
lastPacketTime = 0
REPORT_INTERVAL = 10


def main():
    lastPacketTime = 0
    print ("Starting OpenAWOS...")
    frame = aprs.Frame()
    frame.source = aprs.Callsign('AD7ZJ-14')
    frame.destination = aprs.Callsign('APRS')
    frame.path = [aprs.Callsign('WIDE1-1')]

    print("Opening TNC on %s" % tncSerialPort)
    tnc = kiss.SerialKISS(port=tncSerialPort, speed='19200')
    tnc.start()

    print("Connecting to Ws425 on %s" % ws425SerialPort) 
    port = serial.Serial(baudrate=2400, port=ws425SerialPort, timeout=5)
    anemometer = Ws425()
    anemometer.Update()

    lcdDev = lcd.I2CLcd()
    lcdDev.WriteString("AZ86 Wind      ", lcdDev.LCD_LINE_1)
    
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

            now = time.time()
            if (now - lastPacketTime > REPORT_INTERVAL):
                frame.text = '!3441.14N/11217.40W_%03d/%03dg%03dW425' % (avgDir, avgSpeed, gust)
                tnc.write(frame.encode_kiss())
                lastPacketTime = now
   

    
def CheckSquelch():
    return False
    
    
if __name__ == '__main__':
    main()
