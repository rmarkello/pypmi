# PyPMI

This package provides a Python interface for working with data from the [Parkinson's Progression Markers Initiative](http://www.ppmi-info.org/) (PPMI).

## Installation and setup

This package requires Python >= 3.5.
If you have the correct version of Python installed, you can install this package by opening a terminal and running the following:

```bash
git clone https://github.com/rmarkello/pypmi.git
cd pypmi
python setup.py install
```

Some of the functionality of this package&mdash;primarily, the functions to work with neuroimaging data&mdash;also requires the use of [Docker](https://www.docker.com/).

## Overview

The PPMI is an ongoing longitudinal study that begin in early 2010 with the primary goal of identifying biomarkers of Parkinson's disease (PD) progression.
To date, the PPMI has collected data from over 400 individuals with de novo PD and nearly 200 age-matched healthy participants, in addition to large cohorts of individuals genetically at-risk for PD.
Data, made available on the [PPMI website](http://www.ppmi-info.org/data), include comphrensive clinical-behavioral assessments, biological assays, single-photon emission computed tomography (SPECT) images, and magnetic resonance imaging (MRI) scans.

While accessing this data is straightforward (researchers must simply sign a data usage agreement and provide information on the purpose of their research), the sheer amount of data made available can be quite overwhelming to work with.
Thus, the primary goal of this package is to provide a Python interface to making working with the data provided by the PPMI easier.
While this project is still very much **under development**, it is neverthless functional!
Most useful may be the functions contained in `ppmi.datasets`, which help wrangle the litany of raw CSV files provided by the PPMI, and in `ppmi.bids`, which helps convert raw neuroimaging data from the PPMI into [BIDS format](bids.neuroimaging.io).

I hope to continue adding useful features to this package as I keep working with the data, but take a look below at [development and getting involved](#development-and-getting-involved) if you're interested in contributing, yourself!

## Usage

Once you have access to the [PPMI database](https://www.ppmi-info.org/access-data-specimens/download-data/), log in to the database and follow these instructions:

1. Select "Download" from the navigation bar at the top
2. Select "Study Data" from the options that appear in the navigation bar
3. Select "ALL" at the bottom of the left-hand navigation bar on the new page
4. Click "Select ALL tabular data (csv) format" and then press "Download>>" in the top right hand corner of the page
5. Unzip the downloaded directory and save it somewhere on your computer

Once you've downloaded the files, load up Python and import the data

```python
>>> import ppmi
>>> ppmi_data_path = '/this/is/the/path/to/my/unzipped/data'
>>> data = ppmi.get_all_data(ppmi_data_path)
>>> data.columns
Index(['PARTICIPANT', 'DIAGNOSIS', 'GENDER', 'RACE', 'AGE', 'FAMILY_HISTORY',
       'HANDEDNESS', 'EDUCATION', 'SYMPTOM_DURATION', 'SITE', 'VISIT',
       'VISIT_DATE', 'PAG_NAME', 'TEST', 'SCORE'],
      dtype='object')
```

The call to `ppmi.get_all_data()` may take a few seconds to run&mdash;there's a lot of data to import!
The `data` object returned is a hybrid [wide/narrow](https://en.wikipedia.org/wiki/Wide_and_narrow_data) format [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html), and can be queried in a number of useful ways:

```python
# how many PD participants do we have a MOCA score for at screening?
>>> len(data.query('DIAGNOSIS == "PD" & TEST == "MOCA" & VISIT == "SC"'))
423
# and for control participants?
>>> len(data.query('DIAGNOSIS == "HC" & TEST == "MOCA" & VISIT == "SC"'))
196
```

There's a lot of power gained in leveraging the pandas DataFrame objects, so take a look at the [pandas documentation](https://pandas.pydata.org/) to see what more you can do!

## Development and getting involved

This package has largely been developed in the spare time of a single graduate student ([`@rmarkello`](https://github.com/rmarkello)).
While it would be :sparkles: amazing :sparkles: if anyone else finds it helpful, given the limited time constraints of graduate school, this package is not currently accepting requests for new features.

However, if you're interested in getting involved in the project, we're thrilled to welcome new contributors!
You should start by reading our [contributing guidelines](https://github.com/rmarkello/pyls/blob/master/CONTRIBUTING.md) and [code of conduct](https://github.com/rmarkello/pyls/blob/master/Code_of_Conduct.md).
Once you're done with that, take a look at our [issues](https://github.com/rmarkello/pyls/issues) to see if there's anything you might like to work on.
Alternatively, if you've found a bug, are experience a problem, or have a question, create a new issues with some information about it!

## Acknowledgments

This package relies on data that can be obtained from the Parkinson's Progression Markers Initiative (PPMI) database [http://www.ppmi-info.org/data](http://www.ppmi-info.org/data).
For up-to-date information on the study, visit [http://www.ppmi-info.org/](http://www.ppmi-info.org/)

The PPMI&mdash;a public-private partnership&mdash;is funded by the Michael J. Fox Foundation for Parkinson’s Research and funding partners, including AbbVie, Avid Radiopharmaceuticals, Biogen, BioLegend, Bristol-Myers Squibb, GE Healthcare, Genentech, GlaxoSmithKline (GSK), Eli Lilly and Company, Lundbeck, Merck, Meso Scale Discovery (MSD), Pfizer, Piramal Imaging, Roche, Sanofi Genzyme, Servier, Takeda, Teva, and UCB [www.ppmi-info.org/fundingpartners](www.ppmi-info.org/fundingpartners).

## License information

This codebase is licensed under the 3-clause BSD license. 
The full license can be found in the [LICENSE](https://github.com/rmarkello/abagen/blob/master/LICENSE) file in the `ppmi` distribution.

All trademarks referenced herein are property of their respective holders.
