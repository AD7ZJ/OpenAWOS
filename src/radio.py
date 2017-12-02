import threading
import time
import audio

class Radio:
    MIN_CLICK_SPACING = 0.4
    MAX_CLICK_SPACING = 1.5
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
        if (not self.simulate):
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            # Setup the squelch input pin
            GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # setup the radio PTT pin
            GPIO.setup(17, GPIO.OUT)


        
    def Start(self):
        """Start monitoring the radio's squelch line"""
        self.keepGoing = True
        self.thread = threading.Thread(target=self.Update)
        self.thread.daemon = True
        self.thread.start()
        
    def Stop(self):
        self.keepGoing = False
        if (not self.simulate):
            import RPi.GPIO as GPIO
            GPIO.cleanup()
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
        avgSpeed = int(round(windReport['avgSpeed']))
        avgDir = int(round(windReport['avgDir'], -1))
        gust = int(round(windReport['gust']))
        
        msg = "Goodwin glider port, wind, " 
        
        if (avgSpeed <= 3.0):
            msg += "calm "
        else:
            dirStr = str(avgDir)
            for digit in dirStr:
                msg += "%s, " % digit
            
            msg += "at, "
            
            speedStr = str(avgSpeed)
            for digit in speedStr:
                msg += "%s, " % digit
                
            if (gust != 0):
                msg += "gusting, "
                gustStr = str(gust)
                for digit in gustStr:
                    msg += "%s, " % digit
                    
        self.SetPtt(True)
        self.audioDev.Synthesize(msg)
        self.SetPtt(False)
            
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
            return not GPIO.input(6)
        
    def SetPtt(self, state):
        """Set the raido PTT pin"""
        if (not self.simulate):
            import RPi.GPIO as GPIO
            if (state):
                GPIO.output(17, GPIO.HIGH)
            else:
                GPIO.output(17, GPIO.LOW)
                

    
    
