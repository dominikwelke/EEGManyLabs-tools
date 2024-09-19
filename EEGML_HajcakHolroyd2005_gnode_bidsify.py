"""
make gnode dataset from katpa (more) bids compatible
link: https://gin.g-node.org/katpa/Paul_et_al_Cortex_ManyLabs_Hajcak05

written by: Dominik Welke
18.9.2024
"""
import subprocess
import os

from pathlib import Path
from eegmanylabs_bids.bids_utils import validate_bids

def gitmove(fold: Path, fnew: Path, verbose=False):
    if fold.is_file():
        fnew.parent.mkdir(parents=True, exist_ok=True)
        cmd = f'git mv "{str(fold)}" "{str(fnew)}"'
        if verbose:
            print(cmd)
        _ = subprocess.run(
            cmd, shell=True, universal_newlines=True, check=True)
        #os.system(cmd)

root = Path('/Users/phtn595/Datasets/EEGManyLabs - gnode/Paul_et_al_Cortex_ManyLabs_Hajcak05').absolute()
print(root)

## update sub-id
token_old = 'sub-Doors'
token_new = 'sub-'
# change file+foldernames
for p in root.rglob(f"*{token_old}*"):
    pnew = Path(token_new.join(str(p).split(token_old)))
    p.rename(pnew)
    #gitmove(p, pnew)
    #print(pnew)

# change file content
allowed_types = ['.log', '.tsv', '.csv', '.txt']
for ftype in allowed_types:
    for p in root.rglob(f"*{ftype}"):
        #print(p)
        with p.open('r+') as f:
            txt = f.read()
            if token_old in txt:
                content_new = token_new.join(txt.split(token_old))
                #print(content_new)
                print(p)
                f.truncate(0)
                f.write(content_new)


## remove task-subfolder
token_old = '/task-Doors/'
token_new = '/'
# relocate files
for p in root.rglob(f"*{token_old}*"):
    pnew = Path(token_new.join(str(p).split(token_old)))
    p.rename(pnew)
    #gitmove(p, pnew)
    #print(pnew)

# delete empty directory
for p in root.rglob(f"*{token_old[:-1]}*"):
    p.rmdir()  # must be empty
    #print(p)
    

# move relevant files to bids root
files = [
    'dataset_description.json',
    'participants.json',
    'participants.tsv',
    'README.md',
    'LICENSE'
]

for f in files:
    f_old = root / f
    f_new = root / 'data' / f
    if f_old.exists():
        f_old.rename(f_new)
        #gitmove(f_old, f_new)
        if ('README' in str(f)) or ('LICENSE' in str(f)):
            f_old.write_text(f_new.read_text())


# check BIDS compatibility
validate_bids(root / 'data', verbose=True)
