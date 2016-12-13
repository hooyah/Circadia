"""
    Circadia Sunrise Lamp - HAL entry point

    detect the hardware platform and load the appropriate module

    Author: fhu
"""

import os

__platform = "win32"
if "MANILA_SUNRISE_PLATFORM" in os.environ: # on the lamp this env variable will exist
    __platform = os.environ["raspi"]


if __platform == 'win32':
    import MSR_HAL.circadia_hw_win32 as hw
else:
    import MSR_HAL.circadia_hw_lamp as hw

CircadiaHw = hw





