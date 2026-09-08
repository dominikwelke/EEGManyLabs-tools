"""
initialize a BIDS folder for EEGManyLabs replication data.
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

from pathlib import Path

from eegmanylabs_bids.bids_utils import update_changes

# further variables
cwd = Path(__file__).parents[0]
with (cwd / "templates" / "bids_template.json").open("r") as f:
    BIDS_template = json.load(f)

BIDS_readme = (cwd / "templates" / "bids_readme.txt").resolve()
BIDS_license = (cwd / "templates" / "bids_license.txt").resolve()


# init def
def init_folder(
    BIDS_root,
    participants_json=None,
    readme=None,
    dataset_desciption=None,
    license=None,
    dryrun=False,
):
    # dont do anything for dryrun
    if dryrun:
        return

    if not participants_json:
        participants_json = BIDS_template["participants_json"]

    if not readme:
        readme = BIDS_readme.read_text()

    if not license:
        license = BIDS_license.read_text()  # for text files

    if not dataset_desciption:
        dataset_desciption = BIDS_template["dataset_description"]

    # make BIDS directory
    try:
        BIDS_root.mkdir(parents=True)
    except FileExistsError:
        raise FileExistsError(
            f"Folder {BIDS_root} already exists! check what you're doing"
        )

    # init README file
    with (BIDS_root / "README.txt").open("w+") as f:
        f.write(readme)

    # init CHANGES file
    with (BIDS_root / "CHANGES").open("w+") as f:
        f.write("")
    update_changes(BIDS_root, message="Initial setup.")

    # init LICENSE file
    with (BIDS_root / "LICENSE").open("w+") as f:
        f.write(license)

    # init dataset_description.json
    with (BIDS_root / "dataset_description.json").open("w+") as f:
        # json.dump(dataset_description,f,indent=4)
        json.dump(dataset_desciption, f, indent=4)

    # init participants.json
    with (BIDS_root / "participants.json").open("w+") as f:
        json.dump(participants_json, f, indent=4)

    # init participants.tsv
    participants_tsv = {"participant_id": []}
    for k in participants_json.keys():
        participants_tsv[k] = []

    pd.DataFrame(participants_tsv).to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False
    )

    # init folder structure
    (BIDS_root / "phenotype").mkdir()
