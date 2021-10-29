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
COCO_ANNOTATION_FORMAT = {"id","image_id","category_id","segmentation","area","bbox","iscrowd"}

class CocoWriter:
    def __init__(self, ann_file):
        self.coco = COCO(ann_file)
        