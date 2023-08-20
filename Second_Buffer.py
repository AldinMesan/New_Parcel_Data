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
    buffer_polygon = polygon.buffer(distance)

    buffer_points = []

    # Calculate points along the boundary of the buffer polygon at equal intervals
    for i in range(0, num_points):
        point_on_boundary = buffer_polygon.boundary.interpolate(i / num_points, normalized=True)
        buffer_points.append((point_on_boundary.x, point_on_boundary.y))

    return buffer_points


# Polygon vertices
polygon_vertices = [
    (-101.79553987431, 35.3090191916404),
    (-101.795486993006, 35.2945159538594),
    (-101.782048905939, 35.2944826309803),
    (-101.777676876069, 35.2944716474824),
    (-101.777576416348, 35.2944713938042),
    (-101.777636595966, 35.3090300262766),
    (-101.795381030267, 35.3090284543452),
    (-101.795539840892, 35.3090284222647),
    (-101.79553987431, 35.3090191916404)
]

# Create a shapely Polygon object
polygon = Polygon(polygon_vertices)

buffer_distance = 0.0001
# Find the four corners of the polygon
corners = find_polygon_corners(polygon)
# Find points on corners of the buffer polygon
buffer_points = find_points_on_corners(polygon, buffer_distance, num_points=12)
print("Buffer Points:", buffer_points)

df_buffer_points = pd.DataFrame(buffer_points, columns=['lng', 'lat'])

df_buffer_points.to_csv('buffer_points.csv', index=False)

df_coordinates = pd.read_csv('buffer_points.csv')

# Initialize lists to store the scraped data
parcel_responses = []
for index, row in df_coordinates.iterrows():
    lat = row['lat']
    lng = row['lng']
    response = get_response_with_delay(lat, lng)
    parcel_responses.append(response)

df_coordinates['parcel_data'] = parcel_responses

df_coordinates.to_csv('buffer_points_parcel_data.csv', index=False)

second_buffer_distance = 0.0002

# Find points on corners of the second buffer polygon
second_buffer_points = find_points_on_corners(polygon, second_buffer_distance, num_points=12)
print("Second Buffer Points:", second_buffer_points)

df_second_buffer_points = pd.DataFrame(second_buffer_points, columns=['lng', 'lat'])

# Append the points from the second buffer zone to the original DataFrame
df_combined_buffer_points = pd.concat([df_buffer_points, df_second_buffer_points])

# Save the combined DataFrame to a CSV file
df_combined_buffer_points.to_csv('combined_buffer_points.csv', index=False)

# Read the combined CSV file into a DataFrame
df_combined_coordinates = pd.read_csv('combined_buffer_points.csv')

# Initialize lists to store the scraped data for the second buffer zone
second_buffer_parcel_responses = []
for index, row in df_combined_coordinates.iterrows():
    lat = row['lat']
    lng = row['lng']
    response = get_response_with_delay(lat, lng)
    second_buffer_parcel_responses.append(response)

df_combined_coordinates['parcel_data'] = second_buffer_parcel_responses

df_combined_coordinates.to_csv('combined_buffer_points_parcel_data.csv', index=False)

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

# Extract x and y coordinates for the second buffer zone points if available
if second_buffer_points:
    second_buffer_x, second_buffer_y = zip(*second_buffer_points)
else:
    second_buffer_x, second_buffer_y = [], []

# Visualize the polygons and points for both buffer zones
x, y = polygon.exterior.xy
x_buf, y_buf = polygon.buffer(buffer_distance).exterior.xy

# Create a new subplot for the visualizations
plt.figure(figsize=(12, 6))

# First subplot: Original and First Buffer Zone Visualization
plt.subplot(1, 2, 1)
plt.plot(x, y, label='Original Polygon')
plt.plot(x_buf, y_buf, label='Buffer Polygon')
plt.scatter(buffer_x, buffer_y, color='red', label='Points on Buffer Corners')
plt.scatter(mid_x, mid_y, color='green', label='Midpoints')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Original and Buffer Polygon Visualization')
plt.legend()
plt.grid(True)

# Second subplot: Second Buffer Zone Visualization
plt.subplot(1, 2, 2)
# Visualize the second buffer polygon
x_second_buf, y_second_buf = polygon.buffer(second_buffer_distance).exterior.xy
plt.plot(x, y, label='Original Polygon')
plt.plot(x_second_buf, y_second_buf, label='Second Buffer Polygon',
         linestyle='dashed')  # Dashed line for differentiation
plt.scatter(buffer_x, buffer_y, color='red', label='Points on Buffer Corners (1st Buffer)')
plt.scatter(mid_x, mid_y, color='green', label='Midpoints (1st Buffer)')
plt.scatter(second_buffer_x, second_buffer_y, color='blue', label='Points on Buffer Corners (2nd Buffer)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Second Buffer Polygon Visualization')
plt.legend()
plt.grid(True)

plt.tight_layout()  # To adjust spacing between subplots
plt.show()
