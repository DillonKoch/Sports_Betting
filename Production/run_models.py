# ==============================================================================
# File: run_models.py
# Project: allison
# File Created: Saturday, 21st August 2021 8:09:02 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 21st August 2021 8:09:03 pm
# Modified By: Dillon Koch
# -----
#
# -----
# running saved models on upcoming games for all leagues
# saving data to TODO fill in
# ==============================================================================

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)
