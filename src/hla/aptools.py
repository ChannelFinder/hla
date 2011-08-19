#!/usr/bin/env python

from __future__ import print_function

"""
hla.aptools
~~~~~~~~~~~

Accelerator Physics Tools


"""

import numpy as np
import time, shelve, sys
import matplotlib.pylab as plt

import machines
from orbit import Orbit
from catools import caput, caget 

__all__ = [
    'getLifetime',  'measChromaticity', 'measDispersion',
    'correctOrbitPv', 'correctOrbit'
]

alphac = 3.6261976841792413e-04

def getLifetime(verbose = 0):
    """
    Monitor current change with, calculate lifetime dI/dt

    It takes about 30 seconds, 10 points will be recorded, about 3 seconds
    delay between each.

    least square linear fitting is applied for slop dI/dt
    """

    N = 10
    ret = np.zeros((N, 2), 'd')
    d0 = datetime.datetime.now()
    ret[0, 1] = getCurrent()
    for i in range(1, N):
        time.sleep(3)
        ret[i,1] = getCurrent()
        dt = datetime.datetime.now() - d0
        ret[i,0] = (dt.microseconds/1000000.0 + dt.seconds)/3600.0 + \
            dt.days*24.0
        if verbose:
            print(i, dt, ret[i,1])
    dI = max(ret[:,1]) - min(ret[:,1]) 
    dt = max(ret[:,0]) - min(ret[:,0])
    #print np.average(ret[:,1]), dI, dt
    #print np.average(ret[:,1]) / (dI / dt), "H"
    lft_hour = np.average(ret[:,1]) / (dI / dt)
    return lft_hour


def measChromaticity():
    """
    Measure the chromaticity
    """
    gamma = 3.0e3/.511
    eta = alphac - 1/gamma/gamma

    f0 = getRfFrequency()
    nu0 = getTunes()
    print(f0, nu0)

    f = np.linspace(f0 - 1e-3, f0 + 1e-3, 6)
    nu = np.zeros((len(f), 2), 'd')
    for i,f1 in enumerate(f): 
        putRfFrequency(f1)
        time.sleep(6)
        nu[i,:] = getTunes()

    df = f - f0
    dnu = nu - np.array(nu0)
    p, resi, rank, sing, rcond = np.polyfit(df, dnu, deg=2, full=True)
    print("Coef:", p)
    print("Resi:", resi)
    chrom = p[-2,:] * (-f0*eta)
    print("Chromx:", chrom)
    
    t = np.linspace(1.1*df[0], 1.1*df[-1], 100)
    plt.clf()
    plt.plot(f - f0, nu[:,0] - nu0[0], '-rx')
    plt.plot(f - f0, nu[:,1] - nu0[1], '-go')
    plt.plot(t, t*t*p[-3,0]+t*p[-2,0] + p[-1,0], '--r',
             label="H: %.1fx^2%+.2fx%+.1f" % (p[-3,0], p[-2,0], p[-1,0]))
    plt.plot(t, t*t*p[-3,1]+t*p[-2,1] + p[-1,1], '--g',
             label="V: %.1fx^2%+.2fx%+.1f" % (p[-3,1], p[-2,1], p[-1,1]))
    plt.text(min(df), min(dnu[:,0]),
             r"$\eta=%.3e,\quad C_x=%.2f,\quad C_y=%.2f$" %\
             (eta, chrom[0], chrom[1]))
    
    plt.legend(loc='upper right')
    plt.xlabel("$f-f_0$ [MHz]")
    plt.ylabel(r"$\nu-\nu_0$")
    plt.savefig('measchrom.png')
    putRfFrequency(f0)
    pass


def measDispersion():
    """
    Measure the dispersion
    """

    #print "Measure dispersion"
    
    gamma = 3.0e3/.511
    eta = alphac - 1/gamma/gamma

    #bpm = getElements('P*C0[3-6]*')
    bpm = getElements('P*')
    #print gamma, bpm
    s1 = getLocations(bpm)
    eta0 = getDispersion(bpm)
    
    # f in MHz
    f0 = getRfFrequency()
    f = np.linspace(f0 - 1e-4, f0 + 1e-4, 5)

    # avoid a bug in virtac
    obt = getOrbit(bpm)
    x0 = np.array([v[0] for v in obt])
    y0 = np.array([v[1] for v in obt])
    time.sleep(4)

    codx = np.zeros((len(f), len(bpm)), 'd')
    cody = np.zeros((len(f), len(bpm)), 'd')

    for i,f1 in enumerate(f): 
        putRfFrequency(f1)
        time.sleep(6)
        obt = np.array(getOrbit(bpm))
        x1, y1 = obt[:,0], obt[:,1] 

        putRfFrequency(f1)
        time.sleep(6)
        obt = np.array(getOrbit(bpm))
        x2, y2  = obt[:,0], obt[:,1]
        print(i, getRfFrequency(), x1[0], x2[0], x1[2], x2[2])
        codx[i,:] = x2[:]
        cody[i,:] = y2[:]

    putRfFrequency(f0)

    plt.clf()
    for i in range(len(bpm)):
        plt.plot(f, codx[:,i], 'o-')
    plt.savefig('test-cod.png')

    codx0 = np.zeros(np.shape(codx), 'd')
    for i in range(len(f)):
        codx0[i,:] = x0[:]
    dxc = codx - codx0
    df = -(f - f0)/f0/eta
    print(df)
    print(dxc)
    # p[0,len(bpm)]
    p = np.polyfit(df, dxc, 1)
    print("first order:", p[0,:])
    t = np.linspace(df[0], df[-1], 20)
    plt.clf()
    for i in range(len(bpm)):
        plt.plot(df, dxc[:,i], 'o')
        plt.plot(t, p[0,i]*t + p[1,i], '--')
    plt.savefig('test-disp.png')


    print(eta, f0)
    plt.clf()
    plt.plot(s1, eta0[:,0], 'x-', label="Twiss Calc")
    plt.plot(s1, p[0,:], 'o--', label="Fit")
    plt.legend()
    plt.savefig('test.png')

    dat = [(bpm[i], s1[i], p[0,i], eta0[i,0]) for i in range(len(bpm))]
    f = shelve.open("dispersion.pkl", 'c')
    f["dispersion"] = dat
    f.close()
    

def correctOrbitPv(bpm, trim, ormdata):
    """
    correct orbit use direct pv and catools

    - the input bpm and trim should be uniq in pv names.
    """
    #print "Matrix size: ", len(bpm), len(trim)
    m = np.zeros((len(bpm), len(trim)), 'd')
    for i,b in enumerate(bpm):
        im = ormdata.index(b)
        if im < 0: raise ValueError("PV %s is not found in ormdata" % b)
        for j,t in enumerate(trim):
            jm = ormdata.index(t)
            if jm < 0: raise ValueError("pv %s is not found in ormdata" % t)
            # did not check if the item is masked.
            m[i,j] = ormdata.m[im,jm]

    v0 = np.array(caget(bpm), 'd')
    dk, resids, rank, s = np.linalg.lstsq(m, -1.0*v0)
    k0 = np.array(caget(trim), 'd')
    caput(trim, k0+dk)

def correctOrbit(bpm, trim, **kwargs):
    """
    correct the orbit with given BPMs and Trims

    Example::

      correctOrbit(['BPM1', 'BPM2'], ['T1', 'T2', 'T3'])

    .. seealso:: :func:`hla.getSubOrm`
    """

    plane = kwargs.get('plane', 'HV')

    # an orbit based these bpm
    bpmlst = machines._lat.getElements(bpm)
    pvx = [e.pv(tags=[machines.HLA_TAG_X, machines.HLA_TAG_EGET])
           for e in bpmlst]
    pvy = [e.pv(tags=[machines.HLA_TAG_Y, machines.HLA_TAG_EGET])
           for e in bpmlst]

    if plane == 'H': bpmpv = set(pvx)
    elif plane == 'V': bpmpv = set(pvy)
    else: bpmpv = set(pvx + pvy)

    # pv for trim
    trimlst = machines._lat.getElements(trim)

    trimpv, pvxsp, pvysp = [], [], []
    for e in trimlst:
        pv = e.pv(tags=[machines.HLA_TAG_X, machines.HLA_TAG_EPUT])
        if pv: pvxsp.append(pv)
        if isinstance(pv, (str, unicode)): trimpv.append(pv)
        elif pv: trimpv.extend(pv)
        
        pv = e.pv(tags=[machines.HLA_TAG_Y, machines.HLA_TAG_EPUT])
        if pv: pvysp.append(pv)
        if isinstance(pv, (str, unicode)): trimpv.append(pv)
        else: trimpv.extend(pv)

    if 'H' in plane and len(pvx) > 0 and len(pvxsp) == 0:
        print("WARNING: no HCOR for horizontal orbit correction", file=sys.stderr)
    if 'V' in plane and len(pvy) > 0 and len(pvysp) == 0:
        print("WARNING: no VCOR for vertical orbit correction", file=sys.stderr)

    if not machines._lat.orm:
        print("ERROR: this lattice setting has no ORM data", file=sys.stderr)
    else:
        correctOrbitPv(list(set(bpmpv)), list(set(trimpv)), machines._lat.orm)


    