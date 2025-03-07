#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 12:35:15 2020

@author: twguest
"""


import time
import os
import shutil
import numpy as np
from matplotlib.colors import LogNorm
import wpg.srwlib as srwlib
#from wpg.wpg_uti_wf import calc_pulse_energy, get_axial_power_density, get_centroid
from matplotlib import pyplot as plt
from matplotlib import ticker, cm
from felpy.model.tools import argmax2d
from wpg import srwlib
from tqdm import tqdm
from felpy.model.tools import create_circular_mask
from felpy.analysis.centroid import get_com
#from wpg.wpg_uti_wf import get_axis

from scipy.stats import norm

fwhm_area = norm.cdf(np.sqrt(2*np.log(2))) - norm.cdf(-np.sqrt(2*np.log(2)))

from felpy.model.tools import radial_profile

    
def plot_enclosed_energy(ii, r, c, label = None, outdir = None):
    
    
    fig = plt.figure()
    ax1 = fig.add_subplot()
    
    ax1.imshow(ii, cmap = 'afmhot')
    
    circle = plt.Circle(c, r, color='w', fill=False)
    ax1.add_artist(circle)
    
    plt.axis("off")
    
    ax1.plot(c[0],c[1], marker = 'x', color = 'k')
    
    if label is not None:
        ax1.text(15, ii.shape[1]-15, label, c = 'w')
        


def get_enclosed_energy(ii, dx, dy, efraction = fwhm_area, sdir = None, plot = False, VERBOSE = True, threshold = 0.01):
    
    nx, ny = ii.shape
    c = get_com(ii)
    
    #results, err = finder(ii, nx, ny, c, efraction, VERBOSE = VERBOSE, threshold = threshold)
    
    
    N = np.arange(nx//2) ### number of pixels in radial profile
    
    
    profile = radial_profile(ii, c)[0] ### get radial profile
    
 
    r = np.cumsum(profile)/sum(profile)
    
    dr = np.gradient(r) ### get gradient for sub-pixel estimate
    idx = np.where(abs(r-efraction)==np.amin(abs(r-efraction)))[0][0]
    
    results = (idx - (r[idx]-efraction)/dr[idx]) ### sub-pixel sum(profile)
    err = np.array([results-idx, (idx+1)-results]) ### error to pixel either side of sub-pixel value

    results *= np.array([dx,dy]) ### multiply results by physical pixel-size
    err *= np.max([dx, dy]) ### select largest errorr
 
    if plot:

        plot_enclosed_energy(ii, idx, c)
    
    return results, np.max(err)
    
def n_enclosed_energy(ii, px = 1, py = 1, **kwargs):
    """
    a robust method for calculating the enclosed energy of an n-dimensional array
    
    under construction
    """
    
    data = np.ones([*ii.shape[2:],3])

    if data.ndim == 2:
        for pulse in range(data.shape[0]):
            results = get_enclosed_energy(ii[:,:,pulse], px, py)
            data[pulse,0] = results[0][0]
            data[pulse,1] = results[0][1]
            data[pulse,2] = results[1] 
                

                
            
    elif data.ndim == 3:
        for pulse in range(data.shape[0]):
            for train in range(data.shape[1]):
                results = get_enclosed_energy(ii[:,:,pulse,train], px, py)
                data[pulse,train,0] = results[0][0]
                data[pulse,train,1] = results[0][1]
                data[pulse,train,2] = results[1]

                
            
    return data
if __name__ == '__main__':
    from scipy.ndimage import gaussian_filter
    ii = np.zeros([50,50])
    ii[20,20] = 100
    ii[30,30] = 100
    #ii = gaussian_filter(ii, 5)
    #ii[40,40] = 0.0001
    ii = gaussian_filter(ii, 6)
    dx = 1e-06
    dy = 1e-06
    
    results, err = get_enclosed_energy(ii, dx, dy, plot = True, 
                                  VERBOSE = True)
