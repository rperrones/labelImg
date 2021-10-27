#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 18:36:13 2021

@author: ricardo perrone
e-mail: rperrones@yahoo.com
"""
from libs.constants import DEFAULT_ENCODING
from pycocotools.coco import COCO

COCO_EXT = '.json'
ENCODE_METHOD = DEFAULT_ENCODING
COCO_BASIC_FORMAT ={"info","image","annotation","license"}

class CocoWriter:
    def __init__(self, ann_file):
        self.coco = COCO(ann_file)
        
    def check_coco_basic_format(self):
        count = 0
        for key in self.coco.dataset.keys():
            if key in COCO_BASIC_FORMAT:
                count += 1
        if count < 4:
            return False
        else:
            return True