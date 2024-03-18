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

import shutil
import pandas as pd

from datetime import datetime
from bids_validator import BIDSValidator

from .bids_phenotype import pheno_dtypes


def drop_participant(BIDS_root, participant_id):
    participants_tsv = pd.read_csv(BIDS_root / "participants.tsv", sep="\t")
    participants_tsv = participants_tsv[
        participants_tsv.participant_id != participant_id
    ]
    participants_tsv.to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
    )

    phenotype_folder = BIDS_root / "phenotype"
    if phenotype_folder.is_dir():
        for pheno_file in phenotype_folder.glob("*.tsv"):
            pheno_tsv = pd.read_csv(pheno_file, sep="\t")
            pheno_tsv = pheno_tsv[pheno_tsv.participant_id != participant_id]
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
    pd.DataFrame(participants_tsv).to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
    )

    phenotype_folder = BIDS_root / "phenotype"
    if phenotype_folder.is_dir():
        for pheno_file in phenotype_folder.glob("*.tsv"):
            pheno_tsv = pd.read_csv(pheno_file, sep="\t").to_dict("list")
            for k in pheno_tsv.keys():
                pheno_tsv[k].append(kwargs[k] if (k in kwargs.keys()) else "n/a")
            pd.DataFrame(pheno_tsv).to_csv(
                pheno_file, sep="\t", index=False, na_rep="n/a"
            )

    sort_bids(BIDS_root)
    print(f"{participant_id} added to BIDS dataset")


def update_changes(BIDS_root, message="- add questionnaires to phenotype folder."):
    date = datetime.now().strftime("%Y-%m-%d")
    hist = (BIDS_root / "CHANGES").read_text()
    if hist == "":
        v_new = "0.0.0"
    else:
        v_old = hist.split("\t")[0].split(".")
        v_new = ".".join(v_old[:-1] + [str(int(v_old[-1]) + 1)])
    log = f"{v_new}\t{date}\n\t{message}\n"

    with (BIDS_root / "CHANGES").open("w+") as f:
        f.write(log + hist)


def purge_folder(BIDS_root):
    participants_tsv = pd.read_csv(BIDS_root / "participants.tsv", sep="\t").to_dict(
        "list"
    )
    participants_tsv = {k: [] for k in participants_tsv.keys()}
    pd.DataFrame(participants_tsv).to_csv(
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
        quest_tsv.to_csv(quest_tsv_file, sep="\t", index=False, na_rep="n/a")


def validate_bids(BIDS_root, verbose=True):
    validator = BIDSValidator()
    files = [
        f"/{f.relative_to(BIDS_root)}" for f in BIDS_root.rglob("*") if f.is_file()
    ]
    files = [f for f in files if ".DS_Store" not in f]
    files.sort()
    validation = [validator.is_bids(f) for f in files]
    if verbose:
        print("\nvalidate BIDS format:")
        for val, file in zip(validation, files):
            if not val:
                print(f"{val} - {file}")

    n_incompatible = len(validation) - sum(validation)
    if n_incompatible != 0:
        raise ValueError(f"{n_incompatible} filename(s) not BIDS compatible!")
