# -*- coding: utf-8 -*-
"""
Functions for fetching/downloading data from the PPMI database
"""

from io import BytesIO
import json
import os
from pkg_resources import resource_filename
import re
from typing import Dict, List
import zipfile

import requests
from tqdm import tqdm

from .utils import _get_authentication, _get_data_dir

with open(resource_filename('pypmi', 'data/studydata.json'), 'r') as src:
    _STUDYDATA = json.load(src)
with open(resource_filename('pypmi', 'data/genetics.json'), 'r') as src:
    _GENETICS = json.load(src)


def _get_download_params(url,
                         user: str = None,
                         password: str = None) -> Dict[str, str]:
    """
    Returns credentials for downloading raw study data from the PPMI

    Parameters
    ----------
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for $PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for $PPMI_PASSWORD variable in environment. Default:
        None

    Returns
    -------
    params : dict
        With keys 'userId' and 'authKey', ready to be supplied to a GET call
    """

    user, password = _get_authentication(user, password)

    # check what page we'll be querying for authentication key based on
    # supplied URL; currently only 'genetic' and 'study' are accepted...
    if 'genetic' in url:
        subPage = 'GENETIC_DATA'
        study_url = "https://ida.loni.usc.edu/pages/access/geneticData.jsp"
    elif 'study' in url:
        subPage = 'STUDY_DATA'
        study_url = "https://ida.loni.usc.edu/pages/access/studyData.jsp"
    else:
        raise ValueError('Cannot parse provided URL {} to authenticate user '
                         'and password from PPMI database. Please make sure '
                         'that URL is appropriately formed and try again.')

    # make request to main login page; the returned content has the loginKey
    # embedded within so we have to search for and extract it
    login_url = "https://ida.loni.usc.edu/login.jsp?project=PPMI&page=HOME"
    data = dict(userEmail=user, userPassword=password)
    params = dict(project='PPMI', page='HOME')
    with requests.post(login_url, data=data, params=params) as main:
        main.raise_for_status()
        try:
            login_key = re.search(r'studyData.jsp\?loginKey=(-?\d+)',
                                  main.text).group(1)
        except (AttributeError, IndexError):
            return

    # once we have the loginKey from the main page, we make another request
    # for the study data page; the returned content will have both the userID
    # and authKey embedded within so we have to search for and extract both

    params = dict(loginKey=login_key, userEmail=user, project='PPMI',
                  page='DOWNLOADS', subPage=subPage)
    with requests.post(study_url, params=params) as study:
        study.raise_for_status()
        try:
            user_id = re.search(r'userId=(\d+)', study.text).group(1)
            auth_key = re.search(r'authKey=(-?\d+)', study.text).group(1)
        except (AttributeError, IndexError):
            return

    # we have to return camelCase keys because these will serve as parameters
    # in a request.get call and be used to construct the query URL directly
    return dict(userId=user_id, authKey=auth_key)


def _download_data(info: Dict[str, Dict[str, str]],
                   url: str,
                   path: str = None,
                   user: str = None,
                   password: str = None,
                   overwrite: bool = False,
                   verbose: bool = True,
                   bundle: bool = True) -> List[str]:
    """
    Downloads dataset(s) listed in `info` from `url`

    Parameters
    ----------
    info : dict
        Dataset information to download. Each key must have a value that is
        a dictionary containing keys 'id' (specifying the file ID of the
        dataset in the PPMI database) and 'name' (specifying the file name of
        the dataset in the PPMI database).
    url : str
        URL from which to download data. Will be formatted with authentication
        and requested data.
    path : str, optional
        Filepath where downloaded data should be saved. If data files already
        exist at `path` they will be overwritten unless `overwrite=False`. If
        not specified will look for an environmental variable $PPMI_PATH and,
        if not set, use the current directory. Default: None
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for $PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for $PPMI_PASSWORD variable in environment. Default:
        None
    overwrite : bool, optional
        Whether to overwrite existing PPMI data files at `path` if they already
        exist. Default: False
    verbose : bool, optional
        Whether to print progress bar as download occurs. Default: True
    bundle : bool, optional
        Whether to bundle downloads into a single request instead of making
        individual requests for each dataset. Default: True

    Returns
    -------
    downloaded : list
        Filepath(s) to downloaded datasets
    """

    params = dict(type='GET_FILES', userId=None, authKey=None, fileId=None)
    path = _get_data_dir(path)

    # check provided credentials; if none were supplied, look for creds in
    # user environmental variables
    if verbose:
        print('Fetching authentication key for data download...')
    user, password = _get_authentication(user, password)

    # gets numerical file IDs from relevant JSON file; if the file is already
    # downloaded we store the filename to return to the user
    downloaded = []
    if verbose:
        print('Requesting {} datasets for download...'.format(len(info)))
    file_ids = []
    for dset, file_info in info.items():
        if file_info is None:
            raise ValueError('Provided dataset {} not available. Please see '
                             'available_datasets() for valid entries.'
                             .format(dset))

        file_id = file_info.get('id', None)
        file_name = os.path.join(path, file_info.get('name', ''))

        # if we don't want to overwrite existing data make sure that file
        # does not exist before appending it to request parameters
        if not os.path.isfile(file_name) or overwrite:
            file_ids.append(file_id)
        else:
            downloaded.append(file_name)

    # if we already downloaded all then there is no reason to make requests!
    if len(file_ids) == 0:
        return downloaded

    # we need to get the authentication key and user id; since neither of these
    # can be obtained from a simple request we have to make nested requests.
    # it's possible that these calls might fail (especially if the provided
    # user and password were supplied incorrectly), so confirm before updating
    authentication = _get_download_params(url, user=user, password=password)
    if authentication is None:
        raise ValueError('Provided user and password could not be '
                         'authenticated. Please check inputs and try again. '
                         'If you have not registered for access to the PPMI '
                         'database, please follow instructions outlined here: '
                         'https://www.ppmi-info.org/access-data-specimens/'
                         'download-data/')
    params.update(authentication)

    # determine whether we're bundling the data (i.e., requesting all files at
    # once) or peforming separate downloads
    if bundle:
        file_ids = [file_ids]
    for fid in file_ids:
        params['fileId'] = fid
        # :tada: download the data! :tada:
        with requests.get(url, params=params, stream=True) as data:
            data.raise_for_status()

            # construct progress bar
            try:
                total_size = int(data.headers.get('content-length'))
            except (TypeError, KeyError):
                total_size = None
            if verbose:
                pbar = tqdm(total=total_size, unit='B', unit_scale=True,
                            desc='Fetching data file(s)')
            else:
                pbar = None

            # get the actual data! we're saving it to an internal stream so
            # that we don't have to write to a temporary zipfile if >1 files
            # were requested
            out, wrote = BytesIO(), 0
            for chunk in data.iter_content(1024):
                out.write(chunk)
                wrote += len(chunk)
                if pbar is not None:
                    pbar.update(len(chunk))
            out.seek(0)
            if pbar is not None:
                pbar.close()
            if total_size is not None and total_size != wrote:
                print('Unable to fetch all requested data ({}/{} bytes '
                      'received). Downloaded data may be corrupted; use at '
                      'your own risk.'.format(wrote, total_size))

            # if we're dealing with a zipfile, extract the contents to `path`
            if 'zip-compressed' in data.headers.get('Content-Type', ''):
                with zipfile.ZipFile(out, 'r') as src:
                    src.extractall(path=path)
                    downloaded.extend([os.path.join(path, f.filename) for f in
                                       src.filelist])
            # otherwise it should just be a CSV; save it to `path`
            else:
                fname = data.headers.get('Content-Disposition')
                fname = re.search('filename="(.+)"', fname).group(1)
                downloaded.extend([os.path.join(path, fname)])
                with open(downloaded[0], 'wb') as dest:
                    dest.write(out.read())

    return downloaded


def fetchable_studydata() -> List[str]:
    """
    Lists study data available to download from the PPMI

    Returns
    -------
    available : list
        List of available data files

    See Also
    --------
    pypmi.fetch_studydata
    """

    return list(_STUDYDATA.keys())


def fetchable_genetics(projects: bool = False) -> List[str]:
    """
    Lists genetics data available to download from the PPMI

    Parameters
    ----------
    projects : bool, optional
        List available projects instead of individual data files available for
        download. Due to the size of genetic data, many datasets are split up
        into multiple files associated with a single project or analysis; you
        can specify these projects when downloading data with
        :py:func:`pypmi.datasets.fetch_genetics` and all associated files
        will be fetched.

    Returns
    -------
    available : list
        List of available data files

    See Also
    --------
    pypmi.fetch_genetics
    """

    if projects:
        return ['project {}'.format(project)
                for project in [107, 108, 115, 116, 118, 120, 133]]
    else:
        return list(_GENETICS.keys())


def fetch_studydata(*datasets: str,
                    path: str = None,
                    user: str = None,
                    password: str = None,
                    overwrite: bool = False,
                    verbose: bool = True) -> List[str]:
    """
    Downloads specified study data `datasets` from the PPMI database

    Parameters
    ----------
    *datasets : str
        Datasets to download. Can provide as many as desired, but they should
        be listed in :py:func:`pypmi.fetchable_studydata`. Alternatively, if
        any of the provided values are 'all', then all available datasets will
        be fetched.
    path : str, optional
        Filepath where downloaded data should be saved. If data files already
        exist at `path` they will be overwritten unless `overwrite=False`. If
        not supplied the current directory is used. Default: None
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for $PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for $PPMI_PASSWORD variable in environment. Default:
        None
    overwrite : bool, optional
        Whether to overwrite existing PPMI data files at `path` if they already
        exist. Default: False
    verbose : bool, optional
        Whether to print progress bar as download occurs. Default: True

    Returns
    -------
    downloaded : list
        Filepath(s) to downloaded datasets

    See Also
    --------
    pypmi.fetchable_studydata
    """

    url = "https://utilities.loni.usc.edu/download/study"

    # take subset of available study data based on requested `datasets`
    if 'all' in datasets:
        datasets = fetchable_studydata()
    info = {dset: _STUDYDATA.get(dset) for dset in datasets}

    return _download_data(info, url, path=path, user=user, password=password,
                          overwrite=overwrite, verbose=verbose)


def fetch_genetics(*datasets: str,
                   path: str = None,
                   user: str = None,
                   password: str = None,
                   overwrite: bool = False,
                   verbose: bool = True) -> List[str]:
    """
    Downloads specified genetics data `datasets` from the PPMI database

    Parameters
    ----------
    *datasets : str
        Datasets to download. Can provide as many as desired, but they should
        be listed in :py:func:`pypmi.fetchable_genetics`. Alternatively, if any
        of the provided values are 'all', then all available datasets will be
        fetched.
    path : str, optional
        Filepath where downloaded data should be saved. If data files already
        exist at `path` they will be overwritten unless `overwrite=False`. If
        not supplied the current directory is used. Default: None
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for $PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for $PPMI_PASSWORD variable in environment. Default:
        None
    overwrite : bool, optional
        Whether to overwrite existing PPMI data files at `path` if they already
        exist. Default: False
    verbose : bool, optional
        Whether to print progress bar as download occurs. Default: True

    Returns
    -------
    downloaded : list
        Filepath(s) to downloaded datasets

    See Also
    --------
    pypmi.fetchable_genetics
    """

    url = "https://utilities.loni.usc.edu/download/genetic"
    datasets = list(datasets)

    # take subset of available genetics data based on requested `datasets`
    if 'all' in datasets:
        datasets = fetchable_genetics(projects=False)
    # check for project designations in requested data
    for project in fetchable_genetics(projects=True):
        if project in datasets:
            datasets.remove(project)
            datasets += [f for f in _GENETICS.keys() if project in f.lower()]

    info = {dset: _GENETICS.get(dset) for dset in datasets}

    return _download_data(info, url, path=path, user=user, password=password,
                          overwrite=overwrite, verbose=verbose, bundle=False)
