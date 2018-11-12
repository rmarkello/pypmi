# -*- coding: utf-8 -*-

import re
import pandas as pd


def get_data(fname, gene_list=None):
    """
    Loads PPMI genotyping data stored at `fname`

    Parameters
    ----------
    fname : str
        Filepath to genotyping PLINK files
    gene_list : str, optional
        Path to pandas-compatible csv with at least 'snp', 'target', and
        'odds_ratio' columns denoting rs#, target (effect) allele, and odds
        ratio of target allele in population.

    Returns
    -------
    data : (N, G) pandas.DataFrame
        Wide-format genetics data where `N` is participants and `G` is SNPs
    info : (G, 5) pandas.DataFrame
        Information on SNPs in `data`, including 'odds_ratio' for genetic
        risk score calculation
    """

    try:
        from pandas_plink import read_plink
    except ImportError:
        raise ImportError('Loading genotyping data requires installing the '
                          '`pandas_plink` module. Please install that and try '
                          'again.')

    # make helper function for extracting SNP rs# from PLINK files
    def extract(x):
        try:
            return re.findall('[-_]*(rs[0-9]+)[-_]*', x)[0]
        except IndexError:
            return None

    # load PLINK data
    bim, fam, gen = read_plink(fname, verbose=False)
    participant_id = pd.Series(fam.fid.get_values(), name='PARTICIPANT')
    cols = ['snp', 'a0', 'a1']

    if gene_list is not None:
        # load gene list
        gene_info = pd.read_csv(gene_list).drop_duplicates(subset=['snp'])

        # check where SNPs match desired gene list & subset data
        inds = bim.snp.apply(extract).isin(gene_info.snp.dropna()).get_values()
        bim, gen = bim[inds], gen[inds]

        # clean up ugly bim.snp names with just rs# of SNPs
        bim.loc[:, 'snp'] = bim.snp.map({f: extract(f) for f in bim.snp})

        # get allele info for making sense of the data
        cols += ['target', 'odds_ratio', 'study']
        info = pd.merge(bim, gene_info, on='snp')[cols]

        # if a0/a1 alleles don't match target, confusion ensues
        # drop the non-matched ones and then grab SNPs that need to be reversed
        info = info[~((info.a0 != info.target) & (info.a1 != info.target))]
        flip = info[info.a1 != info.target].snp
        info = info[['snp', 'odds_ratio', 'study']]
    else:
        # placeholders so below code doesn't fail
        info = bim[cols]
        flip = pd.Series([], name='snp')

    # make wide-format participant x SNP dataframe
    data = pd.DataFrame(gen.compute().T, index=participant_id, columns=bim.snp)
    # if multiple columns represent same snp, combine them
    # THEY SHOULD ALL BE THE SAME -- if they aren't, that's bad...
    data = (data.dropna(axis=1, thresh=1)
                .groupby(level=0, axis=1)
                .mean()
                .dropna(axis=0)
                .astype(int)
                .sort_index())
    # flip reverse-coded SNPs
    data[flip] = data[flip].applymap(lambda x: {0: 2, 1: 1, 2: 0}.get(x))

    # retain only relevant SNPs in allele
    info = info[info.snp.isin(data.columns)]
    info = info.drop_duplicates(subset=['snp']).reset_index(drop=True)

    # return sorted data and info
    return data[info.snp], info
