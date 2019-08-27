# -*- coding: utf-8 -*-

import json
import os
from pkg_resources import resource_filename
import pytest
import pypmi

with open(resource_filename('pypmi', 'data/studydata.json'), 'r') as src:
    _STUDYDATA = json.load(src)


@pytest.fixture(scope='session')
def datadir():
    if os.environ.get('PPMI_PATH') is None:
        path = os.path.join(os.environ['HOME'], 'pypmi-data')
        os.makedirs(path, exist_ok=True)
        os.environ['PPMI_PATH'] = path
    else:
        path = os.environ['PPMI_PATH']
    return path


@pytest.fixture(scope='session')
def studydata(datadir):
    # download data (don't overwrite if we already did it)
    pypmi.fetch_studydata('all', path=datadir, overwrite=False)

    # has all the studydata we were supposed to fetch has been fetched?
    fns = [_STUDYDATA.get(d)['name'] for d in pypmi.fetchable_studydata()]
    assert all(os.path.exists(os.path.join(datadir, f)) for f in fns)

    return datadir
