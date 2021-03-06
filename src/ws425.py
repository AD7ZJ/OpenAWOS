import re
import time
import math
import sys

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
        
        # history is an array of dictionaries in the form of { 'dir', 'speed', 'time'}
        self.windHistory = []
        
    def Update(self, nmea="$WIMWV,010,T,07,N,A*01\r\n", ts=0):
        if (ts == 0):
            ts = time.time()
        try:
            nmeaList = nmea.split(',')
            
            # Only try and parse $WIMWV strings with no empty sets
            if (nmeaList[0] == '$WIMWV' and min(map(len, nmeaList)) > 0):
                # Direction in degrees
                self.dir = int(nmeaList[1])
                
                # reference
                refConv = {'R' : self.REF_RELATIVE,
                           'T' : self.REF_TRUE}
                self.reference = refConv[nmeaList[2]]
                    
                # speed
                self.speed = float(nmeaList[3])
                
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
                self.checksum = int(nmeaList[5].split('*')[1], 16)
                
                now = int(ts)
                history = {'dir' : self.dir, 'speed' : self.speed, 'time' : now}
                # keep the last 10 minutes of samples
                self.windHistory.append(history)
                if (now - self.windHistory[0]['time'] > 600):
                    self.windHistory = self.windHistory[1:]

        except:
            e = sys.exc_info()[0]
            print "Exception parsing NMEA message: %s" % e
            #print nmeaList

    def CalcChecksum(self, nmea):
        str = ""
        result = re.search('\$(.*)\*', nmea)
        if (result is not None):
            str = result.group(1)

        checksum = 0        
        for character in str:
            checksum ^= ord(character)
            
        return checksum

    def GetChecksum(self):
        return self.checksum

    def GetAvgSpeed(self):
        """Return the average speed"""
        accum = 0
        count = 0
        # look at the last 2 minutes
        if (len(self.windHistory) > 0):
            lastEntryTime = self.windHistory[len(self.windHistory) - 1]['time']
            for entry in self.windHistory:
                if (lastEntryTime - entry['time'] < 120):
                    accum += entry['speed']
                    count += 1
                
            return accum / count
        else:
            return 0
        
    def GetAvgDir(self):
        """Return the average direction in degrees. Using a vector average"""
        xaccum = 0
        yaccum = 0
        count = 0
        # look at the last 2 minutes
        if (len(self.windHistory) > 0):
            lastEntryTime = self.windHistory[len(self.windHistory) - 1]['time']
            for entry in self.windHistory:
                if (lastEntryTime - entry['time'] < 120):
                    xaccum += math.cos(math.radians(entry['dir'])) * entry['speed']
                    yaccum += math.sin(math.radians(entry['dir'])) * entry['speed']
                    count += 1
                    
            x = xaccum / count
            y = yaccum / count
            
            avgDegrees = round(math.degrees(math.atan2(y, x)))
            if (avgDegrees < 0):
                return avgDegrees + 360
            else:
                return avgDegrees
        else:
            return 0
        
        
    def GetGust(self):
        """Return the gust factor, 0 if no gust is calculated"""
        accum = 0
        count = 0
        min = 200
        max = 0
        
        # look at the last 10 minutes
        if (len(self.windHistory) > 0):
            lastEntryTime = self.windHistory[len(self.windHistory) - 1]['time']
            for entry in self.windHistory:
                if (lastEntryTime - entry['time'] < 600):
                    accum += entry['speed']
                    count += 1
                    
                    if (entry['speed'] < min):
                        min = entry['speed']
                        
                    if (entry['speed'] > max):
                        max = entry['speed']
            
            if (max >= 16):
                if (max - min > 9):
                    return max
                
            return 0
        else:
            return 0
    
