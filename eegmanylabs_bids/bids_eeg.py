"""
BIDS utils related to eeg data

written by
Dominik Welke
d.welke@leeds.ac.uk
https://github.com/dominikwelke
"""

from eegmanylabs_bids.bids_init import BIDS_template
import json


def update_eeg_json(BIDS_root, participant_id, task, **kwargs):
    """
    merge existing sidecar with our template.
    errors out if required fields are missing.
    """
    if not isinstance(kwargs, dict):
        kwargs = {}
    # load existing
    eeg_sidecar_file = (
        BIDS_root / participant_id / "eeg" / f"{participant_id}_task-{task}_eeg.json"
    )
    with eeg_sidecar_file.open("r") as f:
        eeg_sidecar_old = json.load(f)

    # small fixes
    if "RecordingInstitution" in eeg_sidecar_old.keys():
        eeg_sidecar_old["InstitutionName"] = eeg_sidecar_old["RecordingInstitution"]

    # merge
    eeg_sidecar_new = {
        k: (eeg_sidecar_old[k] if (k in eeg_sidecar_old.keys()) else v)
        for k, v in BIDS_template["eeg_json"].items()
    }
    _ = [
        print(
            f"entry '{k}' was present in sidecar, but not requested by BIDS template! - ignored"
        )
        for k in eeg_sidecar_old.keys()
        if k not in eeg_sidecar_new.keys()
    ]

    for k, v in kwargs.items():
        if k in eeg_sidecar_new.keys():
            eeg_sidecar_new[k] = v

    # check results
    assert sum([v == "REQUIRED" for v in eeg_sidecar_new.values()]) == 0

    # save new file
    with eeg_sidecar_file.open("w") as f:
        json.dump(eeg_sidecar_new, f, indent=4)
