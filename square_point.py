from math import radians, cos, sin, sqrt, atan2, degrees


def generate_square_coordinates(coord1, coord2):
    # Convert latitude and longitude from degrees to radians.
    lat1, lon1 = radians(coord1[1]), radians(coord1[0])
    lat2, lon2 = radians(coord2[1]), radians(coord2[0])

    # Calculate the distance (in meters) between the two boundary coordinates using Haversine formula.
    R = 6371000  # Earth's radius in meters
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 *atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    # Determine the size of the square (side length) based on the distance.
    # You can adjust the factor to control the size of the square.
    square_side_length = distance * 0.5

    # Calculate the other two coordinates of the square.
    lat3 = lat1 + square_side_length / R
    lat4 = lat1 - square_side_length / R
    lon3 = lon1 + square_side_length / (R * cos(lat1))
    lon4 = lon1 - square_side_length / (R * cos(lat1))

    # Convert back to degrees and return the four square coordinates.
    square_coordinates = [(degrees(lon1), degrees(lat1)), (degrees(lon2), degrees(lat2)),
                          (degrees(lon3), degrees(lat3)), (degrees(lon4), degrees(lat4))]

    # Calculate central latitude and longitude.
    central_lat = sum(coord[1] for coord in square_coordinates) / 4
    central_lon = sum(coord[0] for coord in square_coordinates) / 4

    return square_coordinates, (central_lon, central_lat)

# Example usage with two boundary coordinates (longitude, latitude) of a county.
boundary_coordinate1 = (-148.963831, 65.881067) # top left
boundary_coordinate2 = (-147.045037, 65.881067) # top right

square_coordinates = generate_square_coordinates(boundary_coordinate1, boundary_coordinate2)
print(square_coordinates)



def generate_point_on_side(side, existing_points=[]):
    if side == 'top':
        # Random point on the top side
        random_latitude = random.uniform(buffer_zone.bounds[0], buffer_zone.bounds[2])
        random_longitude = buffer_zone.bounds[3] + random.uniform(0, 0.1)
    elif side == 'bottom':
        # Random point on the bottom side
        random_latitude = random.uniform(buffer_zone.bounds[0], buffer_zone.bounds[2])
        random_longitude = buffer_zone.bounds[1] - random.uniform(0, 0.1)
    elif side == 'left':
        # Random point on the left side
        random_latitude = buffer_zone.bounds[0] - random.uniform(0.1, 0.1)
        random_longitude = random.uniform(buffer_zone.bounds[1], buffer_zone.bounds[3])
    else:  # 'right'
        # Random point on the right side
        random_latitude = buffer_zone.bounds[2] + random.uniform(0.1, 0.1)
        random_longitude = random.uniform(buffer_zone.bounds[1], buffer_zone.bounds[3])