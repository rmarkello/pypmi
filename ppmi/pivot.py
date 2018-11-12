# -*- coding: utf-8 -*-

import pandas as pd


def _pivot_data(data, return_date=False):
    """
    Helper function for pivoting data

    Parameters
    ----------
    data : pandas.DataFrame
        Long-format DataFrame that has columns ['TEST', 'SCORE', 'PARTICIPANT']
        and is pivot-ready
    return_data : bool, optional
        Whether to also return DataFrame containing visit date of `data`. If
        True, provided `data` must have 'VISIT_DATE', column. Default: False

    Returns
    -------
    wide : (N, G) pandas.DataFrame
        Wide-format data where `N` is samples and `G` is features
    """

    wide = pd.pivot_table(data,
                          columns='TEST',
                          values='SCORE',
                          index='PARTICIPANT')

    if return_date:
        age = data[data.PARTICIPANT.isin(wide.index)]
        age = age[['PARTICIPANT', 'VISIT_DATE']].drop_duplicates('PARTICIPANT')
        return wide, age.set_index('PARTICIPANT')

    return wide


def pivot_datscan(data, visit='SC', return_date=False):
    """
    Extracts DAT scan data from `data`

    Parameters
    ----------
    data : pandas.DataFrame
        Long-format DataFrame as obtained by `ppmi.data.get_all()`
    visit : str, optional
        Visit for which to extract DAT scan data. Default: 'SC'
    return_date : bool, optional
        Whether to also return dataframe containing visit date. Default: False

    Returns
    -------
    data : (N, G) pandas.DataFrame
        Wide-format DAT data where `N` is participants and `G` is variables
    """

    # query appropriate data from input
    all_data = data.query(f'PAG_NAME == "DATSCAN" & VISIT == "{visit}"')

    return _pivot_data(all_data, return_date=return_date)


def pivot_biospecimen(data, visit='BL', return_date=False):
    """
    Extracts biospecimen data from `data`

    Parameters
    ----------
    data : pandas.DataFrame
        Long-format DataFrame as obtained by `ppmi.data.get_all()`
    visit : str, optional
        Visit for which to extract biospecimen data. Default: 'BL'
    return_date : bool, optional
        Whether to also return dataframe containing visit date. Default: False

    Returns
    -------
    data : (N, G) pandas.DataFrame
        Wide-format biospecimen data where N is participants and G is variables
    """

    # query appropriate data from input
    all_data = data.query(f'PAG_NAME == "BIOSPEC" & VISIT == "{visit}"')

    return _pivot_data(all_data, return_date=return_date)


def pivot_behavior(data, return_date=False):
    """
    Extracts behavioral-clinical data from `data`

    Parameters
    ----------
    data : pandas.DataFrame
        Long-format DataFrame as obtained by `ppmi.data.get_all()`
    return_date : bool, optional
        Whether to also return dataframe containing visit date. Default: False

    Returns
    -------
    data : (N, G) pandas.DataFrame
        Wide-format behav data where N is participants and G is variables
    """

    # query appropriate data from input
    # we want to drop non-behavioral data and the unmedicated UPDRS III score
    # also, we need MOCA from the SC visit as it was not administered at BL
    all_data = data.query(
        f'PAG_NAME not in ["DATSCAN", "BIOSPEC", "NUPDRS3A"] & '
        '(VISIT == "BL" & TEST != "MOCA" | (VISIT == "SC" & TEST == "MOCA"))'
    )

    return _pivot_data(all_data, return_date=return_date)
