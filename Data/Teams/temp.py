from os.path import abspath, dirname
import sys

import os


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

import json


def config(path):  # Property
    with open(path, 'r') as f:
        config = json.load(f)
    return config


paths = listdir_fullpath(ROOT_PATH + "/Teams/")
paths = [path for path in paths if '.json' in path]
for path in paths:
    new = {"Teams": {}}
    old = config(path)
    for team in old["Teams"].keys():
        new[team] = old["Teams"][team]["Other Names"]

    print(new)

    with open(path, "w") as f:
        json.dump(new, f)
