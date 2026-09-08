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
    "bfi": {
        k: "Int64" for k in ["bfi_ext", "bfi_agr", "bfi_con", "bfi_neg", "bfi_ope"]
    },
    "bisbas": {
        k: "Int64" for k in ["bis", "bas_drive", "bas_funseek", "bas_rewardresponse"]
    },
    "ces": {"ces_d": "Int64"},
    "ehi": {},
    "kss": {"kss": "Int64"},
    "panas_state": {k: "Int64" for k in ["panas_s_PA", "panas_s_NA"]},
    "stai": {k: "Int64" for k in ["stai_state", "stai_trait"]},
}

pheno_jsons = {
    "EHI": {
        "participant_id": {"Description": "Unique participant identifier"},
        "ehi_handedness": {
            "LongName": "Edinburgh Handedness Inventory - Handedness",
            "Description": "Participant handedness as determined by Edinburgh Handedness Inventory (EHI; original 10 item version). See Oldfield (1971). The assessment and analysis of handedness: The Edinburgh inventory. Neuropsychologia 9(1):97-113",
            "Levels": {"l": "left", "r": "right", "a": "ambidextrous"},
        },
        "ehi_lq": {
            "LongName": "Edinburgh Handedness Inventory - Laterality quotient",
            "Description": "Laterality quotient as determined by Edinburgh Handedness Inventory (EHI; original 10 item version). See Oldfield (1971). The assessment and analysis of handedness: The Edinburgh inventory. Neuropsychologia 9(1):97-113",
        },
    },
    "BFI": {
        "participant_id": {"Description": "Unique participant identifier"},
        "bfi_ext": {
            "LongName": "Big Five Inventory (BFI) - Extraversion Domain Subscore",
            "Description": "can take values in range [3,21]. Collected using 15 item BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
            "Units": "none",
        },
        "bfi_agr": {
            "LongName": "Big Five Inventory (BFI) - Agreeableness Domain Subscore",
            "Description": "can take values in range [3,21]. Collected using 15 item BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
            "Units": "none",
        },
        "bfi_con": {
            "LongName": "Big Five Inventory (BFI) - Conscientiousness Domain Subscore",
            "Description": "can take values in range [3,21]. Collected using 15 item BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
            "Units": "none",
        },
        "bfi_neg": {
            "LongName": "Big Five Inventory (BFI) - Negative Emotionality Domain Subscore",
            "Description": "can take values in range [3,21]. Collected using 15 item BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
            "Units": "none",
        },
        "bfi_ope": {
            "LongName": "Big Five Inventory (BFI) - Open-Mindedness Domain Subscore",
            "Description": "can take values in range [3,21]. Collected using 15 item BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
            "Units": "none",
        },
    },
    "BISBAS": {
        "participant_id": {"Description": "Unique participant identifier"},
        "bis": {
            "LongName": "BIS/BAS scales - behavioral inhibition system (BIS) subscale",
            "Description": "can take values in range [7-28]. Collected using 24-item BIS/BAS version, see Carver and White (1994). Behavioral inhibition, behavioral activation, and affective responses to impending reward and punishment: The BIS/BAS scales. Journal of Personality and Social Psychology, 67, 319-333.",
        },
        "bas_drive": {
            "LongName": "BIS/BAS scales - behavioral approach system (BAS) Drive subscale",
            "Description": "can take values in range [4-16]. Collected using 24-item BIS/BAS version, see Carver and White (1994). Behavioral inhibition, behavioral activation, and affective responses to impending reward and punishment: The BIS/BAS scales. Journal of Personality and Social Psychology, 67, 319-333.",
        },
        "bas_funseek": {
            "LongName": "BIS/BAS scales - behavioral approach system (BAS) Fun Seeking subscale",
            "Description": "can take values in range [4-16]. Collected using 24-item BIS/BAS version, see Carver and White (1994). Behavioral inhibition, behavioral activation, and affective responses to impending reward and punishment: The BIS/BAS scales. Journal of Personality and Social Psychology, 67, 319-333.",
        },
        "bas_rewardresponse": {
            "LongName": "BIS/BAS scales - behavioral approach system (BAS) Reward Responsiveness subscale",
            "Description": "can take values in range [5-20]. Collected using 24-item BIS/BAS version, see Carver and White (1994). Behavioral inhibition, behavioral activation, and affective responses to impending reward and punishment: The BIS/BAS scales. Journal of Personality and Social Psychology, 67, 319-333.",
        },
    },
    "CES": {
        "participant_id": {"Description": "Unique participant identifier"},
        "ces_d": {
            "LongName": "Center for Epidemiologic Studies Depression Scale (CES-D)",
            "Description": "can take values in range [0,60]. Collected using CES-D Form, see Lewinsohn et al (1997). Center for Epidemiological Studies-Depression Scale (CES-D) as a screening instrument for depression among community-residing older adults. Psychology and Aging, 12, 277-287.",
            "Units": "none",
        },
    },
    "STAI_STATE": {
        "participant_id": {"Description": "Unique participant identifier"},
        "stai_state": {
            "LongName": "Stait-Trait Anxiety Inventory (STAI) - State Measure",
            "Description": "can take values in range [20,80]. Collected using STAI-Y Form, see Spielberger et al (1983). Manual for the State-Trait Anxiety Inventory. Palo Alto, CA: Consulting Psychologists Press.",
            "Units": "none",
        },
    },
    "STAI_TRAIT": {
        "participant_id": {"Description": "Unique participant identifier"},
        "stai_trait": {
            "LongName": "Stait-Trait Anxiety Inventory (STAI) - Trait Measure",
            "Description": "can take values in range [20,80]. Collected using STAI-Y Form, see Spielberger et al (1983). Manual for the State-Trait Anxiety Inventory. Palo Alto, CA: Consulting Psychologists Press.",
            "Units": "none",
        },
    },
    "PANAS_STATE": {
        "participant_id": {"Description": "Unique participant identifier"},
        "panas_s_NA": {
            "LongName": "Positive Negative Affect Schedule (PANAS) - State mood - Negative Affect Subscore",
            "Description": "can take values in range [6-30]. Collected using 20 item PANAS, see Watson et al (1988). Development and validation of brief measures of positive and negative affect: the PANAS scales. Journal of personality and social psychology, 54(6), 1063.",
            "Units": "none",
        },
        "panas_s_PA": {
            "LongName": "Positive Negative Affect Schedule (PANAS) - State mood - Positive Affect Subscore",
            "Description": "can take values in range [6-30]. Collected using 20 item PANAS, see Watson et al (1988). Development and validation of brief measures of positive and negative affect: the PANAS scales. Journal of personality and social psychology, 54(6), 1063.",
            "Units": "none",
        },
    },
    "KSS": {
        "participant_id": {"Description": "Unique participant identifier"},
        "kss": {
            "LongName": "Karolinska Sleepiness Scale (KSS)",
            "Description": "can take values in range [1-9]. see Akerstedt & Gillberg (1990). Subjective and objective sleepiness in the active individual. International Journal of Neuroscience, 52, 29–37.",
            "Levels": {
                "1": "extremely alert",
                "2": "very alert",
                "3": "alert",
                "4": "fairly alert",
                "5": "neither alert nor sleepy",
                "6": "some signs of sleepyness",
                "7": "sleepy, but no effort to keep awake",
                "8": "sleepy, some effort to keep awake",
                "9": "very sleepy, great effort to keep awake, fighting sleep",
            },
        },
    },
}


def _prep_df(df: pd.DataFrame):
    return df.rename(columns={k: k.upper() for k in df.columns})


# questionnaire parser defs
def parse_kss(data_in):
    """
    requires column named 'KSS'
    values in range [1,10] or nan
    """
    data_in = _prep_df(data_in)

    # check input
    assert "KSS" in data_in.keys()
    KSS_data = data_in["KSS"].apply(pd.to_numeric, errors="coerce")
    if not sum(KSS_data.isnull()) == len(KSS_data):
        assert KSS_data.min(axis=None, skipna=True) >= 1
        assert KSS_data.max(axis=None, skipna=True) <= 10

    # transcribe
    return KSS_data.astype("Int64")


def parse_cesd(data_in, skipna=False):
    """
    requires columns named 'CESD_[1-20]'
    values in range [0,3] or nan
    """
    data_in = _prep_df(data_in)

    # check input
    CES_keys = [f"CESD_{i}" for i in range(1, 21)]
    assert sum([k in data_in.keys() for k in CES_keys]) == 20
    CES_data = data_in[CES_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(CES_data.min(axis=None, skipna=True)):
        assert CES_data.min(axis=None, skipna=True) >= 0
        assert CES_data.max(axis=None, skipna=True) <= 3

    # transcribe
    CES = CES_data.sum(axis=1, skipna=skipna)
    return CES.astype("Int64")


def parse_bisbas(data_in, order=None, skipna=False):
    """
    requires columns named 'BISBAS_[1-24]'
    values in range [1,4] or nan
    """
    data_in = _prep_df(data_in)

    # check input
    BISBAS_keys = [f"BISBAS_{i}" for i in range(1, 25)]
    assert sum([k in data_in.keys() for k in BISBAS_keys]) == 24
    BISBAS_data = data_in[BISBAS_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(BISBAS_data.min(axis=None, skipna=True)):
        assert BISBAS_data.min(axis=None, skipna=True) >= 1
        assert BISBAS_data.max(axis=None, skipna=True) <= 4

    # transcribe

    # compute subscores
    if order == "general":
        # see https://scales.arabpsychology.com/s/behavioral-avoidance-inhibition-scales-bis-bas/
        BIS_keys = [f"BISBAS_{k}" for k in [2, 8, 13, 16, 19, 22, 24]]
        BAS_dri_keys = [f"BISBAS_{k}" for k in [3, 9, 12, 21]]
        BAS_fun_keys = [f"BISBAS_{k}" for k in [5, 10, 15, 20]]
        BAS_rew_keys = [f"BISBAS_{k}" for k in [4, 7, 14, 18, 23]]
        # filler_keys = [f"BISBAS_{k}" for k in [1, 6, 11, 17]]  # not needed
        reverse_keys = [f"BISBAS_{i}" for i in range(1, 25) if i not in [2, 22]]
    elif order == "general-noreverse":
        # as above but no reversed items (already done by UCM crew)
        BIS_keys = [f"BISBAS_{k}" for k in [2, 8, 13, 16, 19, 22, 24]]
        BAS_dri_keys = [f"BISBAS_{k}" for k in [3, 9, 12, 21]]
        BAS_fun_keys = [f"BISBAS_{k}" for k in [5, 10, 15, 20]]
        BAS_rew_keys = [f"BISBAS_{k}" for k in [4, 7, 14, 18, 23]]
        # filler_keys = [f"BISBAS_{k}" for k in [1, 6, 11, 17]]  # not needed
        reverse_keys = [f"BISBAS_{i}" for i in range(1, 25) if i in []]
    elif order == "en-2":
        # see https://arc.psych.wisc.edu/self-report/behavioral-activation-and-behavioral-inhibition-scales-bai/
        BIS_keys = [f"BISBAS_{k}" for k in [1, 6, 10, 13, 15, 18, 20]]
        BAS_dri_keys = [f"BISBAS_{k}" for k in [4, 8, 12, 16]]
        BAS_fun_keys = [f"BISBAS_{k}" for k in [2, 7, 9, 17]]
        BAS_rew_keys = [f"BISBAS_{k}" for k in [3, 5, 11, 14, 19]]
        # filler_keys = [f"BISBAS_{k}" for k in [1, 6, 11, 17]]  # not needed
        reverse_keys = [f"BISBAS_{i}" for i in range(1, 25) if i not in [2, 22]]

    else:
        raise NotImplementedError

    # reverse code all but 2 items
    BISBAS_data[reverse_keys] = BISBAS_data[reverse_keys] * -1 + 5

    BISBAS = pd.DataFrame(
        {
            "bis": BISBAS_data[BIS_keys].sum(axis=1, skipna=skipna),
            "bas_drive": BISBAS_data[BAS_dri_keys].sum(axis=1, skipna=skipna),
            "bas_funseek": BISBAS_data[BAS_fun_keys].sum(axis=1, skipna=skipna),
            "bas_rewardresponse": BISBAS_data[BAS_rew_keys].sum(axis=1, skipna=skipna),
        }
    )

    return BISBAS.astype("Int64")


def parse_ehi(data_in, skipna=True):
    """
    requires columns named 'EHI_L_[1-10]' and 'EHI_R_[1-10]'
    data range [0-2] or nan
    """
    if not skipna:
        raise NotImplementedError("Handling NaN not yet implemented")

    data_in = _prep_df(data_in)

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
    data_in = _prep_df(data_in)

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
    if order == "nl-1":
        # no internet source found, but checked in ERA
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
    elif order == "en-noreverse":
        # english version
        # see https://www.oecd.org/skills/piaac/Annex-A-Measures-of-the-big-five-dimensions.pdf
        REV_keys = [f"BFI_{i}" for i in []]
        EXT_keys = [f"BFI_{i}" for i in [4, 5, 6]]
        AGR_keys = [f"BFI_{i}" for i in [10, 11, 12]]
        CON_keys = [f"BFI_{i}" for i in [13, 14, 15]]
        NEG_keys = [f"BFI_{i}" for i in [1, 2, 3]]
        OPE_keys = [f"BFI_{i}" for i in [7, 8, 9]]
    elif order == "it-1":
        # italian version (from UNIMORE)
        # same as en-1
        REV_keys = [f"BFI_{i}" for i in [3, 6, 10, 14]]
        EXT_keys = [f"BFI_{i}" for i in [4, 5, 6]]
        AGR_keys = [f"BFI_{i}" for i in [10, 11, 12]]
        CON_keys = [f"BFI_{i}" for i in [13, 14, 15]]
        NEG_keys = [f"BFI_{i}" for i in [1, 2, 3]]
        OPE_keys = [f"BFI_{i}" for i in [7, 8, 9]]
    elif order == "fr-1":
        # italian version (from ONERA)
        # same as en-1
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
    return BFI.astype("Int64")


def parse_panas_state(data_in, order=None, skipna=False):
    """
    requires columns named 'PANAS_S_[1-20]'
    data range [1-5] or nan

    coding:
    items [1,3,5,9,10,12,14,16,17,19] to PA subscale
    items [2,4,6,7,8,11,13,15,18,20] to NA subscale
    """
    data_in = _prep_df(data_in)

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
    elif (
        order == "nl-ERA"
    ):  # this might not be the presentation order, but fits the data..
        PA_keys = [f"PANAS_S_{i}" for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
        NA_keys = [f"PANAS_S_{i}" for i in [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]]
    elif order == "it-1":
        # verfied at UNIMRE
        PA_keys = [f"PANAS_S_{i}" for i in [1, 3, 5, 9, 10, 12, 14, 16, 17, 19]]
        NA_keys = [f"PANAS_S_{i}" for i in [2, 4, 6, 7, 8, 11, 13, 15, 18, 20]]
    elif order == "fr-1":
        # verfied at ONERA
        PA_keys = [f"PANAS_S_{i}" for i in [1, 3, 5, 9, 10, 12, 14, 16, 17, 19]]
        NA_keys = [f"PANAS_S_{i}" for i in [2, 4, 6, 7, 8, 11, 13, 15, 18, 20]]
    else:
        raise NotImplementedError

    PANAS_S_data["panas_s_PA"] = PANAS_S_data[PA_keys].sum(axis=1, skipna=skipna)
    PANAS_S_data["panas_s_NA"] = PANAS_S_data[NA_keys].sum(axis=1, skipna=skipna)

    PANAS_S = PANAS_S_data[["panas_s_NA", "panas_s_PA"]]
    return PANAS_S.astype("Int64")


def parse_panas_trait(data_in, order=None, skipna=False):
    """
    requires columns named 'PANAS_T_[1-20]'
    data range [1-5] or nan

    coding:
    items [1,3,5,9,10,12,14,16,17,19] to PA subscale
    items [2,4,6,7,8,11,13,15,18,20] to NA subscale
    """
    data_in = _prep_df(data_in)

    # check input
    panas_keys = [f"PANAS_T_{i}" for i in range(1, 21)]
    assert sum([k in data_in.keys() for k in panas_keys]) == 20
    PANAS_T_data = data_in[panas_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(PANAS_T_data.min(axis=None, skipna=True)):
        assert PANAS_T_data.min(axis=None, skipna=True) >= 1
        assert PANAS_T_data.max(axis=None, skipna=True) <= 5

    # transcribe
    if order == "en-1":
        # see https://ogg.osu.edu/media/documents/MB%20Stream/PANAS.pdf
        PA_keys = [f"PANAS_T_{i}" for i in [1, 3, 5, 9, 10, 12, 14, 16, 17, 19]]
        NA_keys = [f"PANAS_T_{i}" for i in [2, 4, 6, 7, 8, 11, 13, 15, 18, 20]]
    else:
        raise NotImplementedError

    PANAS_T_data["panas_trait_pa"] = (
        PANAS_T_data[PA_keys].sum(axis=1, skipna=skipna).astype("Int64")
    )
    PANAS_T_data["panas_trait_na"] = (
        PANAS_T_data[NA_keys].sum(axis=1, skipna=skipna).astype("Int64")
    )

    PANAS_T = PANAS_T_data[["panas_trait_na", "panas_trait_pa"]]
    return PANAS_T.astype("Int64")


def parse_stai_state(data_in, order=None, skipna=False):
    """
    requires columns named 'STAI_S_[1-20]'
    data range [1-4] or nan
    """
    data_in = _prep_df(data_in)

    # check input
    stai_keys = [f"STAI_S_{i}" for i in range(1, 21)]
    assert sum([k in data_in.keys() for k in stai_keys]) == 20
    STAI_S_data = data_in[stai_keys].apply(pd.to_numeric, errors="coerce").astype(float)
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
    elif order == "noreverse":
        # already reversed by UCM crew
        REV_keys = [f"STAI_S_{i}" for i in []]
    elif order == "nl-1":
        # verified for ERA
        REV_keys = [f"STAI_S_{i}" for i in [1, 2, 5, 8, 10, 11, 15, 16, 19, 20]]
    elif order == "it-1":
        # verified for UNIMORE
        REV_keys = [f"STAI_S_{i}" for i in [1, 2, 5, 8, 10, 11, 15, 16, 19, 20]]
    elif order == "fr-1":
        # verified for ONERA
        REV_keys = [f"STAI_S_{i}" for i in [1, 2, 5, 8, 10, 11, 15, 16, 19, 20]]
    else:
        raise NotImplementedError
    STAI_S_data.loc[:, REV_keys] *= -1

    # transcribe
    STAI_S = STAI_S_data.sum(axis=1, skipna=skipna) + 20 * t

    return STAI_S.astype("Int64")


def parse_stai_trait(data_in, order=None, skipna=False):
    """
    requires columns named 'STAI_T_[1-20]'
    data range [1-4] or nan
    """
    data_in = _prep_df(data_in)

    # check input
    stai_keys = [f"STAI_T_{i}" for i in range(1, 21)]
    assert sum([k in data_in.keys() for k in stai_keys]) == 20
    STAI_T_data = data_in[stai_keys].apply(pd.to_numeric, errors="coerce").astype(float)
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
    elif order == "nl-1":
        # verified for ERA
        REV_keys = [f"STAI_T_{i}" for i in [1, 3, 7, 10, 13, 14, 15, 16, 19]]
    elif order == "noreverse":
        # already reversed by UCM crew
        REV_keys = [f"STAI_S_{i}" for i in []]
    elif order == "it-1":
        # verified for UNIMORE
        REV_keys = [f"STAI_T_{i}" for i in [1, 3, 6, 7, 10, 13, 14, 16, 19]]
    elif order == "fr-1":
        # verified for ONERA
        REV_keys = [f"STAI_T_{i}" for i in [1, 3, 6, 7, 10, 13, 14, 16, 19]]
    else:
        raise NotImplementedError
    STAI_T_data.loc[:, REV_keys] *= -1

    # transcribe
    STAI_T = STAI_T_data.sum(axis=1, skipna=skipna) + 20 * t

    return STAI_T


def parse_asrs(data_in, skipna=False):
    """
    requires columns named 'ASRS_[1-18]'
    data range [0-4] or nan

    coding:
    ASRS A: item [1-6]
    ASRS B: item [7-18]
    """
    data_in = _prep_df(data_in)

    # check input
    asrs_keys = [f"ASRS_{i}" for i in range(1, 19)]
    assert sum([k in data_in.keys() for k in asrs_keys]) == 18
    ASRS_data = data_in[asrs_keys].apply(pd.to_numeric, errors="coerce")
    if not np.isnan(ASRS_data.min(axis=None, skipna=True)):
        assert ASRS_data.min(axis=None, skipna=True) >= 0
        assert ASRS_data.max(axis=None, skipna=True) <= 4

    # transcribe
    A_keys = [f"ASRS_{i}" for i in range(1, 7)]
    B_keys = [f"ASRS_{i}" for i in range(7, 19)]
    cutoff_3 = [f"ASRS_{i}" for i in [1, 2, 3, 9, 12, 16, 18]]
    cutoff_4 = [f"ASRS_{i}" for i in [4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 17]]

    # updated scores
    ASRS_data["asrs_a_score"] = (
        ASRS_data[A_keys].sum(axis=1, skipna=skipna).astype("Int64")
    )
    ASRS_data["asrs_b_score"] = (
        ASRS_data[B_keys].sum(axis=1, skipna=skipna).astype("Int64")
    )

    ASRS_data["asrs"] = [
        "low negative"
        if 0 <= s <= 9
        else "high negative"
        if 10 <= s <= 13
        else "low positive"
        if 14 <= s <= 17
        else "high positive"
        if 18 <= s <= 24
        else pd.NA
        for s in ASRS_data["asrs_a_score"]
    ]

    # old scores
    for k in cutoff_4:
        ASRS_data[k] = [v if pd.isna(v) else v >= 3 for v in ASRS_data[k]]
    for k in cutoff_3:
        ASRS_data[k] = [v if pd.isna(v) else v >= 2 for v in ASRS_data[k]]
    ASRS_data["asrs_a_score (old)"] = (
        ASRS_data[A_keys].sum(axis=1, skipna=skipna).astype("Int64")
    )
    ASRS_data["asrs_b_score (old)"] = (
        ASRS_data[B_keys].sum(axis=1, skipna=skipna).astype("Int64")
    )

    ASRS = ASRS_data[
        [
            "asrs",
            "asrs_a_score",
            "asrs_b_score",
            "asrs_a_score (old)",
            "asrs_b_score (old)",
        ]
    ]
    return ASRS
