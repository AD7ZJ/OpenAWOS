import unittest
from ws425 import *

class Ws425Tests(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""

    def tearDown(self):
        """Call after every test case."""

    def testDir(self):
        """Test wind direction parsing"""
        anemometer = Ws425()
        anemometer.Update("$WIMWV,010,T,07,N,A*01\r\n")    
        assert anemometer.dir == 10, "Wind direction parsed incorrectly"
        
        anemometer.Update("$WIMWV,19,T,07,N,A*01\r\n")    
        assert anemometer.dir == 19, "Wind direction parsed incorrectly"
        
        anemometer.Update("$WIMWV,360,T,07,N,A*01\r\n")    
        assert anemometer.dir == 360, "Wind direction parsed incorrectly"

        print anemometer.windHistory


if __name__ == "__main__":
    unittest.main() # run all tests