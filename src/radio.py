import threading
import time
import audio

class Radio:
    MIN_CLICK_SPACING = 0.4
    MAX_CLICK_SPACING = 3.0
    audioDev = None
    
    def __init__(self, simulate=False, audioDev = None):
        """Constructor"""
        self.keepGoing = False
        self.thread = None
        self.lock = threading.RLock()
        self.simulate = simulate
        self.simSquelchInput = False
        self.triggered = False
        self.audioDev = audioDev
        if (self.audioDev == None):
            self.audioDev = audio.Audio()
        
    def Start(self):
        """Start monitoring the radio's squelch line"""
        self.keepGoing = True
        self.thread = threading.Thread(target=self.Update)
        self.thread.start()
        
    def Stop(self):
        self.keepGoing = False
        self.thread.join()

    def Update(self):
        """Thread the polls the GPIO for squelch changes"""
        lastSqlState = False
        clickState = "waitingFirst"
        pulseStartTime = 0
        lastClickTime = 0
        
        while self.keepGoing:
            sql = self.GetSquelchStatus()
            now = time.time()
            
            if (sql == True):
                if (lastSqlState == False):
                    pulseStartTime = time.time()
                    lastSqlState = True
            else:
                if (lastSqlState == True):
                    if ((now - pulseStartTime) > 0.2 and (now - pulseStartTime < 1.5)):
                        # pulse is detected
                        if (clickState == "waitingFirst"):
                            lastClickTime = now
                            clickState = "waitingSecond"
                            
                        elif (clickState == "waitingSecond"):
                            if ((now - lastClickTime) > self.MIN_CLICK_SPACING and (now - lastClickTime) < self.MAX_CLICK_SPACING):
                                lastClickTime = now
                                clickState = "waitingThird"
                            else:
                                clickState = "waitingFirst"
                                
                        elif (clickState == "waitingThird"):
                            if ((now - lastClickTime) > self.MIN_CLICK_SPACING and (now - lastClickTime) < self.MAX_CLICK_SPACING):
                                lastClickTime = now
                                self.lock.acquire()
                                self.triggered = True
                                clickState = "waitingFirst"
                                self.lock.release()
                            else:
                                clickState = "waitingFirst"
                            
                    lastSqlState = False
                    
            # timeout for clicks too far apart
            if ((now - lastClickTime) > self.MAX_CLICK_SPACING):
                clickState = "waitingFirst"
                
            time.sleep(0.05)
            
    def SendReport(self, windReport):
        """Keys the radio and outputs the synthesized audio"""
        avgSpeed = windReport['avgSpeed']
        avgDir = windReport['avgDir']
        gust = windReport['gust']
        
        self.SetTxLevel(True)
        
        self.audioDev.PlayWavFile('wind')
        
        if (avgSpeed == 0):
            self.audioDev.PlayWavFile('calm')
        else:
            
            dirStr = str(avgDir)
            for digit in dirStr:
                self.audioDev.PlayWavFile(digit)
            
            self.audioDev.PlayWavFile('at')
            
            speedStr = str(avgSpeed)
            for digit in speedStr:
                self.audioDev.PlayWavFile(digit)
                
            if (gust != 0):
                self.audioDev.PlayWavFile('gusting')
                gustStr = str(gust)
                for digit in gustStr:
                    self.audioDev.PlayWavFile(digit)
        
        self.SetTxLevel(False)
            
    def GetTriggered(self):
        trigd = False
        self.lock.acquire()
        trigd = self.triggered
        self.triggered = False
        self.lock.release()
        return trigd
    
    def SetSimSquelchInput(self, state):
        self.simSquelchInput = state
        
    def GetSquelchStatus(self):
        if (self.simulate):
            return self.simSquelchInput
        else:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            
            GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            return GPIO.input(18)
        
    def SetTxLevel(self, state):
        """Set the TX output pin"""
        
    
    