#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FELPY

__author__ = "Trey Guest"
__credits__ = ["Trey Guest"]
__license__ = "EuXFEL"
__version__ = "0.2.1"
__maintainer__ = "Trey Guest"
__email__ = "trey.guest@xfel.eu"
__status__ = "Developement"
"""

import numpy as np
from scipy.ndimage import gaussian_filter
from matplotlib import pyplot as plt 
from felpy.utils.os_utils import felpy_path

from felpy.utils.job_utils import JobScheduler

def generate_mirror_surface(nx,ny,dx,dy,savedir,mode,mirror_name):
    """
    Generate a plane mirror surface
    
    :param nx: number of horizontal pixels [int]
    :param ny: number of vertical pixels [int]
    :param mirDim: list of mirror dimensions [dx,dy] [m]
    :param outdir: save directory
    :param mode: type of mirror surface to be generated
    """
    
    if mode == 'flat':
        surface = np.zeros([nx,ny])
    elif mode == 'random':
        surface = np.ones([nx,ny])
        surface = gaussian_filter(surface, 30)*1e-09
        
    surface[0,1:] = np.linspace(-dx/2, dy/2, nx-1)
    surface[1:,0] = np.linspace(-dy/2, dx/2, ny-1)
   
    np.savetxt(savedir+ mirror_name + "_mir_" + mode +".dat", surface, delimiter='\t')
    
def genMirrorSurface(nx, ny, mirDim, outdir, mode = 'Flat', plot = False, mirrorName = None):
    """
    Generate a plane mirror surface
    
    :param nx: number of horizontal pixels [int]
    :param ny: number of vertical pixels [int]
    :param mirDim: list of mirror dimensions [dx,dy] [m]
    :param outdir: save directory
    :param mode: type of mirror surface to be generated
    """
    
    mirLen = mirDim[0]
    mirWid = mirDim[1]
    
    if mode == 'flat':
        surface = np.zeros((nx,ny))

    if mode == 'random':
        surface = np.random.normal(size = [nx,ny])*1e-09
        surface = gaussian_filter(surface, 5)
        
        if plot == True:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            
            if mirrorName is not None:
                ax.set_title(mirrorName + " Surface")
            elif mirrorName is None:
                ax.set_title("Mirror Surface")
            
            img = ax.imshow(surface*1e9,
                            extent = [-mirLen/2*1e6, mirLen/2*1e6, -mirWid/2*1e6, mirWid/2*1e6],
                            aspect = 'auto')
            
            ax.set_xlabel("x ($\mu$m)")
            ax.set_ylabel("y ($\mu$m)")
            
            cb = plt.colorbar(img, ax = ax)
            cb.ax.get_yaxis().labelpad = 15
            cb.ax.set_ylabel("Height Error (nm)", rotation = 270)
            
            fig.savefig(outdir + "mir_"+mode+".png")
    
    #surface = add_extent(surface, mirDim)
    surface[0,1:] = np.linspace(-mirWid/2, mirWid/2, nx-1)
    surface[1:,0] = np.linspace(-mirLen/2, mirLen/2, ny-1)
    np.savetxt(outdir+"mir_"+ mode +".dat", surface, delimiter='\t')

def setupHOMsurface():
    for i in [1,2]:
        xlen = 0.010 #m
        
        mirdat = "../../data/spb/mirror_surface/mirror{}.dat".format(i)
        mirdat = np.loadtxt(mirdat)
        
        n = mirdat.shape[0]
        
        ypos = mirdat[:,0]
        xpos = np.linspace(-xlen/2, xlen/2, n)
        height = mirdat[:,1]
        surface = np.ones((n+1,n))
        surface[1:,:] = height.T
        
        
     
    surface[0,:] = ypos
    surface[1:,0] = xpos
        
    np.savetxt("../../data/spb/mirror_surface/hom{}".format(i)+"_mir_real.dat", surface, delimiter='\t')
    return surface

def binArray(data, axis, binstep, binsize, func=np.nanmean):
    data = np.array(data)
    dims = np.array(data.shape)
    argdims = np.arange(data.ndim)
    argdims[0], argdims[axis]= argdims[axis], argdims[0]
    data = data.transpose(argdims)
    data = [func(np.take(data,np.arange(int(i*binstep),int(i*binstep+binsize)),0),0) for i in np.arange(dims[axis]//binstep)]
    data = np.array(data).transpose(argdims)
    return data



def setupNHEsurface():
    
    ylen = 25e-03
    
    mirdat = "../../data/spb/mirror_surface/XFEL_SPB_NHE_horizontal_focusing_ellipse_profile_of_residual_height.dat"
    mirdat = np.loadtxt(mirdat)
    
    height = mirdat[:,1]
    height = binArray(height, 0, 3, 3)
    n = height.shape[0]
    xpos =np.linspace(-950e-03//2, 950e-03//2, n)
    ypos = np.linspace(-ylen/2, ylen/2, n)

    surface = np.ones((n,n))
    
    surface[:,:] = height
     
    surface[0,1:] = ypos[1:]
    surface[1:,0] = xpos[1:]
    
    np.savetxt("../../data/spb/mirror_surface/nhe_mir_real.dat", surface)


def setupNVEsurface():
    
    ylen = 25e-03
    
    mirdat = "../../data/spb/mirror_surface/XFEL_SPB_NVE_vertical_focusing_ellipse_profile_of_residual_height.dat"
    mirdat = np.loadtxt(mirdat)
    
    height = mirdat[:,1]
    height = binArray(height, 0, 3, 3)
    n = height.shape[0]
    xpos =np.linspace(-ylen/2, ylen/2, n)
    ypos = np.linspace(-950e-03//2, 950e-03//2, n)

    surface = np.ones((n,n))
    
    surface[:,:] = height.T
     
    surface[0,1:] = ypos[1:]
    surface[1:,0] = xpos[1:]
    
    np.savetxt("../../data/spb/mirror_surface/nve_mir_real.dat", surface)


def generate_infinite_mirror():
    
    fpath = felpy_path()
    
    generate_mirror_surface(512, 512,
                           dx = 25,
                           dy = 25,
                           savedir = fpath + "/data/spb/tmp/",
                           mode = 'flat',
                           mirror_name = "infinite")

    fdir = fpath + "/data/spb/tmp/infinite_mir_flat.dat"
    return fdir
        
    
if __name__ == '__main__':
    #s = genMirrorSurface(100, 100, [10e-06, 50e-06], "../../tmp/", mode = 'random', plot = True)
    
    setupHOMsurface()   
    setupNHEsurface()
    setupNVEsurface()