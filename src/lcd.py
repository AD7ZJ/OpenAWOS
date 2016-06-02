#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#  lcd_i2c.py
#  LCD test script using I2C backpack.
#  Supports 16x2 and 20x4 screens.
#
# Author : Matt Hawkins
# Date   : 20/09/2015
#
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------
import smbus
import time

class I2CLcd:
    # Define some device parameters
    I2C_ADDR = 0x27  # I2C device address
    LCD_WIDTH = 16  # Maximum characters per line
    
    # Define some device constants
    LCD_CHR = 1  # Mode - Sending data
    LCD_CMD = 0  # Mode - Sending command
    
    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
    LCD_LINE_3 = 0x94  # LCD RAM address for the 3rd line
    LCD_LINE_4 = 0xD4  # LCD RAM address for the 4th line
    
    LCD_BACKLIGHT = 0x08  # On
    # LCD_BACKLIGHT = 0x00  # Off
    
    ENABLE = 0b00000100  # Enable bit
    
    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005
    
    # Open I2C interface
    # bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
    bus = smbus.SMBus(1)  # Rev 2 Pi uses 1
    
    def __init__(self):
        # Initialise display
        self.WriteByte(0x33, self.LCD_CMD)  # 110011 Initialise
        self.WriteByte(0x32, self.LCD_CMD)  # 110010 Initialise
        self.WriteByte(0x06, self.LCD_CMD)  # 000110 Cursor move direction
        self.WriteByte(0x0C, self.LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off 
        self.WriteByte(0x28, self.LCD_CMD)  # 101000 Data length, number of lines, font size
        self.WriteByte(0x01, self.LCD_CMD)  # 000001 Clear display
        time.sleep(self.E_DELAY)
    
    def WriteByte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command
        
        bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | self.LCD_BACKLIGHT
        
        # High bits
        self.bus.write_byte(self.I2C_ADDR, bits_high)
        self.ToggleEnable(bits_high)
        
        # Low bits
        self.bus.write_byte(self.I2C_ADDR, bits_low)
        self.ToggleEnable(bits_low)
    
    def ToggleEnable(self, bits):
        # Toggle enable
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR, (bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)
    
    def WriteString(self, message, line):
        # Send string to display
        message = message.ljust(self.LCD_WIDTH, " ")
        
        self.WriteByte(line, self.LCD_CMD)
        
        for i in range(self.LCD_WIDTH):
            self.WriteByte(ord(message[i]), self.LCD_CHR)
            
    def Clear(self):
        self.lcd_byte(0x01, self.LCD_CMD)

def main():
    # Initialise display
    lcd = I2CLcd()
    
    while True:
        lcd.WriteString("AZ86 Wind      ", lcd.LCD_LINE_1)
        lcd.WriteString(time.strftime("%H:%M:%S"), lcd.LCD_LINE_2)
        
        time.sleep(1)
        

if __name__ == '__main__':
    main()

