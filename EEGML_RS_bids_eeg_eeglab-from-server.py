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
import pandas as pd
import shutil

# from mne_bids import BIDSPath, write_raw_bids
# from mne_bids.copyfiles import copyfile_eeglab

from pathlib import Path
from eegmanylabs_bids.bids_init import init_folder
from eegmanylabs_bids.bids_utils import (
    update_changes,
    drop_participant,
    add_participant,
    validate_bids,
)
from eegmanylabs_bids.bids_eeg import update_eeg_json

# run script
if __name__ == "__main__":
    labs = ["UGE", "UNL", "BON", "UHH", "CIM", "MSH", "GUF", "URE"]
    task = "resting"

    BIDS_folder = "BIDS-data-eeglab"

    cwd = Path(__file__).parents[0]
    BIDS_root = Path(
        f"/Users/dominik.welke/Work/02_projects/2023_EEGmanylabs/2023_11-resting-state-pilot/Questionnaire BIDS/{BIDS_folder}"
    )

    RAW_folder = Path(
        "/Users/dominik.welke/ownCloud - EEGManyLabs/MetaRep BU2/RestingStateSpinOff"
    )

    # init, if nonexisting
    if not BIDS_root.is_dir():
        init_folder(BIDS_root)

    # update CHANGES
    update_changes(BIDS_root, "- add resting state eeg data (eeglab .set).")

    # do
    for study in ["HajcakHolroyd2005"]:
        print("---")
        print(study)
        # labs = (BIDS_root.parents[0] / "sourcedata" / study).glob("*/")
        eeg_files = list((RAW_folder / study).glob("*/"))
        eeg_files.sort()
        labs.sort()
        participant_ids_tsv = list(
            pd.read_csv(BIDS_root / "participants.tsv", sep="\t").participant_id
        )
        participant_ids_eeg = []
        for lab in labs:
            print("-" + lab)
            for eeg_file in eeg_files:
                participant_id = "sub-" + eeg_file.name[-5:]
                if lab in participant_id:
                    # first copy over eeglab version somebody has created
                    src_path = eeg_file / "task-Resting" / "eeg"
                    src_files = list(src_path.glob("*"))
                    if sum([".set" in f.name[-4:] for f in src_files]) != 1:
                        print(f"no .set file found for {participant_id}")
                        continue
                    else:
                        print("--" + participant_id, f"({len(src_files)} files)")

                    dst_path = BIDS_root / participant_id / "eeg"
                    dst_path.mkdir(parents=True, exist_ok=True)
                    for fi in src_files:
                        ft = fi.name.split("_")[-1]
                        if ("electrodes" in ft) or ("coordsystem" in ft):
                            fo = dst_path / f"{participant_id}_{ft}"
                        else:
                            fo = dst_path / f"{participant_id}_task-{task}_{ft}"
                        # print(fo)
                        shutil.copy(fi, fo)  # For Python 3.8+.

                    try:
                        update_eeg_json(
                            BIDS_root,
                            participant_id,
                            task,
                            TaskName="EEGManyLabs Resting State",
                        )
                    except FileNotFoundError:
                        pass

                    participant_ids_eeg.append(participant_id)

        # clean up BIDS participant list
        missing = []
        print(
            "\nupdating BIDS participants.tsv (removing entries with missing eeg / adding entries with missing questionnaires):"
        )
        for participant_id in participant_ids_tsv:
            if participant_id not in participant_ids_eeg:
                missing.append(participant_id)
                drop_participant(BIDS_root, participant_id)
        for participant_id in participant_ids_eeg:
            if participant_id not in participant_ids_tsv:
                add_participant(
                    BIDS_root,
                    participant_id,
                    replication=study,
                    lab=participant_id[4:7],
                )

        # [print("\n"+s, "- no eeg file") for s in missing]
        # print(missing)

# validate BIDS
validate_bids(BIDS_root)
print("\ndone!")
