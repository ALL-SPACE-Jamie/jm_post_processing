# -*- coding: utf-8 -*-
"""
Created on Wed May 20 2026.

@author: jmitchell

@desc: Convert combiner TLM measurements into TX-format calibration files
       and produce a per-PCS verification plot. For each beam the script:
         1. Aggregates the combiner gain across TLM x test (median per
            PCS x frequency).
         2. Computes the beam baseline B = mean of all combiner points.
         3. Computes per-PCS attenuation = (median - B) so positive values
            are points above the baseline (attenuate down to reach B) and
            negative values are points below (would need amplification).
         4. Frequency-shifts the curves by +3937.5 MHz and linearly
            interpolates onto the reference-rig grid.
         5. Writes a TX-format calibration CSV per beam, copying Kev's
            column-C values verbatim.
         6. Plots a 6-subplot verification figure per beam showing the
            file values vs the original combiner samples (with IQR error
            bars) and Kev's reference rig (unaltered, secondary y-axis).
       All shifts/baselines are derived from the combiner data only;
       Kev's data is never modified.
"""


import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def current_time_string() -> str:
    """Return a YYYYMMDD_HHMMSS timestamp for filenames."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def load_combiner_csv(path: str) -> pd.DataFrame:
    """
    Load the combiner measurement CSV.

    The combiner CSV has no header. Columns are:
    PCS, TLM, test, beam, freq (MHz), -, -, gain_b1, gain_b2.
    For beam 1 the gain lives in column 7; for beam 2 in column 8. The
    other column holds the -100.1 dB null marker.

    Parameters
    ----------
    path : str
        Full path to the combiner CSV.

    Returns
    -------
    pd.DataFrame
        Rows from the file with an added 'freq_GHz' column (freq / 1000)
        and a unified 'gain' column drawn from the correct beam column.
        Rows where gain is at the -100.1 null marker are filtered out.
    """
    cols = ['PCS', 'TLM', 'test', 'beam', 'freq', 'ran1', 'ran2',
            'gain_b1', 'gain_b2']
    df = pd.read_csv(path, header=None, names=cols)
    df['freq_GHz'] = df['freq'] / 1000.0
    df['gain'] = df.apply(
        lambda r: r['gain_b1'] if r['beam'] == 1 else r['gain_b2'], axis=1)
    df = df[df['gain'] > -99].reset_index(drop=True)
    return df


def parse_tx_format(path: str) -> tuple:
    """
    Parse a TX-format calibration CSV (combiner output or Kev's-rig file).

    Parameters
    ----------
    path : str
        Full path to a TX-format CSV.

    Returns
    -------
    tuple
        (freqs, gains, col_c) where:
          - freqs : list of N floats (one per frequency block).
          - gains : list of 6 lists, each length N, one per PCS (0..5).
          - col_c : list of N lists of 6 strings (column-C raw strings).
    """
    with open(path, 'r') as fh:
        lines = fh.readlines()

    # locate the frequency line and the start of data blocks
    freqs, data_start = [], None
    for i, line in enumerate(lines):
        if line.startswith('Frequency'):
            freqs = [float(p.strip()) for p in line.split(',')
                     if p.strip() and not p.startswith('Frequency')]
        if data_start is None and line.strip() == '' and freqs:
            data_start = i + 1

    # gather blocks (separated by blank lines)
    blocks, current = [], []
    for line in lines[data_start:]:
        if line.strip() == '':
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    # extract gain (col A) and col C for each PCS in each block
    gains = [[] for _ in range(6)]
    col_c = []
    for blk in blocks:
        row_c = []
        for pcs in range(6):
            parts = blk[pcs * 4].rstrip().split(',')
            gains[pcs].append(float(parts[0]))
            row_c.append(parts[2])
        col_c.append(row_c)

    return freqs, gains, col_c


def write_tx_format(path: str, freqs: list, gains: dict, col_c: list,
                    serial_number: int = 2000, beam_id: int = 2) -> None:
    """
    Write a TX-format calibration CSV.

    The format mirrors Kev's reference files: a small metadata block,
    followed by N frequency blocks of 24 lines each (6 PCS x 4 rows).
    Only the first row of each PCS holds the gain; the other 3 rows hold
    the zero-marker pattern.

    Parameters
    ----------
    path : str
        Output file path.
    freqs : list
        Frequency grid in GHz (N points).
    gains : dict
        Per-PCS gain arrays. Keys 1..6, each a sequence of length N.
    col_c : list
        N-element list of 6-element string lists (col-C raw strings).
    serial_number : int, optional
        Value to write to the 'Serial Number' metadata line. Default 2000.
    beam_id : int, optional
        Value to write to the 'Beam ID' metadata line. Default 2.

    Returns
    -------
    None
    """
    n_freqs = len(freqs)
    with open(path, 'w', newline='\n') as fh:
        # metadata block
        fh.write(f'Serial Number,{serial_number}\n')
        fh.write(f'Beam ID,{beam_id}\n')
        fh.write('RX/TX,TX\n')
        fh.write('\n')
        fh.write('Temperature (deg),35,\n')
        fh.write('Frequency (GHz),' +
                 ','.join(f'{f:.6f}' for f in freqs) + ',\n')
        fh.write('Channel #,0,1,2,3,4,5,\n')
        fh.write('TLM #,0,1,2,\n')
        fh.write('\n')

        # data blocks
        for fi in range(n_freqs):
            for pcs in range(1, 7):
                g = gains[pcs][fi]
                c = col_c[fi][pcs - 1]
                fh.write(f'{g:.6f},0.000000,{c},\n')
                fh.write('0.000000,0.000000,,\n')
                fh.write('0.000000,0.000000,,\n')
                fh.write('0.000000,0.000000,,\n')
            if fi < n_freqs - 1:
                fh.write('\n')


def build_attenuation_curves(df: pd.DataFrame, beam: int,
                             freq_shift_ghz: float,
                             target_grid: list) -> dict:
    """
    Compute per-PCS attenuation curves on a target frequency grid.

    Procedure
    ---------
        1. For each (PCS, freq) take the median across TLM x test runs.
        2. Compute B = mean of all combiner points for the beam.
        3. For each PCS, compute attenuation = median - B at the 8
           original combiner frequencies.
        4. Frequency-shift by freq_shift_ghz and linearly interpolate
           onto (target_grid - grid_step) so the resulting values land
           one grid step to the right when indexed at target_grid.

    Parameters
    ----------
    df : pd.DataFrame
        Combiner data as returned by load_combiner_csv.
    beam : int
        Beam number (1 or 2).
    freq_shift_ghz : float
        Frequency shift applied to the combiner sample points before
        interpolation (positive = shift right).
    target_grid : list
        Target frequency grid (GHz), N points.

    Returns
    -------
    dict
        {'B': float, 'curves': {pcs: np.ndarray of length N for pcs 1..6}}
    """
    med = (df[df['beam'] == beam]
             .groupby(['PCS', 'freq_GHz'])['gain'].median().reset_index())
    B = float(med['gain'].mean())

    curves = {}
    grid_step = target_grid[1] - target_grid[0]
    target_for_interp = [f - grid_step for f in target_grid]
    for pcs in range(1, 7):
        s = med[med['PCS'] == pcs].sort_values('freq_GHz')
        f_src = s['freq_GHz'].to_numpy() + freq_shift_ghz
        atten_src = s['gain'].to_numpy() - B
        curves[pcs] = np.interp(target_for_interp, f_src, atten_src)

    return {'B': B, 'curves': curves}


def plot_verification(df: pd.DataFrame, beam: int, freq_shift_ghz: float,
                      kev_path: str, file_path: str, output_dir: str,
                      terminal: str = '', save_fig: bool = True):
    """
    Plot a 6-subplot verification figure for one beam with 4 traces:

      1. Combiner data, raw and not interpolated: 8 points at the
         original combiner frequencies, no y-shift, with IQR error bars
         from TLM x test.
      2. Combiner data, y-shifted (by -B) and not interpolated: same 8
         points, plotted at the x-shifted frequencies to line up with
         Kev's grid, IQR error bars preserved.
      3. Combiner data, y-shifted and interpolated: N points read
         straight from the calibration CSV file_path.
      4. Kev's reference rig, plotted unaltered.

    All four traces share a single y-axis in absolute dB. The combiner
    y-shift uses combiner data only (B = mean of all combiner medians).

    Parameters
    ----------
    df : pd.DataFrame
        Combiner data as returned by load_combiner_csv.
    beam : int
        Beam number (1 or 2).
    freq_shift_ghz : float
        Frequency shift used when generating file_path.
    kev_path : str
        Path to Kev's reference rig CSV for this beam.
    file_path : str
        Path to the combiner-derived calibration CSV for this beam.
    output_dir : str
        Directory in which to save the figure.
    terminal : str, optional
        Terminal identifier (e.g. 'T14', 'T15') used in the suptitle and
        output filename. Default ''.
    save_fig : bool, optional
        If True, save the figure to output_dir. Default True.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure.
    """
    # parse the two TX-format files
    f_file, g_file, _ = parse_tx_format(file_path)
    f_kev, g_kev, _ = parse_tx_format(kev_path)

    # per-(beam, PCS, freq) stats for the raw / shifted-not-interp traces
    grp = (df[df['beam'] == beam]
             .groupby(['PCS', 'freq_GHz'])['gain']
             .agg(median='median',
                  q1=lambda s: s.quantile(0.25),
                  q3=lambda s: s.quantile(0.75)).reset_index())
    B = float(grp['median'].mean())

    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(15, 8),
                            sharex=True, sharey=True)

    for i, ax in enumerate(axs.flat):
        pcs = i + 1
        sub = grp[grp['PCS'] == pcs].sort_values('freq_GHz')
        f_native = sub['freq_GHz'].to_numpy()
        raw = sub['median'].to_numpy()
        lo = (raw - sub['q1'].to_numpy()).tolist()
        hi = (sub['q3'].to_numpy() - raw).tolist()

        # 1) raw, not interpolated, at original combiner frequencies
        ax.errorbar(f_native, raw, yerr=[lo, hi],
                    marker='s', markersize=6, linewidth=1, linestyle=':',
                    capsize=3, elinewidth=0.8, color='tab:orange',
                    label='Combiner raw, not interp')

        # 2) shifted by -B, not interpolated, at x-shifted frequencies
        ax.errorbar(f_native + freq_shift_ghz, raw - B, yerr=[lo, hi],
                    marker='D', markersize=5, linewidth=1, linestyle='--',
                    capsize=3, elinewidth=0.8, color='tab:red',
                    label=f'Combiner shifted (-{B:+.2f} dB), not interp')

        # 3) shifted and interpolated (the file values)
        ax.plot(f_file, g_file[i],
                marker='^', markersize=3, linewidth=1.2,
                color='tab:purple',
                label='Combiner shifted, interp (file)')

        # 4) Kev's reference rig, unaltered
        ax.plot(f_kev, g_kev[i],
                marker='o', markersize=3, linewidth=1.0,
                color='tab:blue', alpha=0.7,
                label="Kev's rig (unaltered)")

        ax.axhline(0, color='black', linewidth=0.5, alpha=0.4,
                   linestyle='--')

        ax.set_title(f'PCS {pcs} (Kev idx {i})')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc='best')

        if i % 3 == 0:
            ax.set_ylabel('Gain (dB)')

    for ax in axs[-1, :]:
        ax.set_xlabel('Frequency (GHz)')

    title_prefix = f'{terminal} ' if terminal else ''
    fig.suptitle(
        f'{title_prefix}beam {beam} - four-trace comparison (single y-axis)\n'
        f'Combiner y-shift = -B = {-B:+.3f} dB (combiner data only). '
        f'x-shift = +{freq_shift_ghz*1000:.1f} MHz. '
        f"Kev's data unaltered.",
        fontsize=10)
    fig.tight_layout()

    if save_fig is True:
        tag = f'{terminal}_' if terminal else ''
        out = os.path.join(
            output_dir,
            f'{current_time_string()}_{tag}Combiner_verify_beam{beam}.png')
        fig.savefig(out, dpi=150)

    return fig


# main function
if __name__ == '__main__':

    # ---- inputs ----
    TERMINAL = 'T15'
    COMBINER_FILE = r'C:\scratch\20260529\T15-KevsDataCorrupt\T-15_29052026_113328.csv'
    # COMBINER_FILE = r"C:\scratch\20260529\T14\T14_13052026_223001.csv"
    KEV_FILES = {
        1: r'C:\scratch\20260529\T15-KevsDataCorrupt\BF_DSP_SN2000_TX_B1.csv',
        2: r'C:\scratch\20260529\T15-KevsDataCorrupt\BF_DSP_SN2000_TX_B2.csv',
    }
    # KEV_FILES = {
    #     1: r'C:\scratch\20260529\T14\BF_DSP_SN2000_TX_B1.csv',
    #     2: r'C:\scratch\20260529\T14\BF_DSP_SN2000_TX_B2.csv',
    # }
    OUTPUT_DIR = r'C:\scratch\20260529'
    # OUTPUT_DIR = r'C:\scratch\20260529\T14'
    FREQ_SHIFT_GHZ = 3.9375
    SERIAL_NUMBER = 2000
    BEAM_ID_BY_BEAM = {1: 2, 2: 3}    # combiner beam -> Kev's internal Beam ID

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ---- load combiner data once ----
    df = load_combiner_csv(COMBINER_FILE)

    # ---- per beam: build attenuation, write CSV, produce verify plot ----
    for beam in [1, 2]:

        # use Kev's frequency grid and column-C verbatim
        kev_freqs, _, kev_col_c = parse_tx_format(KEV_FILES[beam])

        # build attenuation curves on Kev's grid
        result = build_attenuation_curves(df=df, beam=beam,
                                          freq_shift_ghz=FREQ_SHIFT_GHZ,
                                          target_grid=kev_freqs)
        B = result['B']
        gains = result['curves']

        # write the calibration CSV
        out_csv = os.path.join(OUTPUT_DIR,
                               f'{TERMINAL}_combiner_TX_B{beam}.csv')
        write_tx_format(path=out_csv, freqs=kev_freqs, gains=gains,
                        col_c=kev_col_c, serial_number=SERIAL_NUMBER,
                        beam_id=BEAM_ID_BY_BEAM[beam])
        print(f'beam {beam}: B = {B:+.3f} dB,  wrote {out_csv}')

        # verification plot
        plot_verification(df=df, beam=beam,
                          freq_shift_ghz=FREQ_SHIFT_GHZ,
                          kev_path=KEV_FILES[beam], file_path=out_csv,
                          output_dir=OUTPUT_DIR, terminal=TERMINAL,
                          save_fig=True)

    plt.show()
