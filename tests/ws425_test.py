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
        anemometer.Update("$WIMWV,010,T,07,N,A*01\r\n", 0)    
        self.assertEqual(anemometer.dir, 10, "Wind direction parsed incorrectly")
        
        anemometer.Update("$WIMWV,19,T,07,N,A*01\r\n", 1)    
        self.assertEqual(anemometer.dir, 19, "Wind direction parsed incorrectly")
        
        anemometer.Update("$WIMWV,360,T,07,N,A*01\r\n", 2)    
        self.assertEqual(anemometer.dir, 360, "Wind direction parsed incorrectly")
        
    def testAvgSpeed(self):
        """Test the average speed calculator"""
        anemometer = Ws425()
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 0)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 1)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 2)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 3)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 4)
        anemometer.Update("$WIMWV,010,T,20,N,A*01\r\n", 5)
        anemometer.Update("$WIMWV,010,T,20,N,A*01\r\n", 6)
        anemometer.Update("$WIMWV,010,T,20,N,A*01\r\n", 7)
        anemometer.Update("$WIMWV,010,T,20,N,A*01\r\n", 8)
        anemometer.Update("$WIMWV,010,T,20,N,A*01\r\n", 9)
        
        self.assertEqual(anemometer.GetAvgSpeed(), 15, "Avg wind speed calculated incorrectly")   
        
        # verify entries older than 2 minutes drop out
        anemometer.Update("$WIMWV,010,T,0,N,A*01\r\n", 130)
        anemometer.Update("$WIMWV,010,T,0,N,A*01\r\n", 131)
        anemometer.Update("$WIMWV,010,T,0,N,A*01\r\n", 132)
        anemometer.Update("$WIMWV,010,T,0,N,A*01\r\n", 133)
        anemometer.Update("$WIMWV,010,T,0,N,A*01\r\n", 134)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 135)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 136)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 137)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 138)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 139)
        self.assertEqual(anemometer.GetAvgSpeed(), 5, "Avg wind speed calculated incorrectly") 
        
    def testGust(self):
        """Test the gust calculation"""
        anemometer = Ws425()
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 0)
        anemometer.Update("$WIMWV,010,T,20,N,A*01\r\n", 10)
        anemometer.Update("$WIMWV,010,T,15,N,A*01\r\n", 20)
        anemometer.Update("$WIMWV,010,T,13,N,A*01\r\n", 30)
        anemometer.Update("$WIMWV,010,T,12,N,A*01\r\n", 40)
        anemometer.Update("$WIMWV,010,T,15,N,A*01\r\n", 50)
        anemometer.Update("$WIMWV,010,T,19,N,A*01\r\n", 60)
        anemometer.Update("$WIMWV,010,T,22,N,A*01\r\n", 70)
        anemometer.Update("$WIMWV,010,T,20,N,A*01\r\n", 80)
        anemometer.Update("$WIMWV,010,T,7,N,A*01\r\n", 90)
        self.assertEqual(anemometer.GetGust(), 22, "Wind cust calculated incorrectly")
        
        # verify entries older than 10 minutes drop out
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 700)
        anemometer.Update("$WIMWV,010,T,7,N,A*01\r\n", 701)
        anemometer.Update("$WIMWV,010,T,5,N,A*01\r\n", 702)
        anemometer.Update("$WIMWV,010,T,8,N,A*01\r\n", 703)
        anemometer.Update("$WIMWV,010,T,9,N,A*01\r\n", 704)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 705)
        anemometer.Update("$WIMWV,010,T,12,N,A*01\r\n", 706)
        anemometer.Update("$WIMWV,010,T,15,N,A*01\r\n", 707)
        anemometer.Update("$WIMWV,010,T,13,N,A*01\r\n", 708)
        anemometer.Update("$WIMWV,010,T,10,N,A*01\r\n", 709)
        self.assertEqual(anemometer.GetGust(), 0, "Wind cust calculated incorrectly")
        
    def testAvgDir(self):
        """Test the average direction calculation"""
        anemometer = Ws425()
        anemometer.Update("$WIMWV,020,T,10,N,A*01\r\n", 0)
        anemometer.Update("$WIMWV,350,T,10,N,A*01\r\n", 1)
        
        self.assertEqual(anemometer.GetAvgDir(), 5, "Average direction calculated incorrectly")
        
        anemometer.windHistory = []
        anemometer.Update("$WIMWV,70,T,10,N,A*01\r\n", 0)
        anemometer.Update("$WIMWV,90,T,10,N,A*01\r\n", 1)
        self.assertEqual(anemometer.GetAvgDir(), 80, "Average direction calculated incorrectly")
        
        anemometer.windHistory = []
        anemometer.Update("$WIMWV,280,T,10,N,A*01\r\n", 0)
        anemometer.Update("$WIMWV,260,T,10,N,A*01\r\n", 1)
        self.assertEqual(anemometer.GetAvgDir(), 270, "Average direction calculated incorrectly")
        
        # test that direction is weighted by the speed
        anemometer.windHistory = []
        anemometer.Update("$WIMWV,270,T,10,N,A*01\r\n", 0)
        anemometer.Update("$WIMWV,90,T,20,N,A*01\r\n", 1)
        self.assertEqual(anemometer.GetAvgDir(), 90, "Average direction calculated incorrectly")
        
    def testEmptyPacket(self):
        """Test correct handling of an empty packet"""
        anemometer = Ws425()
        anemometer.Update("$WIMWV,,R,,N,V*34\r\n", 0)
        anemometer.Update("$WIMWV,270,T,,N,A*01\r\n", 0)
        self.assertEqual(anemometer.GetAvgSpeed(), 0, "Failed to correctly calculate avg windspeed when wind history is empty")
        self.assertEqual(anemometer.GetAvgDir(), 0, "Failed to correctly calculate avg wind direction when wind history is empty")
        self.assertEqual(anemometer.GetGust(), 0, "Failed to correctly calculate wind gust when wind history is empty")


        self.assertEqual(len(anemometer.windHistory), 0, "Failed to ignore empty packets")


if __name__ == "__main__":
    unittest.main() # run all tests