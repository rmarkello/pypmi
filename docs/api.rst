.. _ref_api:

Reference API
=============

This is the primary reference of ``pypmi``. Please refer to the :ref:`user
guide <usage>` for more information on how to best implement these functions in
your own workflows.

.. _ref_datasets:

:mod:`pypmi` - Dataset fetchers and loaders
------------------------------------------------------

.. automodule:: pypmi
   :no-members:
   :no-inherited-members:

.. currentmodule:: pypmi

Functions for listing and downloading datasets from the PPMI database:

.. autosummary::
   :template: function.rst
   :toctree:  generated/

    fetchable_studydata
    fetchable_genetics
    fetch_studydata
    fetch_genetics

Functions for loading data from PPMI database into tidy dataframes:

.. autosummary::
   :template: function.rst
   :toctree:  generated/

    load_behavior
    load_biospecimen
    load_datscan
    load_demographics

Functions for listing measures available from relevant ``pypmi.load_X()``
commands:

.. autosummary::
   :template: function.rst
   :toctree:  generated/

    available_behavior
    available_biospecimen
    available_datscan
    available_demographics
