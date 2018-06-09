import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Data was collected in epsg:2274, the TN State Plane, which is defined in ft! Need to convert to lat long for most developers' purposes to WGS 84 epsg:4326. There is a slight precision loss (but by the smallest of margins (~ 10 cm)) Current GeoJSON spec has removed the crs attribute (geopandas still writes one anyways), and GeoJSON must be in WGS 84 spec!

def reproject_to_wgs_84(input_df):
    geometry = [Point(xy) for xy in zip(input_df.X, input_df.Y)]
    crs = {'init': 'epsg:2274'} #http://www.spatialreference.org/ref/epsg/2274/
    geo_trees_df = gpd.GeoDataFrame(input_df, crs=crs, geometry=geometry)
    geo_trees_df = geo_trees_df.to_crs({'init': 'epsg:4326'}) #WGS
    return geo_trees_df

if __name__ == "__main__":
    trees_df = pd.read_csv('data/trees/future_trees.csv', index_col=0)
    geo_trees_df = reproject_to_wgs_84(trees_df)
    geo_trees_df.to_file(driver='GeoJSON', filename='data/trees/trees.geojson')

    future_trees_df = pd.read_csv('data/trees/future_trees.csv', index_col=0)
    geo_future_trees_df = reproject_to_wgs_84(future_trees_df)
    geo_future_trees_df.to_file(driver='GeoJSON', filename='data/trees/future_trees.geojson')