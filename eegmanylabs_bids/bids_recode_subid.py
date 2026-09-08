import pandas as pd


def recode_dict(replication_code, name_list=None):
    if not isinstance(replication_code, str):
        raise ValueError("replication_code must be 'str'")
    if name_list is None:
        raise ValueError(
            "please provide a list of all sub-names following old convention"
        )

    # if providing a list of original labels
    if name_list:
        name_list = list(name_list)
        name_list = [oldid.split("sub-")[-1] for oldid in name_list]
        name_list.sort()
        data = {
            oldid: f"{replication_code}{i + 1:04d}" for i, oldid in enumerate(name_list)
        }

    return data


def recode_df(replication_code, name_list=None):
    data = recode_dict(replication_code=replication_code, name_list=name_list)
    return pd.DataFrame(dict(oldid=list(data.keys()), newid=list(data.values())))
