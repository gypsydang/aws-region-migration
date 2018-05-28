#!/usr/bin/python
# -*- coding: utf8 -*-

import json

def load_json_from_file(filename):
    return json.load(open(filename))

def write_json_to_file(filename, data):
    with open(filename,'w') as f_obj:
        json.dump(data, f_obj)
