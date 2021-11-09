#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 18:36:13 2021

@author: ricardo perrone
e-mail: rperrones@yahoo.com
"""
from libs.constants import DEFAULT_ENCODING
from pycocotools.coco import COCO
from collections import defaultdict
import time

COCO_EXT = '.json'
ENCODE_METHOD = DEFAULT_ENCODING
COCO_BASIC_FORMAT_OBJD = ["info","images","annotations","categories","license"]
COCO_ANNOTATION_FORMAT = ["id","image_id","category_id","segmentation","area","bbox","iscrowd"]
COCO_IMAGE_FORMAT = ["id","width","height","file_name","license","flickr_url","coco_url","date_captured"]
COCO_CATEGORY_FORMAT = ["id","name","supercategory"]

class CocoWriter(COCO):
    def __init__(self, dataset):
        """
        This version was adapted from pycocotools - Constructor of Microsoft COCO helper class for reading and visualizing annotations.
        :param annotation_file (str): location of annotation file
        :param image_folder (str): location to the folder that hosts images.
        :return:
        """
        # load dataset
        self.dataset,self.anns,self.cats,self.imgs = dict(),dict(),dict(),dict()
        self.imgToAnns, self.catToImgs = defaultdict(list), defaultdict(list)
        print('loading annotations into memory...')
        tic = time.time()
        assert type(dataset)==dict, 'annotation file format {} not supported'.format(type(dataset))
        print('Done (t={:0.2f}s)'.format(time.time()- tic))
        self.dataset = dataset
        self.createIndex()
        
    def get_image_id(self, basename):
        id = None
        for image in self.dataset[COCO_BASIC_FORMAT_OBJD[1]]:
            if image.get(COCO_IMAGE_FORMAT[3]) == basename:
                id = image.get(COCO_IMAGE_FORMAT[0])
        return id