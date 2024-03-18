import json
from pathlib import Path
import sys
import pandas as pd

from eegmanylabs_bids.BIDS_utils import sort_bids

def make_base_dummy(BIDS_root, sub_id, t=1):
	participants_tsv = pd.read_csv(BIDS_root / 'participants.tsv', sep='\t').to_dict('list')
	assert(sub_id not in list(participants_tsv["participant_id"]))
	
	# add
	print(participants_tsv)
	participants_tsv["participant_id"].append(sub_id)
	participants_tsv["species"].append("homo sapiens")
	participants_tsv["age"].append("n/a")
	participants_tsv["sex"].append("n/a")
	participants_tsv["handedness"].append("n/a")
	participants_tsv["replication"].append("HajcakHolroy2005")
	if isinstance(t,str):
		participants_tsv["lab"].append(t)
	# save
	pd.DataFrame(participants_tsv).to_csv(BIDS_root / "participants.tsv", sep='\t', index=False,na_rep='n/a')


def make_eeg_dummy(BIDS_root, sub_id):
	(BIDS_root / sub_id / "eeg").mkdir(parents=True)
	tasks = ['DOORS', 'REST']
	for task in tasks:
		dummy = BIDS_root / sub_id / "eeg" / f"sub-DUMMY01_task-{task}_eeg"
		dummy_json = {"TaskName":task,"EEGReference":"Cz","SamplingFrequency":1000,"PowerLineFrequency":50,"SoftwareFilters":"n/a"}
		with dummy.with_suffix(".edf").open('w+') as f:
			f.write("")
		with dummy.with_suffix(".json").open('w+') as f:
			json.dump(dummy_json,f,indent=4)


def make_phenotype_dummy(BIDS_root, sub_id):
	questionaires = ["EHI", "BFI_S", "BISBAS", "CES", "STAI_T_Y2", "PANAS", "KSS"]
	# JSONs
	with open('BIDS_template.json', 'r') as f:
		desc_json = json.load(f)["phenotype_jsons"]
	
	"""
	desc_json = {
		"EHI": {
		    "participant_id": {
		        "Description": "Unique participant identifier"
		    },
		    "ehi_handedness": {
		    	"LongName": "Participant handedness as determined by Edinburgh Handedness Inventory (EHI; original 10 item version)",
		        "Description": "see Oldfield (1971). The assessment and analysis of handedness: The Edinburgh inventory. Neuropsychologia 9(1):97-113",
		        "Levels": {
		            "l": "left",
		            "r": "right",
		            "a": "ambidextrous"
		        }
		    }
	    },
		"BFI_S": {
		    "participant_id": {
		        "Description": "Unique participant identifier"
		    },
		    "bfi_ext": {
		        "LongName": "BFI Extraversion Domain Subscore",
		        "Description": "can take values in range [3,15]. Collected using BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
		        "Units": "none"
		    },
		    "bfi_agr": {
		        "LongName": "BFI Agreeableness Domain Subscore",
		        "Description": "can take values in range [3,15]. Collected using BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
		        "Units": "none"
		    },
		    "bfi_con": {
		        "LongName": "BFI Conscientiousness Domain Subscore",
		        "Description": "can take values in range [3,15]. Collected using BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
		        "Units": "none"
		    },
		    "bfi_neg": {
		        "LongName": "BFI Negative Emotionality Domain Subscore",
		        "Description": "can take values in range [3,15]. Collected using BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
		        "Units": "none"
		    },
		    "bfi_ope": {
		        "LongName": "BFI Open-Mindedness Domain Subscore",
		        "Description": "can take values in range [3,15]. Collected using BFI-S Form, see Soto and John (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. Journal of Research in Personality, 68:69-81",
		        "Units": "none"
		    }
		},
		"BISBAS": {
		    "participant_id": {
		        "Description": "Unique participant identifier"
		    }
	    },
		"CES": {
		    "participant_id": {
		        "Description": "Unique participant identifier"
		    }
	    },
		"STAI_T_Y2": {
		    "participant_id": {
		        "Description": "Unique participant identifier"
		    }
	    },
		"PANAS": {
		    "participant_id": {
		        "Description": "Unique participant identifier"
		    },
		    "panas_NA": {
		        "LongName": "Positive Negative Affect Schedule (PANAS), Negative Affect Subscore",
		        "Description": "can take values in range [6-30]. Collected using PANAS SF, see Thompson (2007). Development and Validation of an Internationally Reliable Short-Form of the Positive and Negative Affect Schedule (PANAS). Journal of Cross-Cultural Psychology, 38(2):227-242",
		        "Units": "none"
		    },
		    "panas_PA": {
		        "LongName": "Positive Negative Affect Schedule (PANAS), Positive Affect Subscore",
		        "Description": "can take values in range [6-30]. Collected using PANAS SF, see Thompson (2007). Development and Validation of an Internationally Reliable Short-Form of the Positive and Negative Affect Schedule (PANAS). Journal of Cross-Cultural Psychology, 38(2):227-242",
		        "Units": "none"
		    }
		},
		"KSS": {
		    "participant_id": {
		        "Description": "Unique participant identifier"
		    }
	    }
	}
	"""

	# create files
	for q in questionaires:
		d_json = desc_json[q]
		file = BIDS_root / "phenotype" / q.lower()
		if not file.with_suffix('.json').exists(): 
			with file.with_suffix('.json').open('w+') as f:
				json.dump(d_json,f,indent=4)
		if not file.with_suffix('.tsv').exists(): 
			d_tsv = {k:["n/a"] for k in d_json.keys()}
			d_tsv["participant_id"] = [sub_id]
		else:
			d_tsv = pd.read_csv(file.with_suffix('.tsv'), sep='\t').to_dict('list')
			for k in d_json.keys():
				d_tsv[k].append(sub_id if (k=='participant_id') else 'n/a')

		pd.DataFrame(d_tsv).to_csv(file.with_suffix('.tsv'),sep='\t',index=False,na_rep='n/a')

# run
if __name__ == '__main__':
	BIDS_root = Path("./BIDS-data")
	print(sys.argv)
	if len(sys.argv) == 2:
		sub_id, t = sys.argv[-1], 1
	elif len(sys.argv) == 3:
		sub_id, t = sys.argv[-2:]
	else:
		raise ValueError
	assert(isinstance(sub_id,str))
	if 'sub-' not in sub_id:
		sub_id = 'sub-'+sub_id

	make_base_dummy(BIDS_root, sub_id, t)
	make_eeg_dummy(BIDS_root, sub_id)
	make_phenotype_dummy(BIDS_root, sub_id)

	sort_bids(BIDS_root)
