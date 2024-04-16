from pa1010d import PA1010D

def get_gps_data(timeout=10):
    gps = PA1010D()
    start_time = time.time()

    while True:
        result = gps.update()
        if result:
            if gps.latitude is not None and gps.longitude is not None and gps.altitude is not None:
                longitude = f"{gps.longitude: .5f} {gps.lon_dir}"
                latitude = f"{gps.latitude: .5f} {gps.lat_dir}"
                altitude = gps.altitude
                return longitude, latitude, altitude
        if time.time() - start_time > timeout:
            break
        time.sleep(1.0)

    return None, None, None
