#!/usr/bin/env python3
'''Manipulates meta files'''

import yaml

from os import sep as path_sep
from constants import MetaArgumentName as meta_arg
from signals import MetaSignals as signal



class MetaDataSourceType:
    '''Defines available sources of meta data.'''
    class YAML: pass



class MetaDocument:
    def __init__(self, product_code, data_dir_path, meta_dir_name, data_file_suffix,
                 record_id_sep, source_type=MetaDataSourceType.YAML):
        self._record_id_sep = record_id_sep
        self.product_code = product_code.lower().strip()
        self.source_type = source_type
        self._data_dir_path = data_dir_path
        self._data_file_suffix = data_file_suffix
        self._meta_dir_name = meta_dir_name
        self._meta_dir_path = path_sep.join([self._data_dir_path,
                                             self._meta_dir_name])

        self._contents = {}


    def read(self):
        status = None

        if self.source_type == MetaDataSourceType.YAML:
            data_source_path = path_sep.join([self._meta_dir_path,
                                         ".".join([self.product_code,
                                                   self._data_file_suffix])])
            data = yaml.load(open(data_source_path))
            for each in data:
                record = data[each]
                file_name = record[meta_arg.file_name]
                target_dir = record[meta_arg.target_dir]
                lib_suffix = record[meta_arg.lib_suffix]

                self.register(MetaRecord(file_name,
                                         target_dir,
                                         lib_suffix))
            if self._contents:
                status = signal.MetaDocumentLoadFromYAMLFile.Ok
            else:
                status = signal.MetaDocumentLoadFromYAMLFile.Failed
        return status


    def make_signature(self, file_name, suffix):
        return self._record_id_sep.join([file_name, suffix])

    
    def register(self, meta_record):
        '''Adds the supplied record to the contents of the meta document
        unless this record is already in contents.

        A record is contents if its file name and lib suffix are
        already recorded in the register of the document.'''

        status = None
        signature = self.make_signature(meta_record.file_name,
                                        meta_record.lib_suffix)
        new_record = MetaRecord(meta_record.file_name,
                                meta_record.target_dir,
                                meta_record.lib_suffix)
        
        if not signature in self._contents:
            self._contents[signature] = dict()
            self._contents[signature][meta_arg.file_name] = new_record.file_name
            self._contents[signature][meta_arg.lib_suffix] = new_record.lib_suffix
            self._contents[signature][meta_arg.target_dir] = new_record.target_dir
        else:
            status = signal.RecordRegister.Failed

        return status


    def save(self):
        output_file_name = ".".join([self.product_code, self._data_file_suffix])
        output_file = open(path_sep.join([self._meta_dir_path,
                                     output_file_name]), "w")

        yaml.dump(self._contents,
                  stream=output_file,
                  default_flow_style=False)


    def get_contents(self):
        '''The keys in contents are not very important as they are constructed
        based on other fields: file_name and lib_suffix.'''

        for each in self._contents:
            yield each, self._contents[each]


    @property
    def contents(self):
        return self._contents

class MetaRecord:
    def __init__(self, file_name, target_dir, lib_suffix):
        self.file_name = file_name
        self.target_dir = target_dir
        self.lib_suffix = lib_suffix



