#!/usr/bin/env python3
'''Defines all configuration options'''
from yaml import load, dump
from os.path import (sep as path_sep,
                     join as path_join,
                     expanduser, isfile, exists)
from collections import OrderedDict

from ui import CLI, InterfaceType
from constants import UIArgumentName as ui_name, OptionName as opt_name

from messages import Info

class ConfLoader:
    '''The base class that all other configuration classes inherit from.

    Defines all configuration settings
    '''
    def __init__(self, conf_path=None):
        '''Inializes all settings to `None'; Arranged alphabetically'''
        self.allow_remote_requests = None
        self.code_sep = None
        self.commit_message_primary_sep = None
        self.commit_message_secondary_sep = None
        self.company_name = None
        self.context = None
        self.data_dir_path = None
        self.data_file_suffix = None
        self.default_doc_format = None
        self.default_encoding = None
        self.directive_default_name_space = None
        self.directive_name_space_sep = None
        self.directive_prefix = None
        self.directive_value_sep = None
        self.doc_file_extensions = None
        self.doc_source_dir_name = None
        self.git_in_workspace = None
        self.home_conf_path = None
        self.include = None
        self.interface_type = None
        self.jira_site = None
        self.key_length = None
        self.lib_dir_name = None
        self.message_horizontal_line = None
        self.message_screen_width = None
        self.meta_dir_name = None
        self.name_sep = None
        self.name_space_sep = None
        self.operation = None
        self.option_sep = None
        self.project_code = None
        self.project_name = None
        self.readme_path = None
        self.require_project_code_in_ticket = None
        self.source_dir = None
        self.static_conf_path = None
        self.target = None
        self.ticket_id = None
        self.ui_arguments = None
        self.workspace_dir_path = None

    @staticmethod
    def make_path(conf_value):
        '''Makes a valid path from the given string or list of parts

        Returns a valid path and an indication if it already exists'''
        try:
            conf_value = path_join(conf_value)
        except TypeError:
            conf_value = path_join(*conf_value)
            
        if path_sep in conf_value:
            conf_value = path_join(*[_dir_
                                     for _dir_
                                     in conf_value.split(path_sep)
                                     if _dir_])
        return expanduser(conf_value), exists(conf_value)
        

class StaticConfLoader(ConfLoader):
    '''Loads static configuration settings. 

    This class contains all settings. Some of these settings can be overridden
    from other sources, such as user interface. '''

    conf_path = '../options.yaml'

    def __init__(self, conf_path=None):
        super().__init__(conf_path)
        self.static_conf_path = conf_path or StaticConfLoader.conf_path
        data = load(open(self.static_conf_path))
        
        self.company_name = data[opt_name.company_name]
        self.project_name = data[opt_name.project_name]
        self.default_doc_format = data[opt_name.default_doc_format]
        self.doc_file_extensions = data[opt_name.doc_file_extensions]
        self.default_encoding = data[opt_name.default_encoding]
        self.key_length = data[opt_name.key_length]
        self.data_file_suffix = data[opt_name.data_file_suffix]
        self.message_screen_width = data[opt_name.message_screen_width]
        self.require_project_code_in_ticket = data[opt_name.require_project_code_in_ticket]
        self.message_horizontal_line = data[opt_name.message_horizontal_line]
        self.jira_site = data[opt_name.jira_site]
        self.allow_remote_requests = data[opt_name.allow_remote_requests]
        self.git_in_workspace = data[opt_name.git_in_workspace]

        path = opt_name.Path
        self.data_dir_path = data[path._][path.data_dir]
        self.workspace_dir_path = data[path._][path.workspace]
        self.readme_path = data[path._][path.readme]

        dir_name = opt_name.DirName
        self.meta_dir_name = data[dir_name._][dir_name.meta]
        self.lib_dir_name = data[dir_name._][dir_name.lib]
        self.doc_source_dir_name = data[dir_name._][dir_name.doc_source]
        
        sep = opt_name.Sep
        self.code_sep = data[sep._][sep.code]
        self.option_sep = data[sep._][sep.opt]
        self.name_sep = data[sep._][sep.name]
        self.commit_message_primary_sep = data[sep._][sep.commit_message_primary]
        self.commit_message_secondary_sep = data[sep._][sep.commit_message_secondary]

        directive = opt_name.Directive
        self.directive_prefix = data[directive._][directive.prefix]
        self.prefix = self.directive_prefix

        self.directive_name_space_sep = data[directive._][directive.name_space_sep]
        self.name_space_sep = self.directive_name_space_sep

        self.directive_value_sep = data[directive._][directive.value_sep]
        self.value_sep = self.directive_value_sep

        self.directive_default_name_space = data[directive._][directive.default_name_space]
        self.default_name_space =  self.directive_default_name_space



class HomeConfLoader(StaticConfLoader):
    '''Loads user redefined settings which are stored in the home directory'''
    def __init__(self, static_conf_path=None, restore_default=False):
        super().__init__(static_conf_path)

        # Saving some of the options from the static configuration to an ordered
        # dict to ensure that the order of properties in the file is always the
        # same.
        self._options = OrderedDict()
        self._options[opt_name.Path.workspace], _ = ConfLoader.make_path(self.workspace_dir_path)
        self._options[opt_name.allow_remote_requests] = self.allow_remote_requests
        self._options[opt_name.Sep.commit_message_primary] = self.commit_message_primary_sep
        self._options[opt_name.Sep.commit_message_secondary] = self.commit_message_secondary_sep
        self._options[opt_name.git_in_workspace] = self.git_in_workspace
        
        if restore_default:
            self.make_default_file()


    def _make_default_file_path(self):
        company_name = self._normalize(self.company_name)
        project_name = self._normalize(self.project_name)
        return ConfLoader.make_path(['~',
                                    '.{}{}{}.yaml'.format(company_name,
                                                          path_sep,
                                                          project_name)])


    def make_default_file(self):
        '''Create a default file if it does not exist'''
        self.home_conf_path = self._make_default_file_path()[0]

        if not isfile(self.home_conf_path):
            with open(self.home_conf_path, 'w') as output_file:
                for _opt_ in self._options:
                    key = _opt_
                    value = self._options[_opt_]
                    entry = {}
                    entry[key] = value
                    dump(entry,
                         stream=output_file,
                         default_flow_style=False)


    def setup(self, options_file=None):
        options_file = options_file or self._make_default_file_path()[0]
        if isfile(options_file):
            self.home_conf_path = options_file
            with open(self.home_conf_path) as options:
                self._options = load(options)
                self.workspace_dir_path, _ = ConfLoader.make_path(self._options[opt_name.Path.workspace])
                self.git_in_workspace = self._options[opt_name.git_in_workspace]
                self.allow_remote_requests = self._options[opt_name.allow_remote_requests]
                self.commit_message_primary_sep = self._options[opt_name.Sep.commit_message_primary]
                self.commit_message_secondary_sep = self._options[opt_name.Sep.commit_message_secondary]


    def _normalize(self, term):
        term = str(term).strip().lower()
        sep = self.name_sep
        return sep.join(term.split())



class UIConfLoader(HomeConfLoader):
    '''Loads user interface configuration settings. 

    This loader has the top priority'''
    def __init__(self, interface_type=InterfaceType.CLI):
        
        super().__init__()
        super().setup(self.home_conf_path)

        self.interface_type = InterfaceType.CLI


    def setup(self):
        if self.interface_type is InterfaceType.CLI:
            self._setup_cli()


    def _setup_cli(self):
        option_sep = str(self.option_sep)[0]
        name_sep = str(self.name_sep)[0]
        cli = CLI(option_sep, name_sep)
        #Setting home_conf_path to a valid path will enable reading home options
        #from a file other than the default file.
        #self.home_conf_path = cli.arguments(ui_name.home_conf_path)

        self.operation = cli.arguments[ui_name.operation]
        self.ui_arguments = cli.arguments
        self.ticket_id = cli.arguments.get(ui_name.ticket_id)
        self.source_dir = cli.arguments.get(ui_name.source_dir)
        self.include = cli.arguments.get(ui_name.include)
        self.context = cli.arguments.get(ui_name.context)
        self.target = cli.arguments.get(ui_name.target)

        project_code = cli.arguments.get(ui_name.project_code)
        self.project_code = project_code and project_code.strip().upper()



class Environment(UIConfLoader):
    '''Combines settings from different sources and exposes these settings
    as if they were its own properties'''

    def __init__(self, conf_file_name=None):
        super().__init__()
        super().setup()

if __name__ == '__main__':
    print(Environment().allow_remote_requests)
