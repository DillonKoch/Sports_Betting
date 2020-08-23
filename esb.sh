#!/bin/sh

conda activate bet

cd ESB
python esb_perform_scrapes.py --league=NFL
python esb_perform_scrapes.py --league=NBA
python esb_perform_scrapes.py --league=NCAAF
python esb_perform_scrapes.py --league=NCAAB

cd ..
