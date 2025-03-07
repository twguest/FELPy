#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 13:12:20 2020

@author: twguest
"""

###############################################################################
import sys
sys.path.append("/opt/WPG/") # LOCAL PATH
sys.path.append("/gpfs/exfel/data/user/guestt/WPG") # DESY MAXWELL PATH

sys.path.append("/opt/spb_model") # LOCAL PATH
sys.path.append("/gpfs/exfel/data/user/guestt/spb_model") # DESY MAXWELL PATH
###############################################################################
###############################################################################

 

import sys
import numpy as np
from numpy.lib.stride_tricks import as_strided
from scipy.ndimage import gaussian_filter
from matplotlib import pyplot as plt
from scipy import optimize


import matplotlib.colors as colors
clist = list(colors._colors_full_map.values())

def _check_arg(x, xname):
    """
    check if the argument x is one-dimensional
    
    :param x: array argument
    :param xname: identifier for x
    """
    
    x = np.asarray(x)
    if x.ndim != 1:
        raise ValueError('%s must be one-dimensional.' % xname)
    

def window(arr, nrows, ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    
    h, w = arr.shape
    assert h % nrows == 0, "{} rows is not evenly divisble by {}".format(h, nrows)
    assert w % ncols == 0, "{} cols is not evenly divisble by {}".format(w, ncols)
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))

def checkRoot(n):
    """
    function to check if value n has an integer root
    
    :param n: input value
    
    :returns BOOL: [bool]
    """    

    if np.sqrt(n) % 1 == 0 and np.sqrt(n)/2 % 1 == 0:
        BOOL = True
    else:
        BOOL = False
    return BOOL

def getWindows(arr, n):
    """
    useful wrapper for window - returns n windows, where sqrt(n) % 0 must be true
    
    :param arr: array to be windowed
    :param n: number of windows
    
    :returns w: 3D array of shape [n, nrows, ncols]
    """
    
    w = None
    
    BOOL = checkRoot(n)
    
    if BOOL:
        w = window(arr, int(arr.shape[0]//np.sqrt(n)), int(arr.shape[1]//np.sqrt(n)))
    elif not BOOL:
        sys.exit("sqrt(n) is not an even integer value")
    
    if w is not None:
        return w
    
    
def autocorrelation(x, maxlag):
    """f
    Autocorrelation with a maximum number of lags.

    `x` must be a one-dimensional numpy array.

    This computes the same result as
        numpy.correlate(x, x, mode='full')[len(x)-1:len(x)+maxlag]

    The return value has length maxlag + 1.
    """
    
    _check_arg(x, 'x')
    p = np.pad(x.conj(), maxlag, mode='constant')
    T = as_strided(p[maxlag:], shape=(maxlag+1, len(x) + maxlag),
                   strides=(-p.strides[0], p.strides[0]))
    return T.dot(p[maxlag:].conj())

def autocovariance2D(roi):
    """ 
    calculates the spatially averaged autocovariance of a two-dimensional window
    
    :param roi: region of interest / window (np array)
    
    :returns acor: averaged autocovariance
    """     
    
    nx = roi.shape[0]
    
    mu = np.average(roi)
    acov = np.zeros_like(autocorrelation(roi[0,:], roi.shape[1]))
    
    for r in range(nx):
        roi[r,:] -= mu
        acov += autocorrelation(roi[r,:], roi.shape[1])/(np.amax(autocorrelation(roi[r,:], maxlag = roi.shape[0])))
    
        
        
    acov /= nx
    
    return acov

def gaussian(x, a, x0, sigma,c):
    """
    gaussian function for fitting
    """
    
    return a * np.exp(-(x-x0)**2/(2*sigma**2)) + c

def fitExponent(acov, ax, sigmaGuess = 1):
    """
    optimisation for fit of autocovariance function
    
    :param acov: autocovariance function [1d array]
    
    :returns params: parameter fit of autocov function
    """
    

    params, params_covariance = optimize.curve_fit(gaussian, ax, acov[:len(acov)-1],
                                                   p0=[1,0,sigmaGuess,0])

    return params


def getFeatureSize(ii, nWindows = 16, px = None, bPlot = False):
    """
    wrapper to calculate average speckle size in a window from the correlation
    length of a detector plane speckle pattern
    
    :param ii: 2D intensity pattern
    :param nWindows: number of windows to break the intensity pattern into
    :param px: (optional) physical pixel size (ie, detector pixel width) [m]
    
    :returns sz: 2D array of average feature sizes per window
    """
    
    if px is not None:
        ax = np.linspace(0, px, int(ii.shape[1]/(np.sqrt(nWindows))))
    else:
        ax = np.linspace(0, ii.shape[1], int(ii.shape[1]/(np.sqrt(nWindows))))
    
    w = getWindows(ii, nWindows) # break intensity array into windows

    
    if bPlot == True:
        
        i = 0
        
        fig, axs = plt.subplots(int(np.sqrt(nWindows)), int(np.sqrt(nWindows)), sharex = True, sharey = True, gridspec_kw = {'wspace':0, 'hspace':-0.0395}, figsize=(8,8))
        
        for j in range(w.shape[0]):
            
            k = int(j % np.sqrt(nWindows))
            
            axs[i,k].imshow(w[j,:,:], vmax = np.amax(w))
            axs[i,k].set_xticks([])
            axs[i,k].set_yticks([])
            if j % np.sqrt(nWindows) == int(np.sqrt(nWindows)-1):
                i += 1

            
        plt.subplots_adjust(wspace=0, hspace=0)
        plt.show()
        
    cors = np.arange(0, nWindows, dtype=np.float64)
    
    if bPlot == True:
        
        fi2 = plt.figure()
        ax2 = fi2.add_subplot()
        
    
    for itr in range(w.shape[0]):
        
        roi = w[itr, :, :]
        acov = autocovariance2D(roi)
        params = fitExponent(acov, ax, abs(ax[0]-ax[1]))
        

        wFeature = params[2]*2

        cors[itr] = wFeature
        
        if bPlot == True: 
            
            cid = np.random.randint(0,len(clist))
            ax2.plot(ax, acov[:acov.shape[0]-1], c = clist[cid])
            ax2.plot(ax, gaussian(ax, *params), linestyle = '--', c = clist[cid])
       
    cors = cors.reshape([int(np.sqrt(nWindows)),int(np.sqrt(nWindows))])
    
    if bPlot == True:
        
        plt.show()

    return cors
        

def test():
    
    from model.src.coherent import construct_SA1_wavefront
    
    wfr = construct_SA1_wavefront(1024, 1024, 1, 0.001, xoff = 0, yoff = -50e-06)
    
    arr = wfr.get_intensity()[:,:,0]
    
    cors = getFeatureSize(ii = arr, nWindows = 64, px = wfr.get_spatial_resolution()[0], bPlot = True)
    
    return cors    


if __name__ == "__main__":
    cors = test()    
    