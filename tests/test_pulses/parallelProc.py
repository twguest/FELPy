#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 15:09:54 2020

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

import multiprocessing

from model.beamline.structure import propagation_parameters
from model.beamline.structure import Instrument

from wpg import srwlib

from wpg.srwlib import SRWLOptD as Drift

from felpy.model.wavefront import Wavefront
from felpy.model.beamline import Beamline

from wpg.wpg_uti_wf import calc_pulse_energy, calculate_fwhm, get_axial_power_density
from wpg.wpg_uti_wf import plot_intensity_map as plotIntensity

from wpg.misc import calcDivergence

from os import listdir

from tqdm import tqdm

focus = "nano"
indir = "../../data/tests/pulseTests/gaussianSource/"
outdir = "../../data/tests/pulseTests/gaussianOut/para/"


def storeWavefrontInfo(wfr):
    
    sz0 = get_axial_power_density(wfr, spectrum = False)
    sz1 = get_axial_power_density(wfr, spectrum = True)
    
    fwhm = calculate_fwhm(wfr)
    
    srwlib.srwl.SetRepresElecField(wfr._srwl_wf, 't')
    pulseEn, photons_per_pulse = calc_pulse_energy(wfr)
    srwlib.srwl.SetRepresElecField(wfr._srwl_wf, 'f')
    
    divergence = wfr.get_divergence()
    
    
    wfr.custom_fields['/source/t_spectrum'] = sz0
    wfr.custom_fields['/source/f_spectrum'] = sz1
    
    wfr.custom_fields['/source/xFWHM'] = fwhm['fwhm_x']
    wfr.custom_fields['/source/yFWHM'] = fwhm['fwhm_y']
    
    wfr.custom_fields['/source/divX'] = divergence[0]
    wfr.custom_fields['/source/divX'] = divergence[1]
    
    wfr.custom_fields['/source/pulseEn'] = pulseEn
    wfr.custom_fields['/source/nPhotons'] = photons_per_pulse
    
   

def getSimpleBl():
    
    bl = Beamline()    
    
    bl.append(Drift(10), propagation_parameters(1, 1, 1, 1, mode = 'quadratic'))
    
    return bl

def getSPB(wfr):
    
    spb = Instrument()
    
    spb.setupHOMs(wfr.params.photonEnergy/1000, 2.2e-03)
    spb.setupKBs(wfr.params.photonEnergy/1000, 3.5e-03)
    
    spb.mirrorProfiles(toggle = "off", aperture = True, overwrite = True)
    
    spb.build_elements(focus)
<<<<<<< HEAD
    spb.build_beamline(focus)
=======
    spb.buildBeamline(focus)
>>>>>>> 108cfb9b6fc97d3841ee1db54862523eee5b184e
    spb.scale(wfr, isc = 512) 
    
    
    bl = spb.get_beamline()
    
    return bl

def propagatePulses(fname):
    

    wfr = Wavefront()
    wfr.load_hdf5(indir + fname)
    
    srwlib.srwl.SetRepresElecField(wfr._srwl_wf, 'f')
    #storeWavefrontInfo(wfr)
    
 
    bl = getSPB(wfr)
    #bl = getSimpleBl()
    bl.propagate_sequential(wfr)
    
    wfr.store_hdf5(outdir + fname)
    

    plotIntensity(wfr)

if __name__ == '__main__':

    MPI = False
      
    f = listdir(indir)
    
    if MPI:
        
        cores = int(multiprocessing.cpu_count()/2)
        p = multiprocessing.Pool(cores)
        
        for _ in tqdm(p.imap_unordered(propagatePulses, f), total = len(f)):
            pass
        
        p.close()
        p.join()
        
    else:
        for fname in f:
            propagatePulses(fname)
            
    