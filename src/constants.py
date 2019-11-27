#!/usr/bin/env python3
'''Constains static objects or objects that are evaluated only when
initialized and never changed at runtime.'''

from string import whitespace, punctuation
from re import split as re_split


class OperationName:
    '''Names of top level operations, such as dli subcommands.'''

    add = 'add'
    checkout = 'checkout'
    checkin = 'checkin'
    merge = 'merge'


class UIArgumentName:
    '''Names of parameters and related variables.'''

    operation = 'operation'
    source_dir = 'source_dir'
    project_code = 'project_code'
    ticket_id = 'ticket_id'
    include = 'include'



class MetaArgumentName:
    '''Argument names used in Meta files.'''

    file_name = 'file_name'
    lib_suffix = 'lib_suffix'
    target_dir = 'target_dir'



class OptionInclude:
    product='product'
    version='version'
    auto='auto'



class DirectiveNameSpace:
    class Only:
      _ = 'only'
    class Default:
      _ = 'dL'
      version = 'version'
      product = 'product'


class OptionName:
    default_doc_format = 'default_doc_format'
    doc_file_extensions = 'doc_file_extensions'
    default_encoding = 'default_encoding'
    key_length = 'key_length'
    data_file_suffix = 'data_file_suffix'
    message_screen_width = 'message_screen_width'
    require_project_code_in_ticket = 'require_project_code_in_ticket'
    message_horizontal_line = 'message_horizontal_line'
    jira_site = 'jira_site'

    class Path:
        _ = 'path'
        data_dir = 'data_dir'
        workspace = 'workspace'
        

    class DirName:
        _ = 'dir_name'
        meta = 'meta'
        lib = 'lib'
        doc_source = 'doc_source'


    class Sep:
        _ = 'sep'
        code = 'code'
        opt = 'opt'
        name = 'name'
        commit_message_primary = 'commit_message_primary'
        commit_message_secondary = 'commit_message_secondary'

    class Directive:
        _ = 'directive'
        prefix = 'prefix'
        name_space_sep = 'name_space_sep'
        value_sep = 'value_sep'
        default_name_space = 'default_name_space'



class NameFactory:
    '''Costructor of Argument instances which generate consistent option
    names and variables.'''
    
    def __init__(self, name_sep_char):
        self._name_sep = name_sep_char[0]

        
    def _normalize(self, sep_char, text):
        '''Replaces all whitespace and punctuation characters in the supplied
        text with the given separator. Consecutive replaceable characters are
        reduced to one occurance.'''
        
        pattern = "[{}{}]".format(whitespace, punctuation)
        processed = [each
                     for each
                     in re_split(pattern, text)
                     if each]
        return sep_char.join(processed)

    
    def make(self, attr_name):
        attr_name = self._normalize(self._name_sep, attr_name)

        class Argument:
            def __init__(self, name):
                self.name = name

        return Argument(name=attr_name)

