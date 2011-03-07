#!/usr/bin/env python

"""
This module mimics Channel Finder service, and makes developing HLA earlier.

It also manages configuration data of HLA.
"""

import cadict
import re, shelve, sys, os
from fnmatch import fnmatch
from time import gmtime, strftime

import lattwiss

# are we using virtual ac
virtac = True

class ChannelFinderAgent:
    """
    Channel Finder Agent

    This module builds a local cache of channel finder service.
    """
    def __init__(self):
        self.__d = {}
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.__elempv = {}
        self.__elemidx = {}
        self.__elemname = []
        self.__elemtype = []
        self.__elemlen = []
        self.__elemloc = []

    def importXml(self, fname):

        raise NotImplementedError()

        #OBSOLETE - the main.xml file does not have latest pv list
        #"""
        ca = cadict.CADict(fname)
        for elem in ca.elements:
            #print elem
            self.__elempv[elem.name] = []
            if len(elem.ca) == 0: continue
            for i, pv in enumerate(elem.ca):
                # for each pv and handle
                #print "'%s'" % pv, 
                if len(pv.strip()) == 0: continue
                self.addChannel(pv, {'handle':elem.handle[i], 
                                     'elementname':elem.name,
                                     'elementtype':elem.type,
                                     'cell': elem.cell,
                                     'girder': elem.girder,
                                     'symmetry': elem.symmetry}, None)
                self.__elempv[elem.name].append(pv)

            #print elem.sequence
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

    def __parseElementName(self, name):
        # for NSLS-2 convention of element name
        a = re.match(r'.+(G\d{1,2})(C\d{1,2})(.)', name)
        if a:
            girder   = a.groups()[0]
            cell     = a.groups()[1]
            symmetry = a.groups()[2]
        elif name == "CAVITY":
            # fix a broken name
            girder   = "CAVITY"
            cell     = "CAVITY"
            symmetry = "CAVITY"
        else:
            girder   = 'G0'
            cell     = 'C00'
            symmetry = '0'
        return cell, girder, symmetry

    def importLatticeTable(self, lattable):
        """
        call signature::
        
          importLatticeTable(self, lattable)

        Import the table used for Tracy-VirtualIOC. The table has columns
        in the following order:

        =======   =============================================
        Index     Description
        =======   =============================================
        1         element index in the whole beam line
        2         channel for read back
        3         channel for set point
        4         element phys name (unique)
        5         element length (effective)
        6         s location of its exit
        7         magnet family(type)
        =======   =============================================

        Data are deliminated by spaces.
        """

        print "Importing file:", lattable

        cnt = {'BPM':0, 'TRIMD':0, 'TRIMX':0, 'TRIMY':0, 'SEXT':0, 'QUAD':0}

        f = open(lattable, 'r').readlines()
        for s in f[1:]:
            t = s.split()
            idx  = int(t[0])     # index
            rb   = t[1].strip()  # PV readback
            sp   = t[2].strip()  # PV setpoint
            phy  = t[3].strip()  # name
            L    = float(t[4])   # length
            s2   = float(t[5])   # s_end location
            grp  = t[6].strip()  # group

            self.__elemname.append(phy)
            self.__elemtype.append(grp)
            self.__elemlen.append(L)
            self.__elemloc.append(s2)

            if not self.__elempv.has_key(phy):
                self.__elempv[phy] = []
            if rb != 'NULL': self.__elempv[phy].append(rb)
            if sp != 'NULL': self.__elempv[phy].append(sp)

            # parse cell/girder/symmetry from name
            cell, girder, symmetry = self.__parseElementName(phy)

            # count element numbers in each type
            if cnt.has_key(grp): cnt[grp] += 1

            # add the readback pv
            if rb != 'NULL':
                self.addChannel(rb,
                                {'handle': 'get', 'elementname': phy,
                                 'elementtype': grp, 'cell': cell, 
                                 'girder': girder, 'symmetry': symmetry,
                                 'elemindex': idx, 's_end': s2}, None)
            if sp != 'NULL':
                self.addChannel(sp,
                                {'handle': 'get', 'elementname': phy,
                                 'elementtype': grp, 'cell': cell,
                                 'girder': girder, 'symmetry': symmetry,
                                 'elemindex': idx, 's_end': s2}, None)
            self.__elemidx[phy] = idx
        print "Summary:"
        for k,v in cnt.items():
            print " %8s %5d" % (k, v)
        print "--"
        print " %8s %5d" % ("Elements", len(self.__elemidx.keys()))
        print " %8s %5d" % ("PVs",len(self.__d.keys()))
        #return d

    def save(self, fname, dbmode = 'c'):
        """
        call signature::
        
          save(self, fname, dbmode = 'c')

        save the configuration into binary data

        *dbmode* has same meaning as in *shelve*/*pickle*/*anydbm* module

        ======   ==========================================
        DBMode   Meaning
        ======   ==========================================
        'r'      Open existing database for reading only(default)
        'w'      Open existing database for reading and writing
        'c'      Open database for reading and writing, creating one if it doesn't exist.
        'n'      Always create a new, empty database, open for reading and writing
        ======   ==========================================
        """
        f = shelve.open(fname, dbmode)
        f['cfa.d']       = self.__d
        f['cfa.cdate']   = self.__cdate
        f['cfa.elempv']  = self.__elempv
        f['cfa.elemidx'] = self.__elemidx
        f['cfa.elemname'] = self.__elemname
        f['cfa.elemtype'] = self.__elemtype
        f['cfa.elemlen']  = self.__elemlen
        f['cfa.elemloc']  = self.__elemloc
        f.close()

    def load(self, fname):
        f = shelve.open(fname, 'r')
        self.__d       = f['cfa.d']
        self.__cdate   = f['cfa.cdate']
        self.__elempv  = f['cfa.elempv']
        self.__elemidx = f['cfa.elemidx']
        self.__elemname = f['cfa.elemname']
        self.__elemtype = f['cfa.elemtype']
        self.__elemlen  = f['cfa.elemlen']
        self.__elemloc  = f['cfa.elemloc']
        f.close()

    def __matchProperties(self, pv, prop = {}):
        if not prop: return True
        for  k, v in prop.keys():
            if not self.__d[pv].has_key(k) or \
                    self.__d[pv][k] != v:
                return False

        return True

    def __matchTags(self, pv, tags = []):
        if not tags: return True
        for tag in tags:
            if not tag in self.__d[pv]['~tags']: return False
        return True
            
    def addChannel(self, pv, props, tags):
        if not self.__d.has_key(pv):
            self.__d[pv] = {'~tags':[]}
        #
        if props:
            for prop, val in props.items(): self.__d[pv][prop] = val

        if tags:
            for tag in tags: 
                if tag in self.__d[pv]['~tags']: continue
                self.__d[pv]['~tags'].append(tag)

    def __repr__(self):
        s = ""
        for k,v in self.__d.items():
            s = s + "%s\n" % k
            for prop in v.keys():
                if prop == '~tags': continue
                s = s + " %s: %s\n" % (prop, v[prop])
            s = s + " "
            s = s + ', '.join(v['~tags'])
            s = s + '\n'
        return s

    def getElementChannel(self, element, prop = {}, tags = []):
        if not self.__elempv.has_key(element):
            return None
        if len(self.__elempv[element]) == 0: return None
        # check against properties
        ret = []
        msg = ''
        for pv in self.__elempv[element]:
            agreed = True
            for k,v in prop.items():
                if not self.__d[pv].has_key(k):
                    agreed = False
                    msg = '%s has no property "%s"' % (pv, k)
                    break
                elif self.__d[pv][k] != v:
                    agreed = False
                    msg = '%s: %s != %s' % (pv, self.__d[pv][k], v)
                    break
            for tag in tags:
                if not tag in self.__d[pv]['~tags']:
                    agreed = False
                    msg = '%s is not in tags' % tag
                    break
            if agreed: ret.append(pv)
        #if len(ret) == 0: print msg
        return ret
    
    def getChannels(self, prop = {}, tags = []):
        ret = []
        for elem in self.__elempv.keys():
            #print elem,
            pvs = self.getElementChannel(elem, prop, tags)
            if pvs: ret.extend(pvs)
        return ret

    def __getElementChannels(self, elem, prop = {}, tags = []):
        """*elem* is the exact name of an element.

        Returns a list of matched PVs."""
        if not self.__elempv._has_key(elem): return []
        ret = []
        for pv in self.__elempv[elem]:
            if self.__matchProperties(pv, prop) and \
                    self.__matchTags(pv, tags):
                ret.append(pv)
        return ret

    def getElements(self, group, cell = [], girder = [],
                    sequence = []):
        """
        call signature::
        
          getElements(self, group, cell=[], girder=[], sequence=[])c

        Get a list of elements
        """
        elem = []
        for pv in self.__d.keys():
            elemname = self.__d[pv]['elementname']
            elemtype = self.__d[pv]['elementtype']
            if group and not fnmatch(elemname, group) \
                    and not fnmatch(elemtype, group):
                continue
            if cell and not self.__d[pv]['cell'] in cell: continue
            if girder and not self.__d[pv]['girder'] in girder: continue
            elem.append(elemname)

        # may have duplicate element
        return [v for v in set(elem)]

    
    def checkMissingChannels(self, pvlist):
        for i, line in enumerate(open(pvlist, 'r').readlines()):
            if self.__d.has_key(line.strip() ): continue
            print "Line: %d %s" % (i, line.strip())
        print "-- DONE --"

    def __cmp_elem_loc(self, a, b):
        return self.__elemname.index(a) - self.__elemname.index(b)

    def sortElements(self, elemlst):
        ret = sorted(elemlst, self.__cmp_elem_loc )
        for elem in ret:
            print elem, self.__elemloc[self.__elemname.index(elem)]


class Element:
    def __init__(self):
        self.name = ''
        self.type = ''
        self.s_beg = 0.0
        self.s_end = 0.0
        self.len = 0.0
        self.cell = 0
        self.girder = 0
        self.sequence = [0, 0]

        
class Lattice:
    def __init__(self):
        self.__group = {}
        self.element = []
        self.twiss = []
        self.mode = ''

    def save(self, fname, dbmode = 'c'):
        pass

    def load(self, fname, mode = 'default'):
        pass


#
# root of stored data
root={
    "nsls2" : "machine/nsls2"
}

ca = ChannelFinderAgent()
__lat = Lattice()
    
# get the HLA root directory
pt = os.path.dirname(os.path.abspath(__file__))

def init(lat):
    """Initialize HLA"""
    ca.load("%s/../../%s/hla.pkl" % (pt, root[lat]))
    __lat.load("%s/../../%s/hla.pkl" % (pt, root[lat]))

#
# initialize the configuration 
init("nsls2")

if __name__ == "__main__":
    import os, sys
    d = ChannelFinderAgent()

    #d.importXml('/home/lyyang/devel/nsls2-hla/machine/nsls2/main.xml')
    hlaroot = '/home/lyyang/devel/nsls2-hla/'
    d.importLatticeTable(hlaroot + 'machine/nsls2/lat_conf_table.txt')

    # example
    print d.getElements('P*G2C2*', cell=['C21'])
    elem = d.getElements('P*')
    print elem[1:3]
    r = d.sortElements(elem)

    d.checkMissingChannels(hlaroot + 'machine/nsls2/pvlist_2011_03_03.txt')
    d.save(hlaroot + 'machine/nsls2/hla.pkl')
    
    
