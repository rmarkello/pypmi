# coding: utf-8

import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype as cdtype
from .. import datasets


COLUMN_ORDER = [
    'PARTICIPANT', 'DIAGNOSIS', 'GENDER', 'RACE', 'AGE', 'FAMILY_HISTORY',
    'HANDEDNESS', 'EDUCATION', 'SYMPTOM_DURATION', 'SITE', 'VISIT',
    'VISIT_DATE', 'PAG_NAME', 'TEST', 'SCORE'
]


def get_data(fpath):
    """
    Converts raw PPMI data in `fpath` into analysis-ready dataframe

    Parameters
    ----------
    fpath : str
        Filepath to directory containing all tabular data downloaded from the
        PPMI database.

    Returns
    -------
    data : pd.core.frame.DataFrame
        All PPMI data
    """

    diagnosis = [
        'PD', 'HC', 'SWEDD', 'PROD', 'GC_PD', 'GC_HC', 'GR_PD', 'GR_HC'
    ]
    sex = [
        'M', 'F', 'NS'
    ]
    race = [
        'WHITE', 'MULTI', 'NS', 'BLACK', 'ASIAN', 'INDALS', 'HAWOPI'
    ]
    visits = [
        'SC', 'BL', 'V01', 'V02', 'V03', 'V04', 'V05', 'V06', 'V07', 'V08',
        'V09', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'PW'
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
        VISIT=cdtype(categories=visits, ordered=True),
        VISIT_DATE=str,
        TEST=str,
        SCORE=float
    )

    # combine all datasets
    beh = datasets.get_behavior(fpath).dropna(subset=['VISIT', 'VISIT_DATE'])
    bio = datasets.get_biospecimen(fpath).dropna(subset=['VISIT'])
    dat = datasets.get_datscan(fpath).dropna(subset=['VISIT'])
    dem = datasets.get_demographics(fpath)

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

    return data[COLUMN_ORDER]
