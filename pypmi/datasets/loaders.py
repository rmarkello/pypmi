# -*- coding: utf-8 -*-
"""
Functions for loading data downloaded from the PPMI database
"""

from functools import reduce
import itertools
import os.path as op
import re
from typing import List

import numpy as np
import pandas as pd

from ._info import BEHAVIORAL_INFO, DEMOGRAPHIC_INFO, VISITS
from .utils import _get_data_dir


def load_biospecimen(path: str = None,
                     measures: List[str] = None) -> pd.DataFrame:
    """
    Loads biospecimen data into tidy dataframe

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None
    measures : list, optional
        Which measures to keep in the final dataframe. There are a number of
        biospecimen measures that are missing for large numbers of subjects, so
        if not specified only those that are present in at least 80% of entries
        are kept. Specifying `measures='all'` will retain everything, but this
        will significantly increase load time. It is highly recommended to
        specify which measures to keep; available biospecimen measures can be
        viewed with :py:func:`pypmi.datasets.available_biospecimen()`. Default:
        None

    Returns
    -------
    data : :obj:`pandas.DataFrame`
        Biospecimen data

    See Also
    --------
    pypmi.datasets.available_biospecimen
    """

    rename_cols = dict(
        PATNO='participant',
        CLINICAL_EVENT='visit',
        TESTNAME='test',
        TESTVALUE='score'
    )
    dtype = dict(
        PATNO=str,
        CLINICAL_EVENT=VISITS,
        TESTNAME=str,
        TESTVALUE=str
    )

    # check for file and get data directory path
    fname = 'Current_Biospecimen_Analysis_Results.csv'
    path = op.join(_get_data_dir(path=path, fnames=[fname]), fname)

    # make scores numeric and clean up test names (no spaces!)
    data = pd.read_csv(path, dtype=dtype).rename(columns=rename_cols)
    data['score'] = pd.to_numeric(data['score'], errors='coerce')
    data['test'] = data['test'].apply(lambda x: x.replace(' ', '_').lower())

    # keep only desired measures
    if measures is None:
        measures = ['abeta_1-42', 'csf_alpha-synuclein', 'ptau', 'ttau']
    elif measures == 'all':
        measures = data['test'].unique()
    data = data.query(f'test in {measures}')

    # convert to tidy dataframe (if lots of measures this takes a while...)
    tidy = pd.pivot_table(data, index=['participant', 'visit'],
                          columns='test', values='score').reset_index()
    tidy = tidy.rename_axis(None, axis=1)

    return tidy.sort_values(['participant', 'visit']).reset_index(drop=True)


def available_biospecimen(path: str = None) -> List[str]:
    """
    Lists measures available in :py:func:`~.datasets.load_biospecimen()`

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None

    Returns
    -------
    measures : list
        Available biospecimen measures (i.e., "tests")

    See Also
    --------
    pypmi.datasets.load_biospecimen
    """

    # check for file and get data directory path
    fname = 'Current_Biospecimen_Analysis_Results.csv'
    path = op.join(_get_data_dir(path=path, fnames=[fname]), fname)

    data = pd.read_csv(path, usecols=['TESTNAME'])

    return [f.replace(' ', '_').lower() for f in data.TESTNAME.unique()]


def load_datscan(path: str = None,
                 measures: List[str] = None) -> pd.DataFrame:
    """
    Loads DaT scan data into tidy dataframe

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None
    measures : list, optional
        Which measures to keep in the final dataframe. If not specified all
        measures are retained; available DaT scan measures can be viewed with
        :py:func:`pypmi.datasets.available_datscan()`. Default: None

    Returns
    -------
    data : :obj:`pandas.DataFrame`
        DaTScan data

    See Also
    --------
    pypmi.datasets.available_datscan
    """

    rename_cols = dict(
        PATNO='participant',
        EVENT_ID='visit'
    )
    dtype = dict(
        PATNO=str,
        EVENT_ID=VISITS
    )

    # check for file and get data directory path
    fname = 'DATScan_Analysis.csv'
    path = op.join(_get_data_dir(path=path, fnames=[fname]), fname)

    # load data and coerce into standard format
    tidy = pd.read_csv(path, dtype=dtype).rename(columns=rename_cols)
    tidy.columns = [f.lower() for f in tidy.columns]

    # keep only desired measures
    if measures is not None:
        if not isinstance(measures, list):
            measures = list(measures)
        for m in measures:
            if m not in tidy.columns:
                raise ValueError('Specified measure {} is not valid. Please '
                                 'see available datscan measures with `pypmi.'
                                 'datasets.available_datscan()`.'.format(m))
        tidy = tidy[['participant', 'visit'] + measures]

    return tidy.sort_values(['participant', 'visit']).reset_index(drop=True)


def available_datscan(path: str = None) -> List[str]:
    """
    Lists measures available in :py:func:`~.datasets.load_datscan()`

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None

    Returns
    -------
    measures : list
        Available DaT scan measures

    See Also
    --------
    pypmi.datasets.load_datscan
    """

    # check for file and get data directory path
    fname = 'DATScan_Analysis.csv'
    path = op.join(_get_data_dir(path=path, fnames=[fname]), fname)

    # only need first line!
    with open(path, 'r') as src:
        return src.readline().strip().replace('"', '').split(',')[2:]


def load_behavior(path: str = None,
                  measures: List[str] = None) -> pd.DataFrame:
    """
    Loads clinical-behavioral data into tidy dataframe

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None
    measures : list, optional
        Which measures to keep in the final dataframe. If not specified all
        measures are retained; available behavioral measures can be viewed with
        :py:func:`pypmi.datasets.available_behavior()`. Default: None

    Returns
    -------
    df : :obj:`pandas.DataFrame`
        Tidy DataFrame with all clinical-behavioral assessments

    See Also
    --------
    pypmi.datasets.available_behavior
    """

    rename_cols = dict(
        PATNO='participant',
        EVENT_ID='visit'
    )

    # determine measures
    if measures is not None:
        beh_info = {d: v for d, v in BEHAVIORAL_INFO.items() if d in measures}
        if 'moca' not in beh_info.keys() and 'education' in beh_info.keys():
            del beh_info['education']
    else:
        beh_info = BEHAVIORAL_INFO

    # check for files and get data directory path
    fnames = []
    for info in beh_info.values():
        fnames.extend(list(info.get('files', {}).keys()))
    path = _get_data_dir(path=path, fnames=set(fnames))

    df = pd.DataFrame()
    # iterate through all keys in dictionary
    for key, info in beh_info.items():
        cextra = info.get('extra', ['PATNO', 'EVENT_ID', 'PAG_NAME'])
        capply = info.get('applymap', itertools.repeat(lambda x: x))
        copera = info.get('operation', itertools.repeat(np.sum))

        temp_scores = []
        # go through relevant files and items for current key and grab scores
        for fname, items in info['files'].items():
            # read in file
            data = pd.read_csv(op.join(path, fname))
            # iterate through items to be retrieved and apply operations
            for n, (it, ap, ope) in enumerate(zip(items, capply, copera)):
                score = ope(data[it].applymap(ap), axis=1)
                temp_scores.append(data[cextra].join(pd.Series(score, name=n)))

        # merge temp score DataFrames
        curr_df = reduce(lambda df1, df2: pd.merge(df1, df2, on=cextra),
                         temp_scores)
        # combine individual scores for key with joinfunc and add to extra info
        joinfunc = info.get('joinfunc', np.sum)
        score = pd.Series(joinfunc(curr_df.drop(cextra, axis=1), axis=1)
                          .astype('float'), name='score')
        curr_df = curr_df[cextra].astype('str').join(score).assign(test=key)
        # append resultant DataFrame to df
        df = df.append(curr_df, ignore_index=True, sort=True)

    # rename post-treatment UDPRS III scores so there's no collision
    # pivot_table would, by default, take the mean. we don't want that!
    df.loc[df['PAG_NAME'] == "NUPDRS3A", 'test'] = 'updrs_iii_a'

    # clean up column names and convert to tidy dataframe
    df = df.rename(columns=rename_cols)
    tidy = pd.pivot_table(df, index=['participant', 'visit'],
                          columns='test', values='score').reset_index()
    tidy = tidy.rename_axis(None, axis=1)

    # get adjusted MOCA scores (add 'education' variable)
    if 'moca' in tidy.columns:
        adjust = tidy['moca'] < 30
        tidy.loc[adjust, 'moca'] += tidy.loc[adjust, 'education'].fillna(0)
        tidy = tidy.drop(['education'], axis=1)

    tidy['participant'] = tidy['participant'].astype(int)
    tidy['visit'] = tidy['visit'].astype(VISITS)

    return tidy.sort_values(['participant', 'visit']).reset_index(drop=True)


def available_behavior(path: str = None) -> List[str]:
    """
    Lists measures available in :py:func:`~.datasets.load_behavior()`

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None

    Returns
    -------
    measures : list
        Available behavioral measures

    See Also
    --------
    pypmi.datasets.load_behavior
    """

    measures = list(BEHAVIORAL_INFO.keys())
    measures.remove('education')

    return measures


def load_demographics(path: str = None,
                      measures: List[str] = None) -> pd.DataFrame:
    """
    Loads demographic data into tidy dataframe

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None

    Returns
    -------
    demographics : :obj:`pandas.DataFrame`
        Tidy data frame containing demographic information for PPMI subjects

    See Also
    --------
    pypmi.datasets.available_demographics
    """

    rename_cols = dict(
        PATNO='participant',
        EVENT_ID='visit'
    )

    # determine measures
    if measures is not None:
        dem_info = {d: v for d, v in DEMOGRAPHIC_INFO.items() if d in measures}
    else:
        dem_info = DEMOGRAPHIC_INFO

    # check for files and get data directory path
    fnames = []
    for info in dem_info.values():
        fnames.extend(list(info.get('files', {}).keys()))
    path = _get_data_dir(path=path, fnames=set(fnames))

    # empty data frame to hold information
    tidy = pd.DataFrame([], columns=['PATNO'])
    # iterate through demographic info to get
    for key, curr_key in dem_info.items():
        for n, (fname, items) in enumerate(curr_key['files'].items()):
            data = pd.read_csv(op.join(path, fname), dtype=dict(PATNO=int))
            curr_score = data[items]
            for attr in [f for f in curr_key.keys() if f not in ['files']]:
                if hasattr(curr_score, attr):
                    fnc = getattr(curr_score, attr)
                    curr_score = fnc(curr_key[attr].get('input', None),
                                     **curr_key[attr].get('kwargs', {}))
            curr_score = pd.Series(curr_score, name=key)
            temp_scores = data[['PATNO']].join(curr_score)
        tidy = pd.merge(tidy, temp_scores, on='PATNO', how='outer')

    # rename columns and remove duplicates (how are there duplicates???)
    tidy = (tidy.rename(columns=rename_cols)
                .drop_duplicates(subset=['participant']))

    return tidy.sort_values('participant').reset_index(drop=True)


def available_demographics(path: str = None) -> List[str]:
    """
    Lists measures available in :py:func:`~.datasets.load_demographics()`

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None

    Returns
    -------
    measures : list
        Available demographic measures

    See Also
    --------
    pypmi.datasets.load_demographics
    """

    return list(DEMOGRAPHIC_INFO.keys())


def load_dates(path: str = None) -> pd.DataFrame:
    """
    Loads visit date information into tidy dataframe

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None

    Returns
    -------
    dates : :obj:`pandas.DataFrame`
        Tidy data frame with columns ['participant', 'visit', 'date'] for
        linking each visit (valued as e.g., "V01", "V02") with a specific
        YYYY-MM-DD date
    """

    rename_cols = dict(
        PATNO='participant',
        EVENT_ID='visit',
        INFODT='date'
    )

    # check for file and get data directory path
    # vital signs are hypothetically supposed to be checked at every visit for
    # all study participants, so this is the best that we can do!
    fname = 'Vital_Signs.csv'
    path = op.join(_get_data_dir(path=path, fnames=[fname]), fname)

    # load data and coerce into standard format
    tidy = pd.read_csv(path, dtype=dict(PATNO=int, EVENT_ID=VISITS),
                       parse_dates=['INFODT'], infer_datetime_format=True)
    tidy = tidy.rename(columns=rename_cols)[rename_cols.values()]

    return tidy.sort_values(['participant', 'visit']).reset_index(drop=True)


def load_genetics(fname: str,
                  gene_list: str = None) -> (pd.DataFrame, pd.DataFrame):
    """
    Loads PPMI genotyping data stored at `fname`

    Parameters
    ----------
    fname : str
        Filepath to genotyping PLINK files
    gene_list : str, optional
        Path to pandas-compatible csv with at least 'snp', 'target', and
        'odds_ratio' columns denoting rs#, target (effect) allele, and odds
        ratio of target allele in population.

    Returns
    -------
    data : (N, G) :obj:`pandas.DataFrame`
        Wide-format genetics data where `N` is participants and `G` is SNPs
    info : (G, 5) :obj:`pandas.DataFrame`
        Information on SNPs in `data`, including 'odds_ratio' for genetic
        risk score calculation
    """

    try:
        from pandas_plink import read_plink
    except ImportError:
        raise ImportError('Loading genotyping data requires installing the '
                          '`pandas_plink` module. Please install that and try '
                          'again.')

    # make helper function for extracting SNP rs# from PLINK files
    def extract(x):
        try:
            return re.findall('[-_]*(rs[0-9]+)[-_]*', x)[0]
        except IndexError:
            return None

    # load PLINK data
    bim, fam, gen = read_plink(fname, verbose=False)
    participant_id = pd.Series(fam.fid.get_values(), name='participant')
    cols = ['snp', 'a0', 'a1']

    if gene_list is not None:
        # load gene list
        gene_info = pd.read_csv(gene_list).drop_duplicates(subset=['snp'])

        # check where SNPs match desired gene list & subset data
        inds = bim.snp.apply(extract).isin(gene_info.snp.dropna()).get_values()
        bim, gen = bim[inds], gen[inds]

        # clean up ugly bim.snp names with just rs# of SNPs
        bim.loc[:, 'snp'] = bim.snp.map({f: extract(f) for f in bim.snp})

        # get allele info for making sense of the data
        cols += ['target', 'odds_ratio', 'study']
        info = pd.merge(bim, gene_info, on='snp')[cols]

        # if a0/a1 alleles don't match target, confusion ensues
        # drop the non-matched ones and then grab SNPs that need to be reversed
        info = info[~((info.a0 != info.target) & (info.a1 != info.target))]
        flip = info[info.a1 != info.target].snp
        info = info[['snp', 'odds_ratio', 'study']]
    else:
        # placeholders so below code doesn't fail
        info = bim[cols]
        flip = pd.Series([], name='snp')

    # make wide-format participant x SNP dataframe
    data = pd.DataFrame(gen.compute().T, index=participant_id, columns=bim.snp)
    # if multiple columns represent same snp, combine them
    # THEY SHOULD ALL BE THE SAME -- if they aren't, that's bad...
    data = (data.dropna(axis=1, how='all')
                .groupby(level=0, axis=1)
                .mean()
                .dropna(axis=0, how='all')
                .sort_index())
    # flip reverse-coded SNPs
    data[flip] = data[flip].applymap(lambda x: {0: 2, 1: 1, 2: 0}.get(x))

    # retain only relevant SNPs in allele
    info = info[info.snp.isin(data.columns)]
    info = info.drop_duplicates(subset=['snp']).reset_index(drop=True)

    # return sorted data and info
    return data[info.snp], info
