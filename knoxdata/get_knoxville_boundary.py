import geopandas as gpd

# Download the file from TN's Open Data ArcGIS portal tn_city_boundaries = requests.get('https://opendata.arcgis.com/datasets/cf079cf338ab4910ab7765da40a11a06_0.geojson')

gdf = gpd.read_file('data/tn_city_boundaries.geojson') #spec is already WGS 84
print(gdf.head)
knoxville_boundary = gdf.query('NAME == "Knoxville"')
print(knoxville_boundary.head)

knoxville_boundary.to_file(driver='GeoJSON', filename='data/knoxville_boundary.geojson')
