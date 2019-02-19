# -*- coding: utf-8 -*-

from io import BytesIO
import json
import os
from pkg_resources import resource_filename
import re
import zipfile

import requests
from tqdm import tqdm

with open(resource_filename('ppmi', 'data/tabular.json'), 'r') as src:
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


def _get_studydata_url(user, password):
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
    url : str
        Download url ready to make requests; file IDs must be appended to the
        query string in order to actually download anything...
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
                        verbose=True):
    """
    Downloads supplied tabular dataset(s) from the PPMI database

    The PPMI (https://ppmi-info.org/)

    Parameters
    ----------
    *dataset : str
        Dataset to download. Can provide as many as desired, but they should
        be valid options listed in `available_datasets()`. Alternatively, if
        any of the provided values are 'all', then all datasets will be
        fetched.
    path : str, optional
        Filepath where downloaded data should be saved. If data files already
        exist at `path` they will be overwritten. If not supplied the current
        directory is used. Default: None
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for PPMI_PASSWORD variable in environment. Default:
        None
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

    # we need to get the authentication key and user id; since neither of these
    # can be obtained from a simple request we have to make nested requests
    # it's possible that these calls might fail (especially if the provided
    # user and password were supplied incorrectly), so confirm before updating
    authentication = _get_studydata_url(user=user, password=password)
    if authentication is None:
        raise ValueError('Provided user and password could not be '
                         'authenticated. Please check inputs and try again. '
                         'If you have not registered for access to the PPMI '
                         'database, please follow instructions outlined here: '
                         'https://www.ppmi-info.org/access-data-specimens/'
                         'download-data/')
    params.update(authentication)

    # gets numerical file IDs from tabular.json and appends the desired ids to
    # the request parameter dictionary
    if 'all' in dataset:
        dataset = available_datasets()
    for dset in dataset:
        file_id = TABULAR.get(dset, None)
        if file_id is None:
            raise ValueError('Provided dataset {} not available. Please see '
                             'available_datasets() for valid entries.'
                             .format(dset))
        else:
            params['fileId'].append(file_id)

    # :tada: download the data! :tada:
    with requests.get(url, params=params, stream=True) as data:
        # catch possible failures and give relatively unhelpful error messages
        if data.status_code != 200:
            raise ValueError('Unable to query data from PPMI. GET request '
                             'failed with status code {} and reason {}'
                             .format(data.status_code, data.reason))

        # construct progress bar
        try:
            total_size = int(data.headers.get('content-length'))
        except (TypeError, KeyError):
            total_size = None
        if verbose:
            pbar = tqdm(total=total_size, unit='B', unit_scale=True)
        else:
            pbar = None

        # get the actual data! we're saving things to an internal stream so
        # that we don't have to write to a temporary zipfile if multiple files
        # were requested
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

        # if we're dealing with a zip file, extract the contents
        if 'zip-compressed' in data.headers.get('Content-Type', ''):
            with zipfile.ZipFile(out, 'r') as src:
                src.extractall(path=path)
                downloaded = [os.path.join(path, f.filename) for f in
                              src.filelist]
        # otherwise it's just a single CSV; get the filename and then save it!
        else:
            fname = re.search('filename="(.+)"',
                              data.headers.get('Content-Disposition')).group(1)
            downloaded = os.path.join(path, fname)
            with open(downloaded, 'wb') as dest:
                dest.write(out.read())

    return downloaded
