import requests
import csv
import pandas as pd
import time
import random
import sqlite3
import json


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
    time.sleep(random.uniform(1, 3))
    return response


def scrape_data(lat, lng):
    response = get_response_with_delay(lat, lng)
    if 'error' in response:
        return {
            'parcel_id': 'None',
            'state': 'None',
            'apn': 'None',
            'acreage': 'None',
            'parcel_address': 'None',
            'parcel_owner': 'None',
            'POLYGON': 'None'
        }
    else:
        parcels = response.get('parcels', [])
        if not parcels:
            return {
                'parcel_id': 'None',
                'state': 'None',
                'apn': 'None',
                'acreage': 'None',
                'parcel_address': 'None',
                'parcel_owner': 'None',
                'POLYGON': 'None'
            }
        else:
            parcel = parcels[0]  # Assuming you only want to retrieve data for the first parcel
            return {
                'parcel_id': parcel['parcel_data']['parcel_id'],
                'state': parcel['parcel_data']['state'],
                'apn': parcel['parcel_data']['apn'],
                'acreage': parcel['parcel_data']['acreage'],
                'parcel_address': parcel['parcel_data']['parcel_address'],
                'parcel_owner': parcel['parcel_data']['parcel_owner'],
                'POLYGON': parcel['parcel_data']['geom_as_wkt']
            }


df = pd.read_csv('buffer_points.csv')
results = []

# Loop through the DataFrame and call the scrape_data function for each coordinate
for _, row in df.iterrows():
    lat = row['lat']
    lng = row['lng']
    scraped_data = scrape_data(lat, lng)
    results.append(scraped_data)

# Convert the list of dictionaries to a DataFrame
df_parcels = pd.DataFrame(results, columns=['parcel_id', 'state', 'apn', 'acreage', 'parcel_address', 'parcel_owner', 'POLYGON'])

# Save the DataFrame to a CSV file
df_parcels.to_csv('parcel_info.csv', index=False)
polygon_vertices = [
    (-101.813784875329, 35.172456066025),
    (-101.813679269762, 35.1724562068822),
    (-101.813661139675, 35.1724751238405),
    (-101.813644457815, 35.1724878396618),
    (-101.813646279369, 35.1727859681255),
    (-101.813786818382, 35.1727857777297),
    (-101.813784875329, 35.172456066025)
]