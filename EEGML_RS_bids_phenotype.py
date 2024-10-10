"""
organize EEGManyLabs resting state pilot date in BIDS folder

for further info on required and recommended BIDS entries see:
https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files.html
and especially
https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html

written by
Dominik Welke
d.welke@leeds.ac.uk
https://github.com/dominikwelke
"""

import json
import pandas as pd
import numpy as np

from shutil import copy
from pathlib import Path
from eegmanylabs_bids.bids_init import init_folder, BIDS_template
from eegmanylabs_bids.bids_utils import (
    update_changes,
    # purge_folder,
    consolidate_bids,
    sort_bids,
    validate_bids,
)
from eegmanylabs_bids.bids_phenotype import (
    parse_bfi_s15,
    parse_bisbas,
    parse_cesd,
    parse_ehi,
    parse_kss,
    parse_panas_state,
    parse_stai_state,
    parse_stai_trait,
)

# settings
ROOT_dir = Path("/Users/phtn595/Datasets/EEGManyLabs RestingState")
BIDS_root = ROOT_dir / "BIDS-data-edf"
BIDS_sourcedata = ROOT_dir / "BIDS-sourcedata"  # BIDS_root / "sourcedata"
RAW_folder = Path("/Users/phtn595/Datasets/EEGManyLabs - Clean/src")


studies = ["HajcakHolroyd2005"]
labs = [
    "BON",
    "CIM",
    "GUF",
    "MSH",
    "TUD",
    "UGE",
    "UHH",
    "UNL",
    "URE",
    "EUR",
    "UCM",
]

changelog = False
changelog_message = ['labs: "EUR", "UCM" ', "- add questionnaires to phenotype folder."]

if (BIDS_root / "participants.tsv").exists():
    mode = "update"
elif not BIDS_root.is_dir():
    mode = "new"
else:
    raise ValueError


# helper defs
def _merge_duplicates(data_in):
    """
    merge duplicate lines for participant_ids; takes the first not NaN value
    """
    return data_in.groupby("participant_id").first().reset_index()


def _rescale_data(data_in, minmax_in, minmax_out):
    data_out = data_in.apply(pd.to_numeric, errors="coerce")
    # reference to 0
    data_out -= minmax_in[0]
    # scale
    scalefactor = np.diff(minmax_out) / np.diff(minmax_in)
    data_out *= scalefactor[0]
    # reference to new min
    data_out += minmax_out[0]
    return data_out


# lab specidific parser
def parse_phenotype_UCM(folder):
    f = folder / "Questionnaire_Data" / "UCM_DATABASE_DOORS_TASK.xlsx"
    d = pd.read_excel(f)

    sub_ids = list(d["2.Code"])

    # basics
    age = list(d["5.Age"].astype(int))

    # sex: info code from excel sheet
    sex = [
        "f" if s == 1 else "m" if s == 2 else "o" if s == 3 else None
        for s in d["7.Gender"]  # only 1 and 2 present
    ]

    # handedness
    EHI_keys = [k for k in d.columns if "17.EDI" in k][:20]
    EHI_rename_dict = {
        k: f"EHI_{"L" if "LH" in k else "R" if "RH" in k else "L" if "MI" in k else None}_{(i//2)+1}"
        for i, k in enumerate(EHI_keys)
    }
    d_ = d[EHI_keys].rename(columns=EHI_rename_dict)  # the other EHIs mess it up
    EHI_data = parse_ehi(d_)

    # trust their computation?
    EHI_data_ = d[
        ["17.EDINGBURGH 24.Laterality", "17.EDINGBURGH 23.Laterality coefficient"]
    ].rename(
        columns={
            "17.EDINGBURGH 24.Laterality": "EHI_handedness",
            "17.EDINGBURGH 23.Laterality coefficient": "EHI_LQ",
        }
    )
    EHI_data_["EHI_handedness"] = EHI_data_["EHI_handedness"].replace(
        {1: "r", 2: "l", 3: "a"}
    )
    assert EHI_data.equals(EHI_data_)

    # BFI
    BFI_keys = [k for k in d.columns if "20.BFI" in k][:15]
    BFI_rename_dict = {k: f"BFI_{i+1}" for i, k in enumerate(BFI_keys)}
    d_ = d[BFI_keys].rename(columns=BFI_rename_dict)  # the other BFIs mess it up
    BFI_data = parse_bfi_s15(
        d_, order="en-noreverse"
    )  # this is what we see in the column headers, but didnt they do it in spanish?

    # trust their values?
    BFI_data_ = d[
        [
            "20.BFI-S 17.Extraversion Score",
            "20.BFI-S 19.Kindness Score",
            "20.BFI-S 20.Responsibility Score",
            "20.BFI-S 16.Emotional Stability Score\n ",
            "20.BFI-S 18.Opening Score",
        ]
    ].rename(
        columns={
            "20.BFI-S 16.Emotional Stability Score\n ": "bfi_neg",
            "20.BFI-S 17.Extraversion Score": "bfi_ext",
            "20.BFI-S 18.Opening Score": "bfi_ope",
            "20.BFI-S 19.Kindness Score": "bfi_agr",
            "20.BFI-S 20.Responsibility Score": "bfi_con",
        }
    )
    assert BFI_data.equals(BFI_data_)  # match!

    # PANAS
    PANAS_keys = [k for k in d.columns if "15.PANAS" in k][:20]
    PANAS_rename_dict = {k: f"PANAS_S_{i+1}" for i, k in enumerate(PANAS_keys)}
    d_ = d[PANAS_keys].rename(columns=PANAS_rename_dict)  # the other values mess it up
    PANAS_data = parse_panas_state(
        d_, order="en-1"
    )  # this is what we see in the column headers, but didnt they do it in spanish?

    # trust their computation?
    PANAS_data_ = d[
        ["15.PANAS 21.Negative Affect Score", "15.PANAS 21.Positive Affect Score"]
    ].rename(
        columns={
            "15.PANAS 21.Positive Affect Score": "panas_s_PA",
            "15.PANAS 21.Negative Affect Score": "panas_s_NA",
        }
    )
    assert PANAS_data.equals(PANAS_data_)  # match!

    # KSS
    d = d.rename(columns={"14.Karolinska Sleeping": "KSS"})
    KSS_data = parse_kss(d)

    # CES-D
    CES_keys = [k for k in d.keys() if "CES-D" in k]
    CES_keys = [
        k for k in CES_keys if k.split(".")[1] in [f"CES-D {i}" for i in range(1, 21)]
    ]
    new_keys = [f"CESD_{iq}" for iq in range(1, 21)]
    d = d.rename(columns=dict(zip(CES_keys, new_keys)))
    CES_data = parse_cesd(d)

    # trust their computation?
    assert list(CES_data) == list(d["19.CES-D 21.total score"])

    # BISBAS
    BISBAS_keys = [k for k in d.columns if "18.BIS-BAS" in k][:24]
    BISBAS_rename_dict = {k: f"BISBAS_{i+1}" for i, k in enumerate(BISBAS_keys)}
    d_ = d[BISBAS_keys].rename(
        columns=BISBAS_rename_dict
    )  # the other values mess it up
    BISBAS_data = parse_bisbas(
        d_, order="general-noreverse"
    )  # this is what we see in the column headers, but didnt they do it in spanish?

    # trust their computation?
    BISBAS_data_ = d[
        [
            "18.BIS-BAS 25.Score BIS",
            "18.BIS-BAS 25.Score BAS Drive",
            "18.BIS-BAS 25.Score BAS Fun Seeking",
            "18.BIS-BAS 25.Score BAS Reward Responsiveness",
        ]
    ].rename(
        columns={
            "18.BIS-BAS 25.Score BIS": "bis",
            "18.BIS-BAS 25.Score BAS Drive": "bas_drive",
            "18.BIS-BAS 25.Score BAS Fun Seeking": "bas_funseek",
            "18.BIS-BAS 25.Score BAS Reward Responsiveness": "bas_rewardresponse",
        }
    )
    assert BISBAS_data.equals(BISBAS_data_)  # match!

    # STAI-T
    STAI_S_keys = [k for k in d.columns if "16.STAI-S" in k][:20]
    STAI_T_keys = [k for k in d.columns if "16.STAI-T" in k][:20]
    STAI_S_rename_dict = {k: f"STAI_S_{i+1}" for i, k in enumerate(STAI_S_keys)}
    STAI_T_rename_dict = {k: f"STAI_T_{i+1}" for i, k in enumerate(STAI_T_keys)}
    d_S = (
        d[STAI_S_keys].rename(columns=STAI_S_rename_dict) + 1
    )  # the other values mess it up. 0-3 range instead of 1-4
    d_T = (
        d[STAI_T_keys].rename(columns=STAI_T_rename_dict) + 1
    )  # the other values mess it up. 0-3 range instead of 1-4
    STAI_data = pd.DataFrame(
        {
            "stai_t_state": parse_stai_state(
                d_S, order="noreverse"
            ),  # this is what we see in the column headers, but didnt they do it in spanish?
            "stai_t_trait": parse_stai_trait(
                d_T, order="noreverse"
            ),  # this is what we see in the column headers, but didnt they do it in spanish?
        }
    )

    # trust their computation?
    STAI_data_ = d[
        [
            "16.STAI-S Anxiety Score - State",
            "16.STAI-T Anxiety Score - Trait",
        ]
    ].rename(
        columns={
            "16.STAI-S Anxiety Score - State": "stai_t_state",
            "16.STAI-T Anxiety Score - Trait": "stai_t_trait",
        }
    )
    assert STAI_data.equals(
        STAI_data_ + 20.0
    )  # matches, after correcting for 0-3 scale!

    return (
        sub_ids,
        age,
        sex,
        EHI_data,
        BFI_data,
        PANAS_data,
        KSS_data,
        CES_data,
        BISBAS_data,
        STAI_data,
        [f],
    )


def parse_phenotype_EUR(folder):
    import pyreadstat

    f1 = folder / "Other_Requested_Files" / "SocioDemoRotterdam.csv"
    df1 = pd.read_csv(f1)

    f2 = (
        folder
        / "Questionnaires"
        / "EEG+Replication_Questionnaire_May+1,+2024_10.23.sav"
    )
    df2, meta = pyreadstat.read_sav(f2)

    # clean data
    # row 29 in df2 is a weird datapoint. wrong participant number and missing responses throughout missing
    outlier = df2.iloc[29]
    df2 = df2.drop(29).reset_index()
    assert df1["Age"].astype(int).equals(df2["Age"].astype(int))

    df1["participant_id"] = df1["ID"].apply(lambda x: f"EUR{x[-2:]}")
    sub_ids = list(df1["participant_id"])

    # basics
    age = list(df1["Age"].astype(int))

    # sex: info is there, BUT only 1 or 2 and no cues for what is what, so..
    # update: the full questionnaires (df2) have this info: 1: male, 2: female, 3: non-binary (see obj "meta")
    sex = [
        "m" if s == 1 else "f" if s == 2 else "o" if s == 3 else None
        for s in df2["Gender"]  # only 1 and 2 present
    ]

    # handedness
    # handcode: 1 -> left 2 -> right (see "meta" obj)
    df2 = df2.rename(
        columns={
            f"EHI_Questions_{ih+1}_{iq}": f"EHI_{vh}_{iq}"
            for ih, vh in enumerate(["L", "R"])
            for iq in range(1, 11)
        }
    )
    EHI_data = parse_ehi(df2)

    # BFI
    df2 = df2.rename(columns={f"BFI_15_{iq}": f"BFI_{iq}" for iq in range(1, 16)})
    BFI_data = parse_bfi_s15(df2, order="nl-1")

    # PANAS
    # column names messed up.. 16 and 16.0 but no 15.. also the order is weird, looks like all positive came in a row, then all negative.. maybe they were randomized..
    rename_dict = {f"PANAS_{iq}": f"PANAS_S_{iq}" for iq in range(1, 21)}
    rename_dict["PANAS_16"] = "PANAS_S_15"
    rename_dict["PANAS_16.0"] = "PANAS_S_16"
    df2 = df2.rename(columns=rename_dict)
    PANAS_data = parse_panas_state(df2, order="nl-EUR")

    # KSS
    df2 = df2.rename(columns={"Karolinska_Sleepines": "KSS"})
    KSS_data = parse_kss(df2)

    # CES-D
    # apparently shifted to 1-4 scale, (instead of 0-3)
    df2 = df2.rename(columns={f"CES_D_{iq}": f"CESD_{iq}" for iq in range(1, 21)})
    for iq in range(1, 21):
        df2[f"CESD_{iq}"] -= 1
    CES_data = parse_cesd(df2)

    # BISBAS
    # apparently dutch order is the same as english
    df2 = df2.rename(columns={f"BIS_BAS_{iq}": f"BISBAS_{iq}" for iq in range(1, 25)})
    BISBAS_data = parse_bisbas(df2, order="general")

    # STAI-T
    STAI_data = pd.DataFrame(
        {
            "stai_t_state": parse_stai_state(df2, order="nl-1"),
            "stai_t_trait": parse_stai_trait(df2, order="nl-1"),
        }
    )
    return (
        sub_ids,
        age,
        sex,
        EHI_data,
        BFI_data,
        PANAS_data,
        KSS_data,
        CES_data,
        BISBAS_data,
        STAI_data,
        [f1, f2],
    )


def parse_phenotype_BON(folder):
    omitlines = 3
    f = folder / "Other_Requested_Files" / "BON_Self_Report.csv"
    d = pd.read_csv(f)
    # d_info = d[:omitlines]
    d = d[omitlines:].reset_index(drop=True)

    d["participant_id"] = [s[6:] for s in list(d["PID"])]
    d = _merge_duplicates(d)
    sub_ids = list(d["participant_id"])

    # basics
    age = list(d["Age"])
    sex = [s if not isinstance(s, str) else s.lower()[0] for s in d["Gender"]]

    # handedness
    d = d.rename(
        columns={
            f"EHI_{i}_{j+1}": f"EHI_{k}_{i}"
            for i in range(1, 11)
            for j, k in enumerate(["L", "R"])
        }
    )
    EHI_data = parse_ehi(d)

    # BFI
    BFI_data = parse_bfi_s15(d, order="en-1")  # 1-5 scale, subtract 3

    # PANAS
    d = d.rename(columns={f"PANAS_{i}": f"PANAS_S_{i}" for i in range(1, 21)})
    PANAS_data = parse_panas_state(d, order="en-1")

    # KSS
    KSS_data = parse_kss(d)

    # CES-D
    d = d.rename(columns={f"CES{i}": f"CESD_{i}" for i in range(1, 21)})
    for col in [f"CESD_{i}" for i in range(1, 21)]:
        d[col] = (
            d[col].apply(pd.to_numeric, errors="coerce") - 1
        )  # transfer to [0-3 coding]
    CES_data = parse_cesd(d)

    # BISBAS
    BISBAS_data = parse_bisbas(d, order="general")

    # STAI-T
    STAI_data = pd.DataFrame(
        {
            "stai_t_state": parse_stai_state(d, order="en-1"),
            "stai_t_trait": parse_stai_trait(d, order="en-1"),
        }
    )
    return (
        sub_ids,
        age,
        sex,
        EHI_data,
        BFI_data,
        PANAS_data,
        KSS_data,
        CES_data,
        BISBAS_data,
        STAI_data,
        [f],
    )


def parse_phenotype_TUD(folder):
    f1 = (
        folder / "Other_Requested_Files" / "ManyLabs_TUD_LimeSurvey_Q1_FullResponse.csv"
    )
    f2 = (
        folder / "Other_Requested_Files" / "ManyLabs_TUD_LimeSurvey_Q2_FullResponse.csv"
    )
    d1 = pd.read_csv(f1).rename(
        columns={"VP-Code/ID:": "participant_id"}
    )  # sub 14/15 might be shifted to 15/16?
    d1 = _merge_duplicates(d1)
    d2 = pd.read_csv(f2).rename(columns={"VP-Code:": "participant_id"})
    d2 = _merge_duplicates(d2)
    d = pd.merge(d1, d2, on="participant_id")

    # lab = str(folder.name)[:3]

    d["participant_id"] = [s[-5:] for s in d["participant_id"]]
    sub_ids = list(d["participant_id"])

    # basics
    age = list(d["Alter in Jahren:"])
    sex = [
        s
        if not isinstance(s, str)
        else "f"
        if (s.lower()[0] == "w")
        else "m"
        if (s.lower()[0] == "m")
        else "o"
        for s in d[
            "Anschließend bitten wir Sie um die Angabe Ihrer demographischen Daten. Bitte geben Sie zunächst Ihr Geschlecht an."
        ]
    ]

    # handedness
    EHI_keys = [k for k in d.keys() if "welche Hand Sie hierfür gebrauchen" in k]
    EHI_dict_R = {
        "immer rechts, nie links": 2,
        "meistens rechts": 1,
        "rechts und links gleich häufig": 0,
        "meistens links": 0,
        "immer links, nie rechts": 0,
        "keine Angabe": "n/a",
        99: "n/a",
    }
    EHI_dict_L = {
        "immer rechts, nie links": 0,
        "meistens rechts": 0,
        "rechts und links gleich häufig": 0,
        "meistens links": 1,
        "immer links, nie rechts": 2,
        "keine Angabe": "n/a",
        99: "n/a",
    }
    for i, k in enumerate(EHI_keys):
        d[f"EHI_R_{i+1}"] = d[k].fillna(99).apply(lambda x: EHI_dict_R[x])
        d[f"EHI_L_{i+1}"] = d[k].fillna(99).apply(lambda x: EHI_dict_L[x])
    EHI_data = parse_ehi(d)

    # BFI
    BFI_keys = [k for k in d.keys() if "ich bin jemand" in k.lower()]
    assert len(BFI_keys) == 15
    for i, k in enumerate(BFI_keys):
        d[f"BFI_{i+1}"] = d[k].apply(lambda x: int(x[0]) if isinstance(x, str) else x)
    BFI_data = parse_bfi_s15(d, order="ger-1")

    # PANAS - needs work (german reordered) - done
    PANAS_keys = [
        k
        for k in d.keys()
        if "Wörtern, die unterschiedliche Gefühle und Empfindungen beschreiben" in k
    ]
    assert len(PANAS_keys) == 20
    PANAS_dict = {
        "Gar nicht": 1,
        "Ein bisschen": 2,
        "Einigermaßen": 3,
        "Erheblich": 4,
        "Äußerst": 5,
    }
    for i, k in enumerate(PANAS_keys):
        d[f"PANAS_S_{i+1}"] = d[k].apply(
            lambda x: PANAS_dict[x] if isinstance(x, str) else x
        )
    PANAS_data = parse_panas_state(d, order="ger-1")

    # KSS
    KSS_key = (
        "[Geben Sie auf einer Skala von 1 bis 9 an, wie schläfrig Sie sich fühlen:]"
    )
    KSS_dict = {
        "Sehr wach": 2,
        "Wach": 3,
        "Ziemlich wach": 4,
        "Anzeichen von Müdigkeit": 6,
    }
    d = d.rename(columns={KSS_key: "KSS"})
    d["KSS"] = d["KSS"].apply(lambda x: KSS_dict[x] if isinstance(x, str) else x)
    KSS_data = parse_kss(d)

    # CES (order doesnt matter)
    CES_keys = [
        k
        for k in d.keys()
        if "Beschreibungen, wie Sie sich möglicherweise zuletzt gefühlt oder verhalten haben"
        in k
    ]
    assert len(CES_keys) == 20
    CES_dict = {
        "Überhaupt nicht oder weniger als 1 Tag": 0,
        "1 bis 2 Tage": 1,
        "3 bis 4 Tage": 2,
        "5 bis 7 Tage": 3,
        "Fast jeden Tag in den letzten 2 Wochen": 3,
    }
    for i, k in enumerate(CES_keys):
        d[f"CESD_{i+1}"] = d[k].apply(
            lambda x: "n/a" if str(x) in ["nan", "na", "NaN", "None"] else CES_dict[x]
        )
    CES_data = parse_cesd(d)

    # BISBAS (english/german same order)
    BISBAS_keys = [
        k
        for k in d.keys()
        if "eine Reihe von Feststellungen, mit denen man sich selbst beschreiben kann"
        in k
    ]
    assert len(BISBAS_keys) == 24
    BISBAS_dict = {
        "trifft für mich gar nicht zu": 4,
        "trifft für mich eher nicht zu": 3,
        "trifft für mich eher zu": 2,
        "trifft für mich genau zu": 1,
        "Very false for me": 4,
        "Somewhat false for me": 3,
        "Somewhat true for me": 2,
        "Very true for me": 1,
    }
    for i, k in enumerate(BISBAS_keys):
        d[f"BISBAS_{i+1}"] = d[k].apply(
            lambda x: BISBAS_dict[x] if isinstance(x, str) else x
        )
    BISBAS_data = parse_bisbas(d, order="general")

    # STAI-T - needs work (different order in german)
    STAI_S_keys = [
        k for k in d.keys() if "die folgenden Gefühlsbeschreibungen im Moment" in k
    ]
    STAI_T_keys = [
        k for k in d.keys() if "wie oft folgende Aussagen im Allgemeinen" in k
    ]
    assert len(STAI_S_keys) == 20
    assert len(STAI_T_keys) == 20

    STAI_dict = {
        "Sehr": 4,
        "Ziemlich": 3,
        "Ein Wenig": 2,
        "Überhaupt nicht": 1,
        "Fast immer": 4,
        "Oft": 3,
        "Manchmal": 2,
        "Fast nie": 1,
    }
    for i in range(1, 21):  # fill with n/a
        d[f"STAI_S_{i}"] = d[STAI_S_keys[i - 1]].apply(
            lambda x: STAI_dict[x] if isinstance(x, str) else x
        )
        d[f"STAI_T_{i}"] = d[STAI_T_keys[i - 1]].apply(
            lambda x: STAI_dict[x] if isinstance(x, str) else x
        )

    STAI_data = pd.DataFrame(
        {
            "stai_t_state": parse_stai_state(d, order="ger-1"),
            "stai_t_trait": parse_stai_trait(d, order="ger-1"),
        }
    )

    return (
        sub_ids,
        age,
        sex,
        EHI_data,
        BFI_data,
        PANAS_data,
        KSS_data,
        CES_data,
        BISBAS_data,
        STAI_data,
        [f1, f2],
    )


def parse_phenotype_UGE(folder):
    f = (
        folder
        / "Other_Requested_Files"
        / "Questionnaires"
        / "UGE_complete_transcribe_questionnaires_120124 DWaccepted.csv"
    )
    d = pd.read_csv(f, sep=";")
    # d_info = d[:omitlines]

    d = _merge_duplicates(d)
    sub_ids = list(d["participant_id"])

    # basics
    age, sex = [], []
    for sub_id in sub_ids:
        UGE_root = Path(
            "/Users/phtn595/Datasets/EEGManyLabs - Clean/src/HajcakHolroyd2005/UGE/Behav_Data"
        )
        try:
            dd = pd.read_csv(UGE_root / f"{sub_id}_cuedDoors.txt", sep="\t")
            age.append(dd.age[0])
            sex.append(dd.gndr[0])
        except FileNotFoundError:
            age.append("n/a")
            sex.append("n/a")

    # handedness
    d = d.rename(
        columns={
            f"EHI_{i}_{k}": f"EHI_{k}_{i}" for i in range(1, 11) for k in ["L", "R"]
        }
    )
    EHI_data = parse_ehi(d)

    # BFI - HERE THEY USED A 1-7 scale
    BFI_data = parse_bfi_s15(d, order="en-1")  # 1-7 scale, subtract 4

    # PANAS
    d = d.rename(columns={f"PANAS_{i}": f"PANAS_S_{i}" for i in range(1, 21)})
    PANAS_data = parse_panas_state(d, order="en-1")

    # KSS
    KSS_data = parse_kss(d)

    # CES
    d = d.rename(columns={f"CES{i}": f"CESD_{i}" for i in range(1, 21)})
    for col in [f"CESD_{i}" for i in range(1, 21)]:
        d[col] = d[col] - 1  # transfer to [0-3 coding]
    CES_data = parse_cesd(d)

    # BISBAS
    BISBAS_data = parse_bisbas(d, order="general")

    # STAI-T
    d = d.rename(
        columns={
            f"STAI_{i}": f"STAI_S_{i}" if (i <= 20) else f"STAI_T_{i-20}"
            for i in range(1, 41)
        }
    )
    STAI_data = pd.DataFrame(
        {
            "stai_t_state": parse_stai_state(d, order="en-1"),
            "stai_t_trait": parse_stai_trait(d, order="en-1"),
        }
    )
    return (
        sub_ids,
        age,
        sex,
        EHI_data,
        BFI_data,
        PANAS_data,
        KSS_data,
        CES_data,
        BISBAS_data,
        STAI_data,
        [f],
    )


def parse_phenotype_UHH(folder):
    f1 = folder.parents[0] / "UHH" / "Other_Requested_Files" / "After_Codes.csv"
    f2 = folder.parents[0] / "UHH" / "Other_Requested_Files" / "After_FullText.csv"
    keys = list(pd.read_csv(f1).keys())
    d = pd.read_csv(f2)
    d = d.rename(columns={list(d.keys())[i]: keys[i] for i in range(len(keys))})

    lab = str(folder.name)[:3]
    d = d.loc[d["VpCode2"].str.contains(lab) == True].reset_index(
        drop=True
    )  # nan values treated as false

    if lab in ["URE", "GUF"]:
        d["participant_id"] = [
            f"{lab}{i:02d}"
            for s in d["VpCode2"]
            for i in range(99)
            if (f"{i:02d}" in s)
        ]
    else:
        d["participant_id"] = [s[-5:] for s in d["VpCode2"]]
    d = _merge_duplicates(d)
    sub_ids = list(d["participant_id"])

    # basics
    age = list(d["Alter"])
    sex = [
        s if not isinstance(s, str) else "f" if (s.lower()[0] == "w") else s.lower()[0]
        for s in d["Geschlecht"]
    ]

    # handedness
    EHI_dict_R = {
        "immer rechts, nie links": 2,
        "meistens rechts": 1,
        "rechts und links gleich häufig": 0,
        "meistens links": 0,
        "immer links, nie rechts": 0,
        "keine Angabe": "n/a",
        99: "n/a",
    }
    EHI_dict_L = {
        "immer rechts, nie links": 0,
        "meistens rechts": 0,
        "rechts und links gleich häufig": 0,
        "meistens links": 1,
        "immer links, nie rechts": 2,
        "keine Angabe": "n/a",
        99: "n/a",
    }
    for i in range(1, 11):
        d[f"EHI_R_{i}"] = (
            d[f"EHI1[SQ{i:03d}]"].fillna(99).apply(lambda x: EHI_dict_R[x])
        )
        d[f"EHI_L_{i}"] = (
            d[f"EHI1[SQ{i:03d}]"].fillna(99).apply(lambda x: EHI_dict_L[x])
        )
    EHI_data = parse_ehi(d)

    # BFI
    d = d.rename(columns={f"BFI1[SQ{i:03d}]": f"BFI_{i}" for i in range(1, 16)})
    for col in [f"BFI_{i}" for i in range(1, 16)]:
        d[col] = d[col].apply(
            lambda x: "n/a" if str(x) in ["nan", "na", "NaN", "None"] else str(x)[0]
        )
    BFI_data = parse_bfi_s15(d, order="ger-1")

    # PANAS
    for i in range(1, 21):  # fill with n/a
        d[f"PANAS_S_{i}"] = ["n/a"] * len(d)
    PANAS_data = parse_panas_state(d, order="ger-1")

    # KSS
    d["KSS"] = ["n/a"] * len(d)  # not done
    KSS_data = parse_kss(d)

    # CES
    d = d.rename(columns={f"CES1[SQ{i:03d}]": f"CESD_{i}" for i in range(1, 21)})
    CES_dict = {
        "Überhaupt nicht oder weniger als 1 Tag": 0,
        "1 bis 2 Tage": 1,
        "3 bis 4 Tage": 2,
        "5 bis 7 Tage": 3,
        "Fast jeden Tag in den letzten 2 Wochen": 3,
    }
    for col in [f"CESD_{i}" for i in range(1, 21)]:
        d[col] = d[col].apply(
            lambda x: "n/a" if str(x) in ["nan", "na", "NaN", "None"] else CES_dict[x]
        )
    CES_data = parse_cesd(d)

    # BISBAS
    d = d.rename(columns={f"BISBAS1[SQ{i:03d}]": f"BISBAS_{i}" for i in range(1, 25)})
    BISBAS_dict = {
        "trifft für mich gar nicht zu": 4,
        "trifft für mich eher nicht zu": 3,
        "trifft für mich eher zu": 2,
        "trifft für mich genau zu": 1,
        "Very false for me": 4,
        "Somewhat false for me": 3,
        "Somewhat true for me": 2,
        "Very true for me": 1,
    }
    for col in [f"BISBAS_{i}" for i in range(1, 25)]:
        d[col] = d[col].apply(
            lambda x: "n/a"
            if str(x) in ["nan", "na", "NaN", "None"]
            else BISBAS_dict[x]
        )
    BISBAS_data = parse_bisbas(d, order="general")

    # STAI-T
    for i in range(1, 21):  # fill with n/a
        d[f"STAI_S_{i}"] = ["n/a"] * len(d)
        d[f"STAI_T_{i}"] = ["n/a"] * len(d)

    STAI_data = pd.DataFrame(
        {
            "stai_t_state": parse_stai_state(d, order="ger-1"),
            "stai_t_trait": parse_stai_trait(d, order="ger-1"),
        }
    )

    return (
        sub_ids,
        age,
        sex,
        EHI_data,
        BFI_data,
        PANAS_data,
        KSS_data,
        CES_data,
        BISBAS_data,
        STAI_data,
        [f1, f2],
    )


def parse_phenotype_UNL(folder):
    f1 = folder / "Other_Requested_Files" / "UNL_Compiled_1.csv"
    f2 = folder / "Other_Requested_Files" / "UNL_Compiled_2.csv"
    omitlines = 1
    d1 = pd.read_csv(f1, sep=";")
    # d1_info = d1[:omitlines]
    d1 = d1[omitlines:].reset_index(drop=True)
    d2 = pd.read_csv(f2, sep=";")
    # d2_info = d2[:omitlines]
    d2 = d2[omitlines:].reset_index(drop=True)

    # basics
    sub_ids = [s[6:] for s in list(d1["Participant_number"])]
    age = list(d1["Age"])
    sex = [
        "f"
        if (s.lower() in ["vrouw", "female"])
        else "m"
        if (s.lower() in ["man", "male"])
        else s
        for s in d1["Gender"]
    ]

    # handedness
    EHI_dict_R = {
        "Rechterhand sterke voorkeur": 2,
        "Rechterhand": 1,
        "Geen voorkeur": 0,
        "Linkerhand": 0,
        "Linkerhand sterke voorkeur": 0,
        "Right hand strong preference": 2,
        "Right hand": 1,
        "Indifferent": 0,
        "Left hand": 0,
        "Left hand strong preference": 0,
    }
    EHI_dict_L = {
        "Rechterhand sterke voorkeur": 0,
        "Rechterhand": 0,
        "Geen voorkeur": 0,
        "Linkerhand": 1,
        "Linkerhand sterke voorkeur": 2,
        "Right hand strong preference": 0,
        "Right hand": 0,
        "Indifferent": 0,
        "Left hand": 1,
        "Left hand strong preference": 2,
    }  # 0, 0, 0, 1, 2, 0, 0, 0, 1, 2
    for i in range(1, 11):
        d2[f"EHI_R_{i}"] = d2[f"Handedness#1_{i}"].apply(lambda x: EHI_dict_R[x])
        d2[f"EHI_L_{i}"] = d2[f"Handedness#1_{i}"].apply(lambda x: EHI_dict_L[x])
    EHI_data = parse_ehi(d2)

    # BFI
    d2 = d2.rename(columns={f"BigFive-15_{i}": f"BFI_{i}" for i in range(1, 16)})
    BFI_data = parse_bfi_s15(d2, order="en-1")

    # PANAS
    d1 = d1.rename(
        columns={f"PANAS State Mood_{i}": f"PANAS_S_{i}" for i in range(1, 21)}
    )
    PANAS_data = parse_panas_state(d1, order="en-1")

    # KSS
    d1 = d1.rename(columns={"KSQ-2": "KSS"})
    d1["KSS"] = d1["KSS"].apply(lambda x: x[0])
    KSS_data = parse_kss(d1)

    # CES
    d2 = d2.rename(columns={f"CES-D_{i}": f"CESD_{i}" for i in range(1, 21)})
    CES_dict = {
        "Zelden of nooit (minder dan 1 dag)": 0,
        "Rarely or none of the time (less than 1 day)": 0,
        "Soms of weinig (1-2 dagen)": 1,
        "Some or a little of the time (1-2 days)": 1,
        "Regelmatig (3-4 dagen)": 2,
        "Occasionally or a moderate amount of time (3-4 days)": 2,
        "Meestal of altijd (5-7 dagen)": 3,
        "Most or all of the time (5-7 days)": 3,
    }
    for col in [f"CESD_{i}" for i in range(1, 21)]:
        d2[col] = d2[col].apply(
            lambda x: "n/a" if str(x) in ["nan", "na", "NaN", "None"] else CES_dict[x]
        )
    CES_data = parse_cesd(d2)

    # BISBAS
    d2 = d2.rename(columns={f"BIS-BAS_{i}": f"BISBAS_{i}" for i in range(1, 25)})
    BISBAS_dict = {
        "Helemaal mee oneens": 4,
        "Beetje mee oneens": 3,
        "Beetje mee eens": 2,
        "Helemaal eens": 1,
        "Very false for me": 4,
        "Somewhat false for me": 3,
        "Somewhat true for me": 2,
        "Very true for me": 1,
    }
    for col in [f"BISBAS_{i}" for i in range(1, 25)]:
        d2[col] = d2[col].apply(
            lambda x: "n/a"
            if str(x) in ["nan", "na", "NaN", "None"]
            else BISBAS_dict[x]
        )
    BISBAS_data = parse_bisbas(d2, order="general")

    # STAI-T
    d1 = d1.rename(columns={f"STAI-Part-1_{i}": f"STAI_S_{i}" for i in range(1, 21)})
    d1 = d1.rename(columns={f"STAI-Part-2_{i}": f"STAI_T_{i}" for i in range(1, 21)})
    STAI_data = pd.DataFrame(
        {
            "stai_t_state": parse_stai_state(d1, order="en-1"),
            "stai_t_trait": parse_stai_trait(d1, order="en-1"),
        }
    )

    return (
        sub_ids,
        age,
        sex,
        EHI_data,
        BFI_data,
        PANAS_data,
        KSS_data,
        CES_data,
        BISBAS_data,
        STAI_data,
        [f1, f2],
    )


quest_parser = dict(
    BON=parse_phenotype_BON,
    CIM=parse_phenotype_UHH,
    EUR=parse_phenotype_EUR,
    GUF=parse_phenotype_UHH,
    MSH=parse_phenotype_UHH,
    TUD=parse_phenotype_TUD,
    UCM=parse_phenotype_UCM,
    UGE=parse_phenotype_UGE,
    UHH=parse_phenotype_UHH,
    UNL=parse_phenotype_UNL,
    URE=parse_phenotype_UHH,
)


# run script
if __name__ == "__main__":
    cwd = Path(__file__).parents[0]

    # init, if nonexisting
    if mode == "new":
        init_folder(BIDS_root)

    # clean up
    # if mode == "update":
    #    purge_folder(BIDS_root)

    # do
    for study in studies:
        print("---")
        print(study)
        for lab in labs:
            lab_folder = RAW_folder / study / lab
            print("-" + lab)

            # load data
            if lab not in quest_parser.keys():
                raise NotImplementedError
            (
                sub_ids,
                age,
                sex,
                EHI,
                BFI,
                PANAS_STATE,
                KSS,
                CES,
                BISBAS,
                STAI,
                rawfiles,
            ) = quest_parser[lab](lab_folder)
            handedness, EHI_LQ = list(EHI["EHI_handedness"]), list(EHI["EHI_LQ"])

            # copy sourcefile
            for rawfile in rawfiles:
                BIDS_sourcefile = BIDS_sourcedata / "phenotype" / lab / rawfile.name
                if not BIDS_sourcefile.exists():
                    BIDS_sourcefile.parent.mkdir(parents=True, exist_ok=True)
                    copy(
                        rawfile, BIDS_sourcefile
                    )  # For Python 3.8+, otherwise must be str

            for i, sub_label in enumerate(sub_ids):
                participants_tsv = pd.read_csv(
                    BIDS_root / "participants.tsv", sep="\t"
                ).to_dict("list")
                if "test" in sub_label.lower():
                    print(f"--{sub_label} skipped")
                    continue
                elif f"sub-{sub_label}" in list(participants_tsv["participant_id"]):
                    print(f"--{sub_label} updated")
                    participants_tsv = pd.DataFrame(participants_tsv)
                    participants_tsv.drop(
                        participants_tsv[
                            participants_tsv.participant_id.str.contains(
                                "sub-" + sub_label
                            )
                        ].index,
                        inplace=True,
                    )
                    participants_tsv = participants_tsv.to_dict("list")
                else:
                    print(f"-- {sub_label} added")
                # fill participants.tsv
                participants_tsv["participant_id"].append("sub-" + sub_label)
                participants_tsv["species"].append("homo sapiens")
                participants_tsv["age"].append(age[i])
                participants_tsv["sex"].append(sex[i])
                participants_tsv["handedness"].append(handedness[i])
                participants_tsv["replication"].append(study)
                participants_tsv["lab"].append(lab)
                pd.DataFrame(participants_tsv).to_csv(
                    BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
                )

                # phenotype (questionnaires)
                questionaires = [
                    "EHI",
                    "BFI_S",
                    "BISBAS",
                    "CES",
                    "STAI_T",
                    "PANAS_STATE",
                    "KSS",
                ]
                # JSONs
                desc_json = BIDS_template["phenotype_jsons"]
                for q in questionaires:
                    d_json = desc_json[q]
                    file = BIDS_root / "phenotype" / q.lower()
                    if not file.with_suffix(".json").exists():
                        with file.with_suffix(".json").open("w+") as f:
                            json.dump(d_json, f, indent=4)
                    # get tsv
                    if not file.with_suffix(".tsv").exists():
                        d_tsv = {k: [] for k in d_json.keys()}
                        # d_tsv = {k:['n/a'] for k in d_json.keys()}
                        # d_tsv["participant_id"] = [sub_id]
                    else:
                        d_tsv = pd.read_csv(file.with_suffix(".tsv"), sep="\t").to_dict(
                            "list"
                        )
                        # for k in d_json.keys():
                        # d_tsv[k].append(sub_id if (k=='participant_id') else 'n/a')

                    # modify
                    if "sub-" + sub_label in d_tsv["participant_id"]:
                        df_tmp = pd.DataFrame(d_tsv)
                        df_tmp.drop(
                            df_tmp[
                                df_tmp.participant_id.str.contains("sub-" + sub_label)
                            ].index,
                            inplace=True,
                        )
                        d_tsv = df_tmp.to_dict("list")

                    d_tsv["participant_id"].append("sub-" + sub_label)
                    if q == "EHI":
                        d_tsv["ehi_lq"].append(EHI_LQ[i])
                        d_tsv["ehi_handedness"].append(handedness[i])
                    elif q == "KSS":
                        d_tsv["kss"].append(KSS[i])
                    elif q == "CES":
                        d_tsv["ces_d"].append(CES[i])
                    elif q == "BISBAS":
                        for k in d_json.keys():
                            if k != "participant_id":
                                d_tsv[k].append(BISBAS[k][i])
                    elif q == "BFI_S":
                        for k in d_json.keys():
                            if k != "participant_id":
                                d_tsv[k].append(BFI[k][i])
                    elif q == "PANAS_STATE":
                        for k in d_json.keys():
                            if k != "participant_id":
                                d_tsv[k].append(PANAS_STATE[k][i])
                    elif q == "STAI_T":
                        for k in d_json.keys():
                            if k != "participant_id":
                                d_tsv[k].append(STAI[k][i])
                    else:
                        for k in d_json.keys():
                            if k != "participant_id":
                                d_tsv[k].append("n/a")

                    # print(d_tsv)
                    pd.DataFrame(d_tsv).to_csv(
                        file.with_suffix(".tsv"),
                        sep="\t",
                        index=False,
                        na_rep="n/a",
                        float_format="%.1f",
                    )

        # check for mismatch between eeg and phenotype
        if mode == "update":
            consolidate_bids(BIDS_root, replication=study)

    # clean up and leave
    sort_bids(BIDS_root)

    # check all files have same length
    tsv_files = [BIDS_root / "participants.tsv"] + [
        BIDS_root / "phenotype" / (q.lower() + ".tsv") for q in questionaires
    ]
    while len(tsv_files) > 1:
        tsv_file_1 = tsv_files.pop(0)
        sub_ids_1 = list(pd.read_csv(tsv_file_1, sep="\t")["participant_id"])
        sub_ids_1.sort()
        for tsv_file_2 in tsv_files:
            sub_ids_2 = list(pd.read_csv(tsv_file_2, sep="\t")["participant_id"])
            sub_ids_2.sort()
            assert sub_ids_1 == sub_ids_2

    # update CHANGES
    if changelog:
        update_changes(BIDS_root, changelog_message)

    # validate BIDS
    validate_bids(BIDS_root)

    print("\ndone!")
