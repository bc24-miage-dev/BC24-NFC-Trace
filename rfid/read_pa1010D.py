import serial
import time

class GPS:
    def __init__(self, port='/dev/serial0', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)

    def read_data(self):
        data = {}
        while True:
            line = self.ser.readline().decode('utf-8').strip()
            if not line:
                continue
            if line[0:6] == '$GPRMC':
                values = line.split(',')
                if len(values) >= 10 and values[2] == 'A':
                    data['timestamp'] = values[1]
                    data['latitude'] = values[3] + values[4]/60.0
                    data['longitude'] = values[5] + values[6]/60.0
                    data['speed_over_ground'] = values[7]
                    data['course_over_ground'] = values[8]
                    data['date'] = values[9]
                    return data
            time.sleep(0.1)
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
