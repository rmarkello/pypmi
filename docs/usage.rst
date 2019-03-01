.. _usage:

.. testsetup::

    from pypmi import datasets
    datasets.fetch_studydata('all', verbose=False)

Usage
=====

Getting the data
----------------

First things first: you need to get the data!
Once you have access to the `PPMI database <https://www.ppmi-info.org/access-
data-specimens/download-data/>`_, log in to the database and follow these
instructions:

1. Select ``Download`` from the navigation bar at the top
2. Select ``Study Data`` from the options that appear in the navigation bar
3. Select ``ALL`` at the bottom of the left-hand navigation bar on the new page
4. Click ``Select ALL tabular data (csv) format`` and then press ``Download>>``
   in the top right hand corner of the page
5. Unzip the downloaded directory and save it somewhere on your computer

Alternatively, you can use the :py:mod:`pypmi.datasets` module to download the
data programatically:

.. doctest::

    >>> from pypmi import datasets
    >>> files = datasets.fetch_studydata('all', user='username', password='password')  # doctest: +SKIP
    Fetching authentication key for data download...
    Requesting 113 datasets for download...
    Downloading PPMI data: 17.3MB [00:33, 519kB/s]

By default, the data will be downloaded to your current directory making it
easy to load them in the future, but you can optionally provide a ``path``
argument to :py:func:`.datasets.fetch_studydata` to specify where you would
like the data to go. (Alternatively, you can set an environmental variable
``$PPMI_PATH`` to specify where they should be downloaded to; this takes
precedence over the current directory.)

Loading and working with the data
---------------------------------

Once you have the data downloaded you can use the functions to load various
portions of it into `tidy <https://cran.r-project.org/web/packages/tidyr/
vignettes/tidy-data.html>`_ data frames.

For example, we can generate a number of clinical-behavioral measures:

.. doctest::

    >>> behavior = datasets.load_behavior()
    >>> behavior.columns
    Index(['participant', 'visit', 'benton', 'epworth', 'gds', 'hvlt_recall',
           'hvlt_recognition', 'hvlt_retention', 'lns', 'moca', 'pigd', 'quip',
           'rbd', 'scopa_aut', 'se_adl', 'semantic_fluency', 'stai_state',
           'stai_trait', 'symbol_digit', 'systolic_bp_drop', 'tremor', 'updrs_i',
           'updrs_ii', 'updrs_iii', 'updrs_iii_a', 'updrs_iv', 'upsit'],
          dtype='object')


The call to :py:func:`.datasets.load_behavior` may take a few seconds to
run---there's a lot of data to import and wrangle!

If we want to query the data with regards to, say, subject diagnosis it might
be useful to load in some demographic information:

.. doctest::

    >>> demographics = datasets.load_demographics()
    >>> demographics.columns
    Index(['participant', 'diagnosis', 'date_birth', 'date_diagnosis',
           'date_enroll', 'status', 'family_history', 'age', 'gender', 'race',
           'site', 'handedness', 'education'],
          dtype='object')

Now we can perform some interesting queries!
As an example, let's just ask how many individuals with Parkinson's disease
have a baseline UPDRS III score.
We'll have to use information from both data frames to answer the question:

.. doctest::

    >>> import pandas as pd
    >>> updrs = (behavior.query('visit == "BL" & ~updrs_iii.isna()')
    ...                  .get(['participant', 'updrs_iii']))
    >>> parkinsons = demographics.query('diagnosis == "pd"').get('participant')
    >>> len(pd.merge(parkinsons, updrs, on='participant'))
    423

And the same for healthy individuals:

.. doctest::

    >>> healthy = demographics.query('diagnosis == "hc"').get('participant')
    >>> len(pd.merge(healthy, updrs))
    195

There's a lot of power gained in leveraging the pandas DataFrame objects, so
take a look at the `pandas documentation <https://pandas.pydata.org/>`_ to see
what more you can do!
