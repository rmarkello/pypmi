__version__ = '0.0.1'

NAME = 'ppmi'
MAINTAINER = 'Ross Markello'
EMAIL = 'rossmarkello@gmail.com'
VERSION = __version__
LICENSE = 'BSD-3'
DESCRIPTION = """\
A toolbox for working with data from the Parkinson's Progression Markers \
Initiative (PPMI)
"""
LONG_DESCRIPTION = 'README.md'
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
URL = 'https://github.com/rmarkello/{name}'.format(name=NAME)
DOWNLOAD_URL = ('http://github.com/rmarkello/{name}/archive/{ver}.tar.gz'
                .format(name=NAME, ver=__version__))

INSTALL_REQUIRES = [
    'docker',
    'numpy',
    'pandas>=0.21.0'
    'scipy',
    'tqdm'
]

TESTS_REQUIRE = [
    'codecov',
    'pytest',
    'pytest-cov',
]

EXTRAS_REQUIRE = {
    'doc': [
        'sphinx>=1.2',
        'sphinx_rt_theme',
    ],
    'tests': TESTS_REQUIRE,
}

EXTRAS_REQUIRE['all'] = list(
    set([v for deps in EXTRAS_REQUIRE.values() for v in deps])
)

PACKAGE_DATA = {
    'ppmi': [
        'data/*'
    ]
}

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
