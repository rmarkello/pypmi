# -*- coding: utf-8 -*-
"""
Functions for loaded data downloaded from the PPMI database
"""

from functools import reduce
import itertools
import os.path as op
import re

import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype as cdtype

from ._info import BEHAVIORAL_INFO, DEMOGRAPHIC_INFO

VISITS = [
    'SC', 'BL', 'V01', 'V02', 'V03', 'V04', 'V05', 'V06', 'V07', 'V08', 'V09',
    'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'PW'
]


def load_biospecimen(fpath):
    """
    Loads biospecimen data for PPMI subjects

    Parameters
    ----------
    fpath : str
        Filepath to directory containing Biospecimen_Analysis_Results.csv file

    Returns
    -------
    data : pd.core.frame.DataFrame
        Biospecimen data
    """

    rename_cols = dict(
        PATNO='PARTICIPANT', CLINICAL_EVENT='VISIT', TESTNAME='TEST',
        TESTVALUE='SCORE'
    )
    retain_cols = [
        'PARTICIPANT', 'PAG_NAME', 'VISIT', 'VISIT_DATE', 'TEST', 'SCORE'
    ]
    dtype = dict(
        PATNO=str, CLINICAL_EVENT=cdtype(VISITS, ordered=True), TESTNAME=str,
        TESTVALUE=str
    )

    fname = op.join(fpath, 'Current_Biospecimen_Analysis_Results.csv')
    data = pd.read_csv(fname, dtype=dtype)

    data['TESTVALUE'] = pd.to_numeric(data['TESTVALUE'], errors='coerce')
    data = (data.rename(columns=rename_cols)
                .assign(PAG_NAME='DATSCAN', VISIT_DATE=np.nan)[retain_cols]
                .dropna(axis=0, subset=['SCORE']))

    return data


def load_datscan(fpath):
    """
    Loads DaTscan data for PPMI subjects

    Parameters
    ----------
    fname : str
        Filepath to directory containing DaTScan_Analysis.csv file

    Returns
    -------
    data : pandas.core.frame.DataFrame
        DaTScan data
    """

    remame_cols = dict(
        PATNO='PARTICIPANT', EVENT_ID='VISIT'
    )
    retain_cols = [
        'PARTICIPANT', 'PAG_NAME', 'VISIT', 'VISIT_DATE', 'TEST', 'SCORE'
    ]
    dtype = dict(
        PATNO=str, EVENT_ID=cdtype(VISITS, ordered=True)
    )

    fname = op.join(fpath, 'DATScan_Analysis.csv')
    data = pd.read_csv(fname, dtype=dtype)

    # melt into tidy DataFrame
    data = pd.melt(data.rename(columns=remame_cols),
                   id_vars=remame_cols.values(),
                   var_name='TEST',
                   value_name='SCORE')
    data = data.dropna(axis=0, subset=['SCORE'])
    data = data.assign(PAG_NAME='DATSCAN', VISIT_DATE=np.nan)[retain_cols]

    return data


def load_genetics(fname, gene_list=None):
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
    data : (N, G) pandas.DataFrame
        Wide-format genetics data where `N` is participants and `G` is SNPs
    info : (G, 5) pandas.DataFrame
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
    participant_id = pd.Series(fam.fid.get_values(), name='PARTICIPANT')
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


def available_behavior():
    """ Lists available clinical-behavioral composite measures """
    # don't return MOCA Unadjusted since we drop it during score calculations
    measures = list(BEHAVIORAL_INFO.keys()) + ['MOCA']
    measures.remove('MOCA Unadjusted')
    return measures


def load_behavior(fpath):
    """
    Loads clinical-behavioral data for PPMI subjects

    Parameters
    ----------
    fpath : str
        Filepath to directory containing all behavioral files

    Returns
    -------
    df : pandas.DataFrame
        Tidy DataFrame with all clinical-behavioral assessments
    """

    rename_cols = dict(
        PATNO='PARTICIPANT', INFODT='VISIT_DATE', EVENT_ID='VISIT'
    )
    retain_cols = [
        'PARTICIPANT', 'PAG_NAME', 'VISIT', 'VISIT_DATE', 'TEST', 'SCORE'
    ]

    df = pd.DataFrame()
    # iterate through all keys in dictionary
    for key, info in BEHAVIORAL_INFO.items():
        cextra = info.get('extra', ['PATNO', 'EVENT_ID', 'PAG_NAME', 'INFODT'])
        capply = info.get('applymap', itertools.repeat(lambda x: x))
        copera = info.get('operation', itertools.repeat(np.sum))

        temp_scores = []
        # go through relevant files and items for current key and grab scores
        for fname, items in info['files'].items():
            # read in file
            data = pd.read_csv(op.join(fpath, fname))
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
                          .astype('float'), name='SCORE')
        curr_df = curr_df[cextra].astype('str').join(score).assign(TEST=key)
        if 'PAG_NAME' not in curr_df.columns:
            curr_df['PAG_NAME'] = 'COMBO'
        # append resultant DataFrame to df
        df = df.append(curr_df, ignore_index=True, sort=True)

    # coerce infodt to datetime format
    df['INFODT'] = pd.to_datetime(df['INFODT'], format='%m/%Y')
    df = _get_adj_moca(df).rename(columns=rename_cols)[retain_cols]

    return df


def _get_adj_moca(df):
    """
    Gets adjusted MOCA score from `df` (i.e., accounts for education)

    Adds 1 to unadjusted MOCA score if years of education is <=12 and
    unadjusted score is <30; otherwise, unadjusted MOCA is carried through.

    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame containing various behavioral metrics

    Returns
    -------
    data : pandas.DataFrame
        DataFrame with adjusted MOCA instead of unadjusted MOCA
    """

    moca = pd.merge(df.query('TEST == "MOCA Unadjusted" & SCORE < 30'),
                    df.query('TEST == "EDUCYRS"')[['PATNO', 'SCORE']],
                    on='PATNO')
    mocaadj = (moca.drop(['SCORE_x', 'SCORE_y'], axis=1)
                   .join(pd.Series(moca[['SCORE_x', 'SCORE_y']]
                                   .sum(axis=1), name='SCORE')))
    mocanoadj = df.query('TEST == "MOCA Unadjusted" & SCORE >= 30')
    mocaadj = mocaadj.append(mocanoadj, sort=True)
    mocaadj.TEST = 'MOCA'

    new_df = df.append(mocaadj, sort=True, ignore_index=True)
    to_drop = new_df.query('TEST == "EDUCYRS" | TEST == "MOCA Unadjusted"')
    data = new_df.drop(to_drop.index, axis=0)

    return data


def load_demographics(fpath):
    """
    Loads demographic data for PPMI subjects

    Parameters
    ----------
    fpath : str
        Filepath to directory containing all demographic files

    Returns
    -------
    df : pandas.core.frame.DataFrame
        Tidy DataFrame with demographic information
    """

    rename_cols = dict(
        PATNO='PARTICIPANT', INFODT='VISIT_DATE', EVENT_ID='VISIT'
    )

    # empty data frame to hold information
    df = pd.DataFrame([], columns=['PATNO'])

    # iterate through demographic info to get
    for key, curr_key in DEMOGRAPHIC_INFO.items():
        for n, (fname, items) in enumerate(curr_key['files'].items()):
            data = pd.read_csv(op.join(fpath, fname))
            curr_score = data[items]
            for attr in [f for f in curr_key.keys() if f not in ['files']]:
                if hasattr(curr_score, attr):
                    fnc = getattr(curr_score, attr)
                    curr_score = fnc(curr_key[attr].get('input', None),
                                     **curr_key[attr].get('kwargs', {}))
            curr_score = pd.Series(curr_score, name=key)
            temp_scores = data[['PATNO']].astype('str').join(curr_score)
        df = pd.merge(df, temp_scores, on='PATNO', how='outer')

    # rename columns
    df = df.rename(columns=rename_cols)

    # for some reason there are duplicate participant entries here????
    return df.drop_duplicates(subset=['PARTICIPANT'])


def load_studydata(fpath):
    """
    Loads raw PPMI study data into analysis-ready dataframe

    Parameters
    ----------
    fpath : str
        Filepath to directory containing all tabular study data downloaded from
        the PPMI database

    Returns
    -------
    data : :obj:`pandas.DataFrame`
        All PPMI data
    """

    column_order = [
        'PARTICIPANT', 'DIAGNOSIS', 'GENDER', 'RACE', 'AGE', 'FAMILY_HISTORY',
        'HANDEDNESS', 'EDUCATION', 'SYMPTOM_DURATION', 'SITE', 'VISIT',
        'VISIT_DATE', 'PAG_NAME', 'TEST', 'SCORE'
    ]
    diagnosis = [
        'PD', 'HC', 'SWEDD', 'PROD', 'GC_PD', 'GC_HC', 'GR_PD', 'GR_HC'
    ]
    sex = [
        'M', 'F', 'NS'
    ]
    race = [
        'WHITE', 'MULTI', 'NS', 'BLACK', 'ASIAN', 'INDALS', 'HAWOPI'
    ]
    dates = [
        'BIRTH_DATE', 'DIAGNOSIS_DATE', 'ENROLL_DATE', 'VISIT_DATE'
    ]
    hand = [
        'LEFT', 'RIGHT', 'BOTH'
    ]

    dtype = dict(
        PARTICIPANT=str,
        DIAGNOSIS=cdtype(categories=diagnosis, ordered=False),
        GENDER=cdtype(categories=sex, ordered=False),
        RACE=cdtype(categories=race, ordered=False),
        AGE=float,
        BIRTH_DATE=str,
        DIAGNOSIS_DATE=str,
        ENROLL_DATE=str,
        FAMILY_HISTORY=str,
        HANDEDNESS=cdtype(categories=hand, ordered=False),
        EDUCATION=str,
        SITE=int,
        PAG_NAME=str,
        VISIT=cdtype(categories=VISITS, ordered=True),
        VISIT_DATE=str,
        TEST=str,
        SCORE=float
    )

    # combine all datasets
    beh = load_behavior(fpath).dropna(subset=['VISIT', 'VISIT_DATE'])
    bio = load_biospecimen(fpath).dropna(subset=['VISIT'])
    dat = load_datscan(fpath).dropna(subset=['VISIT'])
    dem = load_demographics(fpath)

    visits = (beh.get(['PARTICIPANT', 'VISIT', 'VISIT_DATE'])
                 .sort_values('VISIT')
                 .drop_duplicates(subset=['PARTICIPANT', 'VISIT']))

    # add VISIT DATE from `visits` to `bio` and `dat`
    bio = pd.merge(bio.drop('VISIT_DATE', axis=1), visits,
                   on=['PARTICIPANT', 'VISIT'])
    dat = pd.merge(dat.drop('VISIT_DATE', axis=1), visits,
                   on=['PARTICIPANT', 'VISIT'])

    # throw everything together in one giant dataframe
    data = pd.merge(beh.append(bio, sort=True).append(dat, sort=True), dem,
                    on='PARTICIPANT')

    for key, item in dtype.items():
        data[key] = data[key].astype(item)
    for key in dates:
        data[key] = pd.to_datetime(data[key])

    # clean up age and get symptom duration
    data.AGE = (data.VISIT_DATE - data.BIRTH_DATE) / np.timedelta64(1, 'Y')
    duration = (data.VISIT_DATE - data.DIAGNOSIS_DATE) / np.timedelta64(1, 'Y')
    data = (data.assign(SYMPTOM_DURATION=duration)
                .drop(['BIRTH_DATE', 'DIAGNOSIS_DATE', 'ENROLL_DATE'], axis=1))

    return data[column_order]
