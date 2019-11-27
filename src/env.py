#!/usr/bin/env python3
"""This module creates and controls the runtime. It loads and makes available
the values defined in conf files, environment variables, and in the interface."""

from yaml import load

from ui import CLI, InterfaceType
from constants import UIArgumentName as ui_name, OptionName as opt_name


class ConfLoader:
    conf_file_name = "../options.yaml"
    '''Loads static configuration settings. 

    This class contains all settings. Some of these settings can be overridden
    from other sources, such as user interface. '''
    
    def __init__(self, conf_file_name=None):
        conf_file_name = conf_file_name or ConfLoader.conf_file_name
        data = load(open(conf_file_name))
        self.default_doc_format = data[opt_name.default_doc_format]
        self.doc_file_extensions = data[opt_name.doc_file_extensions]
        self.default_encoding = data[opt_name.default_encoding]
        self.key_length = data[opt_name.key_length]
        self.data_file_suffix = data[opt_name.data_file_suffix]
        self.message_screen_width = data[opt_name.message_screen_width]
        self.require_project_code_in_ticket = data[opt_name.require_project_code_in_ticket]
        self.message_horizontal_line = data[opt_name.message_horizontal_line]
        self.jira_site = data[opt_name.jira_site]

        self.project_code = data[ui_name.project_code]
        self.operation = data[ui_name.operation]
        self.source_dir = data[ui_name.source_dir]
        self.ticket_id = data[ui_name.ticket_id]

        path = opt_name.Path
        self.data_dir_path = data[path._][path.data_dir]
        self.workspace_dir_path = data[path._][path.workspace]

        dir_name = opt_name.DirName
        self.meta_dir_name = data[dir_name._][dir_name.meta]
        self.lib_dir_name = data[dir_name._][dir_name.lib]
        self.doc_source_dir_name = data[dir_name._][dir_name.doc_source]
        
        sep = opt_name.Sep
        self.code_sep = data[sep._][sep.code]
        self.opt_sep = data[sep._][sep.opt]
        self.name_sep = data[sep._][sep.name]
        self.commit_message_primary_sep = data[sep._][sep.commit_message_primary]
        self.commit_message_secondary_sep = data[sep._][sep.commit_message_secondary]

        directive = opt_name.Directive
        self.prefix = data[directive._][directive.prefix]
        self.name_space_sep = data[directive._][directive.name_space_sep]
        self.value_sep = data[directive._][directive.value_sep]
        self.default_name_space = data[directive._][directive.default_name_space]


class UILoader:
    def __init__(self, interface_type=InterfaceType.CLI):
        
        self.arguments = None
        self.interface_type = InterfaceType.CLI
        self.operation = ''
        self.ticket_id = ''
        self.project_code = ''
        self.source_dir = ''
        self.include = ''


    def setup(self, option_sep_char='', name_sep_char=''):
        if self.interface_type is InterfaceType.CLI:
            self._setup_cli(option_sep_char, name_sep_char)


    def _setup_cli(self, option_sep_char, name_sep_char):
        option_sep = option_sep_char[0]
        name_sep = name_sep_char[0]
        cli = CLI(option_sep, name_sep)
        self.operation = cli.arguments[ui_name.operation]
        self.arguments = cli.arguments
        self.ticket_id = cli.arguments.get(ui_name.ticket_id)
        self.project_code = cli.arguments.get(ui_name.project_code)
        self.source_dir = cli.arguments.get(ui_name.source_dir)
        self.include = cli.arguments.get(ui_name.include)



class Environment:
    '''Combines settings from different sources and exposes these settings
    as if they were its own properties'''

    def __init__(self, conf_file_name=None):

        #conf_file
        self.conf_file_name = conf_file_name
        self.conf_data = ConfLoader(self.conf_file_name)
        self.default_doc_format = self.conf_data.default_doc_format
        self.doc_file_extensions = self.conf_data.doc_file_extensions
        self.default_encoding = self.conf_data.default_encoding 
        self.key_length = self.conf_data.key_length 
        self.data_file_suffix = self.conf_data.data_file_suffix 
        self.message_screen_width = self.conf_data.message_screen_width 
        self.require_project_code_in_ticket = self.conf_data.require_project_code_in_ticket 
        self.message_horizontal_line = self.conf_data.message_horizontal_line 
        self.jira_site = self.conf_data.jira_site 
        self.data_dir_path = self.conf_data.data_dir_path 
        self.workspace_dir_path = self.conf_data.workspace_dir_path
        self.meta_dir_name = self.conf_data.meta_dir_name 
        self.lib_dir_name = self.conf_data.lib_dir_name
        self.doc_source_dir_name = self.conf_data.doc_source_dir_name
        self.code_sep = self.conf_data.code_sep 
        self.opt_sep = self.conf_data.opt_sep 
        self.name_sep = self.conf_data.name_sep 
        self.commit_message_primary_sep = self.conf_data.commit_message_primary_sep 
        self.commit_message_secondary_sep = self.conf_data.commit_message_secondary_sep
        self.directive_prefix = self.conf_data.prefix
        self.directive_name_space_sep = self.conf_data.name_space_sep
        #alias
        self.name_space_sep = self.conf_data.name_space_sep
        self.directive_value_sep = self.conf_data.value_sep
        self.directive_default_name_space = self.conf_data.default_name_space
        # user input
        self.ui_data = UILoader(interface_type=InterfaceType.CLI)
        self.ui_data.setup(self.opt_sep, self.name_sep)
        self.arguments = self.ui_data.arguments
        self.operation = self.ui_data.operation
        self.project_code = self.ui_data.project_code
        self.ticket_id = self.ui_data.ticket_id
        self.source_dir = self.ui_data.source_dir
        self.include = self.ui_data.include
