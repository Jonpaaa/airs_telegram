import geomag
import geopy.distance
import numpy as np

def spherical_to_cartesian(lat, lon):
    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)
    x = np.cos(lat) * np.cos(lon)
    y = np.cos(lat) * np.sin(lon)
    z = np.sin(lat)
    return x, y, z

def great_circle_heading(start_lat, start_lon, end_lat, end_lon):
    start = spherical_to_cartesian(start_lat, start_lon)
    end = spherical_to_cartesian(end_lat, end_lon)
    dot = np.dot(start, end)
    angle = np.arccos(dot)
    return np.rad2deg(angle)


def heading_to_destination(start_lat, start_lon, end_lat, end_lon):
    distance = round(geopy.distance.distance((start_lat, start_lon), (end_lat, end_lon)).nautical)

    start_lat_rad = np.deg2rad(start_lat)
    start_lon_rad = np.deg2rad(start_lon)
    end_lat_rad = np.deg2rad(end_lat)
    end_lon_rad = np.deg2rad(end_lon)

    y = np.sin(end_lon_rad - start_lon_rad) * np.cos(end_lat_rad)
    x = (np.cos(start_lat_rad)) * (np.sin(end_lat_rad)) - (np.sin(start_lat_rad) * np.cos(end_lat_rad) * np.cos(end_lon_rad - start_lon_rad))
    track_rad = np.arctan2(y, x)
    track_true = (np.degrees(track_rad) + 360) % 360
    track_true = round(track_true)

    magnetic_declination = geomag.declination(start_lat, start_lon, 0)
    track_magnetic = (track_true - magnetic_declination) % 360
    track_magnetic = round(track_magnetic)




    return track_magnetic, track_true, distance



