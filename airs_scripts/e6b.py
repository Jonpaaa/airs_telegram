import math

def e6b_calc(true_Airspeed, track, wind, wind_v, distance=0):
    tas = true_Airspeed
    trk = track
    w = wind
    v = wind_v
    dist = distance


    trk_Rad = math.radians(trk)
    w_Rad = math.radians(w)


    w_Azimuth = ((w + 180) % 360)
    w_Azimuth_Rad = math.radians(w_Azimuth)

    w_Correction_Angle_Rad = math.asin((v*math.sin(w_Azimuth_Rad - trk_Rad)) /tas)

    w_Correction_Angle = math.degrees(w_Correction_Angle_Rad)


    hdg = round(trk - w_Correction_Angle)

    #GS: Calculate the angle factor then apply it to the speeds calculation

    angle_Factor_rad = trk_Rad - w_Rad + w_Correction_Angle_Rad
    angle_Factor = math.cos(angle_Factor_rad)

    gs = math.sqrt ((tas**2) + (v**2) - ((2*tas*v) * math.cos(trk_Rad - (w_Rad + w_Correction_Angle_Rad ))))

    gs = round(gs)



    #Time is calculated in hours then converted to hours and minutes


    if distance == 0:
        return hdg, gs
    else:
        time = dist / gs
        hours = int(time)
        minutes = int((time - hours) * 60)
        hhmm = ("{:02d}:{:02d}".format(hours, minutes))
        return hdg, gs, hhmm

