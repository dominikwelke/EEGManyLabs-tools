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
from eegmanylabs_bids.replications.haycakholroyd2005.parse_phenotype import quest_parser


# settings
ROOT_DIR = Path("/Users/phtn595/Datasets/EEGManyLabs RestingState")
BIDS_ROOT = ROOT_DIR / "BIDS-data-edf"
BIDS_SOURCEDATA = ROOT_DIR / "BIDS-sourcedata"  # BIDS_root / "sourcedata"
RAW_FOLDER = Path("/Users/phtn595/Datasets/EEGManyLabs - Clean/src")

UPDATE_CHANGELOG = False
changelog_message = ['labs: "EUR", "UCM" ', "- add questionnaires to phenotype folder."]

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


# init relevant parameter
if (BIDS_ROOT / "participants.tsv").exists():
    mode = "update"
elif not BIDS_ROOT.is_dir():
    mode = "new"
else:
    raise ValueError


# run script
if __name__ == "__main__":
    cwd = Path(__file__).parents[0]

    # init, if nonexisting
    if mode == "new":
        init_folder(BIDS_ROOT)

    # clean up
    # if mode == "update":
    #    purge_folder(BIDS_root)

    # do
    for study in studies:
        print("---")
        print(study)
        for lab in labs:
            lab_folder = RAW_FOLDER / study / lab
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
                BIDS_sourcefile = BIDS_SOURCEDATA / "phenotype" / lab / rawfile.name
                if not BIDS_sourcefile.exists():
                    BIDS_sourcefile.parent.mkdir(parents=True, exist_ok=True)
                    copy(
                        rawfile, BIDS_sourcefile
                    )  # For Python 3.8+, otherwise must be str

            for i, sub_label in enumerate(sub_ids):
                participants_tsv = pd.read_csv(
                    BIDS_ROOT / "participants.tsv", sep="\t"
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
                    BIDS_ROOT / "participants.tsv", sep="\t", index=False, na_rep="n/a"
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
                    file = BIDS_ROOT / "phenotype" / q.lower()
                    if not file.with_suffix(".json").exists():
                        with file.with_suffix(".json").open("w+") as f:
                            json.dump(d_json, f, indent=4)
                    # get tsv
                    if not file.with_suffix(".tsv").exists():
                        d_tsv = {k: [] for k in d_json.keys()}
                    else:
                        d_tsv = pd.read_csv(file.with_suffix(".tsv"), sep="\t").to_dict(
                            "list"
                        )

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

                    pd.DataFrame(d_tsv).to_csv(
                        file.with_suffix(".tsv"),
                        sep="\t",
                        index=False,
                        na_rep="n/a",
                        float_format="%.1f",
                    )

        # check for mismatch between eeg and phenotype
        if mode == "update":
            consolidate_bids(BIDS_ROOT, replication=study)

    # clean up and leave
    sort_bids(BIDS_ROOT)

    # check all files have same length
    tsv_files = [BIDS_ROOT / "participants.tsv"] + [
        BIDS_ROOT / "phenotype" / (q.lower() + ".tsv") for q in questionaires
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
    if UPDATE_CHANGELOG:
        update_changes(BIDS_ROOT, changelog_message)

    # validate BIDS
    validate_bids(BIDS_ROOT)

    print("\ndone!")
