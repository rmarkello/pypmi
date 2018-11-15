# coding: utf-8

from functools import reduce
import itertools
import os.path as op
import pandas as pd
import numpy as np

RENAME_COLS = dict(PATNO='PARTICIPANT',
                   INFODT='VISIT_DATE',
                   EVENT_ID='VISIT')
RETAIN_COLS = ['PARTICIPANT', 'PAG_NAME', 'VISIT',
               'VISIT_DATE', 'TEST', 'SCORE']
EXTRA = ['PATNO', 'EVENT_ID', 'PAG_NAME', 'INFODT']
APPLYMAP = itertools.repeat(lambda x: x)
OPERATION = itertools.repeat(np.sum)

BEHAVIORAL_INFO = {
    'Benton': {
        'files': {
            'Benton_Judgment_of_Line_Orientation.csv': [
                [f'BJLOT{num}' for num in range(1, 31)]
            ]
        }
    },
    'EDUCYRS': {
        'files': {
            'Socio-Economics.csv': [
                ['EDUCYRS']
            ]
        },
        'applymap': [
            lambda x: 1.0 if x <= 12 else 0
        ]
    },
    'Epworth': {
        'files': {
            'Epworth_Sleepiness_Scale.csv': [
                ['ESS1', 'ESS2', 'ESS3', 'ESS4', 'ESS5', 'ESS6', 'ESS7',
                 'ESS8']
            ]
        }
    },
    'GDS': {
        'files': {
            'Geriatric_Depression_Scale__Short_.csv': [
                ['GDSSATIS', 'GDSGSPIR', 'GDSHAPPY', 'GDSALIVE', 'GDSENRGY'],
                ['GDSDROPD', 'GDSEMPTY', 'GDSBORED', 'GDSAFRAD', 'GDSHLPLS',
                 'GDSHOME', 'GDSMEMRY', 'GDSWRTLS', 'GDSHOPLS', 'GDSBETER']
            ],
        },
        'applymap': [
            lambda x: 1.0 if x == 0.0 else 0.0,
            lambda x: x
        ]
    },
    'HVLT Recall': {
        'files': {
            'Hopkins_Verbal_Learning_Test.csv': [
                ['HVLTRT1', 'HVLTRT2', 'HVLTRT3']
            ]
        }
    },
    'HVLT Recognition': {
        'files': {
            'Hopkins_Verbal_Learning_Test.csv': [
                ['HVLTREC'],
                ['HVLTFPRL'],
                ['HVLTFPUN']
            ]
        },
        'applymap': [
            lambda x: x,
            lambda x: -x,
            lambda x: -x
        ]
    },
    'HVLT Retention': {
        'files': {
            'Hopkins_Verbal_Learning_Test.csv': [
                ['HVLTRDLY'],
                ['HVLTRT2', 'HVLTRT3']
            ]
        },
        'applymap': [
            lambda x: x,
            lambda x: 1. / x if x != 0 else np.inf
        ],
        'operation': [
            np.sum, np.min
        ],
        'joinfunc': np.prod
    },
    'LNS': {
        'files': {
            'Letter_-_Number_Sequencing__PD_.csv': [
                ['LNS1A', 'LNS1B', 'LNS1C', 'LNS2A', 'LNS2B', 'LNS2C', 'LNS3A',
                 'LNS3B', 'LNS3C', 'LNS4A', 'LNS4B', 'LNS4C', 'LNS5A', 'LNS5B',
                 'LNS5C', 'LNS6A', 'LNS6B', 'LNS6C', 'LNS7A', 'LNS7B', 'LNS7C']
            ]
        }
    },
    'MOCA Unadjusted': {
        'files': {
            'Montreal_Cognitive_Assessment__MoCA_.csv': [
                ['MCAALTTM', 'MCACUBE', 'MCACLCKC', 'MCACLCKN', 'MCACLCKH',
                 'MCALION', 'MCARHINO', 'MCACAMEL', 'MCAFDS', 'MCABDS',
                 'MCAVIGIL', 'MCASER7', 'MCASNTNC', 'MCAVF', 'MCAABSTR',
                 'MCAREC1', 'MCAREC2', 'MCAREC3', 'MCAREC4', 'MCAREC5',
                 'MCADATE', 'MCAMONTH', 'MCAYR', 'MCADAY', 'MCAPLACE',
                 'MCACITY']
            ]
        }
    },
    'PIGD': {
        'files': {
            'MDS_UPDRS_Part_II__Patient_Questionnaire.csv': [
                ['NP2WALK', 'NP2FREZ']
            ],
            'MDS_UPDRS_Part_III.csv': [
                ['NP3GAIT', 'NP3FRZGT', 'NP3PSTBL']
            ]
        },
        'extra': [
            'PATNO', 'EVENT_ID', 'INFODT'
        ],
        'joinfunc': np.mean
    },
    'QUIP': {
        'files': {
            'QUIP_Current_Short.csv': [
                ['CNTRLGMB', 'TMGAMBLE'],
                ['CNTRLSEX', 'TMSEX'],
                ['CNTRLBUY', 'TMBUY'],
                ['CNTRLEAT', 'TMEAT'],
                ['TMTORACT', 'TMTMTACT', 'TMTRWD']
            ]
        },
        'operation': [
            np.any, np.any, np.any, np.any, np.sum
        ]
    },
    'RBD': {
        'files': {
            'REM_Sleep_Disorder_Questionnaire.csv': [
                ['DRMVIVID', 'DRMAGRAC', 'DRMNOCTB', 'SLPLMBMV', 'SLPINJUR',
                 'DRMVERBL', 'DRMFIGHT', 'DRMUMV', 'DRMOBJFL', 'MVAWAKEN',
                 'DRMREMEM', 'SLPDSTRB'],
                ['STROKE', 'HETRA', 'PARKISM', 'RLS', 'NARCLPSY', 'DEPRS',
                 'EPILEPSY', 'BRNINFM', 'CNSOTH']
            ]
        },
        'operation': [
            np.sum, np.any
        ]
    },
    'SCOPA AUT': {
        'files': {
            'SCOPA-AUT.csv': [
                [f'SCAU{num}' for num in range(1, 22)],
                ['SCAU22', 'SCAU23', 'SCAU24', 'SCAU25']
            ]
        },
        'applymap': [
            lambda x: 3.0 if x == 9.0 else x,
            lambda x: 0.0 if x == 9.0 else x
        ]
    },
    'SE ADL': {
        'files': {
            'Modified_Schwab_+_England_ADL.csv': [
                ['MSEADLG']
            ]
        }
    },
    'Semantic Fluency': {
        'files': {
            'Semantic_Fluency.csv': [
                ['VLTANIM', 'VLTVEG', 'VLTFRUIT']
            ]
        }
    },
    'STAI State': {
        'files': {
            'State-Trait_Anxiety_Inventory.csv': [
                ['STAIAD3', 'STAIAD4', 'STAIAD6', 'STAIAD7', 'STAIAD9',
                 'STAIAD12', 'STAIAD13', 'STAIAD14', 'STAIAD17', 'STAIAD18'],
                ['STAIAD1', 'STAIAD2', 'STAIAD5', 'STAIAD8', 'STAIAD10',
                 'STAIAD11', 'STAIAD15', 'STAIAD16', 'STAIAD19', 'STAIAD20']
            ]
        },
        'applymap': [
            lambda x: x,
            lambda x: 5 - x
        ]
    },
    'STAI Trait': {
        'files': {
            'State-Trait_Anxiety_Inventory.csv': [
                ['STAIAD22', 'STAIAD24', 'STAIAD25', 'STAIAD28', 'STAIAD29',
                 'STAIAD31', 'STAIAD32', 'STAIAD35', 'STAIAD37', 'STAIAD38',
                 'STAIAD40'],
                ['STAIAD21', 'STAIAD23', 'STAIAD26', 'STAIAD27', 'STAIAD30',
                 'STAIAD33', 'STAIAD34', 'STAIAD36', 'STAIAD39']
            ]
        },
        'applymap': [
            lambda x: x,
            lambda x: 5 - x
        ]
    },
    'Symbol Digit': {
        'files': {
            'Symbol_Digit_Modalities.csv': [
                ['SDMTOTAL']
            ]
        }
    },
    'Systolic BP Drop': {
        'files': {
            'Vital_Signs.csv': [
                ['SYSSUP'],
                ['SYSSTND']
            ]
        },
        'applymap': [
            lambda x: x,
            lambda x: -x
        ]
    },
    'Tremor': {
        'files': {
            'MDS_UPDRS_Part_II__Patient_Questionnaire.csv': [
                ['NP2TRMR']
            ],
            'MDS_UPDRS_Part_III.csv': [
                ['NP3PTRMR', 'NP3PTRML', 'NP3KTRMR', 'NP3KTRML', 'NP3RTARU',
                 'NP3RTALU', 'NP3RTARL', 'NP3RTALL', 'NP3RTALJ', 'NP3RTCON']
            ]
        },
        'extra': [
            'PATNO', 'EVENT_ID', 'INFODT'
        ],
        'joinfunc': np.nanmean
    },
    'UPDRS I': {
        'files': {
            'MDS_UPDRS_Part_I.csv': [
                ['NP1COG', 'NP1HALL', 'NP1DPRS', 'NP1ANXS', 'NP1APAT',
                 'NP1DDS']
            ],
            'MDS_UPDRS_Part_I__Patient_Questionnaire.csv': [
                ['NP1SLPN', 'NP1SLPD', 'NP1PAIN', 'NP1URIN', 'NP1CNST',
                 'NP1LTHD', 'NP1FATG']
            ]
        },
        'extra': [
            'PATNO', 'EVENT_ID', 'INFODT'
        ],
    },
    'UPDRS II': {
        'files': {
            'MDS_UPDRS_Part_II__Patient_Questionnaire.csv': [
                ['NP2SPCH', 'NP2SALV', 'NP2SWAL', 'NP2EAT', 'NP2DRES',
                 'NP2HYGN', 'NP2HWRT', 'NP2HOBB', 'NP2TURN', 'NP2TRMR',
                 'NP2RISE', 'NP2WALK', 'NP2FREZ']
            ]
        }
    },
    'UPDRS III': {
        'files': {
            'MDS_UPDRS_Part_III.csv': [
                ['NP3SPCH', 'NP3FACXP', 'NP3RIGN', 'NP3RIGRU', 'NP3RIGLU',
                 'PN3RIGRL', 'NP3RIGLL', 'NP3FTAPR', 'NP3FTAPL', 'NP3HMOVR',
                 'NP3HMOVL', 'NP3PRSPR', 'NP3PRSPL', 'NP3TTAPR', 'NP3TTAPL',
                 'NP3LGAGR', 'NP3LGAGL', 'NP3RISNG', 'NP3GAIT', 'NP3FRZGT',
                 'NP3PSTBL', 'NP3POSTR', 'NP3BRADY', 'NP3PTRMR', 'NP3PTRML',
                 'NP3KTRMR', 'NP3KTRML', 'NP3RTARU', 'NP3RTALU', 'NP3RTARL',
                 'NP3RTALL', 'NP3RTALJ', 'NP3RTCON']
            ]
        }
    },
    'UPDRS IV': {
        'files': {
            'MDS_UPDRS_Part_IV.csv': [
                ['NP4WDYSK', 'NP4DYSKI', 'NP4OFF', 'NP4FLCTI', 'NP4FLCTX',
                 'NP4DYSTN']
            ]
        }
    },
    'UPSIT': {
        'files': {
            'University_of_Pennsylvania_Smell_ID_Test.csv': [
                ['UPSITBK1', 'UPSITBK2', 'UPSITBK3', 'UPSITBK4']
            ]
        }
    }
}


def get_data(fpath):
    """
    Gets clinical-behavioral data for PPMI subjects

    Parameters
    ----------
    fpath : str
        Filepath to directory containing all behavioral files

    Returns
    -------
    df : pandas.DataFrame
        Tidy DataFrame with all clinical-behavioral assessments
    """

    df = pd.DataFrame()
    # iterate through all keys in dictionary
    for key in BEHAVIORAL_INFO.keys():
        cextra = BEHAVIORAL_INFO[key].get('extra', EXTRA)
        capply = BEHAVIORAL_INFO[key].get('applymap', APPLYMAP)
        copera = BEHAVIORAL_INFO[key].get('operation', OPERATION)

        temp_scores = []
        # go through relevant files and items for current key and grab scores
        for fname, items in BEHAVIORAL_INFO[key]['files'].items():
            # read in file
            data = pd.read_csv(op.join(fpath, fname))
            # iterate through items to be retrieved and apply operations
            for n, (it, ap, ope) in enumerate(zip(items, capply, copera)):
                score = ope(data[it].applymap(ap), axis=1)
                temp_scores.append(data[cextra].join(pd.Series(score, name=n)))

        # merge temp score DataFrames
        curr_df = reduce(lambda df1, df2: pd.merge(df1, df2, on=cextra),
                         temp_scores)
        # combine individual scores for key with joinfunc and add to extra info
        joinfunc = BEHAVIORAL_INFO[key].get('joinfunc', np.sum)
        score = pd.Series(joinfunc(curr_df.drop(cextra, axis=1), axis=1)
                          .astype('float'), name='SCORE')
        curr_df = curr_df[cextra].astype('str').join(score).assign(TEST=key)
        if 'PAG_NAME' not in curr_df.columns:
            curr_df['PAG_NAME'] = 'COMBO'
        # append resultant DataFrame to df
        df = df.append(curr_df, ignore_index=True, sort=True)

    # coerce infodt to datetime format
    df['INFODT'] = pd.to_datetime(df['INFODT'], format='%m/%Y')
    df = get_adj_moca(df).rename(columns=RENAME_COLS)[RETAIN_COLS]

    return df


def get_adj_moca(df):
    """
    Gets adjusted MOCA score from `df` (i.e., accounts for education)

    Adds 1 to unadjusted MOCA score if years of education is <=12 and
    unadjusted score is <30; otherwise, unadjusted MOCA is carried through.

    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame containing various behavioral metrics

    Returns
    -------
    data : pandas.DataFrame
        DataFrame with adjusted MOCA instead of unadjusted MOCA
    """

    moca = pd.merge(df.query('TEST == "MOCA Unadjusted" & SCORE < 30'),
                    df.query('TEST == "EDUCYRS"')[['PATNO', 'SCORE']],
                    on='PATNO')
    mocaadj = (moca.drop(['SCORE_x', 'SCORE_y'], axis=1)
                   .join(pd.Series(moca[['SCORE_x', 'SCORE_y']]
                                   .sum(axis=1), name='SCORE')))
    mocanoadj = df.query('TEST == "MOCA Unadjusted" & SCORE >= 30')
    mocaadj = mocaadj.append(mocanoadj, sort=True)
    mocaadj.TEST = 'MOCA'

    new_df = df.append(mocaadj, sort=True, ignore_index=True)
    to_drop = new_df.query('TEST == "EDUCYRS" | TEST == "MOCA Unadjusted"')
    data = new_df.drop(to_drop.index, axis=0)

    return data
