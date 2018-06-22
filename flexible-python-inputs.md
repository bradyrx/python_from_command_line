+++
date = "2018-06-14T12:00:00"
draft = false
tags = ["python", "data analysis", "climate", "tutorial"]
title = "Flexible python scripts from the command line (Tutorial)"
math = true
summary = """
Create python scripts for data analysis with flexible inputs from the command line.
"""

[header]
image = ""
caption = ""

+++

# Preface
---
For this tutorial, I assume that you can handle installing python and some packages on your machine, can open a text editor and write a python script from scratch (or edit the one I provide), and can use the command line to move to a folder and execute a script. 

Here is an outline of the tutorial (with links to that part of the page):

1. [Dataset and Packages](#dataset) 

2. [Analysis Script](#analysis)

3. [Flexible Header Variables](#flexible)

4. [Leveraging `sys` to Run from Command Line](#sys)

5. [Using `argparse` for More Options and Documentation](#argparse)

6. [Conclusions](#conclusion)

Although my goal here is to teach about creating flexible and reproducable scripts in python for climate data analysis, I hope that readers might also pick up some ideas about visualization and leveraging `xarray` for very easy data analysis.

---
## Dataset and Packages <a name="dataset"></a>
---
If you want to try out some ideas from this post, make sure you have a version of python installed (ideally python3, since the community is moving there soon anyway). You will need to install `xarray`, `netcdf4`, `numpy`, `matplotlib`, and `argparse`. Everything else needed should be included in a default installation of python.

The data used is output from one simulation of the Community Earth System Model Large Ensemble ([CESM-LE](https://journals.ametsoc.org/doi/abs/10.1175/BAMS-D-13-00255.1)). I took monthly surface temperature (TS) output from the atmospheric component of the coupled model (a very technical description of the Community Atmosphere Model can be found [here](http://www.cesm.ucar.edu/models/cesm1.0/cam/docs/description/cam5_desc.pdf)) and sliced it down to January 1990 through December 2000 to make the file small enough. 

You can download the data used in this tutorial and example scripts from my Github repository [here](https://github.com/bradyrx/python_from_command_line).

---
## Analysis Script <a name="analysis"></a>
---
Let's first write a working script to which we'll later return to make it flexible from the command line. Our goal is to take modeled atmospheric surface temperature (TS) and compute the mean seasonal cycle over some region of the world. We'll make it flexible by allowing the user to pass differing latitude/longitude bounds into the script without having to directly edit it.

Since the focus of this tutorial is on command line input, I won't spend as much time on the code itself. You can find the full `compute_seasonal_cycle.py` in my Github repository [here](https://github.com/bradyrx/python_from_command_line). Feel free to suggest changes to the repository or email me with any comments or questions.

First, let's load in the dataset and look at its properties:

```python
import xarray as xr
ds = xr.open_dataset('../data/CESM_LE.TS.002.1990-01.2000-12.nc')
print(ds)

<xarray.Dataset>
Dimensions:  (lat: 192, lon: 288, time: 132)
Coordinates:
  * lat      (lat) float64 -90.0 -89.06 -88.12 -87.17 -86.23 -85.29 -84.35 ...
  * lon      (lon) float64 0.0 1.25 2.5 3.75 5.0 6.25 7.5 8.75 10.0 11.25 ...
  * time     (time) datetime64[ns] 1990-01-31 1990-02-28 1990-03-31 ...
Data variables:
    TS       (time, lat, lon) float32 -32.9582 -32.2339 -32.1969 -32.1775 ...
```

This is a pretty straightforward dataset. We have three dimensions: 

1. latitude in degrees north, which ranges from -90 to 90 by roughly 1 degree 
2. longitude in degrees east, from 0 to 360 in 1.25 degree increments
3. time in months from 1990 to 2000.

After importing our data, we will use `xarray`'s select feature and `slice` to extract our latitude and longitude bounds of interest. In our test case, we extract a region over the tropical Pacific Ocean (Figure 1).

<center>
{{< figure src="/post/command_line_python/region_example.png" title="Region we extract in our test script." >}}
</center>

Let's go ahead and extract that region:

```python
ds = ds.sel(lat=slice(-5, 5), lon=slice(180, 240))
print(ds)

<xarray.Dataset>
Dimensions:  (lat: 10, lon: 49, time: 132)
Coordinates:
  * lat      (lat) float64 -4.241 -3.298 -2.356 -1.414 -0.4712 0.4712 1.414 ...
  * lon      (lon) float64 180.0 181.2 182.5 183.8 185.0 186.2 187.5 188.8 ...
  * time     (time) datetime64[ns] 1990-01-31 1990-02-28 1990-03-31 ...
Data variables:
    TS       (time, lat, lon) float32 27.9247 27.8295 27.7346 27.6447 ...
```

Note that our lat and lon dimensions decreased substantially. Generally, I would area-weight this since the grid cell areas vary with latitude, but we'll just do a simple mean over latitude and longitude to generate our time series (Figure 2).

```python
ds = ds.stack(gridpoints=['lat','lon']).mean('gridpoints')
f, ax = plt.subplots(figsize=(8,3))
ds1['TS'].plot.line('k-')
ax.set_title('Monthly Tropical Pacific Surface Temperature (1990 - 2000)')
```

<center>
{{< figure src="/post/command_line_python/monthly_tropical_temperature.png" title="Time series of TS in the tropical Pacific after taking the mean over the region." >}}
</center>

Lastly, we will find the mean seasonal cycle of this time series (the goal of this analysis). We first need to remove any trend that exists in the time series. To exactly nail down the trend, we would need to remove the CESM-LE ensemble mean, but we do not have access to the full ensemble for this tutorial. Instead, we can approximately remove the trend by subtracting out a 4th-order polynomial fit (Figure 3). 


```python
import numpy.polynomial.polynomial as poly
x = np.arange(0, len(ds['TS']))
# Find polynomial coefficients
coefs = poly.polyfit(x, ds['TS'], deg=4)
# Create time series of trend with these coefficients 
# to remove from the raw time series.
fit = poly.polyval(x, coefs)
# Remove the fit but add back in the mean to maintain
# the magnitude, which we're interested in.
ds = ds - fit + ds['TS'].mean('time')
```

<center>
{{< figure src="/post/command_line_python/detrending.png" title="The top panel shows our time series created in Figure 2 with the 4th-order fit in red. The bottom panel shows our time series after removing that fit and adding back in the mean." >}}
</center>

We can now take the mean of each month of our 11 years of data to roughly extract the climatological seasonal cycle (Figure 4). Generally, we should be doing this for many more decades worth of output, because we are subject to noise from internally generated variability with only 11 years of the model run.


```python
ds = ds.groupby('time.month').mean('time')
f, ax = plt.subplots()
ds.plot()
ax.set_title('Seasonal Cycle of Temperature in the Tropical Pacific')
```

<center>
{{< figure src="/post/command_line_python/mean_cycle.png" title="The mean seasonal cycle of TS over the tropical Pacific Ocean." >}}
</center>

The following sections explore ways to make this script flexible. You'll find a polished version of the script that you can edit [here](https://github.com/bradyrx/python_from_command_line/blob/master/scripts/compute_seasonal_cycle.py).

---

## Flexible Header Variables <a name="flexible"></a>
---
The most straight forward way to make this code flexible would be to define the latitude/longitude bounds of interest in the head of the code. This allows the user to open up the python script and edit those variables directly when wanting to analyze a seasonal cycle from a different part of the globe. 

See `compute_seasonal_cycle.py` for its implementation.

```python
 import ...
 
 LAT_BNDS = [-5, 5]
 LON_BNDS = [180, 240]
 ds = xr.open_dataset('../data/CESM_LE.TS.002.1990-01.2000-12.nc')
 ds = ds.sel(lat=slice(LAT_BNDS[0], LAT_BNDS[1]), lon=slice(LON_BNDS[0], LON_BNDS[1]))
```

Although it is convenient for one to edit these variables directly, it is not the cleanest way to create flexible code. One still has to open and manually edit the headers every time they want to run a different iteration of the script, which can become time consuming. 

Assume you have a list or dictionary of different coordinates you want to analyze. High-throughput computing is the way to go for this---using GNU parallel or a unix loop to run this script multiple times in succession without having to open it and edit it manually every time (**Note**: I intend to do a high-throughput computing tutorial sometime).

---

## Leveraging `sys` to Run from Command Line <a name="sys"></a>
---
The first way to input variables from the command line is to use the `sys` package, which comes with your default python installation. We can use the command `sys.argv[index]` to accept arguments from the command line directly following the script name. 

**NOTE:** `sys.argv[0]` returns the name of the script. So your arguments should begin with `sys.argv[1]`. All arguments enter the script as strings, since they are coming from the command line. Thus, if you want to make your variable an `int`, you need to explicitly force that. See `compute_seasonal_cycle_sys.py` for its implementation.

```python
import statements
 
x0 = int(sys.argv[1])
x1 = int(sys.argv[2])
y0 = int(sys.argv[3])
y1 = int(sys.argv[4])
```

Now we can execute the command flexibly from the command line without opening the script:

```bash
$ python compute_seasonal_cycle.py 180 240 -5 5
```

In turn, the script runs and saves out a plot of the mean seasonal cycle over this domain and saves it to the `../output_figs/` folder.

Although a step ahead of manually editing the script, this implementation comes with one main issue: you have to remember the order of the arguments you're inputting. In general, I mediate this by having detailed documentation at the start of my script. I include very easy to find explanations of the inputs to this script, e.g.:

```python
"""
Compute the mean seasonal cycle of surface temperature given some bounds of
latitude and longitude.

INPUT 1: (int) Minimum longitude
INPUT 2: (int) Maximum longitude
INPUT 3: (int) Minimum latitude
INPUT 4: (int) Maximum latitude
"""
```

You can then run a `head` command on the script before using it as a reminder of the input order. This is a good method if you don't have a ton of inputs, since it is a quicker and cleaner setup than `argparse`.

---

## Using `argparse` for More Options and Documentation <a name="argparse"></a>

---

A more sophisticated way to create a flexible python script is through the `argparse` package. It takes a few more lines of code to setup, but we can create documentation to go along with it that can be read from the command line.

Setting up `argparse` for our example is relatively straight forward. We need to create a parser object, and then declare the command line inputs. The convention for shell scripts is to offer a single dash flag (e.g. -l) as well as a double dash flag (e.g. --lat) that is more verbose. A single dash allows for multiple options to be combined, such as if you want to recursively remove files in a directory (`-r`) as well as to have the system check if you really want to go through with the operation (`-i`). This could be supplied as `rm -ir`. Double dash flags cannot be combined, and thus are passed as single arguments.

In this example, we'll define required double dash flags for the latitude and longitude bounds, and an optional single and double dash flag to display the resulting plot to the user (instead of just saving it out). The purpose of this tutorial is to introduce you to command line flexibility, not to comprehensively review the `argparse` package. After completing these examples, you can explore the advanced features of `argparse` in its [documentation](https://docs.python.org/3/library/argparse.html). 

See `compute_seasonal_cycle_argparse.py` for this implementation.

```python
import argparse
# Initialize the argument parser with a description of the code that will
# show up upon calling --help
ap = argparse.ArgumentParser(
  description="computes the mean seasonal cycle of surface temperature \
  in a CESM-LE simulation given latitude and longitude bounds"
# Add arguments for inputting latitude and longitude bounds.
# nargs tells how many arguments should come after an option (min max)
# required tells the parser whether or not it should expect this option
# type sets the type (so we don't have to explicitly force int() like 
# with sys.argv)
ap.add_argument('--lat', nargs=2, required=True, type=int,
	help="input latitude bounds separated by a space")
ap.add_argument('--lon', nargs=2, required=True, type=int,
	help="input longitude bounds (0-360) separated by a space")
# Add optional flag to output a plot to the screen. The action flag says to
# store a True boolean if this flag is mentioned.
ap.add_argument('-p', '--plot', required=False,
	action='store_true',
  help="whether or not to show the resulting plot to the user")
# Create dictionary of input arguments
args = vars(ap.parse_args())
x0, x1 = args['lon']
y0, y1 = args['lat']
if args['plot']:
	plt.show()
```

Indeed a lot more goes into setting up `argparse` over setting up `sys.argv`, but it pays off for really clean documentation and error reporting. Calling this script with `--help` from the command line results in the following:

```bash
$ python compute_seasonal_cycle_argparse.py --help

usage: compute_seasonal_cycle_argparse.py [-h] --lat LAT LAT --lon LON LON [-p]

computes the mean seasonal cycle of surface temperature in a CESM-LE simulation 
given latitude and longitude bounds

optional arguments:
  -h, --help     show this help message and exit
  --lat LAT LAT  input latitude bounds separated by a space
  --lon LON LON  input longitude bounds (0-360) separated by a space
  -p, --plot     whether or not to show the resulting plot to the user

```

If we enter latitude bounds, but forget to enter longitude bounds, we get very clear error reporting (a feature that does not exist for `sys.argv`):

```bash
$ python compute_seasonal_cycle_argparse.py --lat 40 45

usage: compute_seasonal_cycle_argparse.py [-h] --lat LAT LAT --lon LON LON
                                          [-p]
compute_seasonal_cycle_argparse.py: error: the following arguments are required: --lon
```

To implement from the command line, simply run something like:

```bash
$ python compute_seasonal_cycle_argparse.py -p --lat 40 45 --lon 230 250
```

---

## Conclusions <a name="conclusion"></a>

---

To efficiently analyze climate data, it is a good practice to create flexible python scripts. This allows one to make one `.py` script for a given analysis that can then be modified with inputs (similar to how inputs are given to a function) from the command line. This practice forces proper documentation and saves a lot of time in the long run for analysis.

The easiest way to implement command line argument passing is through the `sys.argv` module. Although this is a straight forward implementation, it lacks documentation and forces the user to check the docstring of the code to know what order to input values into. 

The better way to set up command line arguments is through the `argparse` package. This turns your python code into a well-documented command line script and allows one to pass arguments through single and double dash flags (e.g. -p for optional plotting and --lat to input latitude bounds). `argparse` has extensive options not covered in this tutorial that can be found in its [documentation](https://docs.python.org/3/library/argparse.html).

I hope this tutorial was useful in increasing your efficiency in making python analysis scripts. If you have any suggestions for running flexible scripts from the command line, please reach out.

---

Riley Brady

Email : riley.brady@colorado.edu

Twitter : [@rileyxbrady](http://twitter.com/rileyxbrady)
