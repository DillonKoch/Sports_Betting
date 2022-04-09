#!/bin/sh
python clean_espn.py
python clean_sbo.py
python merge_datasets.py
python modeling_data.py
