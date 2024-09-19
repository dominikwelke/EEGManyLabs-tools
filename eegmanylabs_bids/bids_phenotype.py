"""
parser functions for various questionnaires
written for EEGManyLabs resting state spin-off

v.1.0 - 2024.01.17
    KSS, CES-D, BISBAS, EHI, BFI-S, PANAS-SF (state), STAI-T Y1 (state)/Y2 (trait),

written by
Dominik Welke
d.welke@leeds.ac.uk
https://github.com/dominikwelke
"""

import pandas as pd
import numpy as np

pheno_dtypes = {
    "bfi_s": {
        k: "Int64" for k in ["bfi_ext", "bfi_agr", "bfi_con", "bfi_neg", "bfi_ope"]
    },
    "bisbas": {
        k: "Int64" for k in ["bis", "bas_drive", "bas_funseek", "bas_rewardresponse"]
    },
    "ces": {"ces_d": "Int64"},
    "ehi": {},
    "kss": {"kss": "Int64"},
    "panas_state": {k: "Int64" for k in ["panas_s_PA", "panas_s_NA"]},
    "stai_t": {k: "Int64" for k in ["stai_t_state", "stai_t_trait"]},
}


# questionnaire parser defs
def parse_kss(data_in):
    """
    requires column named 'KSS'
    values in range [1,9] or nan
    """
    # check input
    assert "KSS" in data_in.keys()
    KSS_data = data_in["KSS"].apply(pd.to_numeric, errors="coerce")
    if not sum(KSS_data.isnull()) == len(KSS_data):
        assert KSS_data.min(axis=None, skipna=True) >= 1
        assert KSS_data.max(axis=None, skipna=True) <= 9

    # transcribe
    return KSS_data


def parse_cesd(data_in, skipna=False):
    """
    requires columns named 'CESD_[1-20]'
    values in range [0,3] or nan
    """
    # check input
    CES_keys = [f"CESD_{i}" for i in range(1, 21)]
    assert sum([k in data_in.keys() for k in CES_keys]) == 20
    CES_data = data_in[CES_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(CES_data.min(axis=None, skipna=True)):
        assert CES_data.min(axis=None, skipna=True) >= 0
        assert CES_data.max(axis=None, skipna=True) <= 3

    # transcribe
    CES = CES_data.sum(axis=1, skipna=skipna)
    return CES


def parse_bisbas(data_in, order=None, skipna=False):
    """
    requires columns named 'BISBAS_[1-24]'
    values in range [1,4] or nan
    """
    # check input
    BISBAS_keys = [f"BISBAS_{i}" for i in range(1, 25)]
    assert sum([k in data_in.keys() for k in BISBAS_keys]) == 24
    BISBAS_data = data_in[BISBAS_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(BISBAS_data.min(axis=None, skipna=True)):
        assert BISBAS_data.min(axis=None, skipna=True) >= 1
        assert BISBAS_data.max(axis=None, skipna=True) <= 4

    # transcribe
    # reverse code all but 2 items
    reverse_keys = [f"BISBAS_{i}" for i in range(1, 25) if i not in [2, 22]]
    BISBAS_data[reverse_keys] = BISBAS_data[reverse_keys] * -1 + 5

    # compute subscores
    if order == "general":
        # see https://scales.arabpsychology.com/s/behavioral-avoidance-inhibition-scales-bis-bas/
        BIS_keys = [f"BISBAS_{k}" for k in [2, 8, 13, 16, 19, 22, 24]]
        BAS_dri_keys = [f"BISBAS_{k}" for k in [3, 9, 12, 21]]
        BAS_fun_keys = [f"BISBAS_{k}" for k in [5, 10, 15, 20]]
        BAS_rew_keys = [f"BISBAS_{k}" for k in [4, 7, 14, 18, 23]]
        # filler_keys = [f"BISBAS_{k}" for k in [1, 6, 11, 17]]  # not needed
    elif order == "en-2":
        # see https://arc.psych.wisc.edu/self-report/behavioral-activation-and-behavioral-inhibition-scales-bai/
        BIS_keys = [f"BISBAS_{k}" for k in [1, 6, 10, 13, 15, 18, 20]]
        BAS_dri_keys = [f"BISBAS_{k}" for k in [4, 8, 12, 16]]
        BAS_fun_keys = [f"BISBAS_{k}" for k in [2, 7, 9, 17]]
        BAS_rew_keys = [f"BISBAS_{k}" for k in [3, 5, 11, 14, 19]]
        # filler_keys = [f"BISBAS_{k}" for k in [1, 6, 11, 17]]  # not needed

    else:
        raise NotImplementedError

    BISBAS = pd.DataFrame(
        {
            "bis": BISBAS_data[BIS_keys].sum(axis=1, skipna=skipna),
            "bas_drive": BISBAS_data[BAS_dri_keys].sum(axis=1, skipna=skipna),
            "bas_funseek": BISBAS_data[BAS_fun_keys].sum(axis=1, skipna=skipna),
            "bas_rewardresponse": BISBAS_data[BAS_rew_keys].sum(axis=1, skipna=skipna),
        }
    )

    return BISBAS


def parse_ehi(data_in, skipna=True):
    """
    requires columns named 'EHI_L_[1-10]' and 'EHI_R_[1-10]'
    data range [0-2] or nan
    """
    if not skipna:
        raise NotImplementedError("Handling NaN not yet implemented")

    # check input
    EHI_keys_left = [f"EHI_L_{i}" for i in range(1, 11)]
    EHI_keys_right = [f"EHI_R_{i}" for i in range(1, 11)]
    assert sum([k in data_in.keys() for k in EHI_keys_left]) == 10
    assert sum([k in data_in.keys() for k in EHI_keys_right]) == 10
    left = data_in[EHI_keys_left].apply(pd.to_numeric, errors="coerce")
    right = data_in[EHI_keys_right].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(left.min(axis=None, skipna=True)):
        assert left.min(axis=None, skipna=True) >= 0
        assert left.max(axis=None, skipna=True) <= 2
    if not np.isnan(right.min(axis=None, skipna=True)):
        assert right.min(axis=None, skipna=True) >= 0
        assert right.max(axis=None, skipna=True) <= 2

    # transcribe
    left = left.sum(axis=1, skipna=skipna)
    right = right.sum(axis=1, skipna=skipna)
    lq = (
        (right - left) / (right + left) * 100.0
    )  # laterality quotient, as determined by EHI
    handedness = lq.apply(
        lambda x: x if pd.isna(x) else "r" if x >= 40.0 else "l" if x <= -40.0 else "a"
    )

    EHI = pd.DataFrame({"EHI_handedness": handedness, "EHI_LQ": lq})

    return EHI


def parse_bfi_s15(data_in, order=None, skipna=False):
    """
    BFI-S 15 item version. 1-7 likert scale
    requires columns named 'BFI_[1-15]'
    data range [1-7] or nan
    """

    # check input
    BFI_keys = [f"BFI_{i}" for i in range(1, 16)]
    assert sum([k in data_in.keys() for k in BFI_keys]) == 15

    # transpose data if necessary
    t = 4  # transpose [1,7] to [-3, 3] range
    BFI_data = data_in[BFI_keys].apply(pd.to_numeric, errors="coerce") - t
    if not np.isnan(BFI_data.min(axis=None, skipna=True)):
        assert BFI_data.min(axis=None, skipna=True) >= -3
        assert BFI_data.max(axis=None, skipna=True) <= 3

    # transcribe
    if order == "":
        REV_keys = [f"BFI_{i}" for i in [1, 3, 7, 8, 10, 14]]
        EXT_keys = [f"BFI_{i}" for i in [1, 6, 11]]
        AGR_keys = [f"BFI_{i}" for i in [2, 7, 12]]
        CON_keys = [f"BFI_{i}" for i in [3, 8, 13]]
        NEG_keys = [f"BFI_{i}" for i in [4, 9, 14]]
        OPE_keys = [f"BFI_{i}" for i in [5, 10, 15]]
    elif order == "ger-1":
        # german version
        # see https://zis.gesis.org/skala/Schupp-Gerlitz-Big-Five-Inventory-SOEP-(BFI-S)#
        REV_keys = [f"BFI_{i}" for i in [3, 6, 8, 15]]
        EXT_keys = [f"BFI_{i}" for i in [2, 6, 9]]
        AGR_keys = [f"BFI_{i}" for i in [3, 7, 13]]
        CON_keys = [f"BFI_{i}" for i in [1, 8, 12]]
        NEG_keys = [f"BFI_{i}" for i in [5, 11, 15]]
        OPE_keys = [f"BFI_{i}" for i in [4, 10, 14]]
    elif order == "en-1":
        # english version
        # see https://www.oecd.org/skills/piaac/Annex-A-Measures-of-the-big-five-dimensions.pdf
        REV_keys = [f"BFI_{i}" for i in [3, 6, 10, 14]]
        EXT_keys = [f"BFI_{i}" for i in [4, 5, 6]]
        AGR_keys = [f"BFI_{i}" for i in [10, 11, 12]]
        CON_keys = [f"BFI_{i}" for i in [13, 14, 15]]
        NEG_keys = [f"BFI_{i}" for i in [1, 2, 3]]
        OPE_keys = [f"BFI_{i}" for i in [7, 8, 9]]
    else:
        raise NotImplementedError

    BFI_data.loc[:, REV_keys] *= -1
    BFI_data["bfi_ext"] = BFI_data.loc[:, EXT_keys].sum(axis=1, skipna=skipna)
    BFI_data["bfi_agr"] = BFI_data.loc[:, AGR_keys].sum(axis=1, skipna=skipna)
    BFI_data["bfi_con"] = BFI_data.loc[:, CON_keys].sum(axis=1, skipna=skipna)
    BFI_data["bfi_neg"] = BFI_data.loc[:, NEG_keys].sum(axis=1, skipna=skipna)
    BFI_data["bfi_ope"] = BFI_data.loc[:, OPE_keys].sum(axis=1, skipna=skipna)

    BFI = BFI_data[["bfi_ext", "bfi_agr", "bfi_con", "bfi_neg", "bfi_ope"]] + 3 * t
    return BFI


def parse_panas_state(data_in, order=None, skipna=False):
    """
    requires columns named 'PANAS_S_[1-20]'
    data range [1-5] or nan

    coding:
    items [1,3,5,9,10,12,14,16,17,19] to PA subscale
    items [2,4,6,7,8,11,13,15,18,20] to NA subscale
    """

    # check input
    panas_keys = [f"PANAS_S_{i}" for i in range(1, 21)]
    assert sum([k in data_in.keys() for k in panas_keys]) == 20
    PANAS_S_data = data_in[panas_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(PANAS_S_data.min(axis=None, skipna=True)):
        assert PANAS_S_data.min(axis=None, skipna=True) >= 1
        assert PANAS_S_data.max(axis=None, skipna=True) <= 5

    # transcribe
    if order == "en-1":
        # see https://ogg.osu.edu/media/documents/MB%20Stream/PANAS.pdf
        PA_keys = [f"PANAS_S_{i}" for i in [1, 3, 5, 9, 10, 12, 14, 16, 17, 19]]
        NA_keys = [f"PANAS_S_{i}" for i in [2, 4, 6, 7, 8, 11, 13, 15, 18, 20]]
    elif order == "ger-1":
        PA_keys = [f"PANAS_S_{i}" for i in [1, 3, 4, 6, 10, 11, 13, 15, 17, 18]]
        NA_keys = [f"PANAS_S_{i}" for i in [2, 5, 7, 8, 9, 12, 14, 16, 19, 20]]
    else:
        raise NotImplementedError

    PANAS_S_data["panas_s_PA"] = PANAS_S_data[PA_keys].sum(axis=1, skipna=skipna)
    PANAS_S_data["panas_s_NA"] = PANAS_S_data[NA_keys].sum(axis=1, skipna=skipna)

    PANAS_S = PANAS_S_data[["panas_s_NA", "panas_s_PA"]]
    return PANAS_S


def parse_stai_state(data_in, order=None, skipna=False):
    """
    requires columns named 'STAI_S_[1-20]'
    data range [1-4] or nan
    """
    # check input
    stai_keys = [f"STAI_S_{i}" for i in range(1, 21)]
    assert sum([k in data_in.keys() for k in stai_keys]) == 20
    STAI_S_data = data_in[stai_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(STAI_S_data.min(axis=None, skipna=True)):
        assert STAI_S_data.min(axis=None, skipna=True) >= 1
        assert STAI_S_data.max(axis=None, skipna=True) <= 4

    # transpose to mirrored
    t = 2.5
    STAI_S_data.loc[:, stai_keys] -= t

    # apply reverse coding
    if order == "ger-1":
        # verified for TUD/UHH
        REV_keys = [f"STAI_S_{i}" for i in [1, 2, 5, 8, 10, 11, 15, 16, 19, 20]]
    elif order == "en-1":
        # see https://arc.psych.wisc.edu/self-report/state-trait-anxiety-inventory-sta/
        REV_keys = [f"STAI_S_{i}" for i in [1, 2, 5, 8, 10, 11, 15, 16, 19, 20]]
    else:
        raise NotImplementedError
    STAI_S_data.loc[:, REV_keys] *= -1

    # transcribe
    STAI_S = STAI_S_data.sum(axis=1, skipna=skipna) + 20 * t

    return STAI_S


def parse_stai_trait(data_in, order=None, skipna=False):
    """
    requires columns named 'STAI_T_[1-20]'
    data range [1-4] or nan
    """
    # check input
    stai_keys = [f"STAI_T_{i}" for i in range(1, 21)]
    assert sum([k in data_in.keys() for k in stai_keys]) == 20
    STAI_T_data = data_in[stai_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(STAI_T_data.min(axis=None, skipna=True)):
        assert STAI_T_data.min(axis=None, skipna=True) >= 1
        assert STAI_T_data.max(axis=None, skipna=True) <= 4

    # transpose to mirrored
    t = 2.5
    STAI_T_data.loc[:, stai_keys] -= t

    # apply reverse coding
    if order == "ger-1":
        REV_keys = [f"STAI_T_{i}" for i in [1, 6, 7, 10, 13, 16, 19]]
    elif order == "en-1":
        # see https://arc.psych.wisc.edu/self-report/state-trait-anxiety-inventory-sta/
        REV_keys = [f"STAI_T_{i}" for i in [1, 3, 6, 7, 10, 13, 14, 16, 19]]
    else:
        raise NotImplementedError
    STAI_T_data.loc[:, REV_keys] *= -1

    # transcribe
    STAI_T = STAI_T_data.sum(axis=1, skipna=skipna) + 20 * t

    return STAI_T
