# Copyright (c) 2016 Tzutalin
# Create by TzuTaLin <tzu.ta.lin@gmail.com>

try:
    from PyQt5.QtGui import QImage
except ImportError:
    from PyQt4.QtGui import QImage

from base64 import b64encode, b64decode
from libs.pascal_voc_io import PascalVocWriter
from libs.yolo_io import YOLOWriter, TXT_EXT
from libs.pascal_voc_io import XML_EXT
from libs.create_ml_io import CreateMLWriter
from libs.create_ml_io import JSON_EXT
from enum import Enum
import os.path
import sys
from libs.coco_io import CocoWriter, COCO_BASIC_FORMAT_OBJD, COCO_ANNOTATION_FORMAT, COCO_CATEGORY_FORMAT
import json
from pathlib import Path

class LabelFileFormat(Enum):
    PASCAL_VOC = 1
    YOLO = 2
    CREATE_ML = 3
    COCO = 4

class LabelFileError(Exception):
    pass

class AnnotationFile():
    def __init__(self, filepath):
        self.annotation_format = None
        self.filename = Path(filepath).stem
        self.filepath = filepath
        self.file_extension = Path(filepath).suffix
    
    def save(self, annotation):
        pass
    
    def read(self, image_name=None, image_id=None, category_id=None):
        pass

class XMLFile(AnnotationFile):
    pass

class TXTFile(AnnotationFile):
    pass

class JSONFile(AnnotationFile):
    def __init__(self, filepath):
        super(JSONFile, self).__init__(filepath)

        with open(self.filepath, 'r') as file:
            input_data = file.read()
        self.dataset = json.loads(input_data) 
        if self.__is_coco_format__():
            self.annotation_file = COCOFile(self.dataset)
        elif self.__is_createml_format__():
            self.annotation_file = CreateML()
        else:
            self.json_format = None    
    
    def __is_coco_format__(self):
        coco_count = 0
        coco_annotation_count = 0
        for key in self.dataset.keys():
            if key in COCO_BASIC_FORMAT_OBJD:
                coco_count += 1
        if coco_count == len(COCO_BASIC_FORMAT_OBJD):
            if isinstance(self.dataset[COCO_BASIC_FORMAT_OBJD[2]], list) and len(self.dataset[COCO_BASIC_FORMAT_OBJD[2]]) > 0:
                for innerkey in self.dataset[COCO_BASIC_FORMAT_OBJD[2]][-1]:
                    if innerkey in COCO_ANNOTATION_FORMAT:
                        coco_annotation_count += 1
        if coco_count == len(COCO_BASIC_FORMAT_OBJD) and coco_annotation_count == len(COCO_ANNOTATION_FORMAT):
            return True
        else:
            return False        
        
    def __is_createml_format__(self):
        return False
    
    def get_image_annotation(self, image_name=None, image_id=None):
        return self.annotation_file.get_image_annotation(image_name, image_id)
    
    def get_category_annotation(self):
        return self.annotation_file.get_category_annotation()

    def save(self, annotation):
        self.annotation.save(annotation)
       
class COCOFile():
    def __init__(self, dataset):
        self.dataset = dataset
        self.__current_image_id__ = None
        self.__current_annotation_id__ = None
        self.__current_category_id__ = None
        try:
            self.__current_json_file__ = CocoWriter(self.dataset)
        except Exception:
            raise ValueError('This file does not have a COCO basic format')      
              
        
    def get_image_annotation(self, image_name=None, image_id=None):
        if image_name:
            img_id = self.__current_json_file__.get_image_id(os.path.basename(image_name))
            if img_id:
                ann_id = self.__current_json_file__.getAnnIds(imgIds=img_id)
                annotation = self.__current_json_file__.loadAnns(ids=ann_id)
                if annotation:
                    self.__current_image_id__ = img_id
                    self.__current_annotation_id__ = []
                    self.__current_category_id__ = []
                    for each in annotation:
                        self.__current_annotation_id__.append(each.get(COCO_ANNOTATION_FORMAT[0]))
                        if each.get(COCO_ANNOTATION_FORMAT[2]) not in self.__current_category_id__:
                            self.__current_category_id__.append(each.get(COCO_ANNOTATION_FORMAT[2]))
                    return annotation
                else:
                    return None  
        elif image_id:
            return None
    def get_category_annotation(self):
        if self.__current_image_id__:
            return self.__current_json_file__.loadCats(ids=self.__current_category_id__)
        
    def save(self, annotation):
        pass

class CreateML():
    pass

        
class LabelFile(object):
    # It might be changed as window creates. By default, using XML ext
    # suffix = '.lif'
    suffix = (XML_EXT, JSON_EXT, TXT_EXT)

    def __init__(self, filename=None):
        self.shapes = ()
        self.image_path = None
        self.image_data = None
        self.verified = False
        if filename and Path(filename).suffix == LabelFile.suffix[1]:
            self.json_file = JSONFile(filename)

    def upadte_label_file(self, filename):
        self.__init__(filename)

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
    
    
    def get_annotation(self, image_filename):
        return self.json_file.get_image_annotation(image_name=image_filename)
      
    def get_category(self):
        return self.json_file.get_category_annotation()
            
