# How data was collected

`GET` request to "http://www.kgis.org/proxy/proxy.ashx" with the
following headers and query string. The script querys square blocks of
size 1000x1000. I heavily used caching so that in development I was
not rough on the api.

```python
query_params = {
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

parcels_query_string = {
    **query_params,
    'http://www.kgis.org/arcgis/rest/services/Maps/GlobalSearch/MapServer/0/query?f': 'json'
}

trees_query_string = {
    **query_params,
    'http://www.kgis.org/arcgis/rest/services/Maps/TreeInventory/MapServer/0/query?f': 'json'
}

future_trees_query_string = {
    **query_params,
    'http://www.kgis.org/arcgis/rest/services/Maps/TreeInventory/MapServer/1/query?f': 'json'
}

headers = {'Referer': 'http://www.kgis.org/maps/treeinventory.html'}
```

# File Meanings

## parcels.csv

Parcels csv is a collection of the properties owned in Knoxville TN.

## trees.csv

Trees csv is a collection of all the trees being tracked in Knoxville TN

## future_trees.csv

Future trees is a collection of future trees to plant??

 

