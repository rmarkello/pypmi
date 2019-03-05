# -*- coding: utf-8 -*-

__all__ = [
    '__author__', '__description__', '__email__', '__license__',
    '__maintainer__', '__packagename__', '__url__', '__version__',
    'available_behavior', 'available_biospecimen',
    'available_datscan', 'available_demographics',
    'load_behavior', 'load_biospecimen',
    'load_datscan', 'load_demographics',
    'fetchable_studydata', 'fetchable_genetics',
    'fetch_studydata', 'fetch_genetics'
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .info import (
    __author__,
    __description__,
    __email__,
    __license__,
    __maintainer__,
    __packagename__,
    __url__,
)

from .fetchers import (fetchable_studydata, fetch_studydata,
                       fetchable_genetics, fetch_genetics)
from .loaders import (available_biospecimen, available_behavior,
                      available_datscan, available_demographics,
                      load_behavior, load_biospecimen,
                      load_datscan, load_demographics)
