# coding: utf-8

import os.path as op
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype as cdtype

RENAME_COLS = dict(PATNO='PARTICIPANT',
                   EVENT_ID='VISIT')
ASSIGN_COLS = dict(PAG_NAME='DATSCAN',
                   VISIT_DATE=np.nan)
RETAIN_COLS = ['PARTICIPANT', 'PAG_NAME', 'VISIT',
               'VISIT_DATE', 'TEST', 'SCORE']


def get_data(fpath):
    """
    Gets DaTscan data for PPMI subjects

    Parameters
    ----------
    fname : str
        Filepath to directory containing DaTScan_Analysis.csv file

    Returns
    -------
    data : pandas.core.frame.DataFrame
        DaTScan data
    """

    visits = ['SC', 'BL', 'V01', 'V02', 'V03', 'V04', 'V05', 'V06', 'V07',
              'V08', 'V09', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15']
    dtype = dict(PATNO=str,
                 EVENT_ID=cdtype(visits, ordered=True))

    fname = op.join(fpath, 'DATScan_Analysis.csv')
    data = pd.read_csv(fname, dtype=dtype)

    # melt into tidy DataFrame
    data = pd.melt(data.rename(columns=RENAME_COLS),
                   id_vars=RENAME_COLS.values(),
                   var_name='TEST', value_name='SCORE')
    data = data.dropna(axis=0, subset=['SCORE'])
    data = data.assign(**ASSIGN_COLS)[RETAIN_COLS]

    return data
