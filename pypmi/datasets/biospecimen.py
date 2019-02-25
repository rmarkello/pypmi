# -*- coding: utf-8 -*-

import os.path as op
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype as cdtype

RENAME_COLS = dict(
    PATNO='PARTICIPANT', CLINICAL_EVENT='VISIT', TESTNAME='TEST',
    TESTVALUE='SCORE'
)
ASSIGN_COLS = dict(
    PAG_NAME='BIOSPEC', VISIT_DATE=np.nan
)
RETAIN_COLS = [
    'PARTICIPANT', 'PAG_NAME', 'VISIT', 'VISIT_DATE', 'TEST', 'SCORE'
]


def get_data(fpath):
    """
    Gets biospecimen data for PPMI subjects

    Parameters
    ----------
    fpath : str
        Filepath to directory containing Biospecimen_Analysis_Results.csv file

    Returns
    -------
    data : pd.core.frame.DataFrame
        Biospecimen data
    """

    visits = ['SC', 'BL', 'V01', 'V02', 'V03', 'V04', 'V05', 'V06', 'V07',
              'V08', 'V09', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15']
    dtype = dict(PATNO=str,
                 CLINICAL_EVENT=cdtype(visits, ordered=True),
                 TESTNAME=str,
                 TESTVALUE=str)

    fname = op.join(fpath, 'Current_Biospecimen_Analysis_Results.csv')
    data = pd.read_csv(fname, dtype=dtype)

    data['TESTVALUE'] = pd.to_numeric(data.TESTVALUE, errors='coerce')
    data = data.rename(columns=RENAME_COLS).assign(**ASSIGN_COLS)[RETAIN_COLS]
    data = data.dropna(axis=0, subset=['SCORE'])

    return data
