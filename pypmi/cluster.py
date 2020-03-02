# -*- coding: utf-8 -*-
"""
Various functions for working with PPMI data
"""

import numpy as np
import pandas as pd
import scipy.stats as sstats


def cluster_fereshtehnejad2017(data: pd.DataFrame) -> np.ndarray:
    """
    Clusters subjects in `data` according to criteria defined in [CL1]_

    Subjects will be grouped into one of three clusters: (1) mild motor-
    predominant, (2) intermediate, or (3) diffuse malignant. These groupings
    are determined based solely on raw clinical-behavioral `data`

    Parameters
    ----------
    data : pd.DataFrame
        Clinical-behavioral data for PPMI subjects as obtained from e.g.,
        :func:`pypmi.load_behavior()`

    Returns
    -------
    labels : numpy.ndarray
        Cluster labels for subjects in `data` where 1 indicates mild motor-
        predominant, 2 indicates intermediate, and 3 indiciates diffuse
        malignant subtype

    References
    ----------
    .. [CL1] Fereshtehnejad, S. M., Zeighami, Y., Dagher, A., & Postuma, R. B.
       (2017). Clinical criteria for subtyping Parkinson’s disease: biomarkers
       and longitudinal progression. Brain, 140, 1959-1976.
    """

    mot_measures = [
        ['updrs_ii', 'updrs_iii', 'pigd']
    ]
    cog_measures = [
        ['benton'],
        ['symbol_digit'],
        ['lns', 'semantic_fluency'],
        ['hvlt_recall', 'hvlt_recognition', 'hvlt_retention']
    ]
    rbd_measures = [
        ['rbd']
    ]
    dys_measures = [
        ['scopa_aut']
    ]

    def zavg(data, measures):
        data = [sstats.zscore(data[m], ddof=1).mean(axis=1) for m in measures]
        return np.mean(data, axis=0)

    # load in raw behavioral scores and generate cutoffs
    threshold = sstats.norm.ppf(0.75)
    nonmotor = [
        # reverse threshold for cog: higher cog measures = better
        zavg(data, cog_measures) > -threshold,
        zavg(data, rbd_measures) < threshold,
        zavg(data, dys_measures) < threshold
    ]
    motor = zavg(data, mot_measures) < threshold

    # mild: ALL scores are below 75th %ile
    mild = np.all([motor] + nonmotor, axis=0)

    # severe: motor and 1+ non_motor > 75%ile or all non-motor > 75th %ile
    severe = np.logical_or(
        np.logical_and(~motor, np.any([~f for f in nonmotor], axis=0)),
        np.all([~f for f in nonmotor], axis=0)
    )

    # intermediate: neither mild nor severe
    intermediate = np.logical_not(np.logical_or(mild, severe))

    feresh_labels = np.sum([mild * 1, intermediate * 2, severe * 3], axis=0)

    return feresh_labels


def cluster_faghri2018(path: str = None) -> pd.DataFrame:
    """
    Generates cluster assignments for subjects as in [CL2]_

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None

    Returns
    -------
    labels : numpy.ndarray
        Cluster labels for subjects

    References
    ----------
    .. [CL2] Faghri, F., Hashemi, S. H., Leonard, H., Scholz, S. W., Campbell,
       R. H., Nalls, M. A., & Singleton, A. B. (2018). Predicting onset,
       progression, and clinical subtypes of Parkinson disease using machine
       learning. bioRxiv, 338913.
    """

    raise NotImplementedError
