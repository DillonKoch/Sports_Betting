#!/bin/sh

cd Data_Collection
source run_scraping.sh
cd ..

cd Data_Cleaning
source clean_data.sh
cd ..

cd Modeling
python run_models.py
cd ..

cd Agents
python flat.py
python dynamic.py
cd ..

cd Frontend
python frontend.py
cd ..
