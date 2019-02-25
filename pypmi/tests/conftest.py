# -*- coding: utf-8 -*-

import os
import pytest
from pypmi import datasets


@pytest.fixture(scope='session')
def datadir(tmpdir_factory):
    return tmpdir_factory.mktemp('data')


@pytest.fixture(scope='session')
def studydata(datadir):
    # download data (don't overwrite if we already did it)
    datasets.download_studydata('all', path=datadir, overwrite=False)
    # check to make sure all the datasets were downloaded correctly
    assert len(os.listdir(datadir)) == len(datasets.available_datasets())
    return datadir
