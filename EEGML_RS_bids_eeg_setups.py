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
    "CIM":{
        "format":"vhdr",
        "line_freq": 50,
        "EEGReference": "Cz",
        "sidecar":{
            "Manufacturer": "Brain Products",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "EasyCap",
            "CapManufacturersModelName": "easycap-M1",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            #"InstitutionName": "n/a",
            #"InstitutionalDepartmentName": "n/a",
            #"EEGPlacementScheme": "n/a",
            #"EEGGround": "n/a",
            #"SoftwareFilters": "n/a",
            #"HardwareFilters": "n/a",
            #"SoftwareVersions": "n/a",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "GUF":{
        "format":"vhdr",
        "line_freq": 50,
        #"EEGReference": "Cz",
        "sidecar":{
            "Manufacturer": "Brain Products",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "n/a",
            "CapManufacturersModelName": "n/a",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            #"InstitutionName": "n/a",
            #"InstitutionalDepartmentName": "n/a",
            #"EEGPlacementScheme": "n/a",
            #"EEGGround": "n/a",
            #"SoftwareFilters": "n/a",
            #"HardwareFilters": "n/a",
            #"SoftwareVersions": "n/a",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "MSH":{
        "format":"vhdr",
        "line_freq": 50,
        #"EEGReference": "Cz",
        "sidecar":{
            "Manufacturer": "Brain Products",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "n/a",
            "CapManufacturersModelName": "n/a",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            #"InstitutionName": "n/a",
            #"InstitutionalDepartmentName": "n/a",
            #"EEGPlacementScheme": "n/a",
            #"EEGGround": "n/a",
            #"SoftwareFilters": "n/a",
            #"HardwareFilters": "n/a",
            #"SoftwareVersions": "n/a",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    },
    "BON":{
        "format":"bdf",
        "line_freq": 50,
        "EEGReference":"CMS",
        "sidecar":{
            "Manufacturer": "Biosemi",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "Biosemi",
            "CapManufacturersModelName": "biosemi32",
        }
    },
    "UGE":{
        "format":"bdf",
        "line_freq": 50,
        "EEGReference":"CMS",
        "sidecar":{
            "Manufacturer": "Biosemi",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "Biosemi",
            "CapManufacturersModelName": "biosemi64",
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
            "CapManufacturersModelName": "biosemi64",
        }
    },
    "UNL":{
        "format":"bdf",
        "line_freq": 50,
        "EEGReference":"CMS",
        "sidecar":{
            "Manufacturer": "Biosemi",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "Biosemi",
            "CapManufacturersModelName": "biosemi64",
        }
    },
    "URE":{
        "format":"vhdr",
        "line_freq": 50,
        #"EEGReference": "Cz",
        "sidecar":{
            "Manufacturer": "NeurOne",
            #"ManufacturersModelName": "n/a",
            "CapManufacturer": "n/a",
            "CapManufacturersModelName": "n/a",
            # rest tbd
            #"TaskDescription": "n/a",
            #"Instructions": "n/a",
            #"InstitutionName": "n/a",
            #"InstitutionalDepartmentName": "n/a",
            #"EEGPlacementScheme": "n/a",
            #"EEGGround": "n/a",
            #"SoftwareFilters": "n/a",
            #"HardwareFilters": "n/a",
            #"SoftwareVersions": "n/a",
            #"DeviceSerialNumber": "n/a",
            #"HeadCircumference": "n/a",
        }
    }
}

# corrupted files (parts missing etc) 
corrupted_files = {"HajcakHolroyd2005":["RestCIM14", "Doors_UNL01_2"]}
