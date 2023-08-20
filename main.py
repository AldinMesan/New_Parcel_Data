import csv
import random
import requests
import shapely
from shapely import unary_union, GeometryCollection
from shapely.geometry import Point, Polygon
import geopandas as gpd
import time
import matplotlib.pyplot as plt
from shapely.ops import cascaded_union


# Function to get API response for a given lat and lng
def get_response(lat, lng):
    headers = {
        'X-Auth-Token': 'sajY_zirdieU8d8WfsCn',
        'X-Auth-Email': 'finn.51@gmail.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183',
    }
    url = f'https://green.parcels.id.land/parcels/parcels/by_location.json?lng={lng}&lat={lat}'
    response = requests.get(url, headers=headers)
    return response.json()


# Coordinates for the polygon vertices
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

# Initialize the list to store polygons
polygons_list = []
generated_parcel_ids = []
# Create a Shapely Polygon object for the buffer zone.
buffer_zone = Polygon(polygon_vertices)

# Generate new random points within the buffer zone but outside the polygon.
num_new_points = 4
new_points = []


# Function to check if a point is already in the new_points list
def is_duplicate(point):
    for p in new_points:
        if p.equals(point):
            return True
    return False


# Function to check if a polygon is already in the polygons_list
def is_polygon_duplicate(polygon):
    for poly in polygons_list:
        if poly.equals(polygon):
            return True
    return False


# Generate three new points
while len(new_points) < num_new_points:
    random_longitude = random.uniform(buffer_zone.bounds[0], buffer_zone.bounds[2])
    random_latitude = random.uniform(buffer_zone.bounds[1], buffer_zone.bounds[3])
    random_point = Point(random_longitude, random_latitude)

    if not random_point.within(buffer_zone) and not any(random_point.within(polygon) for polygon in polygons_list):
        new_points.append(random_point)


# Function to generate a random point on a side of the buffer zone
def generate_point_on_side(side, existing_points=[]):
    if side == 'top':
        # Random point on the top side
        random_latitude = buffer_zone.bounds[3] + random.uniform(0, 0.1)
        random_longitude = random.uniform(buffer_zone.bounds[0], buffer_zone.bounds[2])
    elif side == 'bottom':
        # Random point on the bottom side
        random_latitude = buffer_zone.bounds[1] - random.uniform(0, 0.1)
        random_longitude = random.uniform(buffer_zone.bounds[0], buffer_zone.bounds[2])
    elif side == 'left':
        # Random point on the left side
        random_latitude = random.uniform(buffer_zone.bounds[1], buffer_zone.bounds[3])
        random_longitude = buffer_zone.bounds[0] - random.uniform(0, 0.1)  # Corrected this line
    else:  # 'right'
        # Random point on the right side
        random_latitude = random.uniform(buffer_zone.bounds[1], buffer_zone.bounds[3])
        random_longitude = buffer_zone.bounds[2] + random.uniform(0, 0.1)  # Corrected this line

    new_point = Point(random_longitude, random_latitude)

    # Check if the new point is too close to any existing points
    for point in existing_points:
        if new_point.distance(point) < 0.001:  # Adjust the threshold as needed
            return generate_point_on_side(side, existing_points)  # Generate a new point

    # Check if the new point is the same as any of the previous side points
    if any(point.within(new_point.buffer(0.001)) for point in new_points):
        return generate_point_on_side(side, existing_points)  # Generate a new point

    return new_point

    # return Point(random_longitude, random_latitude)


# Generate four different points on four sides of the buffer zone
side_points = []
for side in ['top', 'bottom', 'left', 'right']:
    side_point = generate_point_on_side(side)
    side_points.append(side_point)
# Display the four different points on four sides of the buffer zone
print("Points on Four Sides of Buffer Zone:")
for idx, point in enumerate(side_points):
    print(f"Point {idx + 1}: {point}")

# Create a GeoDataFrame with the buffer zone.
gdf_buffer_zone = gpd.GeoDataFrame(geometry=[buffer_zone])

# Display the buffer zone and new points within it.
print("Buffer Zone:")
print(gdf_buffer_zone.head())
'''
print("New Points Within Buffer Zone:")
for idx, point in enumerate(new_points):
    print(f"New Point {idx + 1}: {point}")
'''

# Get parcel information for the buffer center using the get_response function.
response_data = get_response(buffer_zone.centroid.y, buffer_zone.centroid.x)
print("Parcel Information for Buffer Center:")
print(response_data)


def get_response_with_delay(lat, lng):
    response = get_response(lat, lng)
    time.sleep(random.uniform(1, 3))
    return response


# Function to extract parcel_id from the API response
def extract_parcel_id(response):
    if 'parcels' in response and len(response['parcels']) > 0:
        parcel_id = response['parcels'][0]['parcel_data'].get('parcel_id')
        return parcel_id
    return None


for point in new_points:
    while True:
        lat = point.y
        lng = point.x

        response = get_response_with_delay(lat, lng)
        # Process the response data
        print("Parcel Information for Points Around Buffer Center:")
        print(response)

        # Extract the parcel_id from the API response
        parcel_id = extract_parcel_id(response)

        if parcel_id:
            if parcel_id not in generated_parcel_ids:
                # Add the parcel_id to the list of generated parcel_ids
                generated_parcel_ids.append(parcel_id)
                # The point has a different parcel_id, so add it to polygons_list
                parcel_data = response['parcels'][0]['parcel_data']
                polygon_wkt = parcel_data.get('geom_as_wkt')
                if polygon_wkt:
                    polygon = shapely.wkt.loads(polygon_wkt)
                    if polygon.is_valid and not is_polygon_duplicate(polygon):
                        polygons_list.append(polygon)

                    else:
                        print(f"Invalid or duplicate polygon for the point: ({lat}, {lng})")
                else:
                    print(f"No 'geom_as_wkt' found for the point: ({lat}, {lng})")
                break
            else:
                # The point has the same parcel_id as a previously generated point, generate a new point
                point = generate_point_on_side(side, new_points)
        else:
            print(f"No parcel data found for the point: ({lat}, {lng})")
            break

# Merge the polygons in the polygons_list
merged_polygon = unary_union(polygons_list)

# Check if the merged_polygon is a single Polygon or a GeometryCollection
if isinstance(merged_polygon, Polygon):
    # Single Polygon, print its exterior coordinates
    formatted_coords = ', '.join([f"({coord[0]:.14f}, {coord[1]:.14f})" for coord in merged_polygon.exterior.coords])
    print(f"Merged Polygon: [{formatted_coords}]")
elif isinstance(merged_polygon, GeometryCollection):
    # GeometryCollection, iterate through the geometries and print their exterior coordinates
    for polygon in merged_polygon.geoms:
        formatted_coords = ', '.join([f"({coord[0]:.14f}, {coord[1]:.14f})" for coord in polygon.exterior.coords])
        print(f"Merged Polygon: [{formatted_coords}]")
else:
    print("Merged polygons are of unknown type.")

print(merged_polygon)

# Create a GeoDataFrame with the merged polygon
gdf_merged_polygon = gpd.GeoDataFrame(geometry=[merged_polygon])

# Plot the merged polygon
fig, ax = plt.subplots(figsize=(10, 10))
gdf_buffer_zone.boundary.plot(ax=ax, color='red', linewidth=2, label='Buffer Zone')
gdf_merged_polygon.boundary.plot(ax=ax, color='blue', linewidth=2, label='Merged Polygon')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Buffer Zone and Merged Polygon')
ax.legend()
plt.show()
