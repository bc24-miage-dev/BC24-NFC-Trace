#!/usr/bin/env python3
import time

from pa1010d import PA1010D

def main():
    gps = PA1010D()

    while True:
        result = gps.update()
        if result:
            print("""
Timestamps : {timestamp}
Latitude : {latitude}
Longitude : {longitude}
Altitude : {altitude}
Number of satellites : {num_sats}
GPS quality : {gps_qual}
Speed over ground : {speed_over_ground}
Mode fix type : {mode_fix_type}
PDOP : {pdop}
VDOP : {vdop}
HDOP : {hdop}
""".format(**gps.data))
        time.sleep(1.0)

if __name__ == "__main__":
    main()
