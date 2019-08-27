# -*- coding: utf-8 -*-

import os
import pytest
import pypmi


@pytest.fixture(scope='session')
def datadir():
    path = os.path.join(os.environ['HOME'], 'pypmi-data')
    os.makedirs(path, exist_ok=True)
    os.environ['PPMI_PATH'] = path
    return path


@pytest.fixture(scope='session')
def studydata(datadir):
    # download data (don't overwrite if we already did it)
    pypmi.fetch_studydata('all', path=datadir, overwrite=False)
    # check to make sure all the datasets were downloaded correctly
    assert len(os.listdir(datadir)) == len(pypmi.fetchable_studydata())
    return datadir
