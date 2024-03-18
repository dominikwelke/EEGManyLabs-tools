""" dataset specific settings for BIDS conversion of EEGManyLabs RestingState data
"""

# EEG trigger (resting state paradigm)
event_id = {
	"start":70,
	"eyes open":1,
	"eyes close":2,
	"end":71
	}

# EEG setups
eeg_lab_specs = {
    "TUD":{
        "format":"vhdr",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "Brain Products",
            "ManufacturersModelName": "n/a",
            "CapManufacturer": "EasyCap",
            "CapManufacturersModelName": "n/a",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "Technical University Dresden, Germany",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "custom equidistant montage (No. 10)",
            "EEGReference": "AFF1h",
            "EEGGround": "AFF2h",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Bandpass": {
                    "Low cutoff (s)": 10,
                    "High cutoff (Hz)": 250
                }
            },
            "SoftwareVersions": "n/a",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
            
        }
    },
    "CIM":{
        "format":"vhdr",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "Brain Products",
            "ManufacturersModelName": "n/a",
            "CapManufacturer": "Brain Products",
            "CapManufacturersModelName": "acticap slim",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "Central Institute of Mental Health Mannheim, Germany",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10-10",
            "EEGReference": "Cz",
            "EEGGround": "AFz",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Bandpass": {
                    "Low cutoff (Hz)": 0.1,
                    "High cutoff (Hz)": 100
                }
            },
            "SoftwareVersions": "1.23.003",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
            
        }
    },
    "GUF":{
        "format":"vhdr",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "Brain Products",
            "ManufacturersModelName": "n/a",
            "CapManufacturer": "EasyCap",
            "CapManufacturersModelName": "n/a",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "Goethe University Frankfurt a.M., Germany",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10/20",
            "EEGReference": "Cz",
            "EEGGround": "FCz",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Bandpass": {
                    "Low cuttoff (s)": 10, 
                    "High cuttoff (Hz)": 100
                }
            },
            "SoftwareVersions": "1.23.003",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "MSH":{
        "format":"vhdr",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "Brain Products",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "Brain Products",
            "CapManufacturersModelName": "acticap snap",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "Medical School Hamburg, Germany",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10/20",
            "EEGReference": "FCz",
            "EEGGround": "AFz",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Bandpass": {
                    "Low cuttoff (s)": 10, 
                    "High cuttoff (Hz)": 1000
                }
            },
            "SoftwareVersions": "1.25.0101",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "BON":{
        "format":"bdf",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "Biosemi",
            "ManufacturersModelName": "n/a",
            "CapManufacturer": "Biosemi",
            "CapManufacturersModelName": "n/a",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "Bond University, Australia",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10-20",
            "EEGReference": "CMS/DRL",
            "EEGGround": "CMS/DRL",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Lowpass":{
                    "-3dB cutoff point (Hz)": 102,  # matches sfreq
                    "Filter type": "CIC (FIR)",
                    "Filter order": "5"
                }
            },
            "SoftwareVersions": "ActiView",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "EUR":{
        "format":"bdf",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "Biosemi",
            "ManufacturersModelName": "n/a",
            "CapManufacturer": "Biosemi",
            "CapManufacturersModelName": "n/a",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "Erasmus University Rotterdam, The Netherlands",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10-20",
            "EEGReference": "CMS/DRL",
            "EEGGround": "CMS/DRL",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Lowpass":{
                    "-3dB cutoff point (Hz)": 102,  # matches sfreq
                    "Filter type": "CIC (FIR)",
                    "Filter order": "5"
                }
            },
            "SoftwareVersions": "ActiView",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "UCM":{
        "format":"bdf",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "Biosemi",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "Biosemi",
            #"CapManufacturersModelName": "n/a",
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "CINPSI Neurocog UCMaule, Chile",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10-20",
            "EEGReference": "CMS/DRL",
            "EEGGround": "CMS/DRL",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Lowpass":{
                    "-3dB cutoff point (Hz)": 102,  # doesnt match sfreq
                    "Filter type": "CIC (FIR)",
                    "Filter order": "5"
                }
            },
            "SoftwareVersions": "ActiView",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "UGE":{
        "format":"bdf",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "Biosemi",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "Biosemi",
            #"CapManufacturersModelName": "n/a",
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "Ghent University, Belgium",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10-20",
            "EEGReference": "CMS/DRL",
            "EEGGround": "CMS/DRL",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Lowpass":{
                    "-3dB cutoff point (Hz)": 102,  # matches sfreq
                    "Filter type": "CIC (FIR)",
                    "Filter order": "5"
                }
            },
            "SoftwareVersions": "ActiView",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "UHH":{
        "format":"bdf",
        "line_freq": 50,
        "EEGReference":"CMS",
        "sidecar":{
            "Manufacturer": "Biosemi",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "Biosemi",
            #"CapManufacturersModelName": "n/a",
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "University Hamburg, Germany",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10-20",
            "EEGReference": "CMS/DRL",
            "EEGGround": "CMS/DRL",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Lowpass":{
                    "-3dB cutoff point (Hz)": 102,  # matches sfreq
                    "Filter type": "CIC (FIR)",
                    "Filter order": "5"
                }
            },
            "SoftwareVersions": "ActiView",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "UNL":{
        "format":"bdf",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "Bioemi",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "Biosemi",
            #"CapManufacturersModelName": "n/a",
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "Leiden University, Netherlands",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10-20",
            "EEGReference": "CMS/DRL",
            "EEGGround": "CMS/DRL",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Lowpass":{
                    "-3dB cutoff point (Hz)": 102,  # does not match sfreq!
                    "Filter type": "CIC (FIR)",
                    "Filter order": "5"
                }
            },
            "SoftwareVersions": "ActiView",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "URE":{
        "format":"vhdr",
        "line_freq": 50,
        "sidecar":{
            "Manufacturer": "NeurOne",
            #"ManufacturersModelName": "n/a",
            #"CapManufacturer": "n/a",
            #"CapManufacturersModelName": "n/a",
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            "InstitutionName": "University of Regensburg, Germany",
            #"InstitutionalDepartmentName": "n/a",
            "EEGPlacementScheme": "10-20",
            "EEGReference": "FCz",
            "EEGGround": "AFz",
            #"SoftwareFilters": "n/a",
            "HardwareFilters": {
                "Lowpass": {
                    "High cuttoff (Hz)": 250
                }
            },
            #"SoftwareVersions": "n/a",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    }
}

# corrupted files (parts missing etc) 
corrupted_files = {
    "HajcakHolroyd2005":[
        #BON01, BON03, BON11, GUF14, MSH08  # missing trials
        #CIM05  # too many trials (10 instead of 8)
        "Doors_BON07",  #  RS cut off (only end trigger present)
        "RestCIM14",  # .eeg file missing (.vhdr and .vmrk present)
        "Doors_MSH01",  # no resting state, only Doors
        "Doors_UNL01_2",  # split file
        "Doors_URE02",  # no resting state, only Doors
        ]}
