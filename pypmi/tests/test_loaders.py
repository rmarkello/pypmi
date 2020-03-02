# -*- coding: utf-8 -*-

import numpy as np
import pytest

from pypmi import loaders


@pytest.mark.parametrize(('loader', 'expected'), [
    (loaders.available_behavior, 25),
    (loaders.available_biospecimen, 263),
    (loaders.available_datscan, 4),
    (loaders.available_demographics, 12)
])
def test_available_dsets(studydata, loader, expected):
    dsets = loader(studydata)
    assert isinstance(dsets, list) and len(dsets) == expected


def test_load_dates(studydata):
    out = loaders._load_dates(studydata)
    assert all(out.columns == ['participant', 'visit', 'date'])
    # check that columns have appropriate datatypes
    assert out['participant'].dtype == np.int64
    assert out['visit'].dtype == loaders.VISITS
    assert out['date'].dtype == np.datetime64(1, 'ns').dtype


@pytest.mark.parametrize(('loader', 'measures', 'expected'), [
    (loaders.load_behavior, 'all', loaders.available_behavior),
    (loaders.load_behavior, ['benton', 'epworth'], ['benton', 'epworth']),
    # (loaders.load_biospecimen, 'all', loaders.available_biospecimen),
    (loaders.load_biospecimen, None, ['abeta_1-42', 'csf_alpha-synuclein', 'ptau', 'ttau']),  # noqa
    (loaders.load_biospecimen, ['abeta_1-42'], ['abeta_1-42']),
    (loaders.load_datscan, 'all', loaders.available_datscan),
    (loaders.load_datscan, ['caudate_l', 'caudate_r'], ['caudate_l', 'caudate_r'])  # noqa
])
def test_load_dsets(studydata, loader, measures, expected):
    out = loader(studydata, measures=measures)
    # check that we have all the columns we expect to have
    assert all(out.columns[:3] == ['participant', 'visit', 'date'])
    if callable(expected):
        expected = expected(studydata)
    assert all(out.columns[3:] == expected)


@pytest.mark.parametrize(('measures', 'expected'), [
    ('all', loaders.available_demographics),
    (['diagnosis', 'date_birth'], ['diagnosis', 'date_birth'])
])
def test_load_demographics(studydata, measures, expected):
    out = loaders.load_demographics(studydata, measures=measures)
    if callable(expected):
        expected = expected(studydata)
    assert all(out.columns[:1] == ['participant'])
    assert all(out.columns[1:] == expected)
