import signal
import sys
import os
import glob
import serial
import time
import kiss
import aprs
from ws425 import *
from radio import *
import lcd
from gpiozero import MCP3008
    
class OpenAWOS:
    # All times in seconds
    REPORT_INTERVAL = 300
    STATUS_INTERVAL = 600
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
        self.isTxingAudio = False
        self.lcdDev = None
        self.lastNmeaPacketTime = 0
        self.ds18b20Dev = ""
        self.tempSensorPresent = False
        self.tempF = 0

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


    def DS18B20Init(self):
        try:
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')

            # give the driver time to scan the bus
            time.sleep(1)

            # device files for DS18B20 sensors always start with 28- and take the form of 28-0000061573fa
            ds18b20DevBaseDir = '/sys/bus/w1/devices/'
            ds18b20DevDir = glob.glob(ds18b20DevBaseDir + '28*')[0]
            self.ds18b20Dev = ds18b20DevDir + '/w1_slave'
            self.tempSensorPresent = True
        except IndexError:
            print "No sensor detected"
            self.tempSensorPresent = False


    def DS18B20ReadRaw(self):
        if (self.tempSensorPresent):
            f = open(self.ds18b20Dev, 'r')
            lines = f.readlines()
            f.close()
            return lines


    def GetTemp(self):
        if (self.tempSensorPresent):
            readTries = 0;
            # the output from the tempsensor looks like this:
            # f6 01 4b 46 7f ff 0a 10 eb : crc=eb YES
            # f6 01 4b 46 7f ff 0a 10 eb t=31375

            lines = self.DS18B20ReadRaw()
            while (lines[0].strip()[-3:] != 'YES' and readTries < 10):
                time.sleep(0.2)
                lines = self.DS18B20ReadRaw()
                readTries = readTries + 1

            equals_pos = lines[1].find('t=')

            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                return temp_c, temp_f
        else:
            return -99,-99


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
                    print "Starting audio broadcast..."
                    self.isTxingAudio = True
                    self.radio.SendReport(self.wxReport)
                    self.lastTrigTime = now
                    self.isTxingAudio = False
                    print "Complete!"

            time.sleep(0.05)

            

    def Run(self):
        simulateWx425 = False

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
        self.lastNmeaPacketTime = time.time()

        self.lcdDev = lcd.I2CLcd()
        self.lcdDev.WriteString("AZ86 Wind      ", self.lcdDev.LCD_LINE_1)
    
        self.radio = Radio()
        self.radio.Start()

        print("Initialize temp sensor...");
        self.DS18B20Init()

        print("Starting AudioTX thread...")
        self.StartAudioTX()

        while (1):
            # poll serial port
            if (simulateWx425):
                line = "$WIMWV,030,R,000.2,N,A*3C"
                time.sleep(1)
            else:
                line = port.readline()
            print line 
            if (line):
                anemometer.Update(line)
                if (anemometer.GetChecksum() == anemometer.CalcChecksum(line)):
                    self.lastNmeaPacketTime = time.time()
                    avgSpeed = anemometer.GetAvgSpeed()
                    avgDir = anemometer.GetAvgDir()
                    gust = anemometer.GetGust()
                    self.wxReport = { 'avgSpeed' : avgSpeed,
                                      'avgDir' : avgDir,
                                      'gust' : gust}

                    windString = ""
                    if (avgSpeed <= 2.0):
                        windString = "Calm %dF" % self.tempF
                    elif (gust > 0):
                        windString = "%03d@%02dG%d %dF" % (avgDir, avgSpeed, gust, self.tempF)
                    else:
                        windString = "%03d@%02d %dF" % (avgDir, avgSpeed, self.tempF) 
           
                    if (self.isTxingAudio):
                        self.lcdDev.WriteString("AZ86 Wind ON AIR", self.lcdDev.LCD_LINE_1)
                    else:
                        self.lcdDev.WriteString("AZ86 Wind       ", self.lcdDev.LCD_LINE_1)

                    self.lcdDev.WriteString(windString, self.lcdDev.LCD_LINE_2)

                    # don't send packets while transmitting audio
                    if (not self.isTxingAudio):
                        tempC, self.tempF = self.GetTemp()
                        #print "Temperature: %dF" % self.tempF
                        now = time.time()
                        if (now - self.lastPacketTime > self.REPORT_INTERVAL):
                            frame.text = '!%s/%s_%03d/%03dg%03dt%03dW425' % (self.latString, self.lonString, avgDir, avgSpeed, gust, self.tempF)
                            tnc.write(frame.encode_kiss())
                            self.lastPacketTime = now
               
                        if (now - self.lastStatusPacketTime > self.STATUS_INTERVAL):
                            frame.text = '>Battery: %.02fV' % (self.GetVoltage())
                            tnc.write(frame.encode_kiss())
                            self.lastStatusPacketTime = now

            now = time.time()
            if (now - self.lastNmeaPacketTime > 10):
                self.lcdDev.WriteString("No data :( %dF" % self.tempF, self.lcdDev.LCD_LINE_2)
        
if __name__ == '__main__':
    station = OpenAWOS(tncSerial = "/dev/ttyAMA0", ws425Serial = "/dev/ttyUSB0")
    station.SetCallsign("AD7ZJ-14")
    station.SetPath("WIDE1-1")
 
    try:
        station.SetLatLong(lattitude = 34.68576939, longitude = 112.29003667)
        station.Run()
    except:
        station.StopAudioTX()
        station.radio.Stop()
        sys.exit(0)

