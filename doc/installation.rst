:orphan:

Installation
--------------

.. warning::

   For BNL/NSLS2 users, the most easy way is sending ITD an email requesting
   an account on **lsasd2.ls.bnl.gov** (please CC to Lingyun Yang who is the
   registered owner). It is a Linux server with all HLA software installed.


Depending Packages
~~~~~~~~~~~~~~~~~~

There are some packages required before using HLA. In the following, we will
take Debian/Ubuntu Linux as an example to show how to install them.

::

  $ sudo apt-get install mercurial pyqt4-dev-tools
  $ sudo apt-get install python-qt4 python-qt4-dev
  $ sudo apt-get install python-docutils python-numpy python-scipy


By using BNL Debian/Ubuntu repository from Controls group, we can install some
EPICS tools easily:

::

  deb http://epics.nsls2.bnl.gov/debian/ squeeze main contrib
  deb-src http://epics.nsls2.bnl.gov/debian/ squeeze main contrib

.. code-block:: bash

  $ sudo apt-get install python-cothread epics-catools

Set environment for channel access and HLA. Append the following to
~/.bashrc::

  export EPICS_CA_MAX_ARRAY_BYTES=5000000
  export EPICS_CA_ADDR_LIST="virtac.nsls2.bnl.gov vioc01.nsls2.bnl.gov"

Try to see if virtual accelerator is accessible

.. code-block:: bash

  $ caget 'SR:C00-BI:G00{DCCT:00}CUR-RB'

You should see the beam current of virtual accelerator. Then see if it changes

.. code-block:: bash

  $ camonitor 'SR:C00-BI:G00{DCCT:00}CUR-RB'

Download the *hla-v0.2.0.egg* file or newer version, then install

.. code-block:: bash

  $ sudo easy_install hla-v0.2.0.egg

Before using HLA, we need some environment variables, like EPICS, put the
following in to ~/.bashrc::

  export HLA_DATA_DIRS=/home/lyyang/devel/nsls2-hla
  export HLA_MACHINE=nsls2
  export HLA_CFS_URL=http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder

I am using **HLA_DATA_DIRS** as place to store data, the machine name
working on is *nsls2* and the channel finder service URL is at
**HLA_CFS_URL**. 


Code Repository for HLA Developers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**SKIP THIS PART IF YOU DO NOT NEED TO DEVELOP HLA APPLICATIONS**

Our code is in a Mercurial repository, which keeps every version anyone
checked in. Version controlled repository not only keeps track of the
change of the code, but also support branch and merges of each revision.

I will skip the introduction of the version control tools and only talk
about what/how you should do to work with the HLA code in repository.

A typical work flow is the following. (All under linux)

The very first time, please take a look at ~/.hgrc:

::

  [ui]
  username = Lingyun Yang <lyyang@bnl.gov>

This marks who you are.

.. code-block:: bash

  $ hg clone http://code.nsls2.bnl.gov/hg/ap/hla
  $ cd hla
  $ (working .....)
  $ hg add newfile.py (if you have created a new file)
  $ hg status  ( list the status of current working directory)
  $ hg commit -m "I have improved the code" (check in the code with a message)
  $ hg push (push you change to the server)

If it has been a long time after you checkout the code from the server, you can 

.. code-block:: bash

  $ hg pull (update the local files with server's)

Configuration
----------------

.. code-block:: bash

  $ h5copy -p -i v2sr_twiss.hdf5 -s Twiss -o nsls2v2.hdf5 -d /V2SR/Twiss



``aphla`` can keep several initialized lattices, depending how many
*aphla.sys.* tags in the configuration. Currently we have *aphla.sys.SR*,
*aphla.sys.LTD1*, *aphla.sys.LTD2*, *aphla.sys.LTB* for the real *nsls2*
machine. The `V1` prefix before `SR`, `LTD1` means it is the `virtual
accelerator #1` counter part. :func:`~aphla.machines.lattices` lists the
initialized lattices and :func:`~aphla.machines.use` will switch to the named
lattice as the current lattice. This current lattice is the domain for
functions like :func:`~aphla.hlalib.getElements`.

