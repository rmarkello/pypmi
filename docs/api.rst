.. _ref_api:

Reference API
=============

This is the primary reference of ``pypmi``. Please refer to the :ref:`user
guide <usage>` for more information on how to best implement these functions in
your own workflows.

.. contents:: **List of modules**
   :local:

.. _ref_datasets:

:mod:`pypmi.datasets` - Dataset fetchers and loaders
------------------------------------------------------

.. automodule:: pypmi.datasets
   :no-members:
   :no-inherited-members:

.. currentmodule:: pypmi.datasets

Functions for downloading datasets from the PPMI database

.. autosummary::
   :template: function.rst
   :toctree:  generated/

    available_studydata
    fetch_studydata
    available_genetics
    fetch_genetics

Functions for loading datasets into memory

.. autosummary::
   :template: function.rst
   :toctree:  generated/

    load_studydata
    load_behavior
    load_biospecimen
    load_datscan
    load_demographics
    load_genetics
