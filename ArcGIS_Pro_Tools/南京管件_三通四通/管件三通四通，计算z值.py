def f(rollz, rollx, zx, zy):
    # dir - x
    if -45 <= rollz <= 45 or 135 <= rollz <= 180 or -180 <= rollz <= -135:
        if 0 <= zx <= 90:
            res = rollx + zx
        elif 90 < zx <= 180:
            res = 180 - zx + rollx
        elif 0 > zx >= -90:
            res = rollx + zx
        elif -180 <= zx < -90:
            res = rollx - (180 + zx)
    else:
        if 0 <= zy <= 90:
            res = rollx + zy
        elif 90 < zy <= 180:
            res = 180 - zy + rollx
        elif 0 > zy >= -90:
            res = rollx + zy
        elif -180 <= zy < -90:
            res = rollx - (180 + zy)
    return res

f(!ROLL_Z_!, !ROLL_X_!, !roll_z_adjust_!, !roll_z_adjust_y!)