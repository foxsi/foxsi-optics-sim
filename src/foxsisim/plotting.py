'''
Created on Jul 29, 2011

@author: rtaylor
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import mpl_toolkits.mplot3d.axes3d as axes3d
from foxsisim.reflectivity import Reflectivity
from foxsisim.source import Source
from foxsisim.detector import Detector
# from matplotlib.colors import LogNorm


def get3dAxes(figure):
    '''
    Returns the axes3d object of a figure. If no such axis
    exists, we create one and return it.
    '''
    if isinstance(figure.gca(), axes3d.Axes3D):  # a 3d axis already exitsts
        return figure.gca()
    else:  # a 3d axis has not been made yet
        return axes3d.Axes3D(figure)


def scatterHist(rays, figure=None, binwidth=0.01, colorBounces=True):
    '''
    Creates a scatter-plot for the (x,y) locations of an array
    of rays, assuming they have been caught by the detector.
    Aligned with the plot are histograms displaying
    the frequency distribution of x and y positions. This
    function is adapted from a matplotlib online cookbook.
    '''
    if figure is None:
        fig = plt.figure(figsize=(5, 5), dpi=100)
    else:
        fig = figure
        fig.clf()  # clear all axes

    # create xy coords
    x = np.array([ray.des[0] for ray in rays])
    y = np.array([ray.des[1] for ray in rays])
    if colorBounces:
        colors = []
        for ray in rays:
            if ray.bounces == 1:
                col = 'r'  # red
            elif ray.bounces == 2:
                col = 'g'  # green
            elif ray.bounces == 3:
                col = 'b'  # blue
            else:
                col = 'k'  # black
            colors.append(col)
    else:
        colors = 'b'

    nullfmt = NullFormatter()  # no labels

    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    axScatter = fig.add_axes(rect_scatter)
    axHistx = fig.add_axes(rect_histx)
    axHisty = fig.add_axes(rect_histy)

    # no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    if len(rays) > 0:
        axScatter.scatter(x, y, c=colors)

        # now determine nice limits by hand:
        xymax = np.max([np.max(np.fabs(x)), np.max(np.fabs(y))])
        lim = (int(xymax / binwidth) + 1) * binwidth

        axScatter.set_xlim((-lim, lim))
        axScatter.set_ylim((-lim, lim))

        bins = np.arange(-lim, lim + binwidth, binwidth)
        axHistx.hist(x, bins=bins)
        axHisty.hist(y, bins=bins, orientation='horizontal')

        axHistx.set_xlim(axScatter.get_xlim())
        axHisty.set_ylim(axScatter.get_ylim())

def plot(data_object, figureNum=0, **kwargs):
    '''
    Create a plot of the given data object
    Options are:
        - Reflectivity
        - Source
        - Detector
    '''

    if isinstance(data_object, Reflectivity):
        plt.figure(figureNum)
        _plotReflectivity(data_object, **kwargs)
    if isinstance(data_object, Source):
        plt.figure(figureNum)
        if data_object._spectrum is not None:
            _plotSourceSpectrum(data_object, **kwargs)
    if isinstance(data_object, Detector):
        plt.figure(figureNum)
        _plotDetectorImage(data_object, **kwargs)


def _plotReflectivity(reflectivity):
    energy_range = reflectivity.energy_range()
    angle_range = reflectivity.angle_range()
    energies = reflectivity.energy_ax
    angles = reflectivity.angle_ax

    z = reflectivity.func(angles, energies)
    extent = (energy_range[0], energy_range[1],
              angle_range[0], angle_range[1])
    # can't plot image on log axes
    # im = plt.imshow(z, origin='lower', extent=extent,
    #                norm=LogNorm(vmin=0.01, vmax=1))
    plt.yscale('log')
    plt.xscale('log')
    levels = np.arange(0, 1, 0.1)
    cs = plt.contour(z, levels, origin='lower', linewidths=2, extent=extent)
    plt.clabel(cs, inline=1)
    plt.ylabel('Angle [deg]')
    plt.xlabel('Energy [keV]')
    plt.title('Reflectivity of ' + reflectivity.material)
    # plt.colorbar(im)
    #plt.colorbar(cs, shrink=0.8)


def _plotSourceSpectrum(source):
    energies = np.arange(0, 30, 0.1)
    plt.plot(energies, source._spectrum(energies))
    plt.xlabel('Energy [keV]')
    plt.title('Source Spectrum')


def _plotDetectorImage(detector, energy_range=None):
    '''
    Displays the source background to screen
    '''
    detector._makeImage(energy_range=energy_range)
    plt.imshow(detector.pixels)
    title_str = 'N = ' + str(len(detector.rays))
    if energy_range is not None:
        title_str += ' ' + (str(energy_range[0]) + ' - ' +
                        str(energy_range[1]) + ' keV')
    plt.title(title_str)
    plt.ylabel("Pixels")
    plt.xlabel("Pixels")
