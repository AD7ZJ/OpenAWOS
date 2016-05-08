import unittest
from radio import *

class RadioTests(unittest.TestCase):
    radio = None

    def setUp(self):
        """Call before every test case."""
        self.radio = Radio(simulate = True)
        self.radio.Start()

    def tearDown(self):
        """Call after every test case."""
        self.radio.Stop()
        
    def testSuccessfulMicClick(self):
        """Test the microphone clicking works correctly"""
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertTrue(self.radio.GetTriggered(), "Failed to trigger after three clicks")
        
    def testLongMicClick(self):
        """Test that long duration squelch events do not generate a trigger"""
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(2)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
    def testLongSpacedClicks(self):
        """Test that clicks spaced too far apart do not generate a trigger"""
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        # leave too long a space between clicks
        time.sleep(4)
        
        # now it should take three clicks to trigger again
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(0.5)
        self.assertTrue(self.radio.GetTriggered(), "Failed to trigger after three clicks")
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
if __name__ == "__main__":
    unittest.main() # run all tests
        
