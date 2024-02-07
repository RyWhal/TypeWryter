import time
import keyboard
from waveshare_epd import epd4in2_V2

from TypeWryter import TypeWryter


# Instantiate TypeWryter with the default configuration
type_wryter = TypeWryter()

try:
  type_wryter.epd = epd4in2_V2.EPD() 
  type_wryter.keyboard = keyboard
  type_wryter.ensure_sub_dirs()
  type_wryter.initialize()
  type_wryter.run()

except KeyboardInterrupt:
    pass

finally:
    keyboard.unhook_all()
    type_wryter.epd.init()
    time.sleep(1)
    type_wryter.epd.Clear()
    type_wryter.epd.sleep()

