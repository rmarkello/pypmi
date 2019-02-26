# -*- coding: utf-8 -*-

import pytest

from pypmi.datasets import utils


def test_get_authentication():
    # confirm fetching from environment works
    try:
        assert utils._get_authentication() is not None
    except AssertionError:
        assert False

    # confirm providing only one input still fetches both (from environ)
    try:
        assert utils._get_authentication(user='user') != ('user', None)
        assert utils._get_authentication(password='pass') != (None, 'pass')
    except AssertionError:
        assert False

    # confirm giving both inputs simply returns inputs, as provided
    assert utils._get_authentication('user', 'pass') == ('user', 'pass')


def test_get_download_params():
    # confirm we can retrieve authorization key effectively
    params = utils._get_download_params()
    assert isinstance(params, dict)
    try:
        assert all(f in params.keys() for f in ['authKey', 'userId'])
    except AssertionError:
        assert False

    # confirm bad user/password returns NO authorization
    assert utils._get_download_params('baduser', 'badpass') is None


def test_available_studydata():
    # 113 datasets available, should get a list of them
    assert isinstance(utils.available_studydata(), list)
    assert len(utils.available_studydata()) == 113


@pytest.mark.parametrize(('datasets', 'expected'), [
    (['all'], 113),
    (['Code list', 'Clinical labs'], 2)
])
def test_download_studydata(studydata, datasets, expected):
    # ensure dataset download returns expected number of files
    out = utils.download_studydata(*datasets, path=studydata, verbose=False)
    assert len(out) == expected
