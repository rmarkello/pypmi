# -*- coding: utf-8 -*-

from io import BytesIO
import json
import os
from pkg_resources import resource_filename
import re
import zipfile

import requests
from tqdm import tqdm

with open(resource_filename('pypmi', 'data/tabular.json'), 'r') as src:
    TABULAR = json.load(src)


def _get_authentication(user=None, password=None):
    """
    Gets PPMI authentication from environmental variables if not supplied

    Parameters
    ----------
    user : str, optional
        Provided user login for PPMI database
    password : str, optional
        Provided password for PPMI database

    Returns
    -------
    user, password : str
        Authentication for PPMI database
    """

    var = env = None

    # try and find user in environmental variable "$PPMI_USER"
    if user is None:
        try:
            user = os.environ['PPMI_USER']
        except KeyError:
            var, env = 'user', 'PPMI_USER'

    # try and find password in environmental variable "$PPMI_PASSWORD"
    if password is None:
        try:
            password = os.environ['PPMI_PASSWORD']
        except KeyError:
            var, env = 'password', 'PPMI_PASSWORD'

    if var is not None or env is not None:
        raise ValueError('No `{0}` ID supplied and cannot find {0} in '
                         'local environment. Either supply `{0}` keyword '
                         'argument directly or set environmental variable '
                         '${1}.'.format(var, env))

    return user, password


def _get_studydata_params(user, password):
    """
    Returns credentials for downloading raw study data from the PPMI

    Parameters
    ----------
    user : str
        Email for user authentication
    password : str
        Password for user authentication

    Returns
    -------
    params : dict
        With keys 'userId' and 'authKey', ready to be supplied to a GET call
    """

    # make request to main login page; the returned content has the loginKey
    # embedded within so we have to search for and extract it
    login_url = "https://ida.loni.usc.edu/login.jsp?project=PPMI&page=HOME"
    data = dict(userEmail=user, userPassword=password)
    params = dict(project='PPMI', page='HOME')
    with requests.post(login_url, data=data, params=params) as main:
        try:
            login_key = re.search(r'studyData.jsp\?loginKey=(-?\d+)',
                                  main.text).group(1)
        except (AttributeError, IndexError):
            return

    # once we have the loginKey from the main page, we make another request
    # for the study data page; the returned content will have both the userID
    # and authKey embedded within so we have to search for and extract both
    study_url = "https://ida.loni.usc.edu/pages/access/studyData.jsp"
    params = dict(loginKey=login_key, userEmail=user, project='PPMI',
                  page='DOWNLOADS', subPage='STUDY_DATA')
    with requests.post(study_url, params=params) as study:
        try:
            user_id = re.search(r'userId=(\d+)', study.text).group(1)
            auth_key = re.search(r'authKey=(-?\d+)', study.text).group(1)
        except (AttributeError, IndexError):
            return

    # we have to return camelCase keys because these will serve as parameters
    # in a request.get call and be used to construct the query URL directly
    return dict(userId=user_id, authKey=auth_key)


def available_datasets():
    """ Lists datasets available to download from the PPMI """
    return list(TABULAR.keys())


def download_study_data(*dataset, path=None, user=None, password=None,
                        overwrite=False, verbose=True):
    """
    Downloads supplied tabular dataset(s) from the PPMI database

    The PPMI (https://ppmi-info.org/)

    Parameters
    ----------
    *dataset : str
        Dataset to download. Can provide as many as desired, but they should
        listed in :py:func:`ppmi.datasets.available_datasets()`. Alternatively,
        if any of the provided values are 'all', then all available datasets
        will be fetched.
    path : str, optional
        Filepath where downloaded data should be saved. If data files already
        exist at `path` they will be overwritten unless `overwrite=False`. If
        not supplied the current directory is used. Default: None
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for PPMI_PASSWORD variable in environment. Default:
        None
    overwrite : bool, optional
        Whether to overwrite existing PPMI data files at `path` if they already
        exist. Default: False
    verbose : bool, optional
        Whether to print progress bar as download occurs. Default: True

    Returns
    -------
    downloaded : str or list
        Filepath(s) to downloaded CSV files
    """

    url = "https://utilities.loni.usc.edu/download/study"
    params = dict(type='GET_FILES', userId=None, authKey=None, fileId=[])
    if path is None:
        path = os.getcwd()

    # check provided credentials; if none were supplied, look for creds in
    # user environmentabl variables
    user, password = _get_authentication(user, password)

    # gets numerical file IDs from tabular.json and appends the desired ids to
    # the request parameter dictionary; if the file is already downloaded we
    # store the filename to return to user
    downloaded = []
    if 'all' in dataset:
        dataset = available_datasets()
    for dset in dataset:
        info = TABULAR.get(dset, None)
        if info is None:
            raise ValueError('Provided dataset {} not available. Please see '
                             'available_datasets() for valid entries.'
                             .format(dset))

        file_id = info.get('id', None)
        file_name = os.path.join(path, info.get('name', ''))

        # if we don't want to overwrite existing data make sure that file
        # does not exist before appending it to request parameters
        if not os.path.isfile(file_name) or overwrite:
            params['fileId'].append(file_id)
        else:
            downloaded.append(file_name)

    # if we already downloaded all then there's no reason to make requests!
    if len(params['fileId']) == 0:
        return downloaded

    # we need to get the authentication key and user id; since neither of these
    # can be obtained from a simple request we have to make nested requests
    # it's possible that these calls might fail (especially if the provided
    # user and password were supplied incorrectly), so confirm before updating
    authentication = _get_studydata_params(user=user, password=password)
    if authentication is None:
        raise ValueError('Provided user and password could not be '
                         'authenticated. Please check inputs and try again. '
                         'If you have not registered for access to the PPMI '
                         'database, please follow instructions outlined here: '
                         'https://www.ppmi-info.org/access-data-specimens/'
                         'download-data/')
    params.update(authentication)

    # :tada: download the data! :tada:
    with requests.get(url, params=params, stream=True) as data:
        data.raise_for_status()

        # construct progress bar
        try:
            total_size = int(data.headers.get('content-length'))
        except (TypeError, KeyError):
            total_size = None
        if verbose:
            pbar = tqdm(total=total_size, unit='B', unit_scale=True)
        else:
            pbar = None

        # get the actual data! we're saving iy to an internal stream so that we
        # don't have to write to a temporary zipfile if >1 files were requested
        out, wrote = BytesIO(), 0
        for chunk in data.iter_content(1024):
            out.write(chunk)
            wrote += len(chunk)
            if pbar is not None:
                pbar.update(len(chunk))
        out.seek(0)
        pbar.close()
        if total_size is not None and total_size != wrote:
            print('Unable to fetch all requested data ({}/{} bytes received). '
                  'Downloaded data may be corrupted; use at your own risk.'
                  .format(wrote, total_size))

        # if we're dealing with a zipfile, extract the contents to `path`
        if 'zip-compressed' in data.headers.get('Content-Type', ''):
            with zipfile.ZipFile(out, 'r') as src:
                src.extractall(path=path)
                downloaded.extend([os.path.join(path, f.filename) for f in
                                   src.filelist])
        # otherwise it should just be a CSV; save it to `path`
        else:
            fname = re.search('filename="(.+)"',
                              data.headers.get('Content-Disposition')).group(1)
            downloaded = [os.path.join(path, fname)]
            with open(downloaded[0], 'wb') as dest:
                dest.write(out.read())

    return downloaded
