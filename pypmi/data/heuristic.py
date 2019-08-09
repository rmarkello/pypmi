# -*- coding: utf-8 -*-
"""
This script serves as a heuristic for use with HeuDiConv in converting PPMI
data into BIDS format.
"""

import os
import logging

lgr = logging.getLogger(__name__)
scaninfo_suffix = '.json'

T1W_SERIES = [
    'MPRAGE 2 ADNI',
    'MPRAGE ADNI',
    'MPRAGE GRAPPA 2',
    'MPRAGE GRAPPA2',
    'MPRAGE GRAPPA2(adni)',
    'MPRAGE w/ GRAPPA',
    'MPRAGE_GRAPPA',
    'MPRAGE_GRAPPA_ADNI',
    'MPRAGE GRAPPA',
    'SAG T1 3D MPRAGE',
    'sag mprage',
    'MPRAGEadni',
    'MPRAGE GRAPPA_ND',
    '3D SAG',
    'MPRAGE T1 SAG',
    'MPRAGE SAG',
    'SAG T1 3DMPRAGE',
    'SAG T1 MPRAGE',
    'SAG 3D T1',
    'SAG MPRAGE GRAPPA2-NEW2016',
    'SAG MPRAGE GRAPPA_ND',
    'Sag MPRAGE GRAPPA',
    'AXIAL T1 3D MPRAGE',
    'SAG MPRAGE GRAPPA',
    'sT1W_3D_FFE',
    'sT1W_3D_ISO',
    'sT1W_3D_TFE',
    'sag 3D FSPGR BRAVO straight',
    'SAG T1 3D FSPGR',
    'SAG FSPGR 3D '
    'SAG 3D FSPGR BRAVO STRAIGHT',
    'SAG T1 3D FSPGR 3RD REPEAT',
    'SAG FSPGR BRAVO',
    'SAG SPGR 3D',
    'SAG 3D SPGR',
    'FSPGR 3D SAG',
    'SAG FSPGR 3D',
    'SAG 3D FSPGR BRAVO STRAIGHT',
    'SAG FSPGR 3D ',
    't1_mpr_ns_sag_p2_iso',
    'T1',
    'T1 Repeat',
    'AX T1',
    'axial spgr',
    'T1W_3D_FFE AX',
    # this might have a contrast but I literally can't find any info on it
    'AX T1 SE C+'
]

T2W_SERIES = [
    # single echo only
    't2_tse_tra',
    't2 cor',
    'T2 COR',
    'T2W_TSE',
    'AX T2',
    'AX T2 AC-PC LINE ENTIRE BRAIN',
    'AX T2 AC-PC line Entire Brain',
    'Ax T2 Fse thin ac-pc',
    # mixed single / dual-echo
    'AXIAL FSE T2 FS'
]

PD_SERIES = [
    'Ax T2* GRE'
]

PDT2_SERIES = [
    'AX DE TSE',
    'AX DUAL_TSE',
    'DUAL_TSE',
    'sT2W/PD_TSE',
    'Axial PD-T2-FS TSE',
    'Axial PD-T2 TSE',
    'Axial PD-T2 TSE FS',
    'AXIAL PD-T2 TSE FS',
    'AX PD + T2',
    'PD-T2 DUAL AXIAL TSE',
    'Axial PD-T2 TSE_AC/PC line',
    'Axial PD-T2 TSE_AC PC line',
    'Ax PD /T2',
    'AXIAL PD+T2 TSE',
    'AX T2 DE',
    't2 weighted double echo',
    'T2'
]

FLAIR_SERIES = [
    # FLAIR (no weighting specified)
    'FLAIR_LongTR AX',
    'FLAIR_LongTR SENSE',
    'AX FLAIR',
    'AXIAL FLAIR',
    'FLAIR_longTR',
    'FLAIR AXIAL',
    'ax flair',
    'Cor FLAIR TI_2800ms',
    'FLAIR',
    # T2 FLAIR
    'AX T2 FLAIR',
    'T2  AXIAL FLAIR',
    'Ax T2 FLAIR  ang to ac-pc',
    'T2W_FLAIR',
    'AX FLAIR T2',
    'AX T2 FLAIR 5/1',
    'Ax T2 FLAIR',
    't2_tirm_tra_dark-fluid_',
    't2_tirm_tra_dark-fluid NO BLADE',
    # T1 FLAIR -- should these be here?
    'Ax T1 FLAIR',
    'AX T1 FLAIR'
]

BOLD_SERIES = [
    'ep2d_RESTING_STATE',
    'ep2d_bold_rest'
]

DTI_SERIES = [
    'DTI_gated',
    'DTI_non_gated',
    'DTI_pulse gated_AC/PC line',
    'REPEAT_DTI_GATED',
    'DTI_NONGATED',
    'REPEAT_DTI_NONGATED',
    'TRIGGERED DTI',
    'DTI_NON gated',
    'DTI_ non_gated',
    'DTI_non gated Repeat',
    'DTI_NON-GATED',
    'REPEAT_DTI_NON-GATED',
    'DTI_none_gated',
    'DTI_non gated',
    'Repeat DTI_non gated',
    'REPEAT_NON_GATED',
    'DTI',
    'REPEAT_DTI_ NON GATED',
    'REPEAT_DTI_NON GATED',
    'DTI_NON GATED',
    'DTI Sequence',
    'DTI_ NON gated REPEAT',
    'DTI_ non gated',
    'DTI_GATED',
    'DTI_NON gated REPEAT',
    'DTI_NON_GATED',
    'DTI_Non Gated',
    'DTI_Non gated',
    'DTI_Non gated Repeat',
    'DTI_Non-gated',
    'DTI_UNgated',
    'DTI_UNgated#2',
    'DTI_gated AC-PC LINE',
    'DTI_gated#1',
    'DTI_gated#2',
    'DTI_gated_ADC',
    'DTI_gated_FA',
    'DTI_gated_TRACEW',
    'DTI_non gated repeat',
    'DTI_pulse gated_AC PC line',
    'DTI_ungated',
    'REPEAT DTI_NON GATED',
    'REPEAT DTI_NON gated',
    'REPEAT_NON DTI_GATED',
    'Repeat DTI Sequence'
]

T2W_PDT2_SERIES = [
    'Ax T2 FSE',        # only PD/T2                        (48-65 slices)
    '*AX FSE T2',       # mixed T2w and PD/T2               (24-64 slices)
    'AX T2 FSE',        # only T2w (one subject)            (24-24 slices)
    '*Ax T2 FSE',       # only T2w (one subject)            (22-22 slices)
    'AXIAL  T2  FSE',   # only T2w                          (23-26 slices)
]


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):
    """
    Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

    # {bids_subject_session_dir} : "sub-X/ses-Y"
    # {bids_subject_session_prefix} : "sub-X_ses-Y"
    t1w = create_key('{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_run-{item:02d}_T1w')  # noqa
    t1w_grappa = create_key('{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_acq-grappa2_run-{item:02d}_T1w')  # noqa
    t1w_adni = create_key('{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_acq-adni_run-{item:02d}_T1w')  # noqa
    t2w = create_key('{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_run-{item:02d}_T2w')  # noqa
    pd = create_key('{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_run-{item:02d}_PD')  # noqa
    pdt2 = create_key('{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_run-{item:02d}_PDT2')  # noqa
    flair = create_key('{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_run-{item:02d}_FLAIR')  # noqa
    bold = create_key('{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-rest_run-{item:02d}_bold')  # noqa
    dti = create_key('{bids_subject_session_dir}/dwi/{bids_subject_session_prefix}_run-{item:02d}_dwi')  # noqa

    info = {t1w: [], t1w_grappa: [], t1w_adni: [],
            t2w: [], pd: [], pdt2: [], flair: [], bold: [], dti: []}
    revlookup = {}

    for s in seqinfo:
        revlookup[s.series_id] = s.series_description

        # the straightforward scan series
        if s.series_description in T1W_SERIES:
            info[t1w].append(s.series_id)
        elif s.series_description in T2W_SERIES:
            info[t2w].append(s.series_id)
        elif s.series_description in PD_SERIES:
            info[pd].append(s.series_id)
        elif s.series_description in PDT2_SERIES:
            info[pdt2].append(s.series_id)
        elif s.series_description in FLAIR_SERIES:
            info[flair].append(s.series_id)
        elif s.series_description in BOLD_SERIES:
            info[bold].append(s.series_id)
        elif s.series_description in DTI_SERIES:
            info[dti].append(s.series_id)
        # the less straightforward (mixed) series
        elif s.series_description in T2W_PDT2_SERIES:
            if s.dim3 < 40:
                info[t2w].append(s.series_id)
            else:
                info[pdt2].append(s.series_id)
        # if we don't match _anything_ then we want to know!
        else:
            lgr.warning('Skipping unrecognized series description: {}'
                        .format(s.series_description))

    # if we have multiple t1w runs we want to add an "acq" tag to some of them
    if len(info[t1w]) > 1:
        # copy out t1w image series ids and reset info[t1w]
        all_t1w = info[t1w].copy()
        info[t1w] = []

        for series_id in all_t1w:
            series_description = revlookup[series_id].lower()
            if series_description in ['mprage_grappa', 'sag_mprage_grappa']:
                info[t1w].append(series_id)
            elif 'adni' in series_description:
                info[t1w_adni].append(series_id)
            else:
                info[t1w_grappa].append(series_id)

    return info


def custom_callable(*args):
    """
    Called at the end of `heudiconv.convert.convert()` to perform clean-up

    Checks to see if multiple "clean" output files were generated by
    ``heudiconv``. If so, assumes that this was because they had different echo
    times and tries to rename them and embed metadata from the relevant dicom
    files. This only needs to be done because the PPMI dicoms are a hot mess
    (cf. all the lists above with different series descriptions).
    """

    import glob
    import re
    import pydicom as dcm
    import nibabel as nib
    import numpy as np
    from heudiconv.cli.run import get_parser
    from heudiconv.dicoms import embed_metadata_from_dicoms
    from heudiconv.utils import (
        load_json,
        TempDirs,
        treat_infofile,
        set_readonly
    )

    # unpack inputs and get command line arguments (again)
    # there's gotta be a better way to do this, but c'est la vie
    prefix, outtypes, item_dicoms = args[:3]
    outtype = outtypes[0]
    opts = get_parser().parse_args()

    # if you don't want BIDS format then you're going to have to rename outputs
    # on your own!
    if not opts.bids:
        return

    # do a crappy job of checking if multiple output files were generated
    # if we're only seeing one file, we're good to go
    # otherwise, we need to do some fun re-naming...
    res_files = glob.glob(prefix + '[1-9].' + outtype)
    if len(res_files) < 2:
        return

    # there are few a sequences with some weird stuff that causes >2
    # files to be generated, some of which are two-dimensional (one slice)
    # we don't want that because that's nonsense, so let's design a check
    # for 2D files and just remove them
    for fname in res_files:
        if len([f for f in nib.load(fname).shape if f > 1]) < 3:
            os.remove(fname)
            os.remove(fname.replace(outtype, 'json'))
    res_files = [fname for fname in res_files if os.path.exists(fname)]
    bids_pairs = [(f, f.replace(outtype, 'json')) for f in res_files]

    # if there's only one file remaining don't add a needless 'echo' key
    # just rename the file and be done with it
    if len(bids_pairs) == 1:
        safe_movefile(bids_pairs[0][0], prefix + '.' + outtype)
        safe_movefile(bids_pairs[0][1], prefix + scaninfo_suffix)
        return

    # usually, at least two remaining files will exist
    # the main reason this happens with PPMI data is dual-echo sequences
    # look in the json files for EchoTime and generate a key based on that
    echonums = [load_json(json).get('EchoTime') for (_, json) in bids_pairs]
    if all([f is None for f in echonums]):
        return
    echonums = np.argsort(echonums) + 1

    for echo, (nifti, json) in zip(echonums, bids_pairs):
        # create new prefix with echo specifier
        # this isn't *technically* BIDS compliant, yet, but we're making due...
        split = re.search(r'run-(\d+)_', prefix).end()
        new_prefix = (prefix[:split]
                      + 'echo-%d_' % echo
                      + prefix[split:])
        outname, scaninfo = (new_prefix + '.' + outtype,
                             new_prefix + scaninfo_suffix)

        # safely move files to new name
        safe_movefile(nifti, outname, overwrite=False)
        safe_movefile(json, scaninfo, overwrite=False)

        # embed metadata from relevant dicoms (i.e., with same echo number)
        dicoms = [f for f in item_dicoms if
                  isclose(float(dcm.read_file(f, force=True).EchoTime) / 1000,
                          load_json(scaninfo).get('EchoTime'))]
        prov_file = prefix + '_prov.ttl' if opts.with_prov else None
        embed_metadata_from_dicoms(opts.bids, dicoms,
                                   outname, new_prefix + '.json',
                                   prov_file, scaninfo, TempDirs(),
                                   opts.with_prov, opts.minmeta)

        # perform the bits of heudiconv.convert.convert that were never called
        if scaninfo and os.path.exists(scaninfo):
            lgr.info("Post-treating %s file", scaninfo)
            treat_infofile(scaninfo)
        if outname and os.path.exists(outname):
            set_readonly(outname)

        # huzzah! great success if you've reached this point


def isclose(a, b, rel_tol=1e-06, abs_tol=0.0):
    """
    Determine whether two floating point numbers are close in value.

    Literally just math.isclose() from Python >3.5 as defined in PEP 485

    Parameters
    ----------
    a, b, : float
        Floats to compare
    rel_tol : float
       Maximum difference for being considered "close", relative to the
       magnitude of the input values
    abs_tol : float
       Maximum difference for being considered "close", regardless of the
       magnitude of the input values

    Returns
    -------
    bool
        True if `a` is close in value to `b`, and False otherwise.

    For the values to be considered close, the difference between them must be
    smaller than at least one of the tolerances.
    """

    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def safe_movefile(src, dest, overwrite=False):
    """
    Safely move `source` to `dest`, avoiding overwriting unless `overwrite`

    Uses `heudiconv.utils.safe_copyfile` before calling `os.remove` on `src`

    Parameters
    ----------
    src : str
        Path to source file; will be removed
    dest : str
        Path to dest file; should not exist
    overwrite : bool
        Whether to overwrite destination file, if it exists
    """

    from heudiconv.utils import safe_copyfile

    try:
        safe_copyfile(src, dest, overwrite)
        os.remove(src)
    except RuntimeError:
        lgr.warning('Tried moving %s to %s but %s ' % (src, dest, dest)
                    + 'already exists?! Check your outputs to make sure they '
                    + 'look okay...')
