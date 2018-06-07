import json

import requests
import pandas as pd
import numpy as np


def get_and_write_trees_data():
    # determined from website usage for bounds
    knoxville_bounds = [
        [2509746.9416408655, 2659731.9416408655], # lat
        [567692.794594815, 639302.794594815], # long
    ]
    query_area = 1000.0

    latitudes = np.linspace(knoxville_bounds[0][0], knoxville_bounds[0][1], math.ceil((knoxville_bounds[0][1] - knoxville_bounds[0][0]) / query_area))
    longitudes = np.linspace(knoxville_bounds[1][0], knoxville_bounds[1][1], math.ceil((knoxville_bounds[1][1] - knoxville_bounds[1][0]) / query_area))

    print(len(latitudes), len(longitudes), 'total queries', len(latitudes) * len(longitudes))
    # Caching will be very usefull (but request_cache doesn't work.......)

    geo_data = {}
    session = requests.session()
    session.get('http://www.kgis.org/maps/treeinventory.html') # get cookies

    for latitude in latitudes:
        for longitude in longitudes:
            if (latitude, longitude) in geo_data:
                continue
            geo_data[(latitude, longitude)] = query_tree_inventory(latitude, longitude, query_area, session)

    df = pd.concat([_['parcels'] for _ in geo_data.values()])
    df['geometry'] = df['geometry'].apply(lambda a: json.dumps(a.tolist()))
    parcels_dedup_df = df.drop_duplicates()
    parcels_dedup_df.to_csv('../data/trees/parcels.csv')

    df = pd.concat([_['trees'] for _ in geo_data.values()])
    trees_dedup_df = df.drop_duplicates()
    trees_dedup_df.to_csv('../data/trees/trees.csv')

    df = pd.concat([_['future_trees'] for _ in geo_data.values()])
    future_trees_dedup_df = df.drop_duplicates()
    future_trees_dedup_df.to_csv('../data/trees/future_trees.csv')
    return {'parcels': parcels_dedup_df, 'trees': trees_dedup_df, 'future_trees': trees_dedup_df}


def query_tree_inventory(latitude, longitude, area_square, session):
    query = {
        'returnGeometry': True,
        'spatialRel': 'esriSpatialRelIntersects',
        'geometry': json.dumps({
            "rings":[[
                [latitude, longitude+area_square],
                [latitude+area_square, longitude+area_square],
                [latitude+area_square, longitude],
                [latitude, longitude],
                [latitude, longitude+area_square]
            ]],
            "spatialReference":{"wkid":2915}
        }),
        'geometryType': 'esriGeometryPolygon',
        'inSR': 2915,
        'outFields': '*',
        'outSR': 2915
    }

    headers = {
        'Referer': 'http://www.kgis.org/maps/treeinventory.html'
    }

    try:
        response = session.get('http://www.kgis.org/proxy/proxy.ashx', params={
                'http://www.kgis.org/arcgis/rest/services/Maps/GlobalSearch/MapServer/0/query?f': 'json',
                **query
        }, headers=headers)
        parsels = response.json()
        response = session.get('http://www.kgis.org/proxy/proxy.ashx', params={
                'http://www.kgis.org/arcgis/rest/services/Maps/TreeInventory/MapServer/0/query?f': 'json',
                **query
        }, headers=headers)
        trees = response.json()
        response = session.get('http://www.kgis.org/proxy/proxy.ashx', params={
                'http://www.kgis.org/arcgis/rest/services/Maps/TreeInventory/MapServer/1/query?f': 'json',
                **query
        }, headers=headers)
        future_trees = response.json()
    except json.JSONDecodeError as error:
        print(response.status_code)
        print(response.request.url)
        print(response.content)
        raise Exception()

    rows = []
    for feature in parsels['features']:
        row = feature['attributes'].copy()
        row['geometry'] = np.array(feature['geometry']['rings'])
        rows.append(row)
    parcels_df = pd.DataFrame(rows)
    if rows:
        parcels_df = parcels_df.set_index('PARCELID_1')

    rows = []
    for feature in trees['features']:
        row = feature['attributes'].copy()
        rows.append(row)
    trees_df = pd.DataFrame(rows)
    if rows:
        trees_df = trees_df.set_index('OBJECTID')

    rows = []
    for feature in future_trees['features']:
        row = feature['attributes'].copy()
        rows.append(row)
    future_trees_df = pd.DataFrame(rows)
    if rows:
        future_trees_df = future_trees_df.set_index('OBJECTID')

    return {'parcels': parcels_df, 'trees': trees_df, 'future_trees': future_trees_df}
