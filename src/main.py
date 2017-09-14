import signal
import sys
import serial
import time
import kiss
import aprs
from ws425 import *
from radio import *
import lcd
from gpiozero import MCP3008
    
class OpenAWOS:
    REPORT_INTERVAL = 10
    STATUS_INTERVAL = 20
    MIN_TRIGGER_SPACING = 5

    def __init__(self, tncSerial="", ws425Serial = ""):
        """Constructor"""
        self.callsign = ""
        self.path = ""
        self.latString = "00000.00"
        self.lonString = "00000.00"
        self.lastPacketTime = 0
        self.lastStatusPacketTime = 0
        self.lastTrigTime = 0
        self.ws425SerialPort = ws425Serial
        self.tncSerialPort = tncSerial
        self.keepGoing = False
        self.thread = None
        self.wxReport = None

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

    def GetVoltage(self):
        vref = 3.33
        conversion_factor = 4.677 # 3.3k / 12 k divider
        
        adc = MCP3008(channel=0)
        # average several readings
        readings = 0.0
        repetitions = 20
        for y in range(repetitions):
            readings += adc.value
        average = readings / repetitions
        return (vref * average * conversion_factor)

    def StartAudioTX(self):
        """Start the thread that will send the audio reports"""
        self.keepGoing = True
        self.thread = threading.Thread(target=self.AudioTX)
        self.thread.daemon = True
        self.thread.start()

    def StopAudioTX(self):
        self.keepGoing = False
        self.thread.join()

    def AudioTX(self):
        while(self.keepGoing):
            if (self.radio.GetTriggered()):
                now = time.time()
                if (now - self.lastTrigTime > self.MIN_TRIGGER_SPACING):
                    self.radio.SendReport(self.wxReport)
                    self.lastTrigTime = now

            time.sleep(0.05)

            

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
    
        self.radio = Radio()
        self.radio.Start()

        print("Starting AudioTX thread...")
        self.StartAudioTX()

        while (1):
            # poll serial port
            line = port.readline()
            print line 
            if (line):
                anemometer.Update(line)
                if (anemometer.GetChecksum() == anemometer.CalcChecksum(line)):
                    avgSpeed = anemometer.GetAvgSpeed()
                    avgDir = anemometer.GetAvgDir()
                    gust = anemometer.GetGust()
                    self.wxReport = { 'avgSpeed' : avgSpeed,
                                      'avgDir' : avgDir,
                                      'gust' : gust}

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
           
                    if (now - self.lastStatusPacketTime > self.STATUS_INTERVAL):
                        frame.text = '>Battery: %.02fV' % (self.GetVoltage())
                        tnc.write(frame.encode_kiss())
                        self.lastStatusPacketTime = now
        
if __name__ == '__main__':

    # catch ctrl-c so we can cleanup the GPIO driver and child threads
    def sigHandler(signal, frame):
        print('Caught SIGINT, exiting...\n')
        station.StopAudioTX()
        station.radio.Stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigHandler)


    station = OpenAWOS(tncSerial = "/dev/ttyAMA0", ws425Serial = "/dev/ttyUSB0")
    station.SetCallsign("AD7ZJ-14")
    station.SetPath("WIDE1-1")
    station.SetLatLong(lattitude = 34.68576939, longitude = 112.29003667)

    station.Run()


