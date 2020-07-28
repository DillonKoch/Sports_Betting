# ==============================================================================
# File: transfer_images.py
# Project: FBL_OCR
# File Created: Monday, 27th July 2020 3:10:36 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 28th July 2020 4:57:35 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Quick file for transferring bet screenshots from the "Pictures" folder
# ==============================================================================

import os
import sys
from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

pictures = os.listdir("/home/allison/Pictures")
pictures = [pic for pic in pictures if pic != "Wallpapers"]


for pic in pictures:
    current_path = "/home/allison/Pictures/" + pic
    new_path = ROOT_PATH + "/FBL_OCR/Image_Data/" + pic
    os.rename(current_path, new_path)
    print(f"Moved {pic} to {new_path}")
