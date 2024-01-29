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
from datetime import datetime

# further variables
cwd = Path(__file__).parents[0]
with (cwd / "bids_template.json").open("r") as f:
    BIDS_template = json.load(f)

BIDS_license = (Path(__file__).parents[0] / "bids_license.txt").resolve()


# init def
def init_folder(BIDS_root):
    # BIDS_version = "1.9.0"

    # make BIDS directory
    try:
        BIDS_root.mkdir(parents=True)
    except FileExistsError:
        raise FileExistsError(
            f"Folder {BIDS_root} already exists! check what you're doing"
        )

    # init README file
    with (BIDS_root / "README").open("w+") as f:
        f.write("")

    # init CHANGES file
    date = datetime.now().strftime("%Y-%m-%d")
    with (BIDS_root / "CHANGES").open("w+") as f:
        f.write(f"0.0.0\t{date}\n\t- Initial setup.")

    # init LICENSE file
    with (BIDS_root / "LICENSE").open("w+") as f:
        f.write(BIDS_license.read_text())  # for text files

    # init dataset_description.json
    with (BIDS_root / "dataset_description.json").open("w+") as f:
        # json.dump(dataset_description,f,indent=4)
        json.dump(BIDS_template["dataset_description"], f, indent=4)

    # init participants.json
    with (BIDS_root / "participants.json").open("w+") as f:
        json.dump(BIDS_template["participants_json"], f, indent=4)

    # init participants.tsv
    participants_tsv = {"participant_id": []}
    for k in BIDS_template["participants_json"].keys():
        participants_tsv[k] = []

    pd.DataFrame(participants_tsv).to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False
    )

    # init folder structure
    (BIDS_root / "phenotype").mkdir()
