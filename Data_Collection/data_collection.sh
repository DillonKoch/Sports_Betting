#!/bin/sh

# cd ~/Documents/GITHUB/Sports_Betting/Data_Collection/
cd "$(dirname "$0")";
CWD="$(pwd)"
echo $CWD

python esb.py
python sbro.py
python covers.py
