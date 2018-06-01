import tifffile as tiff
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from os import path
import pandas as pd
from shapely.wkt import loads

from constants import DEFAULT_DATA_DIR

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

class SatelliteImagery:
    def __init__(self, map_name, data_dir=DEFAULT_DATA_DIR):
        self._name = map_name
        self._data_dir = data_dir

    def get_image_name(self, band_type='RGB'):
        if band_type == 'RGB':
            name = path.join(self._data_dir, 'three_band', '{}.tif'.format(self._name))
        elif band_type in ['A', 'M', 'P']:
            name = path.join(self._data_dir, 'sixteen_band', '{}_{}.tif'.format(self._name, band_type))
        else:
            raise ValueError("band_type should be one of ['RGB', 'A', 'M', 'P']")
        if not path.exists(name):
            raise FileNotFoundError 
        return name

    def plot_band(self, band_type='RGB'):
        name = self.get_image_name(band_type)
        P = tiff.imread(name)
        tiff.imshow(P)
        plt.show()

    def plot_band_a(self):
        self.plot_band('A')

    def plot_band_p(self):
        self.plot_band('P')

    def plot_band_m(self):
        self.plot_band('M')

    def plot_band_rgb(self):
        self.plot_band('RGB')

    @run_once
    def _get_polygons(self):
        df = pd.read_csv(path.join(self._data_dir, 'train_wkt_v4.csv'))
        polygons_map = {}
        image = df[df.ImageId == self._name]
        for c_type in image.ClassType.unique():
            polygons_map[c_type] = loads(image[image.ClassType == c_type].MultipolygonWKT.values[0])
        self._polygons_map = polygons_map

    def plot_polygons(self):
        self._get_polygons()
        fig, ax = plt.subplots(figsize=(8, 8))
        # fig, ax = plt.subplots()

        # plotting, color by class type
        patches = []
        colors = []
        for p in self._polygons_map:
            for polygon in self._polygons_map[p]:
                mpl_poly = Polygon(np.array(polygon.exterior))
                #ax.add_patch(mpl_poly)
                patches.append(mpl_poly)
                colors.append(10*p)

        p = PatchCollection(patches, alpha=0.4)
        p.set_array(np.array(colors))
        ax.add_collection(p)
        # fig.colorbar(p, ax=ax)
        # ax.relim()
        ax.autoscale_view()
        plt.show()

if __name__ == "__main__":
    img = SatelliteImagery('6100_1_3')
    # img.plot_polygons()
    # img.plot_band_a()
    # img.plot_band_m()
    img.plot_band_rgb()