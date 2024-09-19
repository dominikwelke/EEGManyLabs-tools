from pathlib import Path
from shutil import copy2 as copy

# settings
export_format = "EDF"  # "EDF" / "BrainVision" - only used if crop=True
method = "owncloud"
overwrite = "all"  # "txt" (all but EEG files), "all" (all files)
verbose = "ERROR"

ROOT_dir = Path("/Users/phtn595/Datasets/EEGManyLabs RestingState")
BIDS_root = ROOT_dir / f"BIDS-data-{export_format.lower()}"
BIDS_sourcedata = ROOT_dir / "BIDS-sourcedata"  # BIDS_root / "sourcedata"

# do it
if __name__ == "__main__":
    if method == "owncloud":
        # upload via owncloud
        ROOT_target = (
            Path("/Users/phtn595/Datasets/EEGManyLabs - Cloud/BIDS-Datasets")
            / "EEGManyLabs RestingState HaycakHolroyd2005"
        )
        BIDS_target = ROOT_target / BIDS_root.name

        pattern = (
            "*[!.edf][!.eeg][!.vhdr][!.vmrk]"
            if (overwrite == "txt")
            else "*"
            if (overwrite == "all")
            else ""
        )

        counter = 0
        for p in BIDS_root.rglob(pattern):
            if (not p.is_dir()) and (p.name != ".DS_Store"):
                (BIDS_target / p.relative_to(BIDS_root)).parent.mkdir(
                    parents=True, exist_ok=True
                )
                copy(
                    p, BIDS_target / p.relative_to(BIDS_root)
                )  # For Python 3.8+, otherwise must be str
                counter += 1
    else:
        raise NotImplementedError

    print(f"done, copied {counter} files")
