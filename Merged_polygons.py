from shapely.geometry import Polygon, Point, LineString, MultiPoint
import matplotlib.pyplot as plt
import requests
import csv
import pandas as pd
from shapely.wkt import loads
from shapely.geometry import MultiPolygon


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
# polygon_vertices = [
#    (-101.830037876095, 35.178138626423),
#    (-101.829703132988, 35.1781256793867),
#    (-101.829701398771, 35.1778606290531),
#    (-101.829699606065, 35.1775865816554),
#    (-101.829697900717, 35.1773259302299),
#    (-101.829714544802, 35.1773121251595),
#    (-101.830035143174, 35.1773108352077),
#    (-101.830368101361, 35.177309372873),
#    (-101.830654799592, 35.1773081063686),
#    (-101.830671402242, 35.1773216327745),
#    (-101.830672006827, 35.1775825218913),
#    (-101.830672892886, 35.1781104163247),
#    (-101.830640462973, 35.1781371436679)
#
# ]

polygon_vertices = [
    (-101.813784875329, 35.172456066025),
    (-101.813679269762, 35.1724562068822),
    (-101.813661139675, 35.1724751238405),
    (-101.813644457815, 35.1724878396618),
    (-101.813646279369, 35.1727859681255),
    (-101.813786818382, 35.1727857777297),
    (-101.813784875329, 35.172456066025)
 ]


# polygon_vertices = [
#     (-101.79553987431, 35.3090191916404),
#     (-101.795486993006, 35.2945159538594),
#     (-101.782048905939, 35.2944826309803),
#     (-101.777676876069, 35.2944716474824),
#     (-101.777576416348, 35.2944713938042),
#     (-101.777636595966, 35.3090300262766),
#     (-101.795381030267, 35.3090284543452),
#     (-101.795539840892, 35.3090284222647),
#     (-101.79553987431, 35.3090191916404)
# ]

# Define your polygon and buffer distances
polygon = Polygon(polygon_vertices)
buffer_distances = [0.00010, 0.00020, 0.01000]  # add more distances if needed


def create_buffer_points(polygon, buffer_distance, num_points=12):
    buffer_points = find_points_on_corners(polygon, buffer_distance, num_points)
    if not buffer_points:
        buffer_points = []
    return pd.DataFrame(buffer_points, columns=['lng', 'lat'])


def scrape_data_within_buffer(buffer_points_df):
    parcel_responses = []
    for index, row in buffer_points_df.iterrows():
        lat = row['lat']
        lng = row['lng']
        response = get_response(lat, lng)
        parcel_responses.append(response)
    return parcel_responses


def create_and_scrape_buffer_zones(polygon, buffer_distances, num_points=12):
    for buffer_distance in buffer_distances[:2]:  # Iterate through the first two buffer zones
        buffer_points_df = create_buffer_points(polygon, buffer_distance, num_points)
        parcel_responses = scrape_data_within_buffer(buffer_points_df)

        # Check if any response is not an error or empty
        valid_responses = [response for response in parcel_responses if response and ("errors" not in response)]

        if valid_responses:
            return buffer_points_df, parcel_responses

        # If no valid response is found in the first two buffer zones, proceed to the third buffer zone
    buffer_distance = buffer_distances[2]
    buffer_points_df = create_buffer_points(polygon, buffer_distance, num_points)
    parcel_responses = scrape_data_within_buffer(buffer_points_df)

    return buffer_points_df, parcel_responses


# Create and scrape buffer zones
buffer_points_df, parcel_responses = create_and_scrape_buffer_zones(polygon, buffer_distances)

if buffer_points_df is not None:
    buffer_points_df['parcel_data'] = parcel_responses

    buffer_points_df.to_csv('buffer_points_parcel_data1.csv', index=False)
else:
    print("No valid response found in any buffer zone. No CSV file will be created.")


merged_polygon = MultiPolygon([polygon])
# Iterate through the DataFrame and merge each polygon with the original one
for index, row in buffer_points_df.iterrows():
    lat = row['lat']
    lng = row['lng']
    response = get_response(lat, lng)
    if 'parcels' in response and len(response['parcels']) > 0:
        parcel_data = response['parcels'][0]['parcel_data']
        parcel_polygon_wkt = parcel_data['geom_as_wkt']
        parcel_polygon = loads(parcel_polygon_wkt)
        merged_polygon = merged_polygon.union(parcel_polygon)
    else:
        # print(f"No parcels found for lat={lat}, lng={lng}")
        continue

if buffer_points_df is not None:
    # Add the parcel_responses list as a new column in the DataFrame
    buffer_points_df['parcel_data'] = parcel_responses

    # Save the DataFrame to a new CSV file with the parcel data
    buffer_points_df.to_csv('buffer_points_parcel_data1.csv', index=False)

    # Plot the original polygon in blue
    x, y = polygon.exterior.xy
    plt.plot(x, y, color='blue')

    # Check if merged_polygon is a MultiPolygon or a single Polygon
    if isinstance(merged_polygon, MultiPolygon):
        for polygon in merged_polygon.geoms:
            x, y = polygon.exterior.xy
            plt.plot(x, y, color='red')
    else:
        x, y = merged_polygon.exterior.xy
        plt.plot(x, y, color='red')

    # Plot the buffer points in green
    plt.scatter(buffer_points_df['lng'], buffer_points_df['lat'], color='green', marker='x', label='Buffer Points')

    # Add legend
    plt.legend()

    # Show the plot
    plt.show()
else:
    print("No valid response found in any buffer zone. No CSV file will be created.")

'''
print(merged_polygon)
# Plot the original polygon in blue
x, y = polygon.exterior.xy
plt.plot(x, y, color='blue')

# Check if merged_polygon is a MultiPolygon or a single Polygon
if isinstance(merged_polygon, MultiPolygon):
    for polygon in merged_polygon.geoms:
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='red')
else:
    x, y = merged_polygon.exterior.xy
    plt.plot(x, y, color='red')

plt.show()
'''