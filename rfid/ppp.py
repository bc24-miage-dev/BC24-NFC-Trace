from pa1010d import PA1010D

def get_gps_data():
    gps = PA1010D()

    while True:
        result = gps.update()
        if result:
            longitude = f"{gps.longitude: .5f} {gps.lon_dir}"
            latitude = f"{gps.latitude: .5f} {gps.lat_dir}"
            altitude = gps.altitude
            return longitude, latitude, altitude
        time.sleep(1.0)

# Example usage
longitude, latitude, altitude = get_gps_data()
print(f"Longitude: {longitude}")
print(f"Latitude: {latitude}")
print(f"Altitude: {altitude}")
