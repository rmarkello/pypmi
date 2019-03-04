# -*- coding: utf-8 -*-
"""
Data structures specifying methods for creating or calculating behavioral and
demographic measures
"""

import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype as cdtype


BEHAVIORAL_INFO = {
    'benton': {
        'files': {
            'Benton_Judgment_of_Line_Orientation.csv': [
                [f'BJLOT{num}' for num in range(1, 31)]
            ]
        }
    },
    'education': {
        'files': {
            'Socio-Economics.csv': [
                ['EDUCYRS']
            ]
        },
        'applymap': [
            lambda x: 1.0 if x <= 12 else 0
        ]
    },
    'epworth': {
        'files': {
            'Epworth_Sleepiness_Scale.csv': [
                ['ESS1', 'ESS2', 'ESS3', 'ESS4', 'ESS5', 'ESS6', 'ESS7',
                 'ESS8']
            ]
        }
    },
    'gds': {
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
    'hvlt_recall': {
        'files': {
            'Hopkins_Verbal_Learning_Test.csv': [
                ['HVLTRT1', 'HVLTRT2', 'HVLTRT3']
            ]
        }
    },
    'hvlt_recognition': {
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
    'hvlt_retention': {
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
    'lns': {
        'files': {
            'Letter_-_Number_Sequencing__PD_.csv': [
                ['LNS1A', 'LNS1B', 'LNS1C', 'LNS2A', 'LNS2B', 'LNS2C', 'LNS3A',
                 'LNS3B', 'LNS3C', 'LNS4A', 'LNS4B', 'LNS4C', 'LNS5A', 'LNS5B',
                 'LNS5C', 'LNS6A', 'LNS6B', 'LNS6C', 'LNS7A', 'LNS7B', 'LNS7C']
            ]
        }
    },
    'moca': {
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
    'pigd': {
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
    'quip': {
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
    'rbd': {
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
    'scopa_aut': {
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
    'se_adl': {
        'files': {
            'Modified_Schwab_+_England_ADL.csv': [
                ['MSEADLG']
            ]
        }
    },
    'semantic_fluency': {
        'files': {
            'Semantic_Fluency.csv': [
                ['VLTANIM', 'VLTVEG', 'VLTFRUIT']
            ]
        }
    },
    'stai_state': {
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
    'stai_trait': {
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
    'symbol_digit': {
        'files': {
            'Symbol_Digit_Modalities.csv': [
                ['SDMTOTAL']
            ]
        }
    },
    'systolic_bp_drop': {
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
    'tremor': {
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
    'updrs_i': {
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
    'updrs_ii': {
        'files': {
            'MDS_UPDRS_Part_II__Patient_Questionnaire.csv': [
                ['NP2SPCH', 'NP2SALV', 'NP2SWAL', 'NP2EAT', 'NP2DRES',
                 'NP2HYGN', 'NP2HWRT', 'NP2HOBB', 'NP2TURN', 'NP2TRMR',
                 'NP2RISE', 'NP2WALK', 'NP2FREZ']
            ]
        }
    },
    'updrs_iii': {
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
    'updrs_iv': {
        'files': {
            'MDS_UPDRS_Part_IV.csv': [
                ['NP4WDYSK', 'NP4DYSKI', 'NP4OFF', 'NP4FLCTI', 'NP4FLCTX',
                 'NP4DYSTN']
            ]
        }
    },
    'upsit': {
        'files': {
            'University_of_Pennsylvania_Smell_ID_Test.csv': [
                ['UPSITBK1', 'UPSITBK2', 'UPSITBK3', 'UPSITBK4']
            ]
        }
    }
}

DEMOGRAPHIC_INFO = {
    'diagnosis': {
        'files': {
            'Patient_Status.csv': 'ENROLL_CAT'
        },
        'replace': {
            'input': {
                'PD': 'pd',
                'HC': 'hc',
                'SWEDD': 'swedd',
                'PRODROMA': 'prod',
                'GENPD': 'genpd',
                'GENUN': 'genun',
                'REGPD': 'regpd',
                'REGUN': 'regun'
            }
        },
        'astype': {
            'input': 'category'
        }
    },
    'date_birth': {
        'files': {
            'Randomization_table.csv': 'BIRTHDT'
        },
        'apply': {
            'input': pd.to_datetime
        }
    },
    'date_diagnosis': {
        'files': {
            'PD_Features.csv': 'PDDXDT'
        },
        'apply': {
            'input': pd.to_datetime
        }
    },
    'date_enroll': {
        'files': {
            'Randomization_table.csv': 'ENROLLDT'
        },
        'apply': {
            'input': pd.to_datetime
        }
    },
    'status': {
        'files': {
            'Patient_Status.csv': 'ENROLL_STATUS'
        },
        'apply': {
            'input': lambda x: x.lower()
        }
    },
    'family_history': {
        'files': {
            'Family_History__PD_.csv': [
                'BIOMOMPD',
                'BIODADPD',
                'FULSIBPD',
                'HAFSIBPD',
                'MAGPARPD',
                'PAGPARPD',
                'MATAUPD',
                'PATAUPD',
                'KIDSPD'
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
        }
    },
    'age': {
        'files': {
            'Randomization_table.csv': [
                'BIRTHDT',
                'ENROLLDT'
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
    'gender': {
        'files': {
            'Randomization_table.csv': 'GENDER'
        },
        'replace': {
            'input': {
                0: 'f',
                1: 'f',
                2: 'm',
                np.nan: 'ns'
            }
        },
        'astype': {
            'input': 'category'
        }
    },
    'race': {
        'files': {
            'Screening___Demographics.csv': [
                'RAINDALS',
                'RAASIAN',
                'RABLACK',
                'RAHAWOPI',
                'RAWHITE',
                'RANOS'
            ]
        },
        'apply': {
            'input': np.where,
            'kwargs': {'axis': 1}
        },
        'transform': {
            'input': lambda x: x[0][0] if len(x[0]) == 1 else 'multi'
        },
        'replace': {
            'input': {
                0: 'indals',
                1: 'asian',
                2: 'black',
                3: 'hawopi',
                4: 'white',
                5: 'ns'
            }
        },
        'astype': {
            'input': 'category'
        }
    },
    'site': {
        'files': {
            'Center-Subject_List.csv': 'CNO'
        }
    },
    'handedness': {
        'files': {
            'Socio-Economics.csv': 'HANDED'
        },
        'replace': {
            'input': {
                1: 'right',
                2: 'left',
                3: 'both'
            }
        },
        'astype': {
            'input': 'category'
        }
    },
    'education': {
        'files': {
            'Socio-Economics.csv': 'EDUCYRS'
        }
    },
}


VISITS = cdtype([
    'SC',
    'RS1',
    'BL',
    'V01',
    'V02',
    'T06',
    'V03',
    'V04',
    'T12',
    'T15',
    'T17',
    'V05',
    'T18',
    'T19',
    'T21',
    'V06',
    'T24',
    'T27',
    'V07',
    'T30',
    'T33',
    'V08',
    'T36',
    'T39',
    'V09',
    'T42',
    'T45',
    'V10',
    'T48',
    'T51',
    'V11',
    'T54',
    'T57',
    'V12',
    'T60',
    'V13',
    'T72',
    'P78',
    'V14',
    'T84',
    'P90',
    'V15',
    'T96',
    'P102',
    'V16',
    'T108',
    'P114',
    'V17',
    'P126',
    'V18',
    'T132',
    'P138',
    'V19',
    'P150',
    'V20',
    'T156',
    'U01',
    'U02',
    'U03',
    'U04',
    'U05',
    'U06',
], ordered=True)
