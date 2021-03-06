#!/usr/bin/env python

"""
NSLS2 V2 Unit Test
-------------------

- test_*_l0 for readonly test
- test_*_l1 for small perturbation, nonvisible to users
- test_*_l2 for beam steering test
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

# cause timeout by nosetest
# from cothread.catools import caget
# print caget('SR:C00-Glb:G00{POS:00}RB-S', timeout=10)

import sys, os, time
from fnmatch import fnmatch
from pkg_resources import resource_string, resource_exists, resource_filename
import matplotlib.pylab as plt

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
elif sys.version_info[:2] == (2,7):
    import unittest

import numpy as np
import random

import logging
logging.basicConfig(filename="utest.log",
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    level=logging.DEBUG)
from cothread import catools

logging.info("initializing NSLS2V2")

MACHINE = ("..", "machines", "nsls2v2")
import aphla as ap
ap.machines.load(MACHINE[-1])

LAT_SR = "V2SR"

logging.info("NSLS2V2 initialized")
PV_SR_DCCT='V:2-SR-BI{DCCT}CUR-I'
PV_REF_RB = [
    "V:2-SR:C15-BI:G2{PL1:1845}SA:X",
    "V:2-SR:C15-BI:G2{PL1:1845}SA:Y",
    "V:2-SR:C15-BI:G2{PL2:1865}SA:X",
    "V:2-SR:C15-BI:G2{PL2:1865}SA:Y",
    "V:2-SR:C15-BI:G4{PM1:1890}SA:X",
    "V:2-SR:C15-BI:G4{PM1:1890}SA:Y",
    "V:2-SR:C15-BI:G4{PM1:1900}SA:X",
    "V:2-SR:C15-BI:G4{PM1:1900}SA:Y",
    "V:2-SR:C15-BI:G6{PH2:1924}SA:X",
    "V:2-SR:C15-BI:G6{PH2:1924}SA:Y",
    "V:2-SR:C15-BI:G6{PH1:1939}SA:X",
    "V:2-SR:C15-BI:G6{PH1:1939}SA:Y"
    ]
ref_v0 = np.array(ap.caget(PV_REF_RB), 'd')

# name of BPMs
BPM1='ph2g2c30a'
BPM2='pm1g4c30a'

# plotting ?
PLOTTING = True
V1LTD1_OFFLINE = False
try:
    catools.caget("LTB:BI{BPM:1}Pos:X-I")
except:
    V1LTD1_OFFLINE = True

logging.info("V1LTD1_OFFLINE={0}".format(V1LTD1_OFFLINE))

def markForStablePv():
    global ref_v0, PV_REF_RB
    ref_v0 = np.array(ap.caget(PV_REF_RB), 'd')
    
def waitForStablePv(**kwargs):
    """
    wait for the orbit to be stable.

    This is in hlalib.py, but here does not need the dependance on getOrbit().
    """
    diffstd = kwargs.get('diffstd', 1e-7)
    minwait = kwargs.get('minwait', 2)
    maxwait = kwargs.get('maxwait', 30)
    step    = kwargs.get('step', 2)
    diffstd_list = kwargs.get('diffstd_list', False)
    verbose = kwargs.get('verbose', 0)

    t0 = time.time()
    time.sleep(minwait)
    global ref_v0
    dv = np.array(caget(PV_REF_RB)) - ref_v0
    dvstd = [dv.std()]  # record the history
    timeout = False

    while dv.std() < diffstd:
        time.sleep(step)
        dt = time.time() - t0
        if dt  > maxwait:
            timeout = True
            break
        dv = np.array(caget(PV_REF_RB)) - ref_v0
        dvstd.append(dv.std())

    if diffstd_list:
        return timeout, dvstd

def figname(name):
    rt, ext = os.path.splitext(name)
    return rt + time.strftime("_%y%m%d_%H%M%S") + ext
    

"""
Channel Finder
~~~~~~~~~~~~~~
"""

class T000_ChanFinder(unittest.TestCase):
    """
    """
    def setUp(self):
        self.cfs_url = os.environ.get('HLA_CFS_URL', None)
        self.cfdb ="test_nsls2v2.sqlite"
        pass

    def test_db_tags_l0(self):
        """read CFS_URL export to sqlite"""
        cfa = ap.chanfinder.ChannelFinderAgent()
        cfa.downloadCfs(self.cfs_url, tagName=ap.machines.HLA_TAG_PREFIX + '.*')
        cfa.saveSqlite(self.cfdb)
        cfa2 = ap.chanfinder.ChannelFinderAgent()
        cfa2.loadSqlite(self.cfdb)

        tags = cfa2.tags(ap.machines.HLA_TAG_SYS_PREFIX + '.V*')
        for t in ['V2SR', 'V1LTB', 'V1LTD1', 'V1LTD2']:
            self.assertIn(ap.machines.HLA_TAG_SYS_PREFIX + '.' + t, tags)

    def test_url_tags_l0(self):
        #http://web01.nsls2.bnl.gov/ChannelFinder
        cfa = ap.chanfinder.ChannelFinderAgent()
        cfa.downloadCfs(self.cfs_url, tagName=ap.machines.HLA_TAG_PREFIX + '.*')
        if self.cfs_url is None: return
        self.assertIsNotNone(self.cfs_url)

        tags = cfa.tags(ap.machines.HLA_TAG_SYS_PREFIX + '.V*')
        for t in ['V2SR', 'V1LTB', 'V1LTD1', 'V1LTD2']:
            self.assertIn(ap.machines.HLA_TAG_SYS_PREFIX + '.' + t, tags)



"""
Element
~~~~~~~
"""

class T010_Element(unittest.TestCase):
    def setUp(self):
        ap.machines.use(LAT_SR)
        pass 
        
    def tearDown(self):
        pass

    def test_nullelement_l0(self):
        pass

    def test_tune_l0(self):
        logging.info("test_tune")
        self.assertEqual(len(ap.getElements('tune')), 1)
        tune = ap.getElements('tune')[0]
        pvx = tune.pv(field='x')[0]
        pvy = tune.pv(field='y')[0]

        nux, nuy = tune.x, tune.y
        self.assertTrue(nux > 30.0)
        self.assertTrue(nuy > 15.0)

    def test_dcct_current_l0(self):
        self.assertGreater(ap.getCurrent(), 100.0)

        dccts = ap.getElements('dcct')
        self.assertEqual(len(dccts), 1)
        dcct = dccts[0]
        # current
        #pv = u'SR:C00-BI:G00{DCCT:00}CUR-RB'
        pv = PV_SR_DCCT
        vsrtag = 'aphla.sys.V2SR'
        self.assertEqual(dcct.name,    'dcct')
        #self.assertEqual(dcct.devname, 'DCCT')
        self.assertEqual(dcct.family,  'DCCT')
        self.assertEqual(len(dcct.pv()), 1)
        #self.assertEqual(dcct.pv(tag='aphla.eget'), [pv])
        self.assertEqual(dcct.pv(tag=vsrtag), [pv])
        #self.assertEqual(dcct.pv(tags=['aphla.eget', vsrtag]), [pv])

        self.assertIn('value', dcct.fields())
        self.assertGreater(dcct.value, 1.0)
        self.assertLess(dcct.value, 600.0)

        self.assertGreater(dcct.value, 1.0)
        self.assertGreater(ap.eget('DCCT', 'value', unitsys=None), 1.0)
        self.assertEqual(len(ap.eget('DCCT', ['value'], unitsys=None)), 1)
        self.assertGreater(ap.eget('DCCT', ['value'], unitsys=None)[0], 1.0)

    def test_bpm_l0(self):
        bpms = ap.getElements('BPM')
        self.assertGreaterEqual(len(bpms), 180)

        bpm = bpms[0]
        #self.assertEqual(bpm.pv(field='xref'), [pvxbba, pvxgold])
        self.assertGreater(bpm.index, 1)
        self.assertFalse(bpm.virtual)
        self.assertEqual(bpm.virtual, 0)
        #self.assertEqual(len(bpm.value), 2)

        self.assertIn('x', bpm.fields())
        self.assertIn('y', bpm.fields())
        self.assertEqual(len(bpm.get(['x', 'y'])), 2)
        self.assertEqual(len(ap.eget('BPM', 'x')), len(bpms))
        self.assertEqual(len(ap.eget('BPM', ['x', 'y'])), len(bpms))

        self.assertGreater(ap.getDistance(bpms[0].name, bpms[1].name), 0.0)

    def test_vbpm_l0(self):
        vbpms = ap.getElements('HLA:VBPM', include_virtual=True)
        self.assertIsNotNone(vbpms)
        vbpm = vbpms[0]
        self.assertIn('x', vbpm.fields())
        self.assertIn('y', vbpm.fields())

        bpms = ap.getElements('BPM')
        nbpm = len(bpms)
        self.assertEqual(len(vbpm.x), nbpm)
        self.assertEqual(len(vbpm.y), nbpm)
        self.assertEqual(len(vbpm.sb), nbpm)
        #print vbpm.x, np.std(vbpm.x)
        #print vbpm.y, np.std(vbpm.y)
        self.assertGreaterEqual(np.std(vbpm.x), 0.0)
        self.assertGreaterEqual(np.std(vbpm.y), 0.0)

    def test_hcor_l0(self):
        # hcor
        hcor = ap.element.CaElement(
            name = 'cxl1g2c01a', index = 125, cell = 'C01',
            devname = 'cl1g2c01a', family = 'HCOR', girder = 'G2', length = 0.2,
            sb = 30.4673, se = 30.6673, symmetry = 'A')

        self.assertTrue(hcor.name == 'cxl1g2c01a')
        self.assertTrue(hcor.cell == 'C01')
        self.assertTrue(hcor.girder == 'G2')
        self.assertTrue(hcor.devname == 'cl1g2c01a')
        self.assertTrue(hcor.family == 'HCOR')
        self.assertTrue(hcor.symmetry == 'A')


        self.assertAlmostEqual(hcor.length, 0.2)
        self.assertAlmostEqual(hcor.sb, 30.4673)
        self.assertAlmostEqual(hcor.se, 30.6673)

        pvrb = 'SR:C01-MG:G02A{HCor:L1}Fld-I'
        pvsp = 'SR:C01-MG:G02A{HCor:L1}Fld-SP'
        hcor.updatePvRecord(pvrb, {'handle': 'readback', 'field': 'x'})
        hcor.updatePvRecord(pvsp, {'handle': 'setpoint', 'field': 'x'}) 

        self.assertIn('x', hcor.fields())
        self.assertEqual(hcor.pv(field='x', handle='readback'), [pvrb])
        self.assertEqual(hcor.pv(field='x', handle='setpoint'), [pvsp])

        self.assertEqual(hcor.pv(field='y'), [])
        self.assertEqual(hcor.pv(field='y', handle='readback'), [])
        self.assertEqual(hcor.pv(field='y', handle='setpoint'), [])
        
        #v = ap.eget(hcor.name, ['x', 'y'])
        #self.assertGreaterEqual(abs(v[0]), 0.0)
        #self.assertIsNone(v[1])

    def test_cor_l0(self):
        hcor = ap.getElements('HCOR')
        self.assertEqual(len(hcor), 180)

        vcor = ap.getElements('VCOR')
        self.assertEqual(len(vcor), 180)

        cor = ap.getElements('COR')
        self.assertEqual(len(cor), 180)

        idcor = ap.getElements('IDCOR')
        self.assertGreater(len(idcor), 0)

        idsimcor = ap.getElements('IDSIMCOR')
        self.assertGreater(len(idsimcor), 0)

        self.assertEqual(len(idcor), len(idsimcor))

    def test_insertion_l0(self):
        ids = ap.getElements("INSERTION")
        self.assertEqual(len(ids), 12)


    def test_rf_l0(self):
        f0 = ap.getRfFrequency()
        v0 = ap.getRfVoltage()





"""
Lattice
-------------
"""

class T020_Lattice(unittest.TestCase):
    """
    Lattice testing
    """
    def setUp(self):
        logging.info("TestLattice")
        # this is the internal default lattice
        self.lat = ap.machines.getLattice("V2SR")
        self.assertTrue(self.lat)
        self.logger = logging.getLogger('tests.TestLattice')

    def test_neighbors_l0(self):
        bpm = self.lat.getElementList('BPM')
        self.assertTrue(bpm)
        self.assertGreaterEqual(len(bpm), 180)

        el = self.lat.getNeighbors(bpm[2].name, 'BPM', 2)
        self.assertEqual(len(el), 5)
        for i in range(5):
            self.assertEqual(el[i].name, bpm[i].name,
                             "%d: %s != %s" % (i, el[i].name, bpm[i].name))

    def test_virtualelements_l0(self):
        velem = ap.machines.HLA_VFAMILY
        elem = self.lat.getElementList(velem)
        self.assertTrue(elem)
        #elem = self.lat.getElementList(velem, 
        self.assertTrue(self.lat.hasGroup(ap.machines.HLA_VFAMILY))

    def test_getelements_l0(self):
        # get an empty list []
        el = ap.getElements('AABBCC')
        self.assertEqual(len(el), 0)
        # get a [None]
        el = ap.getElements(['AABBCC'])
        self.assertEqual(len(el), 1)
        self.assertIsNone(el[0])

        el = ap.getElements(BPM1)
        self.assertEqual(len(el), 1)
        self.assertTrue(isinstance(el[0], ap.element.CaElement))

        elems = self.lat.getElementList('BPM')
        self.assertEqual(len(elems), 180)
        

    def test_locations_l0(self):
        elem1 = self.lat.getElementList('*')
        for i in range(1, len(elem1)):
            if elem1[i-1].name in ['twiss', 'orbit']: continue
            if elem1[i-1].virtual: continue
            if elem1[i].virtual: continue
            #self.assertGreaterEqual(elem1[i].sb, elem1[i-1].sb,
            #                        msg="{0}({4},sb={1})<{2}({5}, sb={3}), d={6}".format(
            #                            elem1[i].name, elem1[i].sb, 
            #                            elem1[i-1].name, elem1[i-1].sb,
            #                            elem1[i].index, elem1[i-1].index,
            #                            elem1[i].sb - elem1[i-1].sb))
            self.assertGreaterEqual(
                elem1[i].sb - elem1[i-1].sb, -1e-9,
                msg="{0}({4},sb={1})<{2}({5}, sb={3}), diff={6}".format(
                    elem1[i].name, elem1[i].sb,
                    elem1[i-1].name, elem1[i-1].sb,
                    elem1[i].index, elem1[i-1].index,
                    elem1[i].sb - elem1[i-1].sb))
            
            self.assertGreaterEqual(
                elem1[i].se, elem1[i-1].sb,
                msg="{0}({4},se={1})<{2}(sb={3})".format(
                    elem1[i].name, elem1[i].se, elem1[i-1].name, elem1[i-1].sb, 
                    i))

        elem1 = self.lat.getElementList('BPM')
        for i in range(1, len(elem1)):
            self.assertGreaterEqual(
                elem1[i].sb, elem1[i-1].sb,
                msg = "%f (%s) %f (%s)" % (
                    elem1[i].sb, elem1[i].name,
                    elem1[i-1].sb, elem1[i-1].name))
            
        elem1 = self.lat.getElementList('QUAD')
        for i in range(1, len(elem1)):
            self.assertGreaterEqual(
                elem1[i].sb, elem1[i-1].sb,
                msg = "%f (%s) %f (%s)" % (
                    elem1[i].sb, elem1[i].name,
                    elem1[i-1].sb, elem1[i-1].name))
        

    def test_groups_l0(self):
        grp = 'HLATEST'
        self.assertFalse(self.lat.hasGroup(grp))
        self.lat.addGroup(grp)
        self.assertTrue(self.lat.hasGroup(grp))

        #with self.assertRaises(ValueError) as ve:
        #    self.lat.addGroupMember(grp, 'A')
        #self.assertEqual(ve.exception, ValueError)

        self.lat.removeGroup(grp)
        self.assertFalse(self.lat.hasGroup(grp))


"""
Test1Lattice
~~~~~~~~~~~~~
"""
        
class T030_LatticeSr(unittest.TestCase):
    def setUp(self):
        logging.info("TestLatticeSr")
        self.lat = ap.machines.getLattice('V2SR')
        self.logger = logging.getLogger('tests.TestLatticeSr')
        pass

    def test_orbit_l0(self):
        v = ap.getOrbit()

    def test_tunes_l0(self):
        tune, = self.lat.getElementList('tune')
        self.assertTrue(abs(tune.x) > 0)
        self.assertTrue(abs(tune.y) > 0)
        
    def test_current_l0(self):
        self.assertTrue(self.lat.hasElement('dcct'))
        
        cur1a = self.lat['dcct']
        cur1b, = self.lat.getElementList('dcct')
        self.assertLessEqual(cur1a.sb, 0.0)
        self.assertGreater(cur1a.value, 0.0)
        self.assertGreater(cur1b.value, 0.0)

    def test_lines_l0(self):
        elem1 = self.lat.getElementList('DIPOLE')
        s0, s1 = elem1[0].sb, elem1[0].se
        i = self.lat._find_element_s((s0+s1)/2.0)
        self.assertTrue(i >= 0)
        i = self.lat.getLine(srange=(0, 25))
        self.assertGreater(len(i), 1)

    def test_getelements_sr_l0(self):
        elems = self.lat.getElementList(['pl1g2c01a', 'pl2g2c01a'])
        self.assertTrue(len(elems) == 2)
        
        # only cell 1,3,5,7,9 and PL1, PL2
        elems = self.lat.getElementList('pl*g2c0*')
        self.assertEqual(len(elems), 10, msg="{0}".format(elems))

    def test_groupmembers_l0(self):
        bpm1 = self.lat.getElementList('BPM')
        g2a = self.lat.getElementList('G2')
        
        b1 = self.lat.getGroupMembers(['BPM', 'C20'], op='intersection')
        self.assertEqual(len(b1), 6)
        
        b1 = self.lat.getGroupMembers(['BPM', 'G2'], op='union')
        self.assertGreater(len(b1), len(bpm1))
        self.assertTrue(len(b1) > len(g2a))
        self.assertTrue(len(b1) < len(bpm1) + len(g2a))
        
        cx1 = self.lat.getElementList('HCOR')
        c1 = self.lat.getGroupMembers(['HCOR', 'QUAD'],
                                            op = 'intersection')
        self.assertFalse(c1)

        elem1 = self.lat.getGroupMembers(
            ['BPMX', 'TRIMX', 'QUAD', 'TRIMY'], op='union')
        self.assertTrue(len(elem1) > 120)
        for i in range(len(elem1)):
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb)

        el1 = self.lat.getGroupMembers(['BPM', 'C0[2-3]', 'G2'],
                                            op='intersection')
        self.assertEqual(len(el1), 4)

    def test_field_l1(self):
        bpm = self.lat.getElementList('BPM')
        self.assertTrue(len(bpm) > 0)
        for e in bpm: 
            self.assertTrue(abs(e.x) >= 0)
            self.assertTrue(abs(e.y) >= 0)

        hcor = self.lat.getElementList('HCOR')
        self.assertTrue(len(bpm) > 0)
        for e in hcor: 
            k = e.x
            e.x = 1e-8
            self.assertTrue(abs(e.x) >= 0)
            e.x = k
            try:
                k = e.y
            except:
                pass
            # the new setting has H/V COR combined. H/V COR is a group name now
            #else:
            #    self.assertTrue(False,
            #"AttributeError exception expected")

    def test_ids_l0(self):
        self.assertIn('INSERTION', self.lat.getGroups())
        self.assertIn('IVU', self.lat.getGroups())
        self.assertIn('EPU', self.lat.getGroups())
        self.assertIn('DW', self.lat.getGroups())

    def test_eget(self):
        v, h = ap.eget('BPM', 'x', header=True)
        self.assertEqual(len(v), len(ap.getElements('BPM')))
        self.assertEqual(len(v), len(h))
        # a tuple of (name, 'x')
        self.assertEqual(len(h[0]), 2)

        v, h = ap.eget('BPM', ['x'], header=True)
        self.assertEqual(len(v), len(ap.getElements('BPM')))
        self.assertEqual(len(v), len(h))
        # a list [(name, 'x')]
        self.assertEqual(len(h[0]), 1)

        v, h = ap.eget('BPM', ['x', 'y', 'x'], header=True)
        self.assertEqual(len(v), len(ap.getElements('BPM')))
        self.assertEqual(len(v), len(h))
        # a list [(name, 'x')]
        self.assertEqual(len(h[0]), 3)

        
class T040_LatticeLtd1(unittest.TestCase):
    def setUp(self):
        logging.info("TestLatticeLtd1")
        ap.machines.use("V1LTD1")
        self.lat  = ap.machines._lat
        self.assertTrue(self.lat)
        self.logger = logging.getLogger('tests.TestLatticeLtd1')
        
    def tearDown(self):
        ap.machines._lat = self.lat

    @unittest.skipIf(V1LTD1_OFFLINE, "V1LTD1 offline")
    def test_image_l0(self):
        #lat = ap.machines._lat
        #ap.machines.use('V1LTD1')
        #vf = ap.getElements('vf1bd1')[0]
        #self.assertIn('image', vf.fields(), "'image' is not defined in '{0}': {1}".format(vf.name, vf.fields()))

        #d = np.reshape(vf.image, (vf.image_ny, vf.image_nx))
        #import matplotlib.pylab as plt
        #plt.imshow(d)
        #plt.savefig("test.png")
        return

    def _gaussian(self, height, center_x, center_y, width_x, width_y):
        """Returns a gaussian function with the given parameters"""
        width_x = float(width_x)
        width_y = float(width_y)
        return lambda x,y: height*np.exp(
            -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

    @unittest.skip("for lower version of Python/modules")
    def test_fit_gaussian_image_l0(self):
        import matplotlib.pylab as plt
        from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
        from mpl_toolkits.axes_grid1.inset_locator import mark_inset
        d1 = ap.catools.caget('LTB-BI:BD1{VF1}Img1:ArrayData')

        self.assertEqual(len(d1), 1220*1620)

        d2 = np.reshape(d1, (1220, 1620))
        params = ap.fitGaussianImage(d2)
        fit = self._gaussian(*params)

        plt.clf()
        extent=(500, 1620, 400, 1220)
        #plt.contour(fit(*np.indices(d2.shape)), cmap=plt.cm.copper)
        plt.imshow(d2, interpolation="nearest", cmap=plt.cm.bwr)
        ax = plt.gca()
        ax.set_xlim(750, 850)
        ax.set_ylim(550, 650)
        (height, y, x, width_y, width_x) = params
        #axins = zoomed_inset_axes(ax, 6, loc=1)
        #axins.contour(fit(*np.indices(d2.shape)), cmap=plt.cm.cool)
        #axins.set_xlim(759, 859)
        #axins.set_ylim(559, 660)
        #mark_inset(ax, axins, loc1=2, loc2=4, fc='none', ec='0.5')

        plt.text(0.95, 0.05, """
        x : %.1f
        y : %.1f
        width_x : %.1f
        width_y : %.1f""" %(x, y, width_x, width_y),
             fontsize=16, horizontalalignment='right',
             verticalalignment='bottom', transform=ax.transAxes)

        plt.savefig(figname("test2.png"))

    @unittest.skipIf(V1LTD1_OFFLINE, "V1LTD1 offline")
    def test_virtualelements_l0(self):
        pass


class T050_LatticeLtb(unittest.TestCase):
    def setUp(self):
        logging.info("TestLatticeLtb")
        self.lat  = ap.machines.getLattice('V1LTB')
        self.assertTrue(self.lat)
        self.logger = logging.getLogger('tests.TestLatticeLtb')

    @unittest.skipIf(V1LTD1_OFFLINE, "V1LTD1 offline")
    def readInvalidFieldY(self, e):
        k = e.y
        
    @unittest.skipIf(V1LTD1_OFFLINE, "V1LTD1 offline")
    def test_field_l0(self):
        bpmlst = self.lat.getElementList('BPM')
        self.assertGreater(len(bpmlst), 0)
        
        elem = bpmlst[0]
        self.logger.info("checking '{0}'".format(elem.name))
        self.assertGreaterEqual(abs(elem.x), 0)
        self.assertGreaterEqual(abs(elem.y), 0)

        hcorlst = self.lat.getElementList('HCOR')
        self.assertGreater(len(hcorlst), 0)
        for e in hcorlst: 
            self.logger.warn("Skipping 'x' of %s" % e.name)
            #self.assertGreaterEqual(abs(e.x), 0.0)
            #k = e.x
            #e.x = k + 1e-10
            #self.assertGreaterEqual(abs(e.x), 0.0)
            pass

    def test_virtualelements_l0(self):
        pass


"""
Twiss
~~~~~
"""

class T060_Tunes(unittest.TestCase):
    def setUp(self):
        ap.machines.use("V2SR")
        logging.info("TestTunes")
        self.plot = True

    def test_tunes_l0(self):
        nu = ap.getTunes()
        self.assertEqual(len(nu), 2)
        self.assertGreater(nu[0], 0.0)
        self.assertGreater(nu[1], 0.0)

    def test_meas_beta_l2(self):
        qs = ap.getGroupMembers(['C30', 'QUAD'])
        beta, k1, nu = ap.measBeta(qs, full=True)
        self.assertEqual(np.shape(beta), (len(qs), 3))
        #self.assertEqual(np.shape(k1)[1], 3)
        self.assertEqual(np.shape(k1)[0], len(qs))
        self.assertEqual(np.shape(nu)[0], len(qs))
        self.assertEqual(np.shape(k1)[1], np.shape(nu)[1])
        #self.assertEqual(np.shape(k1)[0], len(qs))

        if PLOTTING:
            for i,q in enumerate(qs):
                plt.clf()
                plt.subplot(211)
                plt.plot(k1[i,:], nu[i,:,0], 'r-v')
                plt.subplot(212)
                plt.plot(k1[i,:], nu[i,:,1], 'r-v')
                plt.savefig(figname("meas_beta_nu_%s.png" % q.name))

            plt.clf()
            plt.plot(beta[:,-1], beta[:,0], 'r-v')
            plt.plot(beta[:,-1], beta[:,1], 'b-o')
            plt.savefig(figname("meas_beta_beta.png"))

    def test_meas_dispersion_l2(self):
        eta = ap.measDispersion('p*c0[2-4]*')
        s, etax, etay = eta[:,-1], eta[:,0], eta[:,1]

        if PLOTTING:
            plt.clf()
            plt.plot(s, etax, '-x', label=r'$\eta_x$')
            plt.plot(s, etay, '-o', label=r'$\eta_y$')
            plt.legend(loc='upper right')
            plt.savefig(figname('test_twiss_dispersion_meas.png'))

        self.assertGreater(max(abs(etax)), 0.15)
        self.assertGreater(max(abs(etay)), 0.0)
        self.assertGreater(min(abs(s)), 0.0)

    @unittest.skip
    def test_phase_get(self):
        phi = ap.machines.getLattice().getPhase('P*C1[0-1]*')
        s, phix, phiy = phi[:,-1], phi[:,0], phi[:,1]
        if False:
            import matplotlib.pylab as plt
            plt.clf()
            plt.plot(s, phix, '-x', label=r'$\phi_x$')
            plt.plot(s, phiy, '-o', label=r'$\phi_y$')
            plt.legend(loc='upper left')
            plt.savefig(figname('test_twiss_phase_get.png'))
        pass


    def test_beta_get(self):
        beta = ap.machines.getLattice().getBeta('p*c1[5-6]*')
        s, twx, twy = beta[:,-1], beta[:,0], beta[:,1]
        if self.plot:
            import matplotlib.pylab as plt
            twl = ap.machines.getLattice().getBeamlineProfile(sb=s[0], se=s[-1])
            sprof, vprof = [], []
            for tw in twl:
                sprof.extend(tw[0])
                vprof.extend(tw[1])

            plt.clf()
            plt.plot(sprof, vprof, 'k-')
            plt.plot(s, twx, '-x', label=r'$\beta_x$')
            plt.plot(s, twy, '-o', label=r'$\beta_y$')
            plt.legend(loc='upper right')
            plt.savefig(figname('test_twiss_beta_get.png'))
        self.assertGreater(max(abs(twx)), 20.0)
        self.assertGreater(max(abs(twy)), 20.0)

    def test_tune_get(self):
        """
        The tunes stored in lattice._twiss is not live, while ap.getTunes is
        live.
        """

        lat = ap.machines.getLattice()
        tunes0a = lat.getTunes()
        self.assertEqual(int(tunes0a[0]), 33, "wrong nux %f" % tunes0a[0])
        self.assertEqual(int(tunes0a[1]), 16, "wrong nuy %f" % tunes0a[1])

        # adjust quad, live tune should change
        qs = lat.getElementList('QUAD')
        k1 = qs[0].k1
        qs[0].k1 = k1 * 1.02
        time.sleep(6)
        try:
            tunes0b = lat.getTunes()
            tunes1 = ap.getTunes()
        finally:
            qs[0].k1 = k1
        
        self.assertEqual(tunes0a[0], tunes0b[0])
        self.assertEqual(tunes0a[1], tunes0b[1])
        self.assertNotEqual(tunes0b[0], tunes1[0])
        self.assertNotEqual(tunes0b[1], tunes1[1])
        

    @unittest.skip("not implemented")
    def test_chromaticities(self):
        ch = ap.getChromaticities()
        self.assertEqual(abs(ch[0]), 0)
        self.assertEqual(abs(ch[1]), 0)
        pass

"""
Orbit
~~~~~~
"""

class TestOrbit(unittest.TestCase):
    """
    Tested:

    - orbit dimension
    """
    def setUp(self):
        ap.machines.use("V2SR")
        self.logger = logging.getLogger("tests.TestOrbit")
        self.lat = ap.machines.getLattice('V2SR')
        self.assertTrue(self.lat)
        self.kickers = []
        cors = self.lat.getElementList('COR')
        for c in cors:
            cx, cy = None, None
            if 'x' in c.fields(): cx = c.x
            if 'y' in c.fields(): cy = c.y
            self.kickers.append([c, cx, cy])

    def tearDown(self):
        self.logger.info("tearDown")
        for kicker,vx,vy in self.kickers:
            if vx is not None: kicker.x = vx
            if vy is not None: kicker.y = vy
       
    def _random_kick(self, n, vx = 1e-4, vy = 1e-4):
        v0 = ap.getOrbit()
        hcors = self.lat.getElementList('COR')
        for i in range(n):
            k = np.random.randint(len(hcors))
            v0x, v0y = hcors[k].x, hcors[k].y
            self.kickers.append([hcors[k], v0x, v0y])
            hcors[k].x = vx
            hcors[k].y = vy
        ap.hlalib.waitStableOrbit(v0, minwait=3)

    def test_orbit_read_l0(self):
        self.logger.info("reading orbit")    
        self.assertGreater(len(ap.getElements('BPM')), 0)
        bpm = ap.getElements('BPM')
        for i,e in enumerate(bpm):
            self.assertGreaterEqual(abs(e.x), 0)
            self.assertGreaterEqual(abs(e.y), 0)

        v = ap.getOrbit()
        self.assertGreater(len(v), 0)
        v = ap.getOrbit('*')
        self.assertGreater(len(v), 0)
        v = ap.getOrbit('p[lhm]*')
        self.assertGreater(len(v), 0)

    def test_corr_orbit_l2(self):
        self._random_kick(3)
        obt = ap.getOrbit()
        bpm = ap.getElements('BPM')[60:101]
        trim = ap.getGroupMembers(['*', '[HV]COR'], op='intersection')
        v0 = ap.getOrbit('p*', spos=True)
        ap.correctOrbit(bpm, trim, repeat=5, scale=0.9)
        time.sleep(4)
        v1 = ap.getOrbit('p*', spos=True)

        import matplotlib.pylab as plt
        plt.clf()
        ax = plt.subplot(211) 
        fig = plt.plot(v0[:,-1], v0[:,0], 'r-x', label='X(before)') 
        fig = plt.plot(v1[:,-1], v1[:,0], 'g-o', label='X(after)')
        plt.legend()
        ax = plt.subplot(212)
        fig = plt.plot(v0[:,-1], v0[:,1], 'r-x', label='Y(before)')
        fig = plt.plot(v1[:,-1], v1[:,1], 'g-o', label='Y(after)')
        plt.legend()
        plt.savefig(figname("test_nsls2_orbit_correct.png"))

    @unittest.skip
    def test_orbit_bump(self):
        v0 = ap.getOrbit()
        bpm = ap.getElements('BPM')
        hcor = ap.getElements('HCOR')
        hcor1 = ap.getElements('cx*')
        vcor = ap.getElements('VCOR')
        vcor1 = ap.getElements('cy*')
        #for e in hcor:
        #    print e.name, e.pv(field='x')

        self.assertGreater(len(v0), 0)
        self.assertGreaterEqual(len(bpm), 180)
        self.assertEqual(len(hcor1), 180)
        self.assertGreaterEqual(len(hcor), 180)
        self.assertEqual(len(vcor1), 180)
        self.assertGreaterEqual(len(vcor), 180)

        # maximum deviation
        mx, my = max(abs(v0[:,0])), max(abs(v0[:,1]))
        ih = np.random.randint(0, len(hcor), 3)
        iv = np.random.randint(0, len(vcor), 4)

        for i in ih: hcor[i].x = hcor[i].x+np.random.rand()*1e-6
        for i in iv: vcor[i].y = vcor[i].y+np.random.rand()*1e-6

        ap.hlalib.waitStableOrbit(v0, minwait=5)

        v1 = ap.getOrbit()
        self.assertNotEqual(np.std(v1[:,0]), np.std(v0[:,0]))
        self.logger.info("resetting trims")
        ap.hlalib._reset_trims()
        time.sleep(10)

    def test_golden(self):
        f = open("golden.txt", "w")
        cors = ap.getElements('COR')
        for c in cors:
            c.x = 0.0
            c.y = 0.0
        time.sleep(2)
        obt0a = ap.getOrbit(spos=True)
        for scale in [1.0, 0.9, 0.8, 0.7, 0.6]:
            ap.correctOrbit(scale=scale, wait=3)
        time.sleep(6)
        obt0 = ap.getOrbit(spos=True)
        d0 = np.zeros((len(cors), 2), 'd')
        for i,c in enumerate(cors):
            d0[i,0] = c.x
            d0[i,1] = c.y
            c.setGolden('x', d0[i,0], unitsys=None)
            c.setGolden('y', d0[i,1], unitsys=None)
            f.write("{0} x {1}\n".format(c.name, d0[i,0]))
            f.write("{0} y {1}\n".format(c.name, d0[i,1]))
        f.close()
        # now reset the orbit
        time.sleep(5)
        for c in cors:
            c.x = 0.0
            c.y = 0.0
        for i,c in enumerate(cors):
            c.reset('x', data='golden')
            c.reset('y', data='golden')
        time.sleep(6)
        d1 = np.zeros((len(cors), 2), 'd')
        for i,c in enumerate(cors):
            d1[i,0] = c.x
            d1[i,1] = c.y
        obt1 = ap.getOrbit(spos=True)

        plt.subplot(311)
        plt.plot(obt0a[:,-1], obt0a[:,0], 'g-')
        plt.plot(obt0[:,-1], obt0[:,0], 'r-')
        plt.plot(obt1[:,-1], obt1[:,0], 'b--')
        plt.subplot(312)
        plt.plot(d1[:,0] - d0[:,0], 'r-')
        plt.plot(d1[:,1] - d0[:,1], 'b--')
        plt.subplot(313)
        plt.plot(obt0[:,-1], obt1[:,0] - obt0[:,0], 'r-x')
        plt.plot(obt1[:,-1], obt1[:,1] - obt0[:,1], 'b-o')
        plt.savefig(figname("test_golden.png"))


class TestOrbitControl(unittest.TestCase): 
    def setUp(self):
        ap.machines.use("V2SR")
        pass

    def tearDown(self):
        ap.hlalib._reset_trims()
        pass

    @unittest.skip
    def test_correct_orbit(self):
        ap.hlalib._reset_trims()

        # a list of horizontal corrector
        hcor = ap.getElements('HCOR')
        hcor_v0 = [e.x for e in hcor]
        # a list of vertical corrector
        vcor = ap.getElements('VCOR')
        vcor_v0 = [e.y for e in vcor]

        bpm = ap.getElements('BPM')
        bpm_v0 = np.array([(e.x, e.y) for e in bpm], 'd')

        norm0 = (np.linalg.norm(bpm_v0[:,0]), np.linalg.norm(bpm_v0[:,1]))

        ih = np.random.randint(0, len(hcor), 4)
        for i in ih:
            hcor[i].x = np.random.rand() * 1e-5

        iv = np.random.randint(0, len(vcor), 4)
        for i in iv:
            vcor[i].y = np.random.rand() * 1e-5

        #raw_input("Press Enter to correct orbit...")
        time.sleep(6)

        cor = []
        #cor.extend([e.name for e in hcor])
        #cor.extend([e.name for e in vcor])
        cor.extend([hcor[i].name for i in ih])
        cor.extend([vcor[i].name for i in iv])

        bpm_v1 = np.array([(e.x, e.y) for e in bpm], 'd')
        norm1 = (np.linalg.norm(bpm_v1[:,0]), np.linalg.norm(bpm_v1[:,1]))

        self.assertGreater(norm1[0], norm0[0])

        ap.correctOrbit([e.name for e in bpm], cor)
        ap.correctOrbit(bpm, cor)

        #raw_input("Press Enter to recover orbit...")
        bpm_v2 = np.array([(e.x, e.y) for e in bpm], 'd')
        #print "Euclidian norm:", 
        norm2 = (np.linalg.norm(bpm_v2[:,0]), np.linalg.norm(bpm_v2[:,1]))
        self.assertLess(norm2[0], norm1[0])
        self.assertLess(norm2[1], norm1[1])

        for i in ih:
            hcor[i].x = hcor_v0[i]

        for i in iv:
            vcor[i].y = vcor_v0[i]

        time.sleep(4)
        #raw_input("Press Enter ...")
        bpm_v3 = np.array([(e.x, e.y) for e in bpm], 'd')
        #print "Euclidian norm:", 
        norm3 = (np.linalg.norm(bpm_v3[:,0]), np.linalg.norm(bpm_v3[:,1]))
        self.assertLess(norm3[0], norm1[0])
        self.assertLess(norm3[0], norm1[0])

        #for i in range(len(ih)):
        #    x, y = hcor[ih[i]].x, vcor[iv[i]].y
        #    print i, (x - hcor_v0[ih[i]]), (y - vcor_v0[iv[i]])

    def test_orm_x1(self):
        hcor = ap.getElements('HCOR')[2]
        bpm1 = ap.getElements('BPM')[5]
        bpm2 = ap.getElements('BPM')[51]
        x0 = hcor.x
        b1, b2 = bpm1.x, bpm2.x
        d = np.zeros((7, 3), 'd')
        for i,dx in enumerate(np.linspace(-1e-4, 1e-4, len(d))):
            hcor.x = x0 + dx
            d[i,0] = hcor.x
            time.sleep(4)
            d[i,1] = bpm1.x
            d[i,2] = bpm2.x
        #
        ormd = ap.machines._lat.ormdata
        bpmr, trimr = [(bpm1.name, 'x'), (bpm2.name, 'x')], [(hcor.name, 'x')]
        m, b, t = ormd.getMatrix(bpmr, trimr, full=False)
        import matplotlib.pylab as plt
        plt.clf()
        plt.plot(d[:,0], d[:,1], 'bo--')
        plt.plot(d[:,0], m[0,0]*d[:,0] + b1, 'b-')
        plt.plot(d[:,0], d[:,2], 'rv--')
        plt.plot(d[:,0], m[1,0]*d[:,0] + b2, 'r-')
        plt.savefig(figname("test_orm.png"))
        hcor.x = x0

    def test_local_bump(self):
        hcor = ap.getElements('HCOR')
        hcor_v0 = [e.x for e in hcor]
        vcor = ap.getElements('VCOR')
        vcor_v0 = [e.y for e in vcor]

        bpm = ap.getElements('BPM')
        bpm_v0 = [[e.x, e.y] for e in bpm]

        bpm_v1 = [[e.x, e.y] for e in bpm]

        for i in range(0, len(bpm)):
            bpm_v1[i] = [0, 0]
        x1, x2 = 1e-4, 2e-4
        bpm_v1[20][0] = x1
        bpm_v1[21][0] = x1
        bpm_v1[22][0] = x1
        bpm_v1[23][0] = x2
        bpm_v1[24][0] = x2
        bpm_v1[25][0] = x1
        bpm_v1[26][0] = x1

        bpm_v1[100][1] = x2
        bpm_v1[101][1] = x2
        bpm_v1[102][1] = x1
        bpm_v1[103][1] = x1
        bpm_v1[104][1] = x2
        bpm_v1[105][1] = x2

        ap.setLocalBump(bpm, hcor+vcor, bpm_v1, repeat=10, verbose=3)

        import matplotlib.pylab as plt
        plt.clf()
        v = ap.getOrbit(spos=True)
        plt.plot(v[:,-1], v[:,0], '-.')
        plt.plot(v[:,-1], v[:,1], '--')
        plt.savefig(figname("test_localbump.png"))


"""
BBA
~~~
"""

class TestBba(unittest.TestCase):
    def setUp(self):
        # ap.machines.init("nsls2v2")
        # ap.hlalib._reset_trims(verbose=True)
        pass

    def test_quad_l0(self):
        qnamelist = ['qh1g2c02a', 'qh1g2c04a', 'qh1g2c06a', 'qh1g2c08a']

        qlst = ap.getElements(qnamelist)
        for i,q in enumerate(qnamelist):
            self.assertGreater(abs(qlst[i].k1), 0.0)

    def test_bba_l2(self):
        """test bba"""
        # hard coded quad and its strength
        q, cor, bpm = ap.getElements(['ql3g2c29a', 'cl2g2c29a', 'pl2g2c29a'])
        q.put("k1", -1.4894162702, unitsys=None)
        cor.put("x", 0.0, unitsys=None)
        cor.put("y", 0.0, unitsys=None)

        #print q.fields(), q.get('k1', unitsys=None)

        inp = { 'quad': (q, 'k1'), 'cor': (cor, 'x'),
                'bpm': (bpm, 'x'),
                'quad_dkick': -6e-2, 
                'cor_dkicks': np.linspace(-6e-6, 1e-4, 5) }

        bba = ap.bba.BbaBowtie(**inp)
        bba.align()
        bba.plot()

"""
ORM
~~~~
"""

class TestOrm(unittest.TestCase):
    def setUp(self):
        #self.h5filename = "v2sr.hdf5"
        self.lat = ap.machines.getLattice("V2SR")
        self.ormdata = self.lat.ormdata

    def tearDown(self):
        pass

    def test_trim_bpm(self):
        trims = [e.name for e in ap.getElements('COR')]
        for trim in trims:
            self.assertTrue(self.ormdata.hasTrim(trim))

        bpmx = ap.getGroupMembers(['BPM', 'C0[2-4]'], op='intersection')
        self.assertEqual(len(bpmx), 18)
        for bpm in bpmx:
            self.assertTrue(self.ormdata.hasBpm(bpm.name))
        

    def test_measure_orm_sub1_l2(self):
        #trimlst = ['ch1g6c15b', 'cl2g6c14b', 'cm1g4c26a']
        trimlst = ['cl2g6c14b']
        #trimx = ['CXH1G6C15B']
        bpmlst = [e.name for e in ap.getElements('BPM')]
        trims = ap.getElements(trimlst)
        for t in trims: 
            t.x = 0
            t.y = 0

        fname = time.strftime("orm_sub1_%Y%m%d_%H%M.hdf5")
        orm1 = ap.measOrbitRm(bpmlst, trimlst, fname, verbose=2)

        ormdat = ap.apdata.OrmData(fname)
        
        corr = trims[0] 
        x0 = corr.x
        obt0 = ap.getOrbit(spos=True)
        dxlst = np.linspace(-1e-4, 1e-4, 5) + x0
        obt = []
        for i,dx in enumerate(dxlst):
            corr.x = dx
            time.sleep(3)
            obt.append(ap.getOrbit(spos=True))

        jbpm = 36
        bpm = ap.getExactElement(bpmlst[jbpm])
        mij = ormdat.get(bpm.name, 'x', corr.name, 'x')
        dxobt = [obt[i][jbpm,0] for i in range(len(dxlst))]
        plt.clf()
        plt.plot(dxlst, dxobt, 'r--o')
        plt.plot(dxlst, mij*dxlst + obt0[jbpm,0])
        plt.savefig(figname("test_measure_orm_sub1_linearity.png"))
        corr.x = x0

    def test_measure_orm_l2(self):
        bpms = ap.getElements('BPM')
        trims = ap.getElements('COR')
        
        # if jenkins run this test, measure whole ORM
        nbpm, ntrim = 5, 2
        if "JENKINS_URL" in os.environ and \
           int(os.environ.get("BUILD_NUMBER", "0")) % 2 == 0:
            nbpm, ntrim = len(bpms), len(trims)
        bpmlst = [b.name for b in bpms[:nbpm]]
        trimlst = [t.name for t in trims[:ntrim]]
        fname = time.strftime("orm_%Y%m%d_%H%M.hdf5")
        ap.measOrbitRm(bpmlst, trimlst, fname, verbose=2, minwait=5)



    def test_linearity_l2(self):
        bpms = self.ormdata.getBpmNames()
        trims = self.ormdata.getTrimNames()
        corrname = trims[4]
        corr = ap.getExactElement(corrname)
        x0 = corr.x
        obt0 = ap.getOrbit(spos=True)
        dxlst = np.linspace(-1e-4, 1e-4, 5) + x0
        obt = []
        for i,dx in enumerate(dxlst):
            corr.x = dx
            time.sleep(3)
            obt.append(ap.getOrbit(spos=True))

        jbpm = 36
        bpm = ap.getExactElement(bpms[jbpm])
        mij = self.ormdata.get(bpm.name, 'x', corr.name, 'x')
        dxobt = [obt[i][jbpm,0] for i in range(len(dxlst))]
        plt.clf()
        plt.plot(dxlst, dxobt, 'r--o')
        plt.plot(dxlst, mij*dxlst + obt0[jbpm,0])
        plt.savefig(figname("test_ormdata_linearity.png"))
        corr.x = x0
        
        #print orm
        #for i,b in enumerate(orm.bpm):
        #    print i, b[0], b[2]
        #orm.checkLinearity(plot=True)
        pass

    @unittest.skip("not implemented yet")
    def test_update(self):
        """
        same data different mask
        """
        bpmlst = [e.name for e in ap.getElements('BPM')]
        trimlst = ['ch1g6c15b', 'cl2g6c14b', 'cm1g4c26a']
        trimlst1 = trimlst[0:1]
        trimlst2 = trimlst[1:2]

        #trimx = ['CXH1G6C15B']
        trims = ap.getElements(trimlst)
        for t in trims: 
            t.x = 0
            t.y = 0

        nametag = time.strftime("%Y%m%d_%H%M.hdf5")
        fname1 = "orm_update_1_" + nametag
        fname2 = "orm_update_2_" + nametag
        orm1 = ap.measOrbitRm(bpmlst, trimlst1, fname1, verbose=2)
        orm2 = ap.measOrbitRm(bpmlst, trimlst2, fname2, verbose=2)

        ormdata_dst = ap.OrmData(fname1)
        ormdata_src = ap.OrmData(fname2)
        
        ormdata_dst.update(ormdata_src)

        self.assertIn(trimlst2[0], ormdata_dst.getTrimNames())


    @unittest.skip("not implemented yet")
    def test_update_swapped(self):
        """
        same dimension, swapped rows
        """
        self.assertTrue(ap.conf.has(self.h5filename))
        ormdata_dst = ap.OrmData(ap.conf.filename(self.h5filename))
        ormdata_src = ap.OrmData(ap.conf.filename(self.h5filename))
        
        nrow, ncol = len(ormdata_src.bpm), len(ormdata_src.trim)
        # reset data
        for i in range(nrow):
            for j in range(ncol):
                ormdata_src.m[i,j] = 0.0

        # rotate the rows down by 2
        import collections
        rbpm = collections.deque(ormdata_src.bpm)
        rbpm.rotate(2)
        ormdata_src.bpm = [b for b in rbpm]

        for itrial in range(10):
            idx = []
            for i in range(nrow*ncol//4):
                k = random.randint(0, nrow*ncol-1)
                idx.append(divmod(k, ncol))
                ormdata_src._mask[idx[-1][0]][idx[-1][1]] = 0

        ormdata_dst.update(ormdata_src)
        for i,j in idx:
            i0, j0 = (i-2+nrow) % nrow, (j + ncol) % ncol
            self.assertEqual(ormdata_dst.m[i0,j0], 0.0)

    @unittest.skip("not implemented yet")
    def test_update_submatrix(self):
        """
        same dimension, swapped rows
        """
        self.assertTrue(ap.conf.has(self.h5filename))
        ormdata = ap.OrmData(ap.conf.filename(self.h5filename))
        nrow, ncol = len(ormdata.bpm), len(ormdata.trim)

        # prepare for subset
        for itrial1 in range(10):
            idx = []
            bpms, trims = set([]), set([])
            planes = [set([]), set([])]
            for itrial2 in range(nrow*ncol//4):
                k = random.randint(0, nrow*ncol-1)
                i,j = divmod(k, ncol)
                idx.append([i, j])
                bpms.add(ormdata.bpm[i][0])
                planes[0].add(ormdata.bpm[i][1])
                trims.add(ormdata.trim[j][0])
                planes[1].add(ormdata.trim[j][1])

            m = ormdata.getSubMatrix(bpm, trim, planes, full=False)

            for i,j in idx:
                self.assertEqual(ormdata_dst.m[i0,j0], 0.0)



class TestRmCol(unittest.TestCase):
    def setUp(self):
        pass

    def test_measure_orm_sub1_l2(self):
        #trim = ap.getElements('ch1g6c15b')[0]
        trim = ap.getElements('cl2g6c30b')[0]
        bpmlst = [e.name for e in ap.getElements('BPM')]
        trim.put('x', 0.0, unitsys = None)

        fname = time.strftime("orm_sub1_%Y%m%d_%H%M.hdf5")
        ormline = ap.orm.RmCol(bpmlst, trim)
        ormline.measure('x', 'x', verbose = 2)

        # plotting
        if PLOTTING:
            npts, nbpmrow = np.shape(ormline.rawresp)
            plt.figure()
            for j in range(nbpmrow):
                plt.plot(ormline.rawkick[:], ormline.rawresp[:,j], '-o')
            plt.savefig(figname("rm_orm_sub1_%s.png" % trim.name))

    def test_measure_orm_sub2_l2(self):
        #trim = ap.getElements('ch1g6c15b')[0]
        trim = ap.getElements('cl2g6c30b')[0]
        bpmlst = [e.name for e in ap.getElements('BPM')]
        trim.put('x', 0.0, unitsys=None)

        fname = time.strftime("orm_sub1_%Y%m%d_%H%M.hdf5")
        ormline = ap.orm.RmCol(bpmlst, trim)
        ormline.measure(['x', 'y'], 'x', verbose = 2)

        # plotting
        if PLOTTING:
            npts, nbpmrow = np.shape(ormline.rawresp)
            plt.figure()
            for j in range(nbpmrow):
                plt.plot(ormline.rawkick[:], ormline.rawresp[:,j], '-o')
            plt.savefig(figname("rm_orm_sub1_%s.png" % trim.name))



if __name__ == "__main__":
    logging.info("Main")
    unittest.main()
    pass


