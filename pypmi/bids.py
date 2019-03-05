# -*- coding: utf-8 -*-
"""
Code for preparing raw PPMI neuroimaging data to be converted to BIDS format
with heudiconv.
"""

from os import PathLike
import pathlib
from pkg_resources import resource_filename
from typing import List, Union

import pandas as pd

# get list of sessions that won't convert for whatever reason
BAD_SCANS = pd.read_csv(resource_filename('pypmi', 'data/sessions.txt'))
HEURISTIC = resource_filename('pypmi', 'data/heuristic.py')


def _prepare_subject(subj_dir: Union[str, PathLike],
                     timeout: Union[str, PathLike] = None) -> str:
    """
    Reorganizes `subj_dir` to structure more compatible with ``heudiconv``

    Parameters
    ----------
    subj_dir : str or pathlib.Path
        Path to subject directory as downloaded from ppmi-info.org
    timeout : str or pathlib.Path, optional
        If set, path to directory where bad scans should be moved. Default:
        None

    Returns
    -------
    subject : str
        Basename of `subj_dir`
    """

    # coerce subj_dir to path object
    if isinstance(subj_dir, str):
        subj_dir = pathlib.Path(subj_dir).resolve()

    # get all scan types for subject
    scans = [f for f in subj_dir.glob('*') if not f.name.isdigit()]

    # if subject was previously converted update number structure correctly
    prev = len([f for f in subj_dir.glob('*') if f.name.isdigit()])

    # get all sessions for subject (session = same day)
    sessions = [v.name[:7] for v in subj_dir.rglob('????-??-??_??_??_??.?')]
    sessions = sorted(set(sessions))

    # iterate through sessions and copy scans to uniform directory structure
    for n, ses in enumerate(sessions, prev + 1):
        # make session directory
        ses_dir = subj_dir / str(n)
        ses_dir.mkdir(exist_ok=True)

        # iterate through all scans for a given session (visit) and move
        for scan_type in subj_dir.glob('*/{0}*/*'.format(ses)):
            # idk why this would be but check just in case????
            if not scan_type.is_dir():
                continue

            # if this is a bad scan, move it to `timeout`
            if scan_type.name in BAD_SCANS.scan.values and timeout is not None:
                dest = timeout / subj_dir.name / ses_dir.name
                dest.mkdir(parents=True, exist_ok=True)
                scan_type.rename(dest / scan_type.name)
                continue

            # otherwise, move it to the appropriate scan directory
            scan_type.rename(ses_dir / scan_type.name)

            # if there are no more scans in the parent directory, remove it
            remain = [f for f in scan_type.parent.glob('*') if f != scan_type]
            if len(remain) == 0:
                scan_type.parent.rmdir()

    # remove empty directories
    for scan in scans:
        scan.rmdir()

    return subj_dir.name


def _prepare_directory(data_dir: Union[str, PathLike],
                       ignore_bad: bool = True) -> List[str]:
    """
    Reorganizes PPMI `data_dir` to a structure compatible with ``heudiconv``

    PPMI data starts off with a sub-directory structure that is not conducive
    to use with ``heudiconv``. By default, scans are grouped by scan type
    rather than by session, and there are a number of redundant sub-directories
    that we don't need. This script reorganizes the data, moving things around
    so that the general hierarchy is {subject}/{session}/{scan}, which makes
    for a much easier time converting the PPMI dataset into BIDS format.

    An added complication is that a minority of the scans in the PPMI database
    are "bad" to some degree. For most, it is likely that there was some issue
    with exporting/uploading the DICOM files. For others, the conversion
    process we intend to utilize (``heudiconv`` and ``dcm2niix``) fails to
    appropriately convert the files due to some idiosyncratic reason that could
    be fixed but we don't have the patience to fix at the current juncture.
    Nonetheless, these scans need to be removed so that we can run the batch of
    subjects through ``heudiconv`` without any abrupt failures. By default,
    these scans are moved to a sub-directory of `data_dir`; setting
    `ignore_bad` to False will retain these scans (but be warned!)

    Parameters
    ----------
    data_dir : str or pathlib.Path
        Filepath to PPMI dataset, as downloaded from http://ppmi-info.org
    ignore_bad : bool, optional
        Whether to ignore "bad" scans (i.e., ones that are known to fail
        conversion or reconstruction)

    Returns
    -------
    subjects : list
        List of subjects who are ready to be converted / reconstructed with
        ``heudiconv``
    """

    if isinstance(data_dir, str):
        data_dir = pathlib.Path(data_dir).resolve()

    # location where "bad" scans will be moved
    if ignore_bad:
        timeout = data_dir / 'bad'
        timeout.mkdir(exist_ok=True)
    else:
        timeout = None

    subjects = []
    for subj_dir in sorted(data_dir.glob('*')):
        if not subj_dir.is_dir():
            continue
        subj = _prepare_subject(subj_dir, timeout=timeout)
        subjects.append(subj)

    return subjects


def convert_ppmi(raw_dir: Union[str, PathLike],
                 out_dir: Union[str, PathLike],
                 ignore_bad: bool = True) -> pathlib.Path:
    """
    Converts PPMI DICOMs in `raw_dir` to BIDS dataset at `out_dir`

    Processes data using ``heudiconv``. As such, you must have Docker installed
    on your system for this function to work

    Parameters
    ----------
    raw_dir : str or pathlib.Path
        Path to raw PPMI dataset to be converted to BIDS format
    out_dir : str or pathlib.Path
        Path to output directory where BIDS-format PPMI dataset should be
        generated
    ignore_bad : bool, optional
        Whether to ignore "bad" scans (i.e., ones that are known to fail
        conversion or reconstruction). Default: True

    Returns
    -------
    out_dir : pathlib.Path
        Generated BIDS dataset

    Notes
    -----
    The PPMI dataset in `raw_dir` should consistent of DICOM images obtained
    from http://www.ppmi-info.org/access-data-specimens/download-data/ and
    unzipped into a single directory. The structure should look something like:

    └── PPMI/
        ├── SUB-1/
        |   ├── SCAN-TYPE-1/                      (e.g., MPRAGE_GRAPPA)
        |   |   ├── SCAN-DATETIME-1/
        |   |   |   └── SCAN-SERIES-1/
        |   |   |       └── *dcm
        |   |   └── SCAN-DATETIME-2/
        |   ├── SCAN-TYPE-2/                      (e.g., AX_FLAIR)
        |   |   ├── SCAN-DATETIME-1/
        |   |   |   └── SCAN-SERIES-2/
        |   |   |       └── *dcm
        |   |   └── SCAN-DATETIME-2/
        |   ├── .../
        |   └── SCAN-TYPE-N/
        ├── SUB-2/
        ├── .../
        └── SUB-N/

    Where `SUB-N` are PPMI subject numbers, `SCAN-DATETIME-N` are timestamps of
    the format YYYY-MM-DD_HH_MM_SS.0, and `SCAN-SERIES-N` are unique
    identifiers of the format S######.

    This sub-directory structure is not conducive to use with ``heudiconv``. By
    default, scans are grouped by scan type rather than by session, and there
    are a number of redundant sub-directories that we don't need. This function
    reorganizes the data, moving scans around so that the general hierarchy is
    {subject}/{session}/{scan}, which makes for a much easier time converting
    the PPMI dataset into BIDS format.

    An added complication is that a minority of the scans in the PPMI database
    are "bad" to some degree. For most, it is likely that there was some issue
    with exporting/uploading the DICOM files. For others, the conversion
    process we intend to utilize (``heudiconv`` and ``dcm2niix``) fails to
    appropriately convert the files due to some idiosyncratic reason that could
    be fixed but we don't have the patience to fix at the current juncture.
    Nonetheless, these scans need to be removed so that we can run the batch of
    subjects through ``heudiconv`` without any abrupt failures. By default,
    these scans are moved to a sub-directory of `raw_dir`; setting `ignore_bad`
    to False will retain these scans and try to convert them (but be warned!).

    Once re-organization is done the resulting directory is processed with
    ``heudiconv`` and the converted BIDS dataset is stored in `out_dir`.
    """

    try:
        import docker
    except ImportError:
        raise ImportError('Docker-py is not available; cannot convert '
                          'provided dataset without Docker. Either `pip '
                          'install docker` or `conda install docker-py` and '
                          'try again.')

    if isinstance(raw_dir, str):
        raw_dir = pathlib.Path(raw_dir).resolve()
    if isinstance(out_dir, str):
        out_dir = pathlib.Path(out_dir).resolve()

    # generate this, if it doesn't already exist
    out_dir.mkdir(exist_ok=True)

    subjects = _prepare_directory(raw_dir, ignore_bad=ignore_bad)

    # get docker client and pull heudiconv image, if necessary
    client = docker.from_env()
    if len(client.images.list('nipy/heudiconv')) == 0:
        client.images.pull('nipy/heudiconv', tag='latest')

    # run heudiconv over all potential sessions
    for session in range(1, 6):
        cli = client.containers.run(
            image='nipy/heudiconv',
            command=[
                '-d', '/data/{subject}/{session}/*/*dcm',
                '-s', ' '.join(subjects),
                '-ss', session,
                '--outdir', '/out',
                '--heuristic', '/heuristic.py',
                '--converter', 'dcm2niix',
                '--bids',
                '--minmeta'
            ],
            remove=True,
            detach=True,
            volumes={str(raw_dir): {'bind': '/data', 'mode': 'ro'},
                     str(out_dir): {'bind': '/out', 'mode': 'rw'},
                     HEURISTIC: {'bind': '/heuristic.py', 'mode': 'ro'}}
        )
        for log in cli.logs(stream=True):
            print(log.decode(), end='')

    return out_dir
