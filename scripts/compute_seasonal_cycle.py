"""
Compute Seasonal Cycle
----------------------
Author  : Riley X. Brady
Date    : June 14, 2018
Contact : riley.brady@colorado.edu

Compute the mean seasonal cycle of surface temperature given some bounds of
latitude and longitude.
"""
import os
import numpy as np
import numpy.polynomial.polynomial as poly
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
from shapely.geometry.polygon import LinearRing
plt.style.use('ggplot')

def main():
	# Change these variables directly to alter your analysis.
	LON_BNDS = [180, 240]
	LAT_BNDS = [-5, 5]
	# Remind to gunzip if needed
	if not os.path.exists('../data/CESM_LE.TS.002.1990-01.2000-12.nc'):
		raise OSError(
			'''
			It looks like you haven't gunzipped the data provided. Please do so
			before running this analysis by doing the following:

			cd ../data
			gunzip CESM_LE.TS.002.1990-01.2000-12.nc.gz
			'''
			)
	# Load data
	ds = xr.open_dataset('../data/CESM_LE.TS.002.1990-01.2000-12.nc')
	# Extract region of interest
	ds = ds.sel(lat=slice(LAT_BNDS[0], LAT_BNDS[1]), lon=slice(LON_BNDS[0], 
		LON_BNDS[1]))
	# Take mean over region
	ds = ds.stack(gridpoints=['lat','lon']).mean('gridpoints')
	# Remove any trend
	x = np.arange(0, len(ds['TS']))
	coefs = poly.polyfit(x, ds['TS'].values, deg=4)
	fit = poly.polyval(x, coefs)
	ds = ds - fit + ds['TS'].mean('time')
	# Find mean seasonal cycle
	ds = ds.groupby('time.month').mean('time')['TS']
	# Plot seasonal cycle and save as figure in output directory
	f, ax = plt.subplots()
	ds.plot.line('-o')
	title = ('Seasonal Cycle of Surface Temperature' + '\n' + '[Lat: ' +
		str(LAT_BNDS[0]) + ' - ' + str(LAT_BNDS[1]) + '; Lon: ' + 
		str(LON_BNDS[0]) + ' - ' + str(LON_BNDS[1]) + ']')
	ax.set_title(title)
	ax.set_ylabel('Surface Temperature [$^{o}\mathrm{C}$]')
	directory = '../output_figs/'
        if not os.path.exists(directory):
            os.makedirs(directory)	
        fileName = ('mean_seasonal_cycle_lat' + str(LAT_BNDS[0]) + '_to_' +
		str(LAT_BNDS[1]) + '_lon' + str(LON_BNDS[0]) + '_to_' + 
		str(LON_BNDS[1]) + '.png')
	plt.savefig(directory + fileName, bbox_inches='tight', pad_inches=1,
                    transparent=False, dpi=300)
	#plt.show()

if __name__ == '__main__':
	main()
