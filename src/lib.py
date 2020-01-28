#!/usr/bin/env python3
'''Top level operations and helper functions'''

from os import walk, sep, makedirs
from hashlib import sha1
from shutil import copy as copy_file
from git import Repo

# Project modules
from ui import CLIMessage
from meta import MetaDocument, MetaRecord, MetaDataSourceType
from signals import (OperationStatusSignals,
                     VerificationSignals, JIRASignals,
                     TargetMark, ContextMark)
from errors import (DataSourceNotFound,
                    FeatureBranchNotFound)
from messages import (Alert,
                      Info,
                      Request)
from constants import (MetaArgumentName as meta_arg,
                       NameFactory,
                       DirectiveNameSpace)
from connectors import GitConnector, JIRAConnector
from operations import (AddOperation,
                        CheckOutOperation,
                        CheckInOperation,
                        MergeOperation,
                        DetectOperation)


class DocProject:
    def __init__(self, env):
        self.env = env
        if self.env.project_code:
            self.code = self.env.project_code.strip().upper()
            self.workspace_path = sep.join([self.env.workspace_dir_path,
                                            self.code])
        else:
            self.code = None
            self.workspace_path = None

    
    def detect(self):
        '''Searches each asset for actionable patterns'''
        op = DetectOperation(self.env,
                             target=TargetMark.Duplicate,
                             context=ContextMark.Paragraph)
        op.inspect()
        for _ in op.display():
            print('{} => {}'.format(*reversed(_)))

            

    def merge(self):
        '''Scans all assets in the selected project and executes commands.'''
        MergeOperation(self.env)


    def add(self):
        '''Adds documentation assets from the given directory to the library.'''
        AddOperation(self.env)


    def checkout(self):
        '''Loads the assets of the product from the library into the
        workspace.
        '''
        CheckOutOperation(self.env)
        

    def checkin(self):
        '''Updates the library based on the changes in workspace.'''

        CheckInOperation(self.env)
