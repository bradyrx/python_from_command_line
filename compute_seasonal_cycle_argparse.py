"""
Compute Seasonal Cycle
----------------------
Author  : Riley X. Brady
Date    : June 14, 2018
Contact : riley.brady@colorado.edu

Compute the mean seasonal cycle of surface temperature given some bounds of
latitude and longitude.
"""
import numpy as np
import numpy.polynomial.polynomial as poly
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
from shapely.geometry.polygon import LinearRing
plt.style.use('fivethirtyeight')
import argparse

def main():
	# Initialize the argument parser with a description of the code that will
	# show up upon calling --help
	ap = argparse.ArgumentParser(
		description="computes the mean seasonal cycle of a CESM-LENS simulation \
		given latitude and longitude bounds.")
	# Add arguments for inputting latitude and longitude bounds.
	ap.add_argument('--lat', nargs=2, required=True, type=int,
		help="input latitude bounds separated by a space.")
	ap.add_argument('--lon', nargs=2, required=True, type=int,
		help="input longitude bounds (0-360) separated by a space.")
	# Add optional flag to output a plot to the screen. The action flag says to
	# store a True boolean if this flag is mentioned.
	ap.add_argument('-p', '--plot', required=False,
		action='store_true',
		help="whether or not to show the resulting plot to the user")
	# Create dictionary of input arguments
	args = vars(ap.parse_args())
	x0, x1 = args['lon']
	y0, y1 = args['lat']

	# Main body
	ds = xr.open_dataset('data/CESM_LE.TS.002.1990-01.2000-12.nc')
	# Extract region of interest
	ds = ds.sel(lat=slice(y0, y1), lon=slice(x0, x1))
	# Take mean over region
	ds = ds.stack(gridpoints=['lat','lon']).mean('gridpoints')
	# Remove any trend
	x = np.arange(0, len(ds['TS']))
	coefs = poly.polyfit(x, ds['TS'].values, deg=4)
	fit = poly.polyval(x, coefs)
	ds = ds - fit + ds['TS'].mean('time')
	# Find mean seasonal cycle
	ds = ds.groupby('time.month').mean('time')['TS']
	# Plot seasonal cycle and save as figure in current directory
	f, ax = plt.subplots()
	ds.plot.line('-o')
	title = ('Seasonal Cycle of Surface Temperature' + '\n' + '[Lat: ' +
		str(y0) + ' - ' + str(y1) + '; Lon: ' + 
		str(x0) + ' - ' + str(x1) + ']')
	ax.set_title(title)
	ax.set_ylabel('Surface Temperature [$^{o}\mathrm{C}$]')
	plt.savefig('mean_seasonal_cycle.png', bbox_inches='tight', pad_inches=1,
                    transparent=False, dpi=300)
	# Show to user if optional flag is used.
	if args['plot']:
		plt.show()

if __name__ == '__main__':
	main()
