from shapely.geometry import Polygon, Point, LineString, MultiPoint
import matplotlib.pyplot as plt
import requests
import csv
import pandas as pd
import time
import random

def get_response(lat, lng):
    headers = {
        'X-Auth-Token': 'sajY_zirdieU8d8WfsCn',
        'X-Auth-Email': 'finn.51@gmail.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183',
    }
    url = f'https://green.parcels.id.land/parcels/parcels/by_location.json?lng={lng}&lat={lat}'
    response = requests.get(url, headers=headers)
    return response.json()


def get_response_with_delay(lat, lng):
    response = get_response(lat, lng)
    time.sleep(random.uniform(0.5, 1))
    return response


def find_polygon_corners(polygon):
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')

    for x, y in polygon.exterior.coords:
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)

    corners = [
        (min_x, min_y),  # Bottom-left corner
        (max_x, min_y),  # Bottom-right corner
        (max_x, max_y),  # Top-right corner
        (min_x, max_y),  # Top-left corner
    ]
    return corners


def find_midpoints(corners):
    midpoints = []
    num_corners = len(corners)
    for i in range(num_corners):
        x_avg = (corners[i][0] + corners[(i + 1) % num_corners][0]) / 2
        y_avg = (corners[i][1] + corners[(i + 1) % num_corners][1]) / 2
        midpoints.append((x_avg, y_avg))
    return midpoints


def find_points_on_corners(polygon, distance, num_points=12):
    # Create buffer polygon
    buffer_polygon = polygon.buffer(distance)

    buffer_points = []

    # Calculate points along the boundary of the buffer polygon at equal intervals
    for i in range(0, num_points):
        point_on_boundary = buffer_polygon.boundary.interpolate(i / num_points, normalized=True)
        buffer_points.append((point_on_boundary.x, point_on_boundary.y))

    return buffer_points


# Polygon vertices
polygon_vertices = [
    (-101.813784875329, 35.172456066025),
    (-101.813679269762, 35.1724562068822),
    (-101.813661139675, 35.1724751238405),
    (-101.813644457815, 35.1724878396618),
    (-101.813646279369, 35.1727859681255),
    (-101.813786818382, 35.1727857777297),
    (-101.813784875329, 35.172456066025)
]

# Create a shapely Polygon object
polygon = Polygon(polygon_vertices)

# Desired buffer distance
buffer_distance = 0.0001
# Find the four corners of the polygon
corners = find_polygon_corners(polygon)
# Find points on corners of the buffer polygon
buffer_points = find_points_on_corners(polygon, buffer_distance, num_points=12)
print("Buffer Points:", buffer_points)
# Convert buffer points to a DataFrame
df_buffer_points = pd.DataFrame(buffer_points, columns=['lng', 'lat'])

# Save the DataFrame to a CSV file
df_buffer_points.to_csv('buffer_points.csv', index=False)
# Read the CSV file into a DataFrame
df_coordinates = pd.read_csv('buffer_points.csv')

# Initialize lists to store the scraped data
parcel_responses = []
for index, row in df_coordinates.iterrows():
    lat = row['lat']
    lng = row['lng']
    response = get_response_with_delay(lat, lng)
    parcel_responses.append(response)

# Add the parcel_responses list as a new column in the DataFrame
df_coordinates['parcel_data'] = parcel_responses

# Save the DataFrame to a new CSV file with the parcel data
df_coordinates.to_csv('buffer_points_parcel_data.csv', index=False)

# Extract x and y coordinates for scatter plot if points are available
if buffer_points:
    buffer_x, buffer_y = zip(*buffer_points)
else:
    buffer_x, buffer_y = [], []

# Calculate the midpoints between consecutive corners
midpoints = find_midpoints(corners)
print("Midpoints:", midpoints)
# Extract x and y coordinates for midpoints scatter plot if points are available
if midpoints:
    mid_x, mid_y = zip(*midpoints)
else:
    mid_x, mid_y = [], []
# Visualize the polygons
x, y = polygon.exterior.xy
x_buf, y_buf = polygon.buffer(buffer_distance).exterior.xy

plt.figure(figsize=(8, 6))
plt.plot(x, y, label='Original Polygon')
plt.plot(x_buf, y_buf, label='Buffer Polygon')
plt.scatter(buffer_x, buffer_y, color='red', label='Points on Buffer Corners')
plt.scatter(mid_x, mid_y, color='green', label='Midpoints')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Polygon and Buffer Polygon Visualization')
plt.legend()
plt.grid(True)
plt.show()

