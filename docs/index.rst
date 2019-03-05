=======================================================================
pypmi: An API for the Parkinson's Progression Markers Initiative (PPMI)
=======================================================================

.. image:: https://travis-ci.org/rmarkello/pypmi.svg?branch=master
    :target: https://travis-ci.org/rmarkello/pypmi

.. image:: https://codecov.io/gh/rmarkello/pypmi/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/rmarkello/pypmi

.. image:: https://readthedocs.org/projects/pypmi/badge/?version=latest
    :target: http://pypmi.readthedocs.io/en/latest

.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
   :target: https://opensource.org/licenses/BSD-3-Clause

The PPMI is an ongoing longitudinal study that begin in early 2010 with the
primary goal of identifying biomarkers of Parkinson's disease (PD) progression.
To date, the PPMI has collected data from over 400 individuals with de novo PD
and nearly 200 age-matched healthy participants, in addition to large cohorts
of individuals genetically at-risk for PD.
Data, made available on the `PPMI website <https://www.ppmi-info.org/data>`_,
include comphrensive clinical-behavioral assessments, biological assays,
single-photon emission computed tomography (SPECT) images, and magnetic
resonance imaging (MRI) scans.

While accessing this data is straightforward (researchers must simply sign a
data usage agreement and provide information on the purpose of their research),
the sheer amount of data made available can be quite overwhelming to work with.
Thus, the primary goal of this package is to provide a Python interface to
making working with the data provided by the PPMI easier.

While this project is still very much under development it is neverthless
functional.
However, **please note that this project's functionality is liable to change
quite dramatically until an initial release is made**---so be careful!
Check out our :ref:`reference API <api>` for some of the current capabilities
of ``pypmi`` while our :ref:`user guide <usage>` is under construction.

.. toctree::
   :maxdepth: 1
   :caption: Table of Contents

   usage
   api
