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
COCO_BASIC_FORMAT_OBJD = ["info","images","annotations","categories","license"]
COCO_ANNOTATION_FORMAT = ["id","image_id","category_id","segmentation","area","bbox","iscrowd"]
COCO_IMAGE_FORMAT = ["id","width","height","file_name","license","flickr_url","coco_url","date_captured"]

class CocoWriter(COCO):
    def __init__(self, ann_file):
        COCO.__init__(self, ann_file)        
        
    def get_image_id(self, basename):
        id = None
        for image in self.dataset[COCO_BASIC_FORMAT_OBJD[1]]:
            if image.get(COCO_IMAGE_FORMAT[3]) == basename:
                id = image.get(COCO_IMAGE_FORMAT[0])
        return id