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

TODO: probe if trigger are transcribed correctly
"""
import pandas as pd
import json

# from mne_bids import BIDSPath, write_raw_bids
# from mne_bids.copyfiles import copyfile_eeglab

from pathlib import Path
from shutil import copy
from eegmanylabs_bids.bids_init import init_folder
from eegmanylabs_bids.bids_utils import (
    update_changes,
    drop_participant,
    add_participant,
    validate_bids,
)
from eegmanylabs_bids.bids_eeg import update_eeg_json

from mne import find_events, events_from_annotations, pick_events
from mne.io import read_raw_brainvision, read_raw_bdf
from mne_bids import BIDSPath, write_raw_bids
from mne_bids.copyfiles import copyfile_brainvision, copyfile_edf

# from mne.channels import make_standard_montage

from EEGML_RS_bids_eeg_setups import eeg_lab_specs, event_id, corrupted_files

# settings
export_format = "EDF"  # "EDF" / "BrainVision" - only used if crop=True
crop = True
consolidate = True  # clean missing participants from participants.tsv etc
verbose = "ERROR"
overwrite = False
changelog = True

ROOT_dir = Path("/Users/phtn595/Datasets/EEGManyLabs RestingState")
BIDS_root = ROOT_dir / f"BIDS-data-{export_format.lower()}"
BIDS_sourcedata = ROOT_dir / "sourcedata"  # BIDS_root / "sourcedata"
RAW_folder = Path("/Users/phtn595/Datasets/EEGManyLabs - Clean/src")

labs = [
    "BON",
    "CIM",
    "GUF",
    "MSH",
    "UCM",
    "UHH",
    "UNL",
    "URE",
]  # EUR not possible yet (missing trigger info); TUD+UGE skipped (missing channel layout)
task = "resting"
changelog_messages = [
    "- add sourcedata.",
    f"- add resting state eeg data (datasets cropped and converted to {export_format} format)."
    if crop
    else "- add resting state eeg data (original file format).",
    f"- finalize for labs: {labs}",
]


# event parser
def events_BRAINVISION(raw, event_id, beh_file=None):
    events, event_id_load = events_from_annotations(raw, verbose=verbose)
    for stim in (1, 2):
        assert event_id_load[f"Stimulus/S  {stim}"] == stim
    events = pick_events(events, include=list(event_id.values()))
    raw.set_annotations(None)
    return raw, events


def events_BIOSEMI(raw, event_id, beh_file=None):
    events = find_events(raw, initial_event=False, verbose=verbose)
    events = pick_events(events, include=list(event_id.values()))
    return raw, events


def events_EUR(raw, event_id, beh_file=None):
    # tbd
    events = find_events(raw, initial_event=False, verbose=verbose)
    events = pick_events(events, include=list(event_id.values()))
    return raw, events


def events_UHH(raw, event_id, beh_file=None):
    # apparently RS trigger are all 253 or 254 (not 1 or 2) :/ have to parse them
    # only in most files, though.. UHH30 onwards has correct trigger
    if isinstance(beh_file, list):
        raise NotImplementedError  # not implemented for split log files
    events = find_events(raw, initial_event=False, verbose=verbose)
    if "UHH3" in beh_file.name:
        # normal process
        events = pick_events(events, include=list(event_id.values()))
    else:
        # fix stim sequence
        events = pick_events(events, include=[70, 71, 253, 254])
        # real_seq = pd.read_csv(beh_file)["Anweisung"].dropna().to_list()
        # real_seq = [1 if "auf" in x else 2 if "zu" in x else "n/a" for x in real_seq]
        real_seq = pd.read_csv(beh_file)["Instruction_trials"].dropna().to_list()
        real_seq = [
            1 if "open" in x else 2 if "close" in x else "n/a" for x in real_seq
        ]
        wrong_idx = (events[:, 2] == 253) + (events[:, 2] == 254)
        assert len(real_seq) == events[wrong_idx].shape[0]
        events[wrong_idx, 2] = real_seq
    return raw, events


def events_UNL(raw, event_id, beh_file=None):
    events = find_events(raw, initial_event=False, verbose=verbose)
    try:
        events = pick_events(events, include=list(event_id.values()))
    except RuntimeError:
        events[:, 2] -= 32768  # dont ask me why..
        events = pick_events(events, include=list(event_id.values()))
    return raw, events


event_parser = dict(
    BON=events_BIOSEMI,
    CIM=events_BRAINVISION,
    EUR=events_EUR,
    GUF=events_BRAINVISION,
    MSH=events_BRAINVISION,
    TUD=events_BRAINVISION,
    UCM=events_BIOSEMI,
    UGE=events_BIOSEMI,
    UHH=events_UHH,
    UNL=events_UNL,
    URE=events_BRAINVISION,
)

# run script
if __name__ == "__main__":
    cwd = Path(__file__).parents[0]

    # init, if nonexisting
    if not BIDS_root.is_dir():
        init_folder(BIDS_root)

    # store participants.tsv, because it will be overwritten by write_raw_bids
    participant_tsv = pd.read_csv(
        BIDS_root / "participants.tsv", sep="\t", dtype={"age": "Int64"}
    )

    # do
    participant_ids_tsv = list(participant_tsv.participant_id)
    participant_ids_eeg = []
    for study in ["HajcakHolroyd2005"]:
        print("---")
        print(study)
        labs.sort()
        for lab in labs:
            print("-" + lab)
            if lab in ("UGE", "CIM"):
                eeg_files = list(
                    (RAW_folder / study / lab / "EEG_Data").glob(
                        f"[Rr][Ee][Ss][Tt]*.{eeg_lab_specs[lab]['format']}"
                    )
                )
            else:
                eeg_files = list(
                    (RAW_folder / study / lab / "EEG_Data").glob(
                        f"[Dd][Oo][Oo][Rr][Ss]*.{eeg_lab_specs[lab]['format']}"
                    )
                )
            eeg_files.sort()
            for eeg_file in eeg_files:
                participant_id = eeg_file.name.split(".")[0][-5:]
                if lab in participant_id:
                    if eeg_file.name.split(".")[0] in corrupted_files[study]:
                        print(f"--file {participant_id} corrupted!")
                        continue
                    else:
                        print(f"--sub-{participant_id}")

                    # filename to save
                    bids_path = BIDSPath(
                        subject=participant_id, task=task, root=BIDS_root
                    )
                    if not overwrite:
                        try:
                            if (
                                bids_path.fpath.with_suffix(".vhdr").exists()
                                or bids_path.fpath.with_suffix(
                                    "." + eeg_lab_specs[lab]["format"]
                                ).exists()
                                or bids_path.fpath.with_suffix(".edf").exists()
                            ):
                                participant_ids_eeg.append(participant_id)
                                continue
                        except FileNotFoundError:
                            pass  # file doesnt exist

                    # stim sequence filename
                    beh_file = list(
                        (RAW_folder / study / lab / "Behav_Data").glob(
                            f"*{participant_id}*Resting*.csv"
                        )
                    )
                    if len(beh_file) == 1:
                        beh_file = Path(beh_file[0])
                    elif len(beh_file) == 0:
                        beh_file = None
                    else:
                        beh_file = [Path(bf) for bf in beh_file]
                        # raise ValueError

                    # load data
                    if eeg_lab_specs[lab]["format"] == "vhdr":
                        raw = read_raw_brainvision(
                            eeg_file, preload=False, verbose=verbose
                        )
                        # extract metadata for sidecar
                        # WIP: i can get more, like software version etc
                        with eeg_file.open("r") as f:
                            pt = "Reference Channel Name ="
                            try:
                                eeg_lab_specs[lab]["sidecar"]["EEGReference"] = (
                                    [ll for ll in f.readlines() if pt in ll][0]
                                    .split(pt)[-1]
                                    .strip("\n")
                                )
                            except IndexError:
                                pass  # not present in vhdr file (e.g. MSH) - take from template
                            # EEGgnd = "Gnd"  # not in the vhdr file
                        with eeg_file.open("r") as f:
                            pt = ["brainvision recorder", "v."]
                            try:
                                eeg_lab_specs[lab]["sidecar"]["SoftwareVersions"] = [
                                    ll.lower().split("v.")[-1].strip()
                                    for ll in f.readlines()
                                    if pt[0] in ll.lower() and pt[1] in ll.lower()
                                ][0]
                            except IndexError:
                                pass  # not present in vhdr file (e.g. MSH) - take from template

                    elif eeg_lab_specs[lab]["format"] == "bdf":
                        raw = read_raw_bdf(
                            eeg_file, preload=False, verbose=verbose, infer_types=True
                        )
                        # extract metadata for sidecar
                        # pass
                    else:
                        raise NotImplementedError
                    print("sfreq =", raw.info["sfreq"], "Hz")

                    # get initial events
                    raw, events = event_parser[lab](raw, event_id, beh_file)

                    # specify power line frequency as required by BIDS
                    raw.info["line_freq"] = eeg_lab_specs[lab]["line_freq"]

                    # set ch_types (and montage)
                    update_ch_types = dict()
                    update_ch_types.update(
                        {
                            ch_name: "eog"
                            for ch_name in raw.info["ch_names"]
                            if "eog" in ch_name.lower()
                        }
                    )
                    update_ch_types.update(
                        {
                            ch_name: "eog"
                            for ch_name in raw.info["ch_names"]
                            if "he" in ch_name.lower() or "ve" in ch_name.lower()
                        }
                    )
                    update_ch_types.update(
                        {
                            ch_name: "misc"
                            for ch_name in raw.info["ch_names"]
                            if "exg" in ch_name.lower()
                        }
                    )  # biosemi
                    update_ch_types.update(
                        {
                            ch_name: "misc"
                            for ch_name in raw.info["ch_names"]
                            if "erg" in ch_name.lower()
                        }
                    )  # e.g. UHH
                    raw.set_channel_types(update_ch_types, verbose=verbose)
                    # WIP: dont set montage for now, as electrode positions might not be stored corectly anyway
                    # (see https://mne.discourse.group/t/adding-montage-and-fiducials-in-bids-format/7102/2)
                    # montage = make_standard_montage(eeg_lab_specs[lab]["CapManufacturersModelName"])
                    # raw.set_montage(montage)

                    # pick only resting-state events (in case there was a single recording session)
                    try:
                        startevent = pick_events(events, include=event_id["start"])
                        if startevent.shape[0] > 1:
                            print(
                                f"WARNING - more than 1 event with ID: {event_id["start"]} (n={startevent.shape[0]})"
                            )
                        tmin = startevent[0, 0] / raw.info["sfreq"]
                        events = events[events[:, 0] >= startevent[0, 0], :]
                    except RuntimeError:
                        print(f"WARNING - no event with ID: {event_id["start"]}")
                        tmin = 0.0
                    try:
                        endevent = pick_events(events, include=event_id["end"])
                        if endevent.shape[0] > 1:
                            print(
                                f"WARNING - more than 1 event with ID: {event_id["end"]} (n={endevent.shape[0]})"
                            )
                        tmax = endevent[0, 0] / raw.info["sfreq"]
                        events = events[events[:, 0] <= endevent[0, 0], :]
                    except RuntimeError:
                        print(f"WARNING - no event with ID: {event_id["end"]}")
                        if lab in [
                            "CIM",
                            "UGE",
                        ]:  # those have separate files, so no problem
                            tmax = raw.times[-1]
                        elif crop:
                            print(f"ERROR - skipping {participant_id}")
                            continue
                            raise ValueError(
                                "no trigger for end of resting state recording!"
                            )

                    events = pick_events(
                        events, include=[event_id["eyes open"], event_id["eyes close"]]
                    )
                    print(
                        f"n eyes open: {sum(events[:,2]==1)} n eyes close {sum(events[:,2]==2)}"
                    )

                    # harmonization (if wanted)
                    # resample + reref
                    save_kwargs = dict()
                    # WIP: dont resample
                    # WIP: apply Cz ref or dont reref? reref encouraged, at least for biosemi data. average however might be suboptimal, as noise can spill over and PREP would do a better job down the line.

                    # crop data (if wanted)
                    if crop:
                        save_kwargs.update(
                            dict(format=export_format, allow_preload=True)
                        )
                        pad = 30.0  # in s
                        tmin, tmax = (
                            tmin - pad if tmin > pad else 0.0,
                            tmax + pad if tmax < raw.times[-1] - pad else tmax,
                        )
                        # crop and fix events
                        raw.crop(tmin, tmax)
                        # events[:,0] -= int(tmin*raw.info["sfreq"])  # dont do this! mne-bids takes care of it itself

                    #  ..and save at new location using mne-bids
                    try:
                        write_raw_bids(
                            raw,
                            bids_path,
                            events=events,
                            event_id=event_id,
                            **save_kwargs,
                            overwrite=True,
                            verbose=verbose,
                        )
                    except FileExistsError:
                        pass

                    # tidy up
                    try:
                        update_eeg_json(
                            BIDS_root,
                            "sub-" + participant_id,
                            task,
                            TaskName="EEGManyLabs Resting State",
                            **eeg_lab_specs[lab]["sidecar"],
                        )
                    except FileNotFoundError:
                        pass

                    # copy sourcefile
                    # task_sourcefile = task if (lab in ["CIM", "UGE"]) else task+"+replicaton"
                    # bids_path_source = BIDS_sourcedata / ("sub-"+participant_id) / "eeg" / f"sub-{participant_id}_task-{task_sourcefile}_eeg.{eeg_lab_specs[lab]["format"]}"
                    bids_path_source = (
                        BIDS_sourcedata
                        / ("sub-" + participant_id)
                        / "eeg"
                        / eeg_file.name
                    )
                    if not bids_path_source.exists():
                        bids_path_source.parent.mkdir(parents=True, exist_ok=True)
                        if eeg_lab_specs[lab]["format"] == "vhdr":
                            copyfile_brainvision(eeg_file, bids_path_source)
                        elif eeg_lab_specs[lab]["format"] == "bdf":
                            copyfile_edf(eeg_file, bids_path_source)
                        if beh_file:
                            if isinstance(beh_file, Path):
                                # copy(beh_file, bids_path_source.parent / f"sub-{participant_id}_task-{task}_beh.csv")  # For Python 3.8+, otherwise must be str
                                copy(
                                    beh_file, bids_path_source.parent / beh_file.name
                                )  # For Python 3.8+, otherwise must be str
                            else:  # list
                                for i, bf in enumerate(beh_file):
                                    # copy(bf, bids_path_source.parent / f"sub-{participant_id}_task-{task}_beh_part-{i+1}.csv")  # For Python 3.8+, otherwise must be str
                                    copy(
                                        bf, bids_path_source.parent / bf.name
                                    )  # For Python 3.8+, otherwise must be str

                    participant_ids_eeg.append(participant_id)

    # restore participants.tsv
    participant_tsv.to_csv(
        BIDS_root / "participants.tsv", sep="\t", index=False, na_rep="n/a"
    )

    # remove stuff from participants.json that write_raw_bids added
    with (BIDS_root / "participants.json").open("r") as f:
        d = json.load(f)
    with (BIDS_root / "participants.json").open("w") as f:
        json.dump(
            {k: v for k, v in d.items() if k not in ["hand", "weight", "height"]},
            f,
            indent=4,
        )

    # clean up BIDS participant list - NOT NOW
    if consolidate:
        print(
            "\nupdating BIDS participants.tsv (removing entries with missing eeg / adding entries with missing questionnaires):"
        )
        for participant_id in participant_ids_tsv:
            if participant_id[4:] not in participant_ids_eeg:
                print(participant_id, "no eeg file")
                drop_participant(BIDS_root, participant_id)
        for participant_id in participant_ids_eeg:
            if "sub-" + participant_id not in participant_ids_tsv:
                print("sub-" + participant_id, "no entry in participants.tsv")
                add_participant(
                    BIDS_root,
                    "sub-" + participant_id,
                    replication=study,
                    lab=participant_id[:3],
                )


# validate BIDS
print("\nvalidate BIDS compliance")
validate_bids(BIDS_root, verbose=True)

# update CHANGES
if changelog:
    for m in changelog_messages:
        update_changes(BIDS_root, m)

print("\ndone!")
