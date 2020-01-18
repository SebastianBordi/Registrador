import I2C_LCD_driver
from time import *

mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_display_string("Sebastian", 1)
mylcd.lcd_display_string("08/06/19 8:30",2)

