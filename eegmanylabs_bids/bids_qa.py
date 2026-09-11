import json
from pathlib import Path

import pandas as pd


def df_window(df, fname):

    with open(fname, "w") as f:
        df.to_html(f)


def eeg_metadata_to_pandas(
    BIDS_Root,
    keep_col=[],
    drop_col=["TaskName", "RecordingType", "TaskDescription", "CogAtlasID", "CogPOID"],
):
    """
    Generate a pandas DataFrame from BIDS participants.tsv and EEG metadata.

    This function reads participant information from participants.tsv and combines it
    with EEG metadata from *_eeg.json files. The resulting DataFrame is saved as an
    HTML table for visualization.

    :param BIDS_Root: Path to the BIDS root directory containing participants.tsv and *_eeg.json files
    :param keep_col: List of column names from participants.tsv to include in the output DataFrame ('participant_id' included by default)
    :param drop_col: List of EEG metadata fields to exclude from the output DataFrame (default includes common BIDS metadata fields)
    :return: None (saves HTML file with the combined metadata)
    """

    BIDS_Root = Path(BIDS_Root)
    if not isinstance(keep_col, list):
        raise TypeError("'keep_col' must be list")

    # Load participants.tsv
    participants_df = pd.read_csv(BIDS_Root / "participants.tsv", sep="\t")

    new_df = pd.DataFrame()
    # Load metadata from *_eeg.json files
    for ip, participant_id in enumerate(participants_df["participant_id"]):
        json_file_path = next(iter(BIDS_Root.rglob(f"{participant_id}/**/*_eeg.json")))
        eeg_json = json.loads(json_file_path.read_text())
        # Extract relevant metadata
        new_df.at[ip, "participant_id"] = participant_id
        for col_p in keep_col:
            new_df.at[ip, col_p] = participants_df.at[ip, col_p]
        for col_e, v in eeg_json.items():
            if col_e not in drop_col:
                new_df.at[ip, col_e] = str(v)

    # Save the DataFrame to a CSV file
    fname = Path(f"{BIDS_Root.name}_eegsidecar.html")
    df_window(new_df, fname)
    # fname.unlink()


if __name__ == "__main__":
    # fix HajcakHolroyd2005 replication eeg.jsons
    BIDS_Root = Path(
        "/Users/phtn595/Datasets/EEGManyLabs - gnode/replication/EEGManyLabs_Replication_HajcakHolroyd2005_Raw"
    )
    if False:  # already done
        eeg_metadata_to_pandas(
            BIDS_Root,
            keep_col=["site"],
        )

        for eeg_json in sorted(BIDS_Root.glob("sub*/**/*eeg.json")):
            d_old = json.loads(eeg_json.read_text())
            d_old["LeadInstitutionName"] = d_old["OrganisingIstitution"]
            d_old["InstitutionName"] = (
                d_old["RecordingInstitution"]
                if ("RecordingInstitution" in d_old)
                else d_old["InstitutionName"]
            )
            d_new = {
                k: d_old[k]
                for k in [
                    "TaskName",
                    "TaskDescription",
                    "CogAtlasID",
                    "CogPOID",
                    "LeadInstitutionName",
                    "InstitutionName",
                    "SamplingFrequency",
                    "EEGChannelCount",
                    "EOGChannelCount",
                    "ECGChannelCount",
                    "EMGChannelCount",
                    "EEGReference",
                    "PowerLineFrequency",
                    "EEGGround",
                    "EEGPlacementScheme",
                    "Manufacturer",
                    "CapManufacturer",
                    "HardwareFilters",
                    "SoftwareFilters",
                    "RecordingType",
                    "SoftwareVersions",
                ]
            }
            eeg_json.write_text(json.dumps(d_new, indent=4))

        # test again
        eeg_metadata_to_pandas(
            BIDS_Root,
            keep_col=["site"],
        )

        # rename elctrodes.tsv
        for electrodes_tsv in sorted(BIDS_Root.glob("sub*/*/*electrodes.tsv")):
            electrodes_tsv.move(
                electrodes_tsv.with_name(
                    electrodes_tsv.name.replace(
                        "_electrodes", "_space-EEGLAB_electrodes"
                    )
                )
            )
