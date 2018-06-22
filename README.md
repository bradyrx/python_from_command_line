# Flexible python scripts from the command line (tutorial)

This hosts the relevant files and data for my tutorial on creating flexible python scripts for the command line. The tutorial post can be viewed on my website [here](http://www.rileyxbrady.com/post/flexible-python-inputs/) or alternatively by clicking on the `flexible-python-inputs.md` file in this repository.

## Setup

You can follow along with this tutorial by first ensuring you have a proper version of python installed with the necessary packages (see beginning of tutorial for information). Then you can either download this repository from clicking 'Clone or Download' and downloading it as a .zip or by running the following command in your terminal window:

`git clone git@github.com:bradyrx/python_from_command_line.git`

Next, move into the data folder and gunzip the netCDF file

`gunzip CESM_LE.TS.002.1990-01.2000-12.nc.gz`

Now you can follow along! `scripts/compute_seasonal_cycle.py` is the completed analysis script with no command line implementation. The other two scripts include command line flexibility with `sys.argv` and with `argparse`. 

## Contact

Email : riley.brady@colorado.edu

Twitter : [@rileyxbrady](https://twitter.com/rileyxbrady)
