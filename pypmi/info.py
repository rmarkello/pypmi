# -*- coding: utf-8 -*-

__author__ = 'pypmi developers'
__copyright__ = 'Copyright 2018, pypmi developers'
__credits__ = ['Ross Markello']
__license__ = 'BSD-3'
__maintainer__ = 'Ross Markello'
__email__ = 'rossmarkello@gmail.com'
__status__ = 'Prototype'
__url__ = 'http://github.com/rmarkello/pypmi'
__packagename__ = 'pypmi'
__description__ = ('pypmi is a Python toolbox for working with data from the '
                   'Parkinson\'s Progression Markers Initiative (PPMI)')
__longdesc__ = 'README.md'
__longdesctype__ = 'text/markdown'


INSTALL_REQUIRES = [
    'numpy>=0.15',
    'pandas>=0.21',
    'requests',
    'scipy',
    'tqdm'
]

TESTS_REQUIRE = [
    'pytest>=3.6',
    'pytest-cov',
]

EXTRAS_REQUIRE = {
    'doc': [
        'sphinx>=1.2',
        'sphinx_rtd_theme',
    ],
    'bids': [
        'docker',
        'nibabel',
        'pybids>=0.9.3',
        'pydicom>=1.3.0',
    ],
    'tests': TESTS_REQUIRE,
}

EXTRAS_REQUIRE['all'] = list(
    set([v for deps in EXTRAS_REQUIRE.values() for v in deps])
)

PACKAGE_DATA = {
    'pypmi': [
        'data/*'
    ]
}

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
]
