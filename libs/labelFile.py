# Copyright (c) 2016 Tzutalin
# Create by TzuTaLin <tzu.ta.lin@gmail.com>

try:
    from PyQt5.QtGui import QImage
except ImportError:
    from PyQt4.QtGui import QImage

from base64 import b64encode, b64decode
from libs.pascal_voc_io import PascalVocWriter
from libs.yolo_io import YOLOWriter
from libs.pascal_voc_io import XML_EXT
from libs.create_ml_io import CreateMLWriter
from libs.create_ml_io import JSON_EXT
from enum import Enum
import os.path
import sys
from libs.coco_io import CocoWriter, COCO_BASIC_FORMAT, COCO_ANNOTATION_FORMAT
import json

class LabelFileFormat(Enum):
    PASCAL_VOC = 1
    YOLO = 2
    CREATE_ML = 3
    COCO = 4


class LabelFileError(Exception):
    pass


class LabelFile(object):
    # It might be changed as window creates. By default, using XML ext
    # suffix = '.lif'
    #suffix = XML_EXT
    suffix = [XML_EXT, JSON_EXT]

    def __init__(self, filename=None):
        self.shapes = ()
        self.image_path = None
        self.image_data = None
        self.verified = False

    def save_create_ml_format(self, filename, shapes, image_path, image_data, class_list, line_color=None, fill_color=None, database_src=None):
        img_folder_name = os.path.basename(os.path.dirname(image_path))
        img_file_name = os.path.basename(image_path)

        image = QImage()
        image.load(image_path)
        image_shape = [image.height(), image.width(),
                       1 if image.isGrayscale() else 3]
        writer = CreateMLWriter(img_folder_name, img_file_name,
                                image_shape, shapes, filename, local_img_path=image_path)
        writer.verified = self.verified
        writer.write()


    def save_pascal_voc_format(self, filename, shapes, image_path, image_data,
                               line_color=None, fill_color=None, database_src=None):
        img_folder_path = os.path.dirname(image_path)
        img_folder_name = os.path.split(img_folder_path)[-1]
        img_file_name = os.path.basename(image_path)
        # imgFileNameWithoutExt = os.path.splitext(img_file_name)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        if isinstance(image_data, QImage):
            image = image_data
        else:
            image = QImage()
            image.load(image_path)
        image_shape = [image.height(), image.width(),
                       1 if image.isGrayscale() else 3]
        writer = PascalVocWriter(img_folder_name, img_file_name,
                                 image_shape, local_img_path=image_path)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            # Add Chris
            difficult = int(shape['difficult'])
            bnd_box = LabelFile.convert_points_to_bnd_box(points)
            writer.add_bnd_box(bnd_box[0], bnd_box[1], bnd_box[2], bnd_box[3], label, difficult)

        writer.save(target_file=filename)
        return

    def save_yolo_format(self, filename, shapes, image_path, image_data, class_list,
                         line_color=None, fill_color=None, database_src=None):
        img_folder_path = os.path.dirname(image_path)
        img_folder_name = os.path.split(img_folder_path)[-1]
        img_file_name = os.path.basename(image_path)
        # imgFileNameWithoutExt = os.path.splitext(img_file_name)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        if isinstance(image_data, QImage):
            image = image_data
        else:
            image = QImage()
            image.load(image_path)
        image_shape = [image.height(), image.width(),
                       1 if image.isGrayscale() else 3]
        writer = YOLOWriter(img_folder_name, img_file_name,
                            image_shape, local_img_path=image_path)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            # Add Chris
            difficult = int(shape['difficult'])
            bnd_box = LabelFile.convert_points_to_bnd_box(points)
            writer.add_bnd_box(bnd_box[0], bnd_box[1], bnd_box[2], bnd_box[3], label, difficult)

        writer.save(target_file=filename, class_list=class_list)
        return

    def toggle_verify(self):
        self.verified = not self.verified

    ''' ttf is disable
    def load(self, filename):
        import json
        with open(filename, 'rb') as f:
                data = json.load(f)
                imagePath = data['imagePath']
                imageData = b64decode(data['imageData'])
                lineColor = data['lineColor']
                fillColor = data['fillColor']
                shapes = ((s['label'], s['points'], s['line_color'], s['fill_color'])\
                        for s in data['shapes'])
                # Only replace data after everything is loaded.
                self.shapes = shapes
                self.imagePath = imagePath
                self.imageData = imageData
                self.lineColor = lineColor
                self.fillColor = fillColor

    def save(self, filename, shapes, imagePath, imageData, lineColor=None, fillColor=None):
        import json
        with open(filename, 'wb') as f:
                json.dump(dict(
                    shapes=shapes,
                    lineColor=lineColor, fillColor=fillColor,
                    imagePath=imagePath,
                    imageData=b64encode(imageData)),
                    f, ensure_ascii=True, indent=2)
    '''

    @staticmethod
    def is_label_file(filename):
        file_suffix = os.path.splitext(filename)[1].lower()
        if file_suffix in LabelFile.suffix:
            return True
        else:
            return False   
        
    @staticmethod  
    def is_json_file(filename):
        file_suffix = os.path.splitext(filename)[1].lower()
        if file_suffix == LabelFile.suffix[1]:
            return True
        else:
            return False
        
    @staticmethod
    def convert_points_to_bnd_box(points):
        x_min = float('inf')
        y_min = float('inf')
        x_max = float('-inf')
        y_max = float('-inf')
        for p in points:
            x = p[0]
            y = p[1]
            x_min = min(x, x_min)
            y_min = min(y, y_min)
            x_max = max(x, x_max)
            y_max = max(y, y_max)

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        # ==============
        '''if x_min < 1:
            x_min = 1

        if y_min < 1:
            y_min = 1
        '''
        return int(x_min), int(y_min), int(x_max), int(y_max)
    
    def load_create_ml(self, filename):
        return False

    def load_coco_file(self, filename):
        try:
            coco = CocoWriter(filename)
            self._current_label_file_ = coco
            self._type_label_file_ = LabelFileFormat.COCO
        except Exception:
            raise ValueError('This file does not have a COCO basic format')
            
    def _is_createml_format_(self, filename):
        return False
    
    def _is_coco_format_(self, filename):
        with open(filename, 'r') as file:
            input_data = file.read()
        dataset = json.loads(input_data)    
        coco_count = 0
        coco_annotation_count = 0
        for key in dataset.keys():
            if key in COCO_BASIC_FORMAT:
                coco_count += 1
        if coco_count == len(COCO_BASIC_FORMAT):
            if isinstance(dataset['annotation'], list) and len(dataset['annotation']) > 0:
                for innerkey in dataset['annotation'][-1]:
                    if innerkey in COCO_ANNOTATION_FORMAT:
                        coco_annotation_count += 1
        if coco_count == len(COCO_BASIC_FORMAT) and coco_annotation_count == len(COCO_ANNOTATION_FORMAT):
            return True
        else:
            return False
        
    def load_json(self, filename):
        if self._is_coco_format_(filename):
            self.load_coco_file(filename)
        elif self._is_createml_format_(filename):
            self.load_create_ml(filename)
        else:
            raise ValueError('This file does not have a label format supported.')
           