#!/bin/sh

cd Data_Collection
source run_scraping.sh
cd ..

cd Data_Cleaning
source clean_data.sh
cd ..

cd Modeling
source train_models.sh
cd ..