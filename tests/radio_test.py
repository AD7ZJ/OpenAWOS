import unittest
import audio
from radio import *

class MockAudio(audio.Audio):
    reportMsg = ""
    
    def Synthesize(self, msg):
        self.reportMsg = msg

class RadioTests(unittest.TestCase):
    radio = None
    mockAudio = None

    def setUp(self):
        """Call before every test case."""
        self.mockAudio = MockAudio()
        self.radio = Radio(simulate = True, audioDev = self.mockAudio)
        self.radio.Start()

    def tearDown(self):
        """Call after every test case."""
        self.radio.Stop()
        
    def testSuccessfulMicClick(self):
        """Test the microphone clicking works correctly"""
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSimSquelchInput(True)
        time.sleep(0.3)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSimSquelchInput(True)
        time.sleep(0.3)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSimSquelchInput(True)
        time.sleep(0.3)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertTrue(self.radio.GetTriggered(), "Failed to trigger after three clicks")
        
    def testLongMicClick(self):
        """Test that long duration squelch events do not generate a trigger"""
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSimSquelchInput(True)
        time.sleep(2)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSimSquelchInput(True)
        time.sleep(0.3)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSimSquelchInput(True)
        time.sleep(0.3)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
    def testLongSpacedClicks(self):
        """Test that clicks spaced too far apart do not generate a trigger"""
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSimSquelchInput(True)
        time.sleep(0.3)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        # leave too long a space between clicks
        time.sleep(4)
        
        # now it should take three clicks to trigger again
        self.radio.SetSimSquelchInput(True)
        time.sleep(0.3)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSimSquelchInput(True)
        time.sleep(0.3)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSimSquelchInput(True)
        time.sleep(0.3)
        self.radio.SetSimSquelchInput(False)
        time.sleep(0.5)
        self.assertTrue(self.radio.GetTriggered(), "Failed to trigger after three clicks")
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
    def testReportTx(self):
        rpt = { 'avgSpeed' : 0, 'avgDir' : 100, 'gust' : 0}  
        self.radio.SendReport(rpt)
        self.assertTrue(self.mockAudio.reportMsg == "Wind, calm ", "failed to play correct files")
        self.mockAudio.fileList = []
        
        rpt = { 'avgSpeed' : 17, 'avgDir' : 100, 'gust' : 0}  
        self.radio.SendReport(rpt)
        self.assertTrue(self.mockAudio.reportMsg == "Wind, 1, 0, 0, at, 1, 7, ", "failed to play correct files")
        self.mockAudio.fileList = []
        
        rpt = { 'avgSpeed' : 17.32, 'avgDir' : 257, 'gust' : 24.8}  
        self.radio.SendReport(rpt)
        self.assertTrue(self.mockAudio.reportMsg == "Wind, 2, 6, 0, at, 1, 7, gusting, 2, 5, ", "failed to play correct files")
        
if __name__ == "__main__":
    unittest.main()

        
