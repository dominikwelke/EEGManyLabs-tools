"""
test the parser functiionality without writing anything to disc

written by
Dominik Welke
d.welke@leeds.ac.uk
https://github.com/dominikwelke
"""

from pathlib import Path

from eegmanylabs_bids.replications.haycakholroyd2005.parse_phenotype import quest_parser


# settings
ROOT_DIR = Path("/Users/phtn595/Datasets/EEGManyLabs RestingState")
BIDS_ROOT = ROOT_DIR / "BIDS-data-edf"
RAW_FOLDER = Path("/Users/phtn595/Datasets/EEGManyLabs - Clean/src")


study = "HajcakHolroyd2005"
labs = [
    "BON",
    "CIM",
    "EUR",
    "GUF",
    "MSH",
    "TUD",
    "UCM",
    "UGE",
    "UHH",
    "UNL",
    "URE",
]

if (BIDS_ROOT / "participants.tsv").exists():
    mode = "update"
elif not BIDS_ROOT.is_dir():
    mode = "new"
else:
    raise ValueError

#########################
# test for specified labs
for lab in labs:
    lab_folder = RAW_FOLDER / study / lab
    print("-" + lab)
    try:
        res = quest_parser[lab](lab_folder)
        print("no errors")
        # print(res)
    except Exception as e:
        print(e)
