# ==============================================================================
# File: read_image.py
# Project: FBL_OCR
# File Created: Monday, 27th July 2020 2:18:32 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 27th July 2020 4:06:35 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for using Tesseract to read a screenshot from a Fox Bet Live bet
# ==============================================================================

import os

import cv2
import matplotlib.pyplot as plt
import pytesseract
from pytesseract import Output


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


image_paths = listdir_fullpath("./Image_Data")

img = cv2.imread(image_paths[2])


# custom_config = '--0em 3 --psm 6'
# pytesseract.image_to_string(img, config=custom_config)


def get_greyscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_noise(image):
    return cv2.medianBlur(image, 5)


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# img = get_greyscale(img)
# img = remove_noise(img)
# img = thresholding(img)


# plt.imshow(img)


# boxes:
# def show_boxes(img):
d = pytesseract.image_to_data(img, output_type=Output.DICT)
n_boxes = len(d['level'])
for i in range(n_boxes):
    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

# cv2.imshow('img', img)
# cv2.waitKey(0)
