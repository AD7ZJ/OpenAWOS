import re
import time

class Ws425:
    REF_TRUE = 0
    REF_RELATIVE = 1
    UNITS_KPH = 0
    UNITS_MPS = 1
    UNITS_KTS = 2
    
    def __init__(self):
        """Constructor"""
        self.dir = 0
        self.speed = 0
        self.reference = self.REF_TRUE
        self.units = self.UNITS_KPH   
        self.valid = False
        self.checksum = 0
        
        self.windHistory = []
        
    def Update(self, nmea="$WIMWV,010,T,07,N,A*01\r\n"):
        nmeaList = nmea.split(',')
        
        if (nmeaList[0] == '$WIMWV'):
            # Direction in degrees
            self.dir = int(nmeaList[1])
            
            # reference
            refConv = {'R' : self.REF_RELATIVE,
                       'T' : self.REF_TRUE}
            self.reference = refConv[nmeaList[2]]
                
            # speed
            self.speed = int(nmeaList[3])
            
            # units
            unitConv = {'K' : self.UNITS_KPH,
                        'M' : self.UNITS_MPS,
                        'N' : self.UNITS_KTS}
            self.units = unitConv[nmeaList[4]]
            
            # status
            validConv = {'A' : True,
                         'V' : False}
            self.valid = validConv[nmeaList[5].split('*')[0]]
            
            # checksum
            self.checksum = int(nmeaList[5].split('*')[1])
            
            now = int(time.time())
            history = (self.dir, self.speed, now)
            # keep the last 10 minutes of samples
            self.windHistory.append(history)
            if (now - self.windHistory[0][2] > 600):
                self.windHistory = self.windHistory[1:]
            
    def CalcChecksum(self, nmea):
        result = re.search('\$(.*)\*', nmea)
        str = result.group(1)
        checksum = 0
        
        for character in str:
            checksum ^= ord(character)
            
        return checksum

    def GetAvgSpeed(self):
        """Return the average speed"""
        
    def GetAvgDir(self):
        """Return the average direction in degrees"""
        
    def GetGust(self):
        """Return the gust factor, 0 if no gust is calculated"""
    