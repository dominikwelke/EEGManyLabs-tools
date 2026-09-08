"""
various hepler functions for BIDS formatting
EEGManyLabs resting state spin-off

v.1.0 - 2024.01.17
    ..

written by
Dominik Welke
d.welke@leeds.ac.uk
https://github.com/dominikwelke
"""

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from bids_validator import BIDSValidator

from .bids_phenotype import pheno_dtypes

BIDS_readme = (Path(__file__).parents[0] / "templates" / "bids_readme.txt").resolve()

INT_KEYS = [
    "age",
    "education_year",
    "bfi_ext",
    "bfi_agr",
    "bfi_con",
    "bfi_neg",
    "bfi_ope",
    "bis",
    "bas_drive",
    "bas_funseek",
    "bas_rewardresponse",
    "ces_d",
    "kss",
    "panas_s_NA",
    "panas_s_PA",
    "stai_state",
    "stai_trait",
]


def _save_dtypes(df):
    for k in df.keys():
        if k in INT_KEYS:
            df[k] = df[k].astype("Int64")
    return df


def drop_participant(BIDS_root, participant_id):
    participants_tsv = pd.read_csv(BIDS_root / "participants.tsv", sep="\t")
    participants_tsv = participants_tsv[
        participants_tsv.participant_id != participant_id
    ]
    participants_tsv = _save_dtypes(participants_tsv)
    participants_tsv.to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
    )

    phenotype_folder = BIDS_root / "phenotype"
    if phenotype_folder.is_dir():
        for pheno_file in phenotype_folder.glob("*.tsv"):
            pheno_tsv = pd.read_csv(pheno_file, sep="\t")
            pheno_tsv = pheno_tsv[pheno_tsv.participant_id != participant_id]
            pheno_tsv = _save_dtypes(pheno_tsv)
            pheno_tsv.to_csv(pheno_file, sep="\t", index=False, na_rep="n/a")

    print(f"{participant_id} removed from BIDS dataset")


def add_participant(BIDS_root, participant_id, **kwargs):
    if not isinstance(kwargs, dict):
        kwargs = {}
    kwargs["participant_id"] = participant_id
    participants_tsv = pd.read_csv(BIDS_root / "participants.tsv", sep="\t").to_dict(
        "list"
    )

    for k in participants_tsv.keys():
        participants_tsv[k].append(kwargs[k] if (k in kwargs.keys()) else "n/a")
    participants_tsv = _save_dtypes(pd.DataFrame(participants_tsv))
    participants_tsv.to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
    )

    phenotype_folder = BIDS_root / "phenotype"
    if phenotype_folder.is_dir():
        for pheno_file in phenotype_folder.glob("*.tsv"):
            pheno_tsv = pd.read_csv(pheno_file, sep="\t").to_dict("list")
            for k in pheno_tsv.keys():
                pheno_tsv[k].append(kwargs[k] if (k in kwargs.keys()) else "n/a")
            pheno_tsv = _save_dtypes(pd.DataFrame(pheno_tsv))
            pheno_tsv.to_csv(pheno_file, sep="\t", index=False, na_rep="n/a")

    sort_bids(BIDS_root)
    print(f"{participant_id} added to BIDS dataset")


def _update_tsv(df, participant_id, **kwargs):
    if (participant_id not in list(df.participant_id)) and (kwargs != {}):
        df.loc[len(df), "participant_id"] = participant_id
    for k, v in kwargs.items():
        df.loc[df["participant_id"] == participant_id, k] = v
    return df


def update_participants_tsv(BIDS_root, participant_id, **kwargs):
    if not isinstance(kwargs, dict):
        kwargs = {}
    if "sub_id_recode" in kwargs.keys():
        sub_id_recode = kwargs.pop("sub_id_recode")

    if "sub_id_recode" in locals():
        try:
            oldid = sub_id_recode.loc[
                sub_id_recode["newid"] == participant_id.split("sub-")[-1],
                "oldid",
            ].item()
            kwargs["old_id"] = oldid
            kwargs["lab"] = oldid[:3]
        except ValueError:
            pass

    participants_tsv = pd.read_csv(BIDS_root / "participants.tsv", sep="\t")
    participants_tsv = _update_tsv(participants_tsv, participant_id, **kwargs)
    participants_tsv = _save_dtypes(participants_tsv)
    participants_tsv.to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
    )

    sort_bids(BIDS_root)
    print(f"{participant_id} updated in particpants.tsv")


def update_participants_json(BIDS_root, **kwargs):
    # load
    with (BIDS_root / "participants.json").open("r") as f:
        participants_json = json.load(f)
    # update
    participants_json.update(kwargs)
    # save
    with (BIDS_root / "participants.json").open("w+") as f:
        json.dump(participants_json, f, indent=4)


def update_changes(
    BIDS_root, message="- add questionnaires to phenotype folder.", release=0
):
    date = datetime.now().strftime("%Y-%m-%d")
    hist = (BIDS_root / "CHANGES").read_text()
    if hist == "":
        v_new = f"{release}.0"
    else:
        v_old = hist.split("\t")[0].split(".")
        assert int(release) >= int(v_old[0])
        if int(release) == int(v_old[0]):
            v_new = ".".join(v_old[:-1] + [str(int(v_old[-1]) + 1)])
        else:  # increment
            v_new = f"{release}.0"
    if isinstance(message, list):
        message = "\n\t".join(message)
    log = f"{v_new}\t{date}\n\t{message}\n"

    with (BIDS_root / "CHANGES").open("w+") as f:
        f.write(log + hist)


def update_readme(BIDS_root):
    # copy README file
    with (BIDS_root / "README.txt").open("w+") as f:
        f.write(BIDS_readme.read_text())  # for text files


def purge_folder(BIDS_root):
    participants_tsv = pd.read_csv(BIDS_root / "participants.tsv", sep="\t").to_dict(
        "list"
    )
    participants_tsv = {k: [] for k in participants_tsv.keys()}
    participants_tsv = _save_dtypes(pd.DataFrame(participants_tsv))
    participants_tsv.to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
    )

    if (BIDS_root / "phenotype").is_dir():
        shutil.rmtree(BIDS_root / "phenotype")
        (BIDS_root / "phenotype").mkdir(parents=True)


def sort_bids(BIDS_root):
    # participants_tsv
    participants_tsv = pd.read_csv(
        BIDS_root / "participants.tsv", sep="\t", dtype={"age": "Int64"}
    )
    participants_tsv.sort_values("participant_id", inplace=True)
    participants_tsv = _save_dtypes(participants_tsv)
    participants_tsv.to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
    )

    # phenotype
    for quest_tsv_file in (BIDS_root / "phenotype").glob("*.tsv"):
        quest_tsv = pd.read_csv(
            quest_tsv_file,
            sep="\t",
            dtype=pheno_dtypes[quest_tsv_file.with_suffix("").name],
        )
        quest_tsv.sort_values("participant_id", inplace=True)
        quest_tsv = _save_dtypes(quest_tsv)
        quest_tsv.to_csv(quest_tsv_file, sep="\t", index=False, na_rep="n/a")


def consolidate_bids(BIDS_root, verbose=True, **kwargs):
    if verbose:
        print(
            "\nupdating BIDS participants.tsv (removing entries with missing eeg / adding entries with missing questionnaires):"
        )
    if "sub_id_recode" in kwargs:
        sub_id_recode = kwargs.pop("sub_id_recode")
    participant_ids_tsv = list(
        pd.read_csv(BIDS_root / "participants.tsv", sep="\t")["participant_id"]
    )
    participant_ids_eeg = [f.name for f in BIDS_root.glob("sub-*")]
    for participant_id in participant_ids_tsv:
        if participant_id not in participant_ids_eeg:
            print(participant_id, "no eeg file")
            drop_participant(BIDS_root, participant_id)
    for participant_id in participant_ids_eeg:
        if participant_id not in participant_ids_tsv:
            print(participant_id, "no entry in participants.tsv")
            # try to get more info from coding scheme
            if "sub_id_recode" in locals():
                try:
                    oldid = sub_id_recode.loc[
                        sub_id_recode["newid"] == participant_id.split("sub-")[-1],
                        "oldid",
                    ].item()
                    kwargs["old_id"] = oldid
                    kwargs["lab"] = oldid[:3]
                except ValueError:
                    pass

            # add participant
            add_participant(
                BIDS_root,
                participant_id,
                # lab=participant_id[4:7],
                species="homo sapiens",
                **kwargs,
            )
            # remove new info
            kwargs = {k: v for k, v in kwargs.items() if k not in ["old_id", "lab"]}


def clean_levels_in_sidecar_jsons(BIDS_root, verbose=True):
    """
    Keep only levels that are present in the tsv

    :param BIDS_root: Description
    :param verbose: Description
    """
    if verbose:
        print("dropping surplus 'Levels' entries from *.json files:")

    files = [
        (f, f.with_suffix(".tsv"))
        for f in sorted(BIDS_root.rglob("*.json"))
        if (f.exists() and f.with_suffix(".tsv").exists())
    ]
    for f_json, f_tsv in files:
        t_json = f_json.read_text()
        if "Levels" in t_json:
            d_json = json.loads(t_json)
            d_json_out = json.loads(t_json)
            d_tsv = pd.read_csv(f_tsv, sep="\t",dtype=str)
            for k, v in d_json.items():
                if isinstance(v, dict) and "Levels" in v:
                    levels_emp = sorted([l for l in d_tsv[k].unique() if not pd.isna(l)])
                    d_json_out[k]["Levels"] = {
                        kk: vv for kk, vv in v.copy()["Levels"].items() if kk in levels_emp
                    }
                    levels_json = sorted(d_json_out[k]["Levels"].keys())
                    if levels_emp!=levels_json:
                        print(f"-{f_json.name}")
                        print(f"{levels_json} != {levels_emp}")
                    assert levels_emp==levels_json
            if d_json_out != d_json:
                if verbose:
                    print(f"-{f_json.name}")
                f_json.write_text(json.dumps(d_json_out, indent=4))
                

        else:
            continue


def drop_na_from_sidecar_jsons(BIDS_root, verbose=True):
    """
    in json files, n/a entries must be removed unless explicitly allowed.
    only in REQUIRED or explicitly allowed RECOMMENDED fields n/a can remain.

    see discussion here: https://github.com/bids-standard/bids-specification/issues/1982
    """
    REQUIRED = [
        "EEGReference",
        "SamplingFrequency",
        "PowerLineFrequency",
        "SoftwareFilters",
    ]
    RECOMMENDED_ALLOWED = ["HardwareFilters"]

    if verbose:
        print("dropping n/a entries from *_eeg.json files:")

    files = [f for f in BIDS_root.rglob("*_eeg.json") if f.is_file()]
    files = [f for f in files if ".DS_Store" not in str(f)]
    files = [f for f in files if ".git" not in str(f)]
    files.sort()

    dropped = 0
    for fname in files:
        # load
        with fname.open("r") as f:
            d = json.load(f)
        # find
        drop = []
        for key, value in d.items():
            if value == "n/a" and key not in REQUIRED + RECOMMENDED_ALLOWED:
                drop.append(key)
                dropped += 1
                if verbose:
                    print(
                        f"- {fname.relative_to(BIDS_root)} - dropped '{key}: {value}'"
                    )
        # drop
        for key in drop:
            del d[key]
        # save
        with fname.open("w+") as f:
            json.dump(d, f, indent=4)
    if verbose and dropped == 0:
        print("- nothing to drop")


def validate_bids(BIDS_root, verbose=True):
    validator = BIDSValidator()
    files = [
        f"/{f.relative_to(BIDS_root)}" for f in BIDS_root.rglob("*") if f.is_file()
    ]
    files = [f for f in files if ".DS_Store" not in f]
    files = [f for f in files if ".git" not in f]
    files.sort()
    validation = [validator.is_bids(f) for f in files]
    if verbose:
        print("\nvalidate BIDS format:")
        for val, file in zip(validation, files):
            if not val:
                print(f"- {val} - {file}")
        if sum(validation) == len(validation):
            print("- all seems fine")

    n_incompatible = len(validation) - sum(validation)
    if n_incompatible != 0:
        raise ValueError(f"{n_incompatible} filename(s) not BIDS compatible!")


def deidentify_eeg(inst, export_format=None, meas_date=datetime(1924, 7, 6, 0, 0)):
    """
    anonymize eeg recording by setting to a date  prior to 1925
    see

    we'll set it to 6th of July 1924, the date of the first official human EEG recording by Hans Berger.
    """
    hour, minute = meas_date.hour, meas_date.minute
    minute = minute - minute % 30  # round to half hours

    newtime = datetime(
        2024
        if ("edf" in str(export_format).lower())
        else 1924,  # edf can only handle recent dates (1980ish - 2100ish)
        7,
        6,
        hour,
        minute,
        tzinfo=UTC,
    )
    return inst.set_meas_date(newtime)


def update_tod(BIDS_root, tod_dict):
    participants_tsv = pd.read_csv(BIDS_root / "participants.tsv", sep="\t")
    for participant_id, tod in tod_dict.items():
        current_tod = participants_tsv.loc[
            participants_tsv.participant_id == participant_id, "tod"
        ].values[0]
        if list(
            participants_tsv.loc[
                participants_tsv.participant_id == participant_id, "tod"
            ].isnull()
        ):
            participants_tsv.loc[
                participants_tsv.participant_id == participant_id, "tod"
            ] = tod
        else:
            print(f"WARNING - different timestamps found! {current_tod} vs {tod}")

    participants_tsv = _save_dtypes(participants_tsv)
    participants_tsv.to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
    )
