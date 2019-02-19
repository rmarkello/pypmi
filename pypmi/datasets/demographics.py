# coding: utf-8

import os.path as op
import pandas as pd
import numpy as np

RENAME_COLS = dict(
    PATNO='PARTICIPANT', INFODT='VISIT_DATE', EVENT_ID='VISIT'
)

DEMOGRAPHIC_INFO = {
    'DIAGNOSIS': {
        'files': {
            'Screening___Demographics.csv': 'APPRDX'
        },
        'replace': {
            'input': {
                1: 'PD', 2: 'HC', 3: 'SWEDD', 4: 'PROD', 5: 'GC_PD',
                6: 'GC_HC', 7: 'GR_PD', 8: 'GR_HC'
            }
        }
    },
    'BIRTH_DATE': {
        'files': {
            'Randomization_table.csv': 'BIRTHDT'
        },
        'apply': {
            'input': pd.to_datetime
        }
    },
    'DIAGNOSIS_DATE': {
        'files': {
            'PD_Features.csv': 'PDDXDT'
        },
        'apply': {
            'input': pd.to_datetime
        }
    },
    'ENROLL_DATE': {
        'files': {
            'Randomization_table.csv': 'ENROLLDT'
        },
        'apply': {
            'input': pd.to_datetime
        }
    },
    'FAMILY_HISTORY': {
        'files': {
            'Family_History__PD_.csv': [
                'BIOMOMPD', 'BIODADPD', 'FULSIBPD', 'HAFSIBPD', 'MAGPARPD',
                'PAGPARPD', 'MATAUPD', 'PATAUPD', 'KIDSPD'
            ]
        },
        'apply': {
            'input': np.nansum,
            'kwargs': {
                'axis': 1
            }
        },
        'astype': {
            'input': 'bool'
        },
        'replace': {
            'input': {
                True: 1, False: 0
            }
        }
    },
    'AGE': {
        'files': {
            'Randomization_table.csv': [
                'BIRTHDT', 'ENROLLDT'
            ]
        },
        'apply': {
            'input': pd.to_datetime
        },
        'diff': {
            'input': 1,
            'kwargs': {
                'axis': 1
            }
        },
        'get': {
            'input': 'ENROLLDT'
        },
        'divide': {
            'input': np.timedelta64(1, 'Y')
        }
    },
    'GENDER': {
        'files': {
            'Randomization_table.csv': 'GENDER'
        },
        'replace': {
            'input': {
                0: 'F', 1: 'F', 2: 'M', np.nan: 'NS'
            }
        }
    },
    'RACE': {
        'files': {
            'Screening___Demographics.csv': [
                'RAINDALS', 'RAASIAN', 'RABLACK', 'RAHAWOPI', 'RAWHITE',
                'RANOS'
            ]
        },
        'apply': {
            'input': np.where,
            'kwargs': {'axis': 1}
        },
        'transform': {
            'input': lambda x: x[0][0] if len(x[0]) == 1 else 'MULTI'
        },
        'replace': {
            'input': {
                0: 'INDALS', 1: 'ASIAN', 2: 'BLACK', 3: 'HAWOPI', 4: 'WHITE',
                5: 'NOTSPECIFIED'
            }
        }
    },
    'SITE': {
        'files': {
            'Center-Subject_List.csv': 'CNO'
        }
    },
    'HANDEDNESS': {
        'files': {
            'Socio-Economics.csv': 'HANDED'
        },
        'replace': {
            'input': {
                1: 'RIGHT', 2: 'LEFT', 3: 'BOTH'
            }
        }
    },
    'EDUCATION': {
        'files': {
            'Socio-Economics.csv': 'EDUCYRS'
        }
    },
}


def get_data(fpath):
    """
    Gets demographic data for PPMI subjects

    Parameters
    ----------
    fpath : str
        Filepath to directory containing all demographic files

    Returns
    -------
    df : pandas.core.frame.DataFrame
        Tidy DataFrame with demographic information
    """

    # empty data frame to hold information
    df = pd.DataFrame([], columns=['PATNO'])

    # iterate through demographic info to get
    for key in DEMOGRAPHIC_INFO.keys():
        curr_key = DEMOGRAPHIC_INFO[key]
        for n, (fname, items) in enumerate(curr_key['files'].items()):
            data = pd.read_csv(op.join(fpath, fname))
            curr_score = data[items]
            for attr in [f for f in curr_key.keys() if f not in ['files']]:
                if hasattr(curr_score, attr):
                    fnc = getattr(curr_score, attr)
                    curr_score = fnc(curr_key[attr].get('input', None),
                                     **curr_key[attr].get('kwargs', {}))
            curr_score = pd.Series(curr_score, name=key)
            temp_scores = data[['PATNO']].astype('str').join(curr_score)
        df = pd.merge(df, temp_scores, on='PATNO', how='outer')

    # rename columns
    df = df.rename(columns=RENAME_COLS)

    # for some reason there are duplicate participant entries here????
    return df.drop_duplicates(subset=['PARTICIPANT'])
