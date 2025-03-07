#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

import h5py_wrapper as h5w

from pprint import pprint
from numpy import fft

from wpg import srwlib

from copy import copy
from felpy.model.optics.tilt import wavefront_tilt
from felpy.utils.opt_utils import ekev2k, geometric_focus
from felpy.backend.wpg_converters import wavefront_from_array
from felpy.model.src.coherent import modify_beam_divergence
from felpy.utils.opt_utils import ekev2wav, ekev2k
from felpy.utils.os_utils import timing
from wpg.wpg_uti_wf import calc_pulse_energy, plot_intensity_map
from felpy.model.mesh import Mesh
from felpy.model.src.SA1 import analytical_pulse_divergence, analytical_pulse_energy, analytical_pulse_width, analytical_pulse_duration

FWHM2RMS = np.sqrt(8*np.log(2))  # FWHM = sqrt(8ln(2))*sigma
FWHM2E2 = 5/3 ##2*abs(1/np.sqrt(-2*np.log(0.5))) ##1.66




class Source:
    """
    generalised source class
rei
    note: this could be much more general as to not take ekev and fwhm
    """


    def __init__(self, **kwargs):

            
        self.metadata = {}
        self.metadata['pulses'] = []
        
        self.source_properties = {}
        self.source_properties.update(kwargs)

        if "mesh" in kwargs:
            self.source_properties.update(**kwargs['mesh'].get_attributes())
    
    @property
    def _control(self):
        """
        a tool to return the longest array in the source properties (ie. the control variable)
        """
        d = {}
        for item in self.source_properties:
            if isinstance(self.source_properties[item], np.ndarray):
                d[item] = self.source_properties[item]
        try: 
            l = len(self.source_properties[max(d, key=lambda x:len(d[x]))])
        except(TypeError, ValueError):
            l = 1
        return l
    
    def build_properties(self):
        
        g = self._control
        
        for item in self.source_properties:
            
            if isinstance(self.source_properties[item], np.ndarray):

                if self.source_properties[item].shape[0] == g:
                    pass
                else:
                    self.source_properties[item] = np.repeat(self.source_properties[item], g)
                    
            elif type(self.source_properties[item]) is list:
                
                if len(self.source_properties[item]) == g:
                    pass
                else:
                    self.source_properties[item]*=np.ones(g).astype(type(self.source_properties[item][0]))
            
            else:
                self.source_properties[item] = np.repeat(self.source_properties[item], g)
                   
 
    def set_property(self, property_name, value):
        """
        wrapper function to store a source property
        
        :param property_name: name of the proeprty to be stored in dict 
        :type: str
        (
        :param value: value of the property
        :type: single value or list of values.
        """
        self.source_properties[property_name] = value


    def get_property(self, property_name):
        """
        return the value of a specific source property
    
        :param property_name: name of the proeprty to be read from dict 
        :type: str
        
        """
        assert property_name in self.source_properties, "Source property is not currently defined"
        return self.source_properties[property_name]
    
    
    def generate(self, array, pulse_properties, outdir = "./wfr_", save = True):
        

        
            
        wfr =  wavefront_from_array(array, nx=pulse_properties['nx'], ny=pulse_properties['ny'],
                                    nz=pulse_properties['nz'],
                                    dx=(pulse_properties['xMin']-pulse_properties['xMax'])/pulse_properties['nx'],
                                    dy=(pulse_properties['yMin']-pulse_properties['yMax'])/pulse_properties['ny'],
                                    dz=(pulse_properties['yMin']/pulse_properties['nz']),                                    
                                    ekev=pulse_properties['ekev'],
                                    pulse_duration=pulse_properties['pulse_duration'],
                                    source_properties = pulse_properties)
<<<<<<< HEAD

=======
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
        wfr.scale_beam_energy(pulse_properties['pulse_energy'])
        
        self.metadata['pulses'].append(outdir)
        
        if save:
            wfr.store_hdf5(outdir)
        else:
            return wfr

<<<<<<< HEAD


=======
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
    def store_hdf5(self, outdir, overwrite = False):
        """
        function to write source data( to a hdf5 file
        
        :param outdir: outdir of ".h5" file
        :type: str
        """
        
        if ".h5" or ".hdf5" in outdir:
            pass
        else: outdir+".h5"
        
        h5w.save(outdir, self.metadata, path = 'metadata/', write_mode = 'a', overwrite_dataset = overwrite)
        h5w.save(outdir, self.source_properties, path = 'source_properties/', write_mode = 'a', overwrite_dataset = overwrite)
        
    def load_hdf5(self, indir):
        """
        function to read data from a hdf5 file
        
        :param indir: directory to read ".h5" file from
        :type: str
        """
        self.metadata = h5w.load(indir,  path = 'metadata/')
        self.source_properties = h5w.load(indir,  path = 'source_properties/')
    
    @property
    def pulses(self):
        return self.metadata['pulses']
        
    @property
    def pulses(self):
        """ 
        list of pulses generated by this source
        """
        return self.metadata['pulses']
    
    
class LinearGaussian(Source):
    """
    A model of a gaussian beam w/ linear photon statistics
    """    
    
    def __init__(self, ekev, mesh, x, y, i, s0, sz, div,
<<<<<<< HEAD
                theta_x = 0, theta_y = 0, x0 = 0, y0 = 0,
=======
                tilt_x = 0, tilt_y = 0, x0 = 0, y0 = 0,
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
                pulse_duration = 100e-15, **kwargs):

        """
        initialisation function. 
        
        :param ekev: photon energy in keV
        :param mesh: felpy style mesh file defining xMin, xMax, yMin, yMax, nx, ny
        :param x: horizontal coordinates
        :param y: vertical coordinates
        :param i: on-axis beam intensity
        :param s0: waist fwhm 
        :param sz: fwhm @ a distance z from the source
        :param div: beam divergence
<<<<<<< HEAD
        :param theta_x: horizontal tilt wavevector
        :param theta_y: vertical tilt wavevector
=======
        :param tilt_x: horizontal tilt wavevector
        :param tilt_y: vertical tilt wavevector
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
        :param x0: horizontal shift 
        :param y0: vertical shift
        :param pulse_duration: temporal duration of the pulse
        """
        super().__init__(**kwargs)
        
        self.source_properties.update(kwargs)
       
        
        self.source_properties['ekev'] = ekev
        self.source_properties['i'] = i
<<<<<<< HEAD
        self.source_properties['s0'] = s0 
        self.source_properties['sz'] = sz/FWHM2E2
        self.source_properties['div'] = div
        if theta_x is list:
            self.source_properties['theta_x'] = [-t for t in theta_x]
        else:
            self.source_properties['theta_x'] = theta_x
        if theta_y is list:
            self.source_properties['theta_y'] = [-t for t in theta_y]
        else:
            self.source_properties['theta_y'] = theta_y        
=======
        self.source_properties['s0'] = s0
        self.source_properties['sz'] = sz/FWHM2E2
        self.source_properties['sz'] = sz
        self.source_properties['div'] = div
        self.source_properties['tilt_x'] = tilt_x
        self.source_properties['tilt_y'] = tilt_y
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
        self.source_properties['x0'] = x0
        self.source_properties['y0'] = y0
        self.source_properties['pulse_duration'] = pulse_duration
        self.source_properties['pulse_energy'] = i

        for item in self.source_properties:

            if type(self.source_properties[item]) == list:
                self.source_properties[item] = np.asarray(self.source_properties[item])
                
        self.source_properties.update(mesh.get_attributes())
        
        
        if 'z0' in kwargs:
            self.source_properties['z0'] = kwargs['z0'] 
        else:
            self.source_properties['z0'] = 0
        

    def generate_beam_envelope(self, pulse_properties):
        """
        a function to generate a gaussian photon field based on the source properties

        this can be extended at a later date to include perturbations, i.e the zernike polynomials.
        """

        xx, yy = np.meshgrid(np.linspace(pulse_properties['xMin'], pulse_properties['xMax'], pulse_properties['nx']), np.linspace(pulse_properties['yMin'], pulse_properties['yMax'], pulse_properties['ny']))
        
<<<<<<< HEAD
        return complex_gaussian_beam(x = xx, y = yy, ekev = pulse_properties['ekev'],
        i = pulse_properties['i'], s0 = pulse_properties['s0'],
        sz = pulse_properties['sz'], div = pulse_properties['div'],
        theta_x = pulse_properties['theta_x'], theta_y = pulse_properties['theta_y'],
        x0 = pulse_properties['x0'], y0 = pulse_properties['y0'])
=======
        return complex_gaussian_beam(x = xx, y = yy,
        i = self.source_properties['i'], s0 = self.source_properties['s0'],
        sz = self.source_properties['sz'], div = self.source_properties['div'],
        tilt_x = self.source_properties['tilt_x'], tilt_y = self.source_properties['tilt_y'],
        x0 = self.source_properties['x0'], y0 = self.source_properties['y0'])

>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0





    def generator(self, outdir = "", N = 1, save = True):
        """
        this is the emission process, and generates N wavefronts according to the rules given by the source paramters file.
        
        currently, it will only support cases where the input dictionary has values in the form of a single value or list.
        
        :param
        """
        
        wavefronts = [] ### N*self._control length list of wavefronts

            

        for n in range(N):

            self.build_properties()

            for itr in range(self._control):
<<<<<<< HEAD

                pulse_properties = {item:self.source_properties[item][itr] for item in self.source_properties}
                tp = self.get_temporal_profile(pulse_properties)
                pulse_properties['nz'] = len(tp)

                tilt = wavefront_tilt(np.meshgrid(np.linspace(pulse_properties['xMin'], pulse_properties['xMax'], pulse_properties['nx']),
                                                np.linspace(pulse_properties['yMin'], pulse_properties['yMax'], pulse_properties['ny'])),
                                    2*np.pi*np.sin(pulse_properties['theta_x'])/ekev2wav(pulse_properties['ekev']),
                                    2*np.pi*np.sin(pulse_properties['theta_y'])/ekev2wav(pulse_properties['ekev']))
                
                
                spherical = spherical_phase(nx = pulse_properties['nx'],
                ny= pulse_properties['ny'], 
                xMin= pulse_properties['xMin'], 
                xMax= pulse_properties['xMax'], 
                yMin= pulse_properties['yMin'], 
                yMax= pulse_properties['yMax'], 
                fwhm= pulse_properties['sz'], 
                divergence= pulse_properties['div'], 
                ekev= pulse_properties['ekev'])

                efield = self.generate_beam_envelope(pulse_properties)[:,:,np.newaxis]*tilt[:,:,np.newaxis]*tp
                
                if save:
                    self.generate(efield, pulse_properties, outdir = outdir + "_{:02}_{:04}.h5".format(n,itr), save = save)
                else:
                    wavefronts.append(self.generate(efield, pulse_properties, outdir = outdir + "_{:02}_{:04}.h5".format(n,itr), save = save))
        if save is False:
            return wavefronts
=======
                pulse_properties = {item:self.source_properties[item][itr] for item in self.source_properties}
                tp = self.get_temporal_profile(pulse_properties)
                pulse_properties['nz'] = len(tp)
 
                
                efield = self.generate_beam_envelope(pulse_properties)[:,:,np.newaxis]*tp
                
            
                self.generate(efield, pulse_properties, outdir = outdir + "_{:02}_{:04}.h5".format(n,itr))
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0

            
 
        
    def get_temporal_profile(self, pulse_properties, sigma=4, refresh=False):
        ### note this gets and sets - should be changed
    
        n_samples, sampling_interval_t = temporal_sampling_requirements(
            pulse_properties['pulse_duration'], VERBOSE=True, S=4)

        n_samples *= sigma
        self.source_properties['nz'] = n_samples * np.ones(self._control).astype(type(n_samples))
        
        return generate_temporal_SASE_pulse(pulse_time=pulse_properties['pulse_duration'],
                                                             n_samples=n_samples,
                                                             sigma=sigma)
        

<<<<<<< HEAD



























class SA1_Source(LinearGaussian):
    """
    Analytical SA1 Source Model
    """    

    
    def __init__(self, ekev, q, nx = 512, ny = 512, theta_x = 0, theta_y = 0, x0 = 0, y0 = 0, z = 0, **kwargs):

        """
        initialisation function. 

        :param ekev: photon energy in keV [float or list of floats of length N]
        :param q: beam charge in nC [float or list of floats of length N]
        :param nx: number of horizontal grid/mesh points (int)
        :param ny: number of vertical grid/mesh points (int)
        :param theta_x: horizontal pointing error [float or list of floats of length N]
        :param theta_y: vertical pointing error [float or list of floats of length N]
        :param x0: horizontal beam center [float or list of floats of length N]
        :param y0: vertical beam center [float or list of floats of length N]
        :param z: position from source waist (float64)

        :keyword i: pulse energy (J) [float or list of floats of length N]
        :keyword div: beam divergence (rad) [float or list of floats of length N]
        :keyword s0: beam size at waist (m) [float or list of floats of length N]
        """
        
        self.source_properties = {}
        
        self.metadata = {}
        self.metadata['pulses'] = []

        self.source_properties['ekev'] = ekev
        self.source_properties['z0'] = z  

        if 'i' in kwargs:
            self.source_properties['i'] =  kwargs.get('i')
            self.source_properties['pulse_energy'] = kwargs.get('i')
        else:
            self.source_properties['i'] = analytical_pulse_energy(q, ekev) 
            self.source_properties['pulse_energy'] = analytical_pulse_energy(q, ekev) 

        if 's0' in kwargs:
            self.source_properties['s0'] = kwargs.get('s0')
        else:
            self.source_properties['s0'] = analytical_pulse_width(ekev) 
        
        if 'div' in kwargs:
            self.source_properties['div'] = kwargs.get('div')
        else:
            self.source_properties['div'] = analytical_pulse_divergence(ekev, 'mean')


        self.source_properties['sz'] =  (analytical_pulse_width(ekev) + (2*z*np.tan(self.source_properties['div'])))
        self.source_properties['sz'] /= FWHM2E2
        
        if theta_x is list:
            self.source_properties['theta_x'] = [-t for t in theta_x]
        else:
            self.source_properties['theta_x'] = theta_x
        
        if theta_y is list:
            self.source_properties['theta_y'] = [-t for t in theta_y]
        else:
            self.source_properties['theta_y'] = theta_y   

        ### geometry approximation:
        self.source_properties['x0'] = x0 + np.tan(theta_x)*z
        self.source_properties['y0'] = y0 + np.tan(theta_y)*z

        if 'pulse_duration' not in kwargs:
            self.source_properties['pulse_duration'] = analytical_pulse_duration(q)
 
=======
class SA1_Source(LinearGaussian):
    """
    fixed case of the SA1 source
    """    

    
    def __init__(self, ekev, q, theta_x = 0, theta_y = 0, **kwargs):

        """
        initialisation function. 
        """
        super().__init__(**kwargs)
        
        self.source_properties['stochastic'] = stochastic
        self.source_properties.update(kwargs)
        
        
        self.source_properties['ekev'] = ekev

        self.source_properties['q'] = q 
        self.source_properties['theta_x'] = theta_x
        self.source_properties['theta_y'] = theta_y
        
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
        for item in self.source_properties:

            if type(self.source_properties[item]) == list:
                self.source_properties[item] = np.asarray(self.source_properties[item])
<<<<<<< HEAD
        
        ### approximations:
        # let -xMin = xMax = 1.5w, likewise for vertical coordinates
        r = 5
        self.source_properties['xMin'] = -r*FWHM2E2*self.source_properties['sz']+self.source_properties['x0'] 
        self.source_properties['yMin'] = -r*FWHM2E2*self.source_properties['sz']+self.source_properties['y0']

        self.source_properties['xMax'] = r*FWHM2E2*self.source_properties['sz']+self.source_properties['x0']
        self.source_properties['yMax'] = r*FWHM2E2*self.source_properties['sz']+self.source_properties['y0']
        
        self.source_properties['nx'] = nx
        self.source_properties['ny'] = ny
        
=======
                
        self.source_properties.pop('mesh')
        

                
        if 'z0' in kwargs:
            self.source_properties['z0'] = kwargs['z0'] 
        else:
            self.source_properties['z0'] = 0,

        if 'divergence' not in self.source_properties.keys():      
            self.source_properties['divergence'] = analytical_pulse_divergence(self.ekev, 'mean')
        if 'pulse_energy' not in self.source_properties.keys():
            self.source_properties['pulse_energy'] = analytical_pulse_energy(self.q, self.ekev)
        if 'fwhm' not in self.source_properties.keys():
            self.source_properties['fwhm'] = 2*self.source_properties['z0']*np.tan(self.source_properties['divergence'])*analytical_pulse_width(self.ekev) +analytical_pulse_width(self.ekev)
        if 'pulse_duration' not in self.source_properties.keys():
            self.source_properties['pulse_duration'] = analytical_pulse_duration(self.q)
    
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
    @property
    def ekev(self):
        """
        return photon beam energy
        """
        return self.source_properties['ekev']
    
    
    @property
    def q(self):
        """
        return photon beam charge
        """
        return self.source_properties['q']
 
                    
                    





<<<<<<< HEAD













=======
        
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0

class Source_WPG(Source):
    """
    Empty-type class to build a source definition from a wpg wavefront
    """
    def __init__(self, wfr):

        self.wfr = wfr

        ekev = wfr.params.photonEnergy/1000

        xMin, xMax, yMin, yMax = wfr.get_limits()
        nx, ny = wfr.params.Mesh.nx, wfr.params.Mesh.ny

        zMin, zMax = wfr.params.Mesh.sliceMin, wfr.params.Mesh.sliceMax
        nz = wfr.params.Mesh.nSlices

        m = Mesh(nx=nx, ny=ny, nz=nz,
                 xMin=xMin, xMax=xMax,
                 yMin=yMin, yMax=yMax,
                 zMin=zMin, zMax=zMax)

        super().__init__(mesh=m)


def gaussian_profile(x, x0, width):
    """
    generate a gaussian envelope for modelling the integrated pulse_data

    :param x: 1D list of time/frequency positions
    :param x0: central time/frequency
    :param width: width of XFEL pulse
    """
    return np.exp(-np.power(x - x0, 2.) / (2 * np.power(width, 2.)))


def temporal_sampling_requirements(pulse_time, S=10, VERBOSE=False):
    """
    calculate the number of samples required for the defined pulse length.

    from Partial-coherence method to model experimental free-electron laser pulse statistics - Pfeifer - 2021 -
    Optics Letters - Vol. 35 No 20.

    We expect the number of sampling intervals to satisfy
    |w_{i} - w_{i+1} << 2\pi/tau
    where tau is pulse time.

    :params pulse_time: length of the XFEL pulse
    :param S: sampling fadctor
    :returns n: number of sampling intervals req.

    NOTE: a<<b is set to satisfy a*10<b
    """
    freq_sampling = (2*np.pi)/(pulse_time)
    temporal_sampling = 1/(freq_sampling)
    n = np.ceil(S*pulse_time/(temporal_sampling))

    if VERBOSE:
        #print("Frequency Sampling Interval: {:.2e} Hz".format(freq_sampling))
        #print("Temporal Sampling Interval: {:.2e} s".format(temporal_sampling))
        #print("Number of Req. Samples: {}".format(n))
        pass

    return int(n), temporal_sampling


def generate_temporal_SASE_pulse(pulse_time, n_samples=100, sigma=4, t0=0):
    """
    generate a single SASE pulse

    - assumes that the spectral and temporal bandwidth are the pulse are reciprocal,
    - assumes that the spectral and temporal profiles are gaussian,
    - assumes that there is no jitter from the central value of the Gaussian (ie, the pulse profile
    is persistent).

    in future, we will extend this extned the functionality to account for non-Gaussian profiles,
    and pulse-length jitter.

    it will also be useful to trim the function to the relevant regions (and thus reduce the number of points)

    :param pulse_time: expectation value of the SASE pulse time
    :param VERBOSE: [bool] enables printing and plotting
    """

    t = np.linspace(-pulse_time*sigma, pulse_time*sigma, n_samples)

    temporal_envelope = (1/np.sqrt(2*np.pi)) * \
        gaussian_profile(t, t0, pulse_time)

    spectral_bw = 1/pulse_time
    w = 1/t

    if t0 == 0:
        w0 = t0
    elif t0 != 0:
        w0 = 1/t0

    spectral_envelope = gaussian_profile(w, w0, spectral_bw)

    random_phases = np.random.uniform(-np.pi, np.pi, temporal_envelope.shape)

    E_t = fft.fft(spectral_envelope*np.exp(1j*random_phases))*temporal_envelope

    return E_t


def wavefront_to_wavefield(spatial_wfr, temporal_profile=1):
    """
    this function is primarily a WPG conversion function that takes two wavefields,
    a spatial and temporal, two define a single WPG array.

    note: in future we might just define a single input wavefront.
    """
    new_wfr = spatial_wfr.as_complex_array()[:, :, :]*temporal_profile

    dx, dy = spatial_wfr.get_spatial_resolution()
    dz = spatial_wfr.get_temporal_resolution()

    wfr = wavefront_from_array(new_wfr,
                               nx=spatial_wfr.params.Mesh.nx,
                               ny=spatial_wfr.params.Mesh.ny,
                               nz=len(temporal_profile),
                               dx=dx,
                               dy=dy,
                               dz=dz,
                               ekev=spatial_wfr.params.photonEnergy/1000)
    return wfr


<<<<<<< HEAD
def complex_gaussian_beam(x,y,ekev,i,s0,sz,div,theta_x = 0, theta_y = 0,x0 = 0, y0 = 0):
=======
def complex_gaussian_beam(x,y,i,s0,sz,div,tilt_x = 0, tilt_y = 0,x0 = 0, y0 = 0):
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
    """
    Analytical model for a complex gaussian source
    
    :param x: horizontal coordinates
    :param y: vertical coordinates
    :param i: on-axis beam intensity
    :param s0: waist fwhm 
    :param sz: fwhm @ a distance z from the source
    :param div: beam divergence
<<<<<<< HEAD
    :param theta_x: horizontal tilt wavevector
    :param theta_y: vertical tilt wavevector
=======
    :param tilt_x: horizontal tilt wavevector
    :param tilt_y: vertical tilt wavevector
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
    :param x0: horizontal shift 
    :param y0: vertical shift
    """

<<<<<<< HEAD
    R = (sz*1.6)/div

    a = np.sqrt(i)*(sz/s0)
    b = -((x-x0)**2+(y-y0)**2)/(2*sz**2)
    c = ((x-x0)**2+(y-y0)**2)/(4*R)
     
    d = theta_x*x+theta_y*y

    k = (2*np.pi/ekev2wav(ekev))

    ### note, removed c and d (tilt)
    return a*np.exp(b-1j*k*c)



=======
    R = -div/sz

    a = np.sqrt(i)*(sz/s0)
    b = -((x-x0)**2+(y-y0)**2)/sz**2
    c = ((x-x0)**2+(y-y0)**2)/R
    d = tilt_x*x+tilt_y*y

    return a*np.exp(b-1j*(c*d))
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0

def gaussian_envelope(nx, ny,
                      xMin, xMax,
                      yMin, yMax,
                      fwhm, x0=0, y0=0):
    """

    :param nx: DESCRIPTION
    :param ny: DESCRIPTION
    :param dx: DESCRIPTION
    :param dy: DESCRIPTION
    :param fwhm: DESCRIPTION
    :param divergence: DESCRIPTION

    :return gaussian: DESCRIPTION
    """

    # Initializing value of x-axis and y-axis
    # in the range -1 to 1
    x, y = np.meshgrid(np.linspace(xMin, xMax, nx),
                       np.linspace(yMin, yMax, ny))
    dst = np.sqrt(x*x+y*y)

    # Initializing sigma and muu
    sigma = fwhm/FWHM2E2

    # Calculating Gaussian array
    gaussian = np.exp(-(((x-x0)**2+(y-y0)**2) / (2*sigma**2)))

    return gaussian


def spherical_phase(nx, ny,
                    xMin, xMax,
                    yMin, yMax,
                    fwhm, divergence,
                    ekev, x0=0, y0=0):

    k = ekev2k(ekev)
    f = geometric_focus(fwhm, divergence)

    # Initializing value of x-axis and y-axis
    # in the range -1 to 1
    x, y = np.meshgrid(np.linspace(xMin, xMax, nx),
                       np.linspace(yMin, yMax, ny))

    # Initializing sigma and muu

    # Calculating Gaussian array
    spherical_phase_term = np.exp(1j*k*((x-x0)**2+(y-y0)**2)/(4*f))

    return spherical_phase_term


 


if __name__ == '__main__':

<<<<<<< HEAD
    test_spherical_phase()
=======
    from felpy.model.mesh import Mesh

    from felpy.model.wavefront import Wavefront
    from wpg.wpg_uti_wf import plot_intensity_map
    
    m = Mesh(nx=512, ny=512, xMin=-450e-06, xMax=450e-06, yMin=-450e-06, yMax= 450e-06, nz = 10)

    src = SA1_Source(ekev = 9.2, q = 0.25, mesh=m,  pulse_energy = [5e-06], fwhm = 100e-06)
    src.generator("/home/guestt/Documents/tmp_dir", N = 1)
    
    for p in src.pulses:
        wfr = Wavefront()
        wfr.load_hdf5(p)
        print(wfr.divergence)
        plot_intensity_map(wfr)
        print(src.__dict__)
    #wfr.load_hdf5("./test.h5")
# =============================================================================
#     nx = ny = 512
#     xMin = yMin = -300e-06
#     yMax = xMax = -1*xMin
#     fwhm = 5e-06
#     divergence = 5e-06
#     ekev = 10
#
#     env = complex_gaussian_envelope(nx, ny,
#                                     xMin, xMax, yMin, yMax,
#                                     fwhm,
#                                     divergence,
#                                     ekev)
#
#     pulse_time = 55e-15
#     sigma = 4
#     S = 4
#     Seff = S/sigma
#
#     n_samples, sampling_interval_t = temporal_sampling_requirements(pulse_time, VERBOSE = False, S = S)
#     sampling_interval_w = 1/sampling_interval_t
#
#     n_samples *= sigma
#     #n_samples = 10
#     t = np.arange(-pulse_time, pulse_time, pulse_time/n_samples)
#
#     temporal_profile = generate_temporal_SASE_pulse(pulse_time = pulse_time,
#                                                     n_samples = n_samples,
#                                                     sigma = sigma)
#     env = env[:,:,np.newaxis]*temporal_profile
#
#     wfr = wavefront_from_array(env, nx = nx, ny = ny,
#                               nz = n_samples, dx = (xMax-xMin)/nx,
#                               dy = (yMax-yMin)/ny, dz = (pulse_time/n_samples),
#                               ekev = ekev, pulse_duration = pulse_time)
#
#     print(wfr.get_divergence())
#
#     #modify_beam_divergence(wfr, wfr.get_fwhm()[0], divergence)
#
#     plot_intensity_map(wfr)
#
#
#     plot_intensity_map(wfr)
# =============================================================================
    #srwlib.srwl.SetRepresElecField(wfr._srwl_wf, 'f')
# =============================================================================
#
#     # =============================================================================
#     #     plot_intensity_map(wfr)
#     #     print(wfr.get_divergence())
#     #     plot_intensity_map(wfr)
#     #
#     #     #print(wfr.get_spatial_resolution())
#     #     modify_beam_divergence(wfr, fwhm, divergence)
#     #     #print(wfr)
#     #
#     #     #env = env[:,:,np.newaxis] * temporal_profile
#     # =============================================================================
# =============================================================================
# =============================================================================
#
#
# if __name__ == '__main__':
#
#     from wpg.wpg_uti_wf import plot_intensity_map, plot_intensity_qmap
#
#     nx = 512
#     ny = 512
#
#     xMin = yMin = -400e-06
#     xMax = yMax =  400e-06
#
#     #for fwhm in np.linspace(50e-06, 150e-06, 10):
#
#
#     from felpy.experiments.source_diagnostics import scan_source_divergence
#
#     data = scan_source_divergence(e(kev = np.arange(5,10), q = [0.1], n = 1)
#
# =============================================================================


    import os
    
    m = Mesh(nx=512, ny=256, xMin=-300e-06, xMax=300e-06, yMin=-300e-06, yMax=300e-06, nz = 10)
    theta_x = [-3e-06, -2e-06, -1e-06, 0, 1e-06, 2e-06,3e-06]
    
    
    src = SA1_Source([5], [0.2], mesh=m, theta_x = theta_x)
    
    src.generator("../data/tmp/test")
    
    try:
        src.store_hdf5("../data/tmp/source.h5")
    except(KeyError):
        os.remove("../data/tmp/source.h5")
        src.store_hdf5("../data/tmp/source.h5")

    src = Source()
    src.load_hdf5("../data/tmp/source.h5")
    from felpy.model.wavefront import Wavefront
    from wpg.wpg_uti_wf import plot_intensity_map
    wfr = Wavefront()
    
    from felpy.model.beamline import Beamline
    from wpg.optical_elements import Drift
    from felpy.model.tools import propagation_parameters
    from matplotlib import pyplot as plt
    
    bl = Beamline()
    bl.append(Drift(50), propagation_parameters(1,1,1,1,mode = 'fresnel'))
    
    for w in src.pulses:
        
        wfr.load_hdf5(w)
        bl.propagate(wfr)
        plt.plot(wfr.x_axis, wfr.get_x_profile(), label = "{} $\mu$ rad".format(wfr.source_properties['theta_x']*1e6))
        #plot_intensity_map(wfr)
        print(wfr.com)
    
    plt.legend()
>>>>>>> 1672e49b78fdc70c02ce0f2053703c0f360368f0
