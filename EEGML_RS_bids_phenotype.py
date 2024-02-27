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
import json	
import pandas as pd
import numpy as np

from pathlib import Path
from eegmanylabs_bids.bids_init import init_folder, BIDS_template
from eegmanylabs_bids.bids_utils import update_changes, purge_folder, sort_bids, validate_bids
from eegmanylabs_bids.bids_phenotype import (
	parse_bfi_s,parse_bisbas,parse_cesd,parse_ehi,
	parse_kss,parse_panas_state,parse_stai_state,parse_stai_trait
	)

# helper defs
def _merge_duplicates(data_in):
	"""
	merge duplicate lines for participant_ids; takes the first not NaN value
	"""
	return data_in.groupby('participant_id').first().reset_index()


def _rescale_data(data_in, minmax_in, minmax_out):
	data_out = data_in.apply(pd.to_numeric, errors='coerce')
	# reference to 0
	data_out -= minmax_in[0]
	# scale
	scalefactor = np.diff(minmax_out) / np.diff(minmax_in)
	data_out *=  scalefactor[0]
	# reference to new min
	data_out += minmax_out[0]
	return data_out


# lab specidific parser
def parse_phenotype_BON(folder):
	omitlines = 3

	d = pd.read_csv(folder / "phenotype" / "BON_Self_Report.csv")
	#d_info = d[:omitlines]
	d = d[omitlines:].reset_index(drop=True)

	d["participant_id"] = [s[6:] for s in list(d["PID"])]
	d = _merge_duplicates(d)
	sub_ids = list(d["participant_id"])

	# basics
	age = list(d["Age"])
	sex = [s if not isinstance(s, str) else s.lower()[0] for s in d["Gender"]]

	# handedness
	d = d.rename(columns={f"EHI_{i}_{j+1}":f"EHI_{k}_{i}" for i in range(1,11) for j,k in enumerate(['L','R'])})
	EHI_data = parse_ehi(d)

	# BFI
	BFI_data = parse_bfi_s(d)  # 1-5 scale, subtract 3

	# PANAS
	d = d.rename(columns={f"PANAS_{i}":f"PANAS_S_{i}" for i in range(1,21)})
	PANAS_data = parse_panas_state(d)
	
	# KSS
	KSS_data = parse_kss(d)

	# CES-D
	d = d.rename(columns={f"CES{i}":f"CESD_{i}" for i in range(1,21)})
	for col in [f"CESD_{i}" for i in range(1,21)]:
		d[col] = d[col].apply(pd.to_numeric, errors='coerce')-1  # transfer to [0-3 coding]
	CES_data = parse_cesd(d)

	# BISBAS
	BISBAS_data = parse_bisbas(d)

	# STAI-T
	STAI_data = pd.DataFrame({
		"stai_t_state":parse_stai_state(d),
		"stai_t_trait":parse_stai_trait(d)
		})
	return sub_ids, age, sex, EHI_data, BFI_data, PANAS_data, KSS_data, CES_data, BISBAS_data, STAI_data


def parse_phenotype_UGE(folder):
	d = pd.read_csv(folder / "phenotype" / "questionnaires" / "complete_transcribe_questionnaires_120124 DWaccepted.csv", sep=";")
	#d_info = d[:omitlines]

	d = _merge_duplicates(d)
	sub_ids = list(d["participant_id"])

	# basics
	age, sex = [],[]
	for sub_id in sub_ids:
		UGE_root = Path("/Users/dominik.welke/ownCloud - EEGManyLabs/MetaRep BU2/RestingStateSpinOff/HajcakHolroyd2005/")
		try:
			dd = pd.read_csv(UGE_root / f"sub-Doors{sub_id}/task-Doors/beh/sub-Doors{sub_id}_task-Doors_beh.txt", sep="\t")
			age.append(dd.age[0])
			sex.append(dd.gndr[0])
		except FileNotFoundError:
			age.append("n/a")
			sex.append("n/a")
	
	# handedness
	d = d.rename(columns={f"EHI_{i}_{k}":f"EHI_{k}_{i}" for i in range(1,11) for k in ['L','R']})
	EHI_data = parse_ehi(d)

	# BFI - HERE THEY USED A 1-7 scale
	BFI_data = parse_bfi_s(d)  # 1-7 scale, subtract 4

	# PANAS
	d = d.rename(columns={f"PANAS_{i}":f"PANAS_S_{i}" for i in range(1,21)})
	PANAS_data = parse_panas_state(d)

	# KSS
	KSS_data = parse_kss(d)

	# CES
	d = d.rename(columns={f"CES{i}":f"CESD_{i}" for i in range(1,21)})
	for col in [f"CESD_{i}" for i in range(1,21)]:
		d[col] = d[col]-1  # transfer to [0-3 coding]
	CES_data = parse_cesd(d)

	# BISBAS
	BISBAS_data = parse_bisbas(d)

	# STAI-T
	d = d.rename(columns={f"STAI_{i}":f"STAI_S_{i}" if (i <=20) else f"STAI_T_{i-20}" for i in range(1,41)})
	STAI_data = pd.DataFrame({
		"stai_t_state":parse_stai_state(d),
		"stai_t_trait":parse_stai_trait(d)
		})
	return sub_ids, age, sex, EHI_data, BFI_data, PANAS_data, KSS_data, CES_data, BISBAS_data, STAI_data


def parse_phenotype_UHH(folder):
	keys = list(pd.read_csv(folder.parents[0] / "UHH_Hamburg" / "phenotype" / "After_Codes.csv").keys())
	d = pd.read_csv(folder.parents[0] / "UHH_Hamburg" / "phenotype" / "After_FullText.csv")
	d = d.rename(columns={list(d.keys())[i]:keys[i] for i in range(len(keys))})

	lab = str(folder.name)[:3]
	d = d.loc[d["VpCode2"].str.contains(lab).fillna(False)].reset_index(drop=True)

	if lab in ["URE", "GUF"]:
		d["participant_id"] = [f"{lab}{i:02d}" for s in d["VpCode2"] for i in range(99) if (f"{i:02d}" in s)]
	else:
		d["participant_id"] = [s[-5:] for s in d["VpCode2"]]
	d = _merge_duplicates(d)
	sub_ids = list(d["participant_id"])

	# basics
	age = list(d["Alter"])
	sex = [s if not isinstance(s, str) else "f" if (s.lower()[0] == "w") else s.lower()[0] for s in d["Geschlecht"]]

	# handedness
	EHI_dict_R = {"immer rechts, nie links":2, "meistens rechts":1, "rechts und links gleich häufig":0, "meistens links":0, "immer links, nie rechts":0, "keine Angabe":"n/a", 99:'n/a'}
	EHI_dict_L = {"immer rechts, nie links":0, "meistens rechts":0, "rechts und links gleich häufig":0, "meistens links":1, "immer links, nie rechts":2, "keine Angabe":"n/a", 99:'n/a'}
	for i in range(1,11):
		d[f"EHI_R_{i}"] = d[f"EHI1[SQ{i:03d}]"].fillna(99).apply(lambda x: EHI_dict_R[x])
		d[f"EHI_L_{i}"] = d[f"EHI1[SQ{i:03d}]"].fillna(99).apply(lambda x: EHI_dict_L[x])
	EHI_data = parse_ehi(d)

	# BFI
	d = d.rename(columns={f"BFI1[SQ{i:03d}]":f"BFI_{i}" for i in range(1,16)})
	for col in [f"BFI_{i}" for i in range(1,16)]:
		d[col] = d[col].apply(lambda x: "n/a" if str(x) in ["nan", "na", "NaN", "None"] else str(x)[0])
	BFI_data = parse_bfi_s(d)

	# PANAS
	for i in range(1,21):  # fill with n/a
		d[f"PANAS_S_{i}"] = ['n/a']*len(d)
	PANAS_data = parse_panas_state(d)
	
	# KSS
	d["KSS"] = ['n/a'] * len(d)  # not done
	KSS_data = parse_kss(d)

	# CES
	d = d.rename(columns={f"CES1[SQ{i:03d}]":f"CESD_{i}" for i in range(1,21)})
	CES_dict = {
		'Überhaupt nicht oder weniger als 1 Tag':0,
		"1 bis 2 Tage":1,
		"3 bis 4 Tage":2,
		"5 bis 7 Tage":3,
		"Fast jeden Tag in den letzten 2 Wochen":3
		}
	for col in [f"CESD_{i}" for i in range(1,21)]:
		d[col] = d[col].apply(lambda x: "n/a" if str(x) in ["nan", "na", "NaN", "None"] else CES_dict[x])
	CES_data = parse_cesd(d)

	# BISBAS
	d = d.rename(columns={f"BISBAS1[SQ{i:03d}]":f"BISBAS_{i}" for i in range(1,25)})
	BISBAS_dict = {
		"trifft für mich gar nicht zu":4,
		"trifft für mich eher nicht zu":3,
		"trifft für mich eher zu":2,
		"trifft für mich genau zu":1,
		"Very false for me":4,
		"Somewhat false for me":3,
		"Somewhat true for me":2,
		"Very true for me":1
		}
	for col in [f"BISBAS_{i}" for i in range(1,25)]:
		d[col] = d[col].apply(lambda x: "n/a" if str(x) in ["nan", "na", "NaN", "None"] else BISBAS_dict[x])
	BISBAS_data = parse_bisbas(d)

	# STAI-T
	for i in range(1,21):  # fill with n/a
		d[f"STAI_S_{i}"] = ['n/a']*len(d)
		d[f"STAI_T_{i}"] = ['n/a']*len(d)

	STAI_data = pd.DataFrame({
		"stai_t_state":parse_stai_state(d),
		"stai_t_trait":parse_stai_trait(d)
		})
	
	return sub_ids, age, sex, EHI_data, BFI_data, PANAS_data, KSS_data, CES_data, BISBAS_data, STAI_data


def parse_phenotype_UNL(folder):
	omitlines = 1
	d1 = pd.read_csv(folder / "phenotype" / "UNL_Compiled_1.csv", sep=";")
	#d1_info = d1[:omitlines]
	d1 = d1[omitlines:].reset_index(drop=True)
	d2 = pd.read_csv(folder / "phenotype" / "UNL_Compiled_2.csv", sep=";")
	#d2_info = d2[:omitlines]
	d2 = d2[omitlines:].reset_index(drop=True)
	
	# basics
	sub_ids = [s[6:] for s in list(d1["Participant_number"])]
	age = list(d1["Age"])
	sex = ["f" if (s.lower() in ['vrouw', 'female']) else "m" if (s.lower() in ["man", "male"]) else s for s in d1["Gender"]]

	# handedness
	EHI_dict_R = {"Rechterhand sterke voorkeur":2, "Rechterhand":1, "Geen voorkeur":0, "Linkerhand":0, "Linkerhand sterke voorkeur":0,"Right hand strong preference":2, "Right hand":1, "Indifferent":0,"Left hand":0,"Left hand strong preference":0}
	EHI_dict_L = {"Rechterhand sterke voorkeur":0, "Rechterhand":0, "Geen voorkeur":0, "Linkerhand":1, "Linkerhand sterke voorkeur":2,"Right hand strong preference":0, "Right hand":0, "Indifferent":0,"Left hand":1,"Left hand strong preference":2}#0, 0, 0, 1, 2, 0, 0, 0, 1, 2
	for i in range(1,11):
		d2[f"EHI_R_{i}"] = d2[f"Handedness#1_{i}"].apply(lambda x: EHI_dict_R[x])
		d2[f"EHI_L_{i}"] = d2[f"Handedness#1_{i}"].apply(lambda x: EHI_dict_L[x])
	EHI_data = parse_ehi(d2)

	# BFI
	d2 = d2.rename(columns={f"BigFive-15_{i}":f"BFI_{i}" for i in range(1,16)})
	BFI_data = parse_bfi_s(d2)  # 1-5 scale. subtract 3

	# PANAS
	d1 = d1.rename(columns={f"PANAS State Mood_{i}":f"PANAS_S_{i}" for i in range(1,21)})
	PANAS_data = parse_panas_state(d1)

	# KSS
	d1 = d1.rename(columns={"KSQ-2":"KSS"})
	d1["KSS"] = d1["KSS"].apply(lambda x: x[0])
	KSS_data = parse_kss(d1)

	# CES
	d2 = d2.rename(columns={f"CES-D_{i}":f"CESD_{i}" for i in range(1,21)})
	CES_dict = {
		"Zelden of nooit (minder dan 1 dag)":0,
		"Rarely or none of the time (less than 1 day)":0,
		"Soms of weinig (1-2 dagen)":1,
		"Some or a little of the time (1-2 days)":1,
		"Regelmatig (3-4 dagen)":2,
		"Occasionally or a moderate amount of time (3-4 days)":2,
		"Meestal of altijd (5-7 dagen)":3,
		"Most or all of the time (5-7 days)":3
		}
	for col in [f"CESD_{i}" for i in range(1,21)]:
		d2[col] = d2[col].apply(lambda x: "n/a" if str(x) in ["nan", "na", "NaN", "None"] else CES_dict[x])
	CES_data = parse_cesd(d2)

	# BISBAS
	d2 = d2.rename(columns={f"BIS-BAS_{i}":f"BISBAS_{i}" for i in range(1,25)})
	BISBAS_dict = {
		"Helemaal mee oneens":4,
		"Beetje mee oneens":3,
		"Beetje mee eens":2,
		"Helemaal eens":1,
		"Very false for me":4,
		"Somewhat false for me":3,
		"Somewhat true for me":2,
		"Very true for me":1
		}
	for col in [f"BISBAS_{i}" for i in range(1,25)]:
		d2[col] = d2[col].apply(lambda x: "n/a" if str(x) in ["nan", "na", "NaN", "None"] else BISBAS_dict[x])
	BISBAS_data = parse_bisbas(d2)

	# STAI-T
	d1 = d1.rename(columns={f"STAI-Part-1_{i}":f"STAI_S_{i}" for i in range(1,21)})
	d1 = d1.rename(columns={f"STAI-Part-2_{i}":f"STAI_T_{i}" for i in range(1,21)})
	STAI_data = pd.DataFrame({
		"stai_t_state":parse_stai_state(d1),
		"stai_t_trait":parse_stai_trait(d1)
		})
	
	return sub_ids, age, sex, EHI_data, BFI_data, PANAS_data, KSS_data, CES_data, BISBAS_data, STAI_data


# run script
if __name__=="__main__":
	BIDS_folder = "BIDS-data-brainvision"
	BIDS_root = Path(f"/Users/phtn595/Datasets/WIP/{BIDS_folder}")

	cwd = Path(__file__).parents[0]
	
	# init, if nonexisting
	if not BIDS_root.is_dir():
		init_folder(BIDS_root)

	# clean up
	purge = True
	if purge:
		purge_folder(BIDS_root)

	# update CHANGES
	update_changes(BIDS_root, "- add questionnaires to phenotype folder.")

	# do
	for study in ["HajcakHolroyd2005"]:
		print("---")
		print(study)
		labs = (BIDS_root.parents[0] / "sourcedata" / study).glob("*/")
		for lab_folder in labs:
			lab = str(lab_folder.name)[:3]
			print("-"+lab)
			if lab == ".DS":
				continue
			elif lab in ["UGE", "UNL", "BON"]:
				parsefun = locals()[f"parse_phenotype_{lab}"]
				sub_ids, age, sex, EHI, BFI, PANAS_STATE, KSS, CES, BISBAS, STAI = parsefun(lab_folder)
				handedness, EHI_LQ = list(EHI['EHI_handedness']), list(EHI['EHI_LQ'])
			elif lab in ["UHH", "CIM", "MSH", "GUF", "URE"]:
				sub_ids, age, sex, EHI, BFI, PANAS_STATE, KSS, CES, BISBAS, STAI = parse_phenotype_UHH(lab_folder)
				handedness, EHI_LQ = list(EHI['EHI_handedness']), list(EHI['EHI_LQ'])
			else:
				sub_ids = []
			for i, sub_label in enumerate(sub_ids):
				participants_tsv = pd.read_csv(BIDS_root / 'participants.tsv', sep='\t').to_dict('list')
				if sub_label in list(participants_tsv["participant_id"]):
					print(f"--{sub_label} already in data")
					continue
				elif "test" in sub_label.lower():
					print(f"--{sub_label} skipped")
					continue
				else:
					print("--"+sub_label)
				# fill participants.tsv
				participants_tsv["participant_id"].append("sub-"+sub_label)
				participants_tsv["species"].append("homo sapiens")
				participants_tsv["age"].append(age[i])
				participants_tsv["sex"].append(sex[i])
				participants_tsv["handedness"].append(handedness[i])
				participants_tsv["replication"].append(study)
				participants_tsv["lab"].append(lab)
				pd.DataFrame(participants_tsv).to_csv(BIDS_root / "participants.tsv", sep='\t', index=False,na_rep='n/a')

				# phenotype (questionnaires)
				questionaires = ["EHI", "BFI_S", "BISBAS", "CES", "STAI_T", "PANAS_STATE", "KSS"]
				# JSONs
				desc_json = BIDS_template["phenotype_jsons"]
				for q in questionaires:
					d_json = desc_json[q]
					file = BIDS_root / "phenotype" / q.lower()
					if not file.with_suffix('.json').exists(): 
						with file.with_suffix('.json').open('w+') as f:
							json.dump(d_json,f,indent=4)
					# get tsv
					if not file.with_suffix('.tsv').exists(): 
						d_tsv = {k:[] for k in d_json.keys()}
						#d_tsv = {k:['n/a'] for k in d_json.keys()}
						#d_tsv["participant_id"] = [sub_id]
					else:
						d_tsv = pd.read_csv(file.with_suffix('.tsv'), sep='\t').to_dict('list')
						#for k in d_json.keys():
						#	d_tsv[k].append(sub_id if (k=='participant_id') else 'n/a')
					
					#modify
					d_tsv["participant_id"].append("sub-"+sub_label)					
					if q == "EHI":
						d_tsv["ehi_lq"].append(EHI_LQ[i])
						d_tsv["ehi_handedness"].append(handedness[i])
					elif q == "KSS":
						d_tsv["kss"].append(KSS[i])
					elif q == "CES":
						d_tsv["ces_d"].append(CES[i])
					elif q == "BISBAS":
						for k in d_json.keys():
							if k!='participant_id':
								d_tsv[k].append(BISBAS[k][i])
					elif q == "BFI_S":
						for k in d_json.keys():
							if k!='participant_id':
								d_tsv[k].append(BFI[k][i])
					elif q == "PANAS_STATE":
						for k in d_json.keys():
							if k!='participant_id':
								d_tsv[k].append(PANAS_STATE[k][i])
					elif q == "STAI_T":
						for k in d_json.keys():
							if k!='participant_id':
								d_tsv[k].append(STAI[k][i])
					else:
						for k in d_json.keys():
							if k!='participant_id':
								d_tsv[k].append('n/a')

					#print(d_tsv)
					pd.DataFrame(d_tsv).to_csv(file.with_suffix('.tsv'),sep='\t',index=False,na_rep='n/a', float_format='%.1f')

	# validate BIDS
	validate_bids(BIDS_root)

	# clean up and leave
	sort_bids(BIDS_root)
	print("\ndone!")
