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


def parse_bisbas(data_in, skipna=False):
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
    BIS_keys = [f"BISBAS_{k}" for k in [2, 8, 13, 16, 19, 22, 24]]
    BAS_dri_keys = [f"BISBAS_{k}" for k in [3, 9, 12, 21]]
    BAS_fun_keys = [f"BISBAS_{k}" for k in [5, 10, 15, 20]]
    BAS_rew_keys = [f"BISBAS_{k}" for k in [4, 7, 14, 18, 23]]
    # filler_keys = [f"BISBAS_{k}" for k in [1, 6, 11, 17]]  # not needed
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


def parse_bfi_s(data_in, skipna=False):
    """
    requires columns named 'BFI_[1-15]'
    data range [1-7] or nan
    """
    if skipna:
        raise NotImplementedError("Ignoring NaN not yet implemented")

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
    BFI_data["bfi_ext"] = (
        -BFI_data["BFI_1"] + BFI_data["BFI_6"] + BFI_data["BFI_11"] + 3 * t
    )
    BFI_data["bfi_agr"] = (
        BFI_data["BFI_2"] - BFI_data["BFI_7"] + BFI_data["BFI_12"] + 3 * t
    )
    BFI_data["bfi_con"] = (
        -BFI_data["BFI_3"] - BFI_data["BFI_8"] + BFI_data["BFI_13"] + 3 * t
    )
    BFI_data["bfi_neg"] = (
        BFI_data["BFI_4"] + BFI_data["BFI_9"] - BFI_data["BFI_14"] + 3 * t
    )
    BFI_data["bfi_ope"] = (
        BFI_data["BFI_5"] - BFI_data["BFI_10"] + BFI_data["BFI_15"] + 3 * t
    )

    BFI = BFI_data[["bfi_ext", "bfi_agr", "bfi_con", "bfi_neg", "bfi_ope"]]
    return BFI


def parse_panas_state(data_in, skipna=False):
    """
    requires columns named 'PANAS_S_[1-20]'
    data range [1-5] or nan

    coding:
    items [1,3,5,9,10,12,14,16,17,19] to PA subscale
    items [2,4,6,7,8,11,13,15,18,20] to NA subscale
    """
    if skipna:
        raise NotImplementedError("Ignoring NaN not yet implemented")

    # check input
    panas_keys = [f"PANAS_S_{i}" for i in range(1, 21)]
    assert sum([k in data_in.keys() for k in panas_keys]) == 20
    PANAS_S_data = data_in[panas_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(PANAS_S_data.min(axis=None, skipna=True)):
        assert PANAS_S_data.min(axis=None, skipna=True) >= 1
        assert PANAS_S_data.max(axis=None, skipna=True) <= 5

    # transcribe
    PANAS_S_data["panas_s_PA"] = (
        PANAS_S_data["PANAS_S_1"]
        + PANAS_S_data["PANAS_S_3"]
        + PANAS_S_data["PANAS_S_5"]
        + PANAS_S_data["PANAS_S_9"]
        + PANAS_S_data["PANAS_S_10"]
        + PANAS_S_data["PANAS_S_12"]
        + PANAS_S_data["PANAS_S_14"]
        + PANAS_S_data["PANAS_S_16"]
        + PANAS_S_data["PANAS_S_17"]
        + PANAS_S_data["PANAS_S_19"]
    )

    PANAS_S_data["panas_s_NA"] = (
        PANAS_S_data["PANAS_S_2"]
        + PANAS_S_data["PANAS_S_4"]
        + PANAS_S_data["PANAS_S_6"]
        + PANAS_S_data["PANAS_S_7"]
        + PANAS_S_data["PANAS_S_8"]
        + PANAS_S_data["PANAS_S_11"]
        + PANAS_S_data["PANAS_S_13"]
        + PANAS_S_data["PANAS_S_15"]
        + PANAS_S_data["PANAS_S_18"]
        + PANAS_S_data["PANAS_S_20"]
    )

    PANAS_S = PANAS_S_data[["panas_s_NA", "panas_s_PA"]]
    return PANAS_S


def parse_stai_state(data_in, skipna=False):
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

    # transcribe
    STAI_S = STAI_S_data.sum(axis=1, skipna=skipna)

    return STAI_S


def parse_stai_trait(data_in, skipna=False):
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

    # transcribe
    STAI_T = STAI_T_data.sum(axis=1, skipna=skipna)

    return STAI_T
