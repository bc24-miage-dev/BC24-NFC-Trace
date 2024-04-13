#!/usr/bin/env python3

import time
from pa1010d import PA1010D

class GPS:
    def __init__(self):
        self.gps = PA1010D()

    def read_data(self):
        result = self.gps.update()
        if result:
            data = {
                "timestamp": self.gps.data["timestamp"],
                "latitude": self.gps.data["latitude"],
                "longitude": self.gps.data["longitude"],
                "altitude": self.gps.data["altitude"],
                "num_sats": self.gps.data["num_sats"],
                "gps_qual": self.gps.data["gps_qual"],
                "speed_over_ground": self.gps.data["speed_over_ground"],
                "mode_fix_type": self.gps.data["mode_fix_type"],
                "pdop": self.gps.data["pdop"],
                "vdop": self.gps.data["vdop"],
                "hdop": self.gps.data["hdop"],
            }
            return data
        else:
            return None

def loop():
    gps = GPS()
    sum_cnt = 0
    ok_cnt = 0
    while True:
        sum_cnt += 1
        data = gps.read_data()
        if data is not None:
            ok_cnt += 1
        ok_rate = 100.0 * ok_cnt / sum_cnt
        print(f"sumCnt : {sum_cnt}, \t okRate : {ok_rate:.2f}% ")
        if data is not None:
            print("Status: 0, \t Timestamp: {}, \t Latitude: {}, \t Longitude: {}".format(data["timestamp"], data["latitude"], data["longitude"]))
        else:
            print("Status: -1, \t Timestamp: n/a, \t Latitude: n/a, \t Longitude: n/a")
        time.sleep(1)

if __name__ == '__main__':
    print('Program is starting...')
    try:
        loop()
    except KeyboardInterrupt:
        pass
