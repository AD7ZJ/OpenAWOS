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
        time.sleep(1)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(1)
        self.assertFalse(self.radio.GetTriggered(), "Reported triggered when it shouldn't")
        
        self.radio.SetSquelchInputStatus(True)
        time.sleep(0.3)
        self.radio.SetSquelchInputStatus(False)
        time.sleep(1)
        self.assertTrue(self.radio.GetTriggered(), "Failed to trigger after three clicks")
        
        
        
        
        