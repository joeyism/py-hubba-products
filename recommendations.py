import json
import os
filedir = os.path.dirname(os.path.abspath(__file__))

def get():
    return json.load(open(filedir + "/recommendations.json"))
