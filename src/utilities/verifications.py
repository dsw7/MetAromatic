def verify_input_distance(distance):
    return bool(distance > 0.00)

def verify_input_angle(angle):
    return bool(0.00 <= angle <= 360.00)
