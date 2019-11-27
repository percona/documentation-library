#!/usr/bin/env python3
'''Top level operations and helper functions'''

import yaml

from os import walk, sep, makedirs
from hashlib import sha1
from shutil import copy as copy_file
from git import Repo

# Project modules
from ui import CLIMessage
from meta import MetaDocument, MetaRecord, MetaDataSourceType
from signals import (OperationStatusSignals,
                     VerificationSignals, JIRASignals)
from errors import (DataSourceNotFound,
                    FeatureBranchNotFound)
from messages import (Alert,
                      Info,
                      Request)
from constants import (MetaArgumentName as meta_arg,
                       NameFactory,
                       DirectiveNameSpace)
from connectors import GitConnector, JIRAConnector
from directives import (DirectiveBuffer,
                        AutoAgent,
                        ProductAgent,
                        VersionAgent)


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
        #key=lib file name, value=workdir directory full path
        #special case: when creating a new project from an existing directory,
        #the value is the full path in the source directory
        self.collection = dict() 


    def merge(self):
        op_status = []
        auto_directive = DirectiveBuffer.doc_property(name_space=DirectiveNameSpace.Only._,
                                                      attribute='',
                                                      sep=self.env.name_space_sep)
        product_directive = DirectiveBuffer.doc_property(name_space=DirectiveNameSpace.Default._,
                                                      attribute=DirectiveNameSpace.Default.product,
                                                      sep=self.env.name_space_sep)
        version_directive = DirectiveBuffer.doc_property(name_space=DirectiveNameSpace.Default._,
                                                      attribute=DirectiveNameSpace.Default.version,
                                                      sep=self.env.name_space_sep)


        if self.workspace_path:
            meta_doc = MetaDocument(product_code=self.code,
                                    data_dir_path=self.env.data_dir_path,
                                    meta_dir_name=self.env.meta_dir_name,
                                    data_file_suffix=self.env.data_file_suffix,
                                    record_id_sep=self.env.code_sep)
            meta_doc.read()
            for each in meta_doc.get_contents():
                signature, record = each
                record = MetaRecord(**record)
                if record.file_name.endswith(self.env.default_doc_format):
                    target_dir = self._make_workspace_path(record.target_dir)
                    target_file_path = sep.join([target_dir,
                                                 record.file_name])
                    with open(target_file_path) as doc_file:
                        buffer = DirectiveBuffer(doc_file, self.env)
                        for each_directive in buffer.directives:
                            if each_directive == auto_directive:
                                agent = AutoAgent(self.env, doc_file)
                                agent.run(buffer.directives[each_directive])
                            elif each_directive == product_directive:
                                agent = ProductAgent(self.env, doc_file)
                                agent.run(buffer.directives[each_directive])
                            elif each_directive == version_directive:
                                agent = VersionAgent(self.env, doc_file)
                                agent.run(buffer.directives[each_directive])
                else:
                    op_status.append(OperationStatusSignals.Merge.Failed)

        else:
            op_status.append(OperationStatusSignals.Merge.Failed)

        return op_status


    def add(self):
        '''Adds documentation assets from the given directory to the library.'''

        op_status = None
        source_dir = sep.join([self.env.source_dir,
                               self.env.doc_source_dir_name])

        if self._copy_from_dir(source_dir):
            op_status = OperationStatusSignals.Add.Ok
        else:
            op_status = OperationStatusSignals.Add.Failed

        return op_status


    def checkout(self):
        '''Loads the assets of the product from the library into the
        workspace.
        '''

        op_status = []
        meta_doc = MetaDocument(product_code=self.code,
                                data_dir_path=self.env.data_dir_path,
                                meta_dir_name=self.env.meta_dir_name,
                                data_file_suffix=self.env.data_file_suffix,
                                record_id_sep=self.env.code_sep)
        meta_doc.read()
        for each in meta_doc.get_contents():
            signature, record = each
            record = MetaRecord(**record)
            source_file_path = sep.join([self.env.data_dir_path,
                                         self.env.lib_dir_name,
                                         signature])
            target_dir = self._make_workspace_path(record.target_dir)
            makedirs(target_dir, exist_ok=True)            
            target_file_path = sep.join([target_dir,
                                         record.file_name])
            copy_file(source_file_path, target_file_path)
            op_status.append(OperationStatusSignals.CheckOut.Ok)

        if self.env.ticket_id:
            jira = JIRAConnector(self.env.jira_site)
            ticket_found = jira.find_ticket(self.env.ticket_id, self.env.code_sep)

            if ticket_found.status is VerificationSignals.TicketCodeValid.Ok:
                jira_ticket = ticket_found.info
                message_legend = '{}\n{}\n'.format(Request.ticket_summary(jira_ticket.ticket_id),
                                                   Request.ticket_default_summary(jira_ticket.text))
                message_prompt = Request.ticket_summary_prompt()
                message = CLIMessage(prompt=message_prompt,
                                     legend=message_legend,
                                     text_width=self.env.message_screen_width,
                                     decoration_token=self.env.message_horizontal_line)

                update_status = jira_ticket.update_summary(request_format=message)

                if update_status is JIRASignals.TicketSummaryUpdate.Ok:
                    repo = GitConnector(self.workspace_path)
                    repo.make_branch(product_id=self.code,
                                     ticket_summary=jira_ticket,
                                     doc_source_dir_path=self.env.doc_source_dir_name)
                    op_status.append(OperationStatusSignals.CheckOut.Ok)
            else:
                op_status.append(OperationStatusSignals.CheckOut.Failed)

        else:
            print(Alert.jira_ticket_not_found)

        return op_status


    def checkin(self):
        '''Updates the library based on the changes in workspace.'''

        op_status = None
        
        meta_doc = MetaDocument(product_code=self.code,
                                data_dir_path=self.env.data_dir_path,
                                meta_dir_name=self.env.meta_dir_name,
                                data_file_suffix=self.env.data_file_suffix,
                                record_id_sep=self.env.code_sep)
        meta_doc.read()
        records = meta_doc.get_contents()# not used

        jira = JIRAConnector(self.env.jira_site)
        ticket_found = jira.find_ticket(self.env.ticket_id, self.env.code_sep)
        if ticket_found.status is VerificationSignals.TicketCodeValid.Ok:
            jira_ticket = ticket_found.info
        else:
            print(Alert.jira_ticket_not_found)

        git_conn = GitConnector(self.workspace_path)
        git_repo = git_conn.repository
        collected_paths = set()

        if git_repo.is_dirty():
            op_status = OperationStatusSignals.CheckIn.Failed
            print(Alert.project_has_unsaved_changes(self.code))
        else:
            # detect the last commit in the master branch
            feature_branch = None
            for each in git_repo.branches:
                if each.name.startswith(jira_ticket.ticket_id) and not feature_branch:
                    feature_branch=each
            if feature_branch:
                current_head = git_repo.heads['master'].checkout()

                git_repo.index.merge_tree(feature_branch)
                git_repo.index.commit(Info.commit_message(self.env.ticket_id),
                                      parent_commits=(feature_branch.commit, current_head.commit))

                self._copy_from_dir(self.workspace_path)

                lib_conn = GitConnector(self.env.data_dir_path)
                lib_conn.make_branch(product_id=self.code,
                                     ticket_summary=jira_ticket,
                                     doc_source_dir_path=self.env.lib_dir_name)
                
                op_status = OperationStatusSignals.CheckIn.Ok

            else:
                raise FeatureBranchNotFound
            # merge changes from the feature branch

        return op_status


    def _copy_from_dir(self, target_dir):
        collected = self._collect(target_dir)
        meta_doc = MetaDocument(product_code=self.code,
                                data_dir_path=self.env.data_dir_path,
                                meta_dir_name=self.env.meta_dir_name,
                                data_file_suffix=self.env.data_file_suffix,
                                record_id_sep=self.env.code_sep)
        
        for each in collected:
            local_file_path = each.partition(sep+self.env.doc_source_dir_name+sep)[-1]
            file_dir, _, file_name = local_file_path.rpartition(sep)

            suffix= sha1(bytes(sep.join([self.code, file_dir]),
                               self.env.default_encoding)).hexdigest()[:self.env.key_length]

            lib_file_name = self.env.code_sep.join([file_name, suffix])
            
            meta_rec = MetaRecord(file_name=file_name,
                                  target_dir=file_dir,
                                  lib_suffix=suffix)
            meta_doc.register(meta_rec)
            self.collection[lib_file_name] = each
          
        meta_doc.save()
        self._save()
        return self.collection


    def _save(self):
        if self.collection:
            for each in self.collection:
                source = self.collection[each]
                destination = sep.join([self.env.data_dir_path,
                                        self.env.lib_dir_name, each])
                copy_file(source, destination)


    def _collect(self, target_dir, selected_file_types=None):
        selected_file_types = selected_file_types or self.env.doc_file_extensions
        collected_paths = set()
        data_dir = self.env.data_dir_path

        for each_path in walk(target_dir):
            current_dir = each_path[0]
            files = each_path[2]
            
            for each_file in files:
                if each_file.rpartition(".")[-1] in selected_file_types:
                    
                    collected_paths.add(sep.join([current_dir, each_file]))
        return collected_paths


    def _make_workspace_path(self, target_dir):
        if target_dir:
            workspace_path = sep.join([self.env.workspace_dir_path,
                                       self.code,
                                       self.env.doc_source_dir_name,
                                       target_dir])
        else:
            workspace_path = sep.join([self.env.workspace_dir_path,
                                       self.code,
                                       self.env.doc_source_dir_name])
        return workspace_path
