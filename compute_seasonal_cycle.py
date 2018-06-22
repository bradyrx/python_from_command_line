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

def main():
	# Change these variables directly to alter your analysis.
	LON_BNDS = [180, 240]
	LAT_BNDS = [-5, 5]
	ds = xr.open_dataset('data/CESM_LE.TS.002.1990-01.2000-12.nc')
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
	# Plot seasonal cycle and save as figure in current directory
	f, ax = plt.subplots()
	ds.plot.line('-o')
	title = ('Seasonal Cycle of Surface Temperature' + '\n' + '[Lat: ' +
		str(LAT_BNDS[0]) + ' - ' + str(LAT_BNDS[1]) + '; Lon: ' + 
		str(LON_BNDS[0]) + ' - ' + str(LON_BNDS[1]) + ']')
	ax.set_title(title)
	ax.set_ylabel('Surface Temperature [$^{o}\mathrm{C}$]')
	plt.savefig('mean_seasonal_cycle.png', bbox_inches='tight', pad_inches=1,
                    transparent=False, dpi=300)

if __name__ == '__main__':
	main()