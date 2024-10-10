"""
test the parser functiionality without writing anything to disc

written by
Dominik Welke
d.welke@leeds.ac.uk
https://github.com/dominikwelke
"""
from pathlib import Path


from EEGML_RS_bids_phenotype import (
    parse_phenotype_BON,
    parse_phenotype_EUR,
    parse_phenotype_TUD,
    parse_phenotype_UGE,
    parse_phenotype_UHH,
    parse_phenotype_UNL,
    parse_phenotype_UCM,
)

# settings
ROOT_dir = Path("/Users/phtn595/Datasets/EEGManyLabs RestingState")
BIDS_root = ROOT_dir / "BIDS-data-edf"
BIDS_sourcedata = ROOT_dir / "BIDS-sourcedata"  # BIDS_root / "sourcedata"
RAW_folder = Path("/Users/phtn595/Datasets/EEGManyLabs - Clean/src")


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
]  # UCM, EUR not (fully) possible yet (missing questionnaire data)

quest_parser = dict(
    BON=parse_phenotype_BON,
    CIM=parse_phenotype_UHH,
    EUR=parse_phenotype_EUR,
    GUF=parse_phenotype_UHH,
    MSH=parse_phenotype_UHH,
    TUD=parse_phenotype_TUD,
    UCM=parse_phenotype_UCM,
    UGE=parse_phenotype_UGE,
    UHH=parse_phenotype_UHH,
    UNL=parse_phenotype_UNL,
    URE=parse_phenotype_UHH,
)

if (BIDS_root / "participants.tsv").exists():
    mode = "update"
elif not BIDS_root.is_dir():
    mode = "new"
else:
    raise ValueError

#########################
# test for specified labs
for lab in labs:
    lab_folder = RAW_folder / study / lab
    print("-" + lab)
    try:
        res = quest_parser[lab](lab_folder)
        print("no errors")
        # print(res)
    except Exception as e:
        print(e)
