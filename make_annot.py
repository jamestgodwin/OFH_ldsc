#!/usr/bin/env python
"""
make_annot.py -- pybedtools-free reimplementation.

Produces the same annot file output as the original LDSC make_annot.py,
using only pandas / numpy instead of pybedtools. Two behaviors from the
original are intentionally preserved for output-compatibility:

  1. The final merge that assigns ANNOT values to bim rows matches on BP
     only (not CHR + BP), matching the original script's behavior.
  2. With --nomerge, a SNP that overlaps multiple annotation intervals can
     produce duplicate rows in the intermediate hits table, exactly as the
     original bedtools-intersect-then-merge pipeline did.
"""
import pandas as pd
import numpy as np
import argparse
import gzip


def _chrom_from_gene(chrom):
    # Original: 'chr' + str(x).lstrip('chr')  -- strips a leading 'chr' if present
    return 'chr' + str(chrom).lstrip('chr')


def _chrom_from_bim(chrom):
    # Original: 'chr' + str(x)  -- always prefixes, no stripping
    return 'chr' + str(chrom)


def _sort_and_merge(chroms, starts, ends):
    """
    Equivalent to BedTool(...).sort().merge():
    sort by (chrom, start), then collapse overlapping/book-ended intervals
    within each chromosome. All inputs are 0-based, half-open.
    """
    order = np.lexsort((starts, chroms))
    chroms, starts, ends = chroms[order], starts[order], ends[order]

    m_chrom, m_start, m_end = [], [], []
    cur_c = cur_s = cur_e = None
    for c, s, e in zip(chroms, starts, ends):
        if cur_c is None:
            cur_c, cur_s, cur_e = c, s, e
        elif c == cur_c and s <= cur_e:
            if e > cur_e:
                cur_e = e
        else:
            m_chrom.append(cur_c); m_start.append(cur_s); m_end.append(cur_e)
            cur_c, cur_s, cur_e = c, s, e
    if cur_c is not None:
        m_chrom.append(cur_c); m_start.append(cur_s); m_end.append(cur_e)

    return (np.array(m_chrom), np.array(m_start), np.array(m_end))


def _sort_only(chroms, starts, ends):
    order = np.lexsort((starts, chroms))
    return chroms[order], starts[order], ends[order]


def gene_set_to_bed(args):
    print('making gene set bed file')
    GeneSet = pd.read_csv(args.gene_set_file, header=None, names=['GENE'])
    all_genes = pd.read_csv(args.gene_coord_file, sep='\s+')
    df = pd.merge(GeneSet, all_genes, on='GENE', how='inner')
    df['START'] = np.maximum(1, df['START'] - args.windowsize)
    df['END'] = df['END'] + args.windowsize

    chroms = np.array([_chrom_from_gene(c) for c in df['CHR']])
    starts0 = df['START'].to_numpy() - 1  # 1-based -> 0-based, as the original did
    ends = df['END'].to_numpy()

    return _sort_and_merge(chroms, starts0, ends)


def bed_from_file(path, merge):
    bed = pd.read_csv(path, sep='\s+', header=None, usecols=[0, 1, 2],
                       names=['CHR', 'START', 'END'])
    chroms = bed['CHR'].astype(str).to_numpy()
    starts = bed['START'].to_numpy()
    ends = bed['END'].to_numpy()
    if merge:
        return _sort_and_merge(chroms, starts, ends)
    return _sort_only(chroms, starts, ends)


def find_overlapping_bp(bim_chrom, bim_bp0, ann_chrom, ann_start, ann_end):
    """
    For each bim SNP (0-based position bim_bp0 on chromosome bim_chrom),
    find every annotation interval it overlaps. Returns a list of 1-based
    BP values -- one entry per overlap -- replicating what
    `bimbed.intersect(bed_for_annot)` followed by `[x.start + 1 for x in
    annotbed]` produced in the original. When ann_* has already been
    merged (the default), each SNP overlaps at most one interval; with
    --nomerge it can overlap several, so duplicate BPs can legitimately
    appear here.
    """
    hits = []
    for chrom in np.unique(bim_chrom):
        pts_mask = bim_chrom == chrom
        pts = bim_bp0[pts_mask]
        ann_mask = ann_chrom == chrom
        if not ann_mask.any() or pts.size == 0:
            continue
        starts = ann_start[ann_mask]
        ends = ann_end[ann_mask]
        # n_points x n_intervals overlap matrix (0-based half-open BED semantics)
        overlap = (pts[:, None] >= starts[None, :]) & (pts[:, None] < ends[None, :])
        rows, _ = np.where(overlap)
        hits.extend((pts[rows] + 1).tolist())  # back to 1-based BP
    return hits


def make_annot_files(args, bed_for_annot):
    print('making annot file')
    ann_chrom, ann_start, ann_end = bed_for_annot

    df_bim = pd.read_csv(args.bimfile, sep='\s+', usecols=[0, 1, 2, 3],
                          names=['CHR', 'SNP', 'CM', 'BP'])
    bim_chrom = np.array([_chrom_from_bim(c) for c in df_bim['CHR']])
    bim_bp0 = df_bim['BP'].to_numpy() - 1

    bp_hits = find_overlapping_bp(bim_chrom, bim_bp0, ann_chrom, ann_start, ann_end)

    df_int = pd.DataFrame({'BP': bp_hits, 'ANNOT': 1})
    df_annot = pd.merge(df_bim, df_int, how='left', on='BP')  # BP-only match, matches original
    df_annot.fillna(0, inplace=True)
    df_annot = df_annot[['ANNOT']].astype(int)

    if args.annot_file.endswith('.gz'):
        with gzip.open(args.annot_file, 'wt') as f:
            df_annot.to_csv(f, sep="\t", index=False)
    else:
        df_annot.to_csv(args.annot_file, sep="\t", index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gene-set-file', type=str, help='a file of gene names, one line per gene.')
    parser.add_argument('--gene-coord-file', type=str, default='ENSG_coord.txt',
                         help='a file with columns GENE, CHR, START, and END, where START and END '
                              'are base pair coordinates of TSS and TES. This file can contain more '
                              'genes than are in the gene set. We provide ENSG_coord.txt as a default.')
    parser.add_argument('--windowsize', type=int,
                         help='how many base pairs to add around the transcribed region to make the annotation?')
    parser.add_argument('--bed-file', type=str, help='the UCSC bed file with the regions that make up your annotation')
    parser.add_argument('--nomerge', action='store_true', default=False,
                         help="don't merge the bed file; make an annot file with values proportional "
                              "to the number of intervals in the bedfile overlapping the SNP.")
    parser.add_argument('--bimfile', type=str, help='plink bim file for the dataset you will use to compute LD scores.')
    parser.add_argument('--annot-file', type=str, help='the name of the annot file to output.')
    args = parser.parse_args()

    if args.gene_set_file is not None:
        bed_for_annot = gene_set_to_bed(args)
    else:
        bed_for_annot = bed_from_file(args.bed_file, merge=not args.nomerge)

    make_annot_files(args, bed_for_annot)
