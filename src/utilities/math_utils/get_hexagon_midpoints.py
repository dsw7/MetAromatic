def get_hexagon_midpoints(x_coord, y_coord, z_coord):
    """
    Function for computing midpoints between vertices in a hexagon
    Parameters:
        x, y, z -> list objects of x, y, and z hexagon coordinates
    Returns:
        x_mid, y_mid, z_mid -> a list of x, y, and z hexagon midpoint coordinates
    """
    x_f = x_coord[1:] + [x_coord[0]]
    y_f = y_coord[1:] + [y_coord[0]]
    z_f = z_coord[1:] + [z_coord[0]]

    x_mid = [0.5 * (a + b) for a, b in zip(x_coord, x_f)]
    y_mid = [0.5 * (a + b) for a, b in zip(y_coord, y_f)]
    z_mid = [0.5 * (a + b) for a, b in zip(z_coord, z_f)]

    return x_mid, y_mid, z_mid
