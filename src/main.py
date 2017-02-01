import serial
import time
import kiss
import aprs
from ws425 import *
import lcd

    
class OpenAWOS:
    REPORT_INTERVAL = 10


    def __init__(self, tncSerial="", ws425Serial = ""):
        """Constructor"""
        self.callsign = ""
        self.path = ""
        self.latString = "00000.00"
        self.lonString = "00000.00"
        self.lastPacketTime = 0
        self.ws425SerialPort = ws425Serial
        self.tncSerialPort = tncSerial


    def SetCallsign(self, callsign):
        self.callsign = callsign


    def SetPath(self, path):
        self.path = path


    def SetLatLong(self, lattitude, longitude):
        degreesLat = int(lattitude)
        degreesLon = int(longitude)
        minutesLat = (lattitude - degreesLat) * 60
        minutesLon = (longitude - degreesLon) * 60

        self.latString = "%02d%02d.%02dN" % (int(degreesLat), int(minutesLat), (minutesLat - int(minutesLat)) * 100)
        self.lonString = "%03d%02d.%02dW" % (int(degreesLon), int(minutesLon), (minutesLon - int(minutesLon)) * 100)


    def Run(self):
        print ("Starting OpenAWOS...")
        frame = aprs.Frame()
        frame.source = aprs.Callsign(self.callsign)
        frame.destination = aprs.Callsign('APRS')
        frame.path = [aprs.Callsign(self.path)]

        print("Opening TNC on %s" % self.tncSerialPort)
        tnc = kiss.SerialKISS(port=self.tncSerialPort, speed='19200')
        tnc.start()

        print("Connecting to Ws425 on %s" % self.ws425SerialPort) 
        port = serial.Serial(baudrate=2400, port=self.ws425SerialPort, timeout=5)
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
                if (now - self.lastPacketTime > self.REPORT_INTERVAL):
                    frame.text = '!%s/%s_%03d/%03dg%03dW425' % (self.latString, self.lonString, avgDir, avgSpeed, gust)
                    tnc.write(frame.encode_kiss())
                    self.lastPacketTime = now
       

    
if __name__ == '__main__':
    station = OpenAWOS(tncSerial = "/dev/ttyAMA0", ws425Serial = "/dev/ttyUSB0")
    station.SetCallsign("AD7ZJ-14")
    station.SetPath("WIDE1-1")
    station.SetLatLong(lattitude = 34.68576939, longitude = 112.29003667)

    station.Run()


