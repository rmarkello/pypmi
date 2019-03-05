# -*- coding: utf-8 -*-

import os
from typing import List, Tuple


def _get_authentication(user: str = None,
                        password: str = None) -> Tuple[str, str]:
    """
    Gets PPMI authentication from environmental variables if not supplied

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


def _get_data_dir(path: str = None,
                  fnames: List[str] = None) -> str:
    """
    Gets `path` to PPMI data directory, searching environment if necessary

    Will optionally check whether supplied `fnames` are present at `path`

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None
    fnames : list, optional
        Filenames to check for at `path` (once `path` has been determined). If
        any of the files listed in `fnames` do not exist a FileNotFoundError
        will be raised.

    Returns
    -------
    path : str
        Filepath to directory containing PPMI data files

    Raises
    ------
    FileNotFoundError
    """

    # try and find directory in environmental variable "$PPMI_PATH"
    if path is None:
        try:
            path = os.environ['PPMI_PATH']
        except KeyError:
            path = os.getcwd()

    if fnames is not None:
        for fn in fnames:
            if not os.path.isfile(os.path.join(path, fn)):
                raise FileNotFoundError('{} does not exist in {}. Please make '
                                        'sure you have downloaded the '
                                        'appropriate files from the PPMI '
                                        'database and try again. You can use '
                                        '`pypmi.datasets.fetch_studydata(\'all'
                                        '\')` to automatically download all '
                                        'required data files.'
                                        .format(fn, path))

    return path
