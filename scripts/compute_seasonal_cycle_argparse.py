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
plt.style.use('ggplot')
import argparse

def main():
	# Initialize the argument parser with a description of the code that will
	# show up upon calling --help
	ap = argparse.ArgumentParser(
		description="computes the mean seasonal cycle of surface temperature \
		in a CESM-LE simulation given latitude and longitude bounds")
	# Add arguments for inputting latitude and longitude bounds.
	# nargs tells how many arguments should come after an option (min max)
	# required tells the parser whether or not it should expect this option
	# type sets the type (so we don't have to explicitly force int() like 
	# with sys.argv)
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

	# + + + Main body + + +
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
	ds = xr.open_dataset('../data/CESM_LE.TS.002.1990-01.2000-12.nc')
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
	directory = '../output_figs/'
        if not os.path.exists(directory):
            os.makedirs(directory)
	fileName = ('mean_seasonal_cycle_lat' + str(LAT_BNDS[0]) + '_to_' +
		str(LAT_BNDS[1]) + '_lon' + str(LON_BNDS[0]) + '_to_' + 
		str(LON_BNDS[1]) + '.png')
	plt.savefig(directory + fileName, bbox_inches='tight', pad_inches=1,
                    transparent=False, dpi=300)
	# Show to user if optional flag is used.
	if args['plot']:
		plt.show()

if __name__ == '__main__':
	main()
