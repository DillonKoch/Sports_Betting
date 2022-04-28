#!/bin/sh

python clean_espn.py
python clean_sbo.py
python merge_datasets.py
python modeling_data.py

python label_predictions.py
python label_agents.py
