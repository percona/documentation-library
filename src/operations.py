#!/usr/bin/env python3
'''Implementations of the top level features'''

from os.path import sep as path_sep, join as path_join
from os import walk, makedirs
from hashlib import sha1
from shutil import copy as copy_file
from collections import namedtuple

from ui import CLIMessage
from signals import (OperationStatusSignals,
                     VerificationSignals, JIRASignals,
                     TargetMark, ContextMark)
from text import Text
from meta import MetaDocument, MetaRecord, MetaDataSourceType
from errors import (DataSourceNotFound,
                    FeatureBranchNotFound,
                    FeatureBranchTooMany)
from messages import (Alert,
                      Info,
                      Request)
from constants import (MetaArgumentName as meta_arg,
                       NameFactory,
                       DirectiveNameSpace)
from connectors import GitConnector, JIRAConnector, JIRATicketInfo
from directives import (DirectiveBuffer,
                        AutoAgent,
                        ProductAgent,
                        VersionAgent)


class Operation:
    '''Base class for all operations'''
    def __init__(self, env):
        self.env = env
        self.status = []
        self.collection = dict()
        self.workspace_path = None

        if self.env.project_code:
            self.workspace_path = path_join(self.env.workspace_dir_path,
                                            self.env.project_code)

    def request_jira_ticket(self):
        #+BEGIN_nested_functions
        def work_online():
            ticket = None
            jira = JIRAConnector(self.env.jira_site)
            ticket_found = jira.find_ticket(self.env.ticket_id, self.env.code_sep)
            if ticket_found.status is VerificationSignals.TicketCodeValid.Ok:
                ticket = ticket_found.info
                message_legend = '{}\n{}\n'.format(Request.ticket_summary(ticket.ticket_id),
                                                   Request.ticket_default_summary(ticket.text))
                message_prompt = Request.ticket_summary_prompt()
                message = CLIMessage(title=self.env.operation,
                                     prompt=message_prompt,
                                     legend=message_legend,
                                     text_width=self.env.message_screen_width,
                                     decoration_token=self.env.message_horizontal_line).make()
                self.status.append(ticket.update_summary(text=message))
            else:
                print(Alert.jira_ticket_not_found(self.env.ticket_id))
                print(Info.work_offline())
                work_offline()
            return ticket


        def work_offline():
            ticket = None
            message = CLIMessage(title=self.env.operation,
                                 prompt=Request.ticket_summary(self.env.ticket_id),
                                 text_width=self.env.message_screen_width,
                                 decoration_token=self.env.message_horizontal_line).make()

            ticket = JIRATicketInfo(ticket_id=self.env.ticket_id,
                                    text=message,
                                    ticket_id_sep=self.env.code_sep)

            self.status.append(ticket.update_summary(message))
            return ticket
        #+END_nested_functions

        return self.env.allow_remote_requests and work_online() or work_offline()


    def copy_project(self, target_dir):
        collected = self.collect(target_dir)
        meta_doc = MetaDocument(product_code=self.env.project_code,
                                data_dir_path=self.env.data_dir_path,
                                meta_dir_name=self.env.meta_dir_name,
                                data_file_suffix=self.env.data_file_suffix,
                                record_id_sep=self.env.code_sep)
        
        for _file_path_ in collected:
            local_file_path = _file_path_.partition(path_sep+self.env.doc_source_dir_name+path_sep)[-1]
            file_dir, _, file_name = local_file_path.rpartition(path_sep)

            suffix= sha1(bytes(path_join(self.env.project_code, file_dir),
                               self.env.default_encoding)).hexdigest()[:self.env.key_length]

            lib_file_name = self.env.code_sep.join([file_name, suffix])
            
            meta_rec = MetaRecord(file_name=file_name,
                                  target_dir=file_dir,
                                  lib_suffix=suffix)
            meta_doc.register(meta_rec)
            self.collection[lib_file_name] = _file_path_
          
        meta_doc.save()
        self._save()
        return self.collection

    
    def _save(self):
        if self.collection:
            for _file_name_ in self.collection:
                source = self.collection[_file_name_]
                destination = path_join(self.env.data_dir_path,
                                        self.env.lib_dir_name, _file_name_)
                copy_file(source, destination)


    def make_workspace_path(self, target_dir=None):
        if target_dir:
            workspace_path = path_join(self.env.workspace_dir_path,
                                       self.env.project_code,
                                       self.env.doc_source_dir_name,
                                       target_dir)
        else:
            workspace_path = path_join(self.env.workspace_dir_path,
                                       self.env.project_code,
                                       self.env.doc_source_dir_name)
        return workspace_path


    def collect(self, target_dir):
        collected_paths = set()

        for _dir_ in walk(target_dir):
            current_dir = _dir_[0]
            files = _dir_[2]
            
            for _file_name_ in files:
                if _file_name_.rpartition(".")[-1] in self.env.doc_file_extensions:
                    collected_paths.add(path_join(current_dir, _file_name_))
        return collected_paths



class AddOperation(Operation):
    def __init__(self, env):
        super().__init__(env)
        source_dir = path_join(self.env.source_dir,
                               self.env.doc_source_dir_name)

        if self.copy_project(source_dir):
            self.status.append(OperationStatusSignals.Add.Ok)
        else:
            self.status.append(OperationStatusSignals.Add.Failed)



class CheckOutOperation(Operation):
    def __init__(self, env):
        super().__init__(env)
        meta_doc = MetaDocument(product_code=self.env.project_code,
                                data_dir_path=self.env.data_dir_path,
                                meta_dir_name=self.env.meta_dir_name,
                                data_file_suffix=self.env.data_file_suffix,
                                record_id_sep=self.env.code_sep)
        meta_doc.read()
        for _ in meta_doc.get_contents():
            signature, record = _
            record = MetaRecord(**record)
            source_file_path = path_join(self.env.data_dir_path,
                                         self.env.lib_dir_name,
                                         signature)
            target_dir = self.make_workspace_path(record.target_dir)
            makedirs(target_dir, exist_ok=True)            
            target_file_path = path_join(target_dir,
                                         record.file_name)
            copy_file(source_file_path, target_file_path)
            self.status.append(OperationStatusSignals.CheckOut.Ok)

        jira_ticket = self.request_jira_ticket()
        ticket_summary_updated = not JIRASignals.TicketSummaryUpdate.Failed in self.status
        if ticket_summary_updated and self.env.git_in_workspace:
            repo = GitConnector(self.workspace_path)
            repo.make_branch(product_id=self.env.project_code,
                             ticket_summary=jira_ticket,
                             doc_source_dir_path=self.env.doc_source_dir_name)
            self.status.append(OperationStatusSignals.CheckOut.Ok)

    

class CheckInOperation(Operation):
    def __init__(self, env):
        super().__init__(env)
        meta_doc = MetaDocument(product_code=self.env.project_code,
                                data_dir_path=self.env.data_dir_path,
                                meta_dir_name=self.env.meta_dir_name,
                                data_file_suffix=self.env.data_file_suffix,
                                record_id_sep=self.env.code_sep)
        self.feature_branches = []
        meta_doc.read()
        self.copy_project(self.workspace_path)
        jira_ticket = self.request_jira_ticket()
        GitConnector(self.env.data_dir_path).make_branch(
            product_id=self.env.project_code,
            ticket_summary=jira_ticket,
            doc_source_dir_path=self.env.lib_dir_name)
        self.status = OperationStatusSignals.CheckIn.Ok



class MergeOperation(Operation):
    def __init__(self, env):
        super().__init__(env)
        auto_directive = DirectiveBuffer.doc_property(
            name_space=DirectiveNameSpace.Only._,
            attribute='',
            sep=self.env.name_space_sep)
        product_directive = DirectiveBuffer.doc_property(
            name_space=DirectiveNameSpace.Default._,
            attribute=DirectiveNameSpace.Default.product,
            sep=self.env.name_space_sep)

        version_directive = DirectiveBuffer.doc_property(
            name_space=DirectiveNameSpace.Default._,
            attribute=DirectiveNameSpace.Default.version,
            sep=self.env.name_space_sep)

        if self.workspace_path:
            meta_doc = MetaDocument(product_code=self.env.project_code,
                                    data_dir_path=self.env.data_dir_path,
                                    meta_dir_name=self.env.meta_dir_name,
                                    data_file_suffix=self.env.data_file_suffix,
                                    record_id_sep=self.env.code_sep)
            meta_doc.read()

            for _ in meta_doc.get_contents():
                signature, record = _
                record = MetaRecord(**record)

                if record.file_name.endswith(self.env.default_doc_format):
                    target_dir = self.make_workspace_path(record.target_dir)
                    target_file_path = path_join(target_dir,
                                                 record.file_name)
                    with open(target_file_path) as doc_file:
                        buffer = DirectiveBuffer(doc_file, self.env)
                        for _directive_ in buffer.directives:
                            if _directive_ == auto_directive:
                                agent = AutoAgent(self.env, doc_file)
                                agent.run(buffer.directives[_directive_])
                            elif _directive_ == product_directive:
                                agent = ProductAgent(self.env, doc_file)
                                agent.run(buffer.directives[_directive_])
                            elif _directive_ == version_directive:
                                agent = VersionAgent(self.env, doc_file)
                                agent.run(buffer.directives[_directive_])
                else:
                    self.status.append(OperationStatusSignals.Merge.Failed)
        else:
            self.status.append(OperationStatusSignals.Merge.Failed)


Statistics = namedtuple('Statistics', ['file_path',
                                       'sentence'])



class DetectOperation(Operation):
    '''Evaluates the given documentation project using the requested criterion (target). 

    Initially, this operation only detects duplicates.
    '''
    def __init__(self, env,
                 target=TargetMark.Duplicate,
                 context=ContextMark.Paragraph):
        super().__init__(env)
        self.target = target
        self.context = context
        self.contents = {}

    def inspect(self):
        '''Iterates through the assets in the context of the supplied target'''
        project_documents = self.make_workspace_path()
        if self.target == TargetMark.Duplicate:
            for _doc_ in self.collect(project_documents):
                if _doc_.endswith(self.env.default_doc_format):
                    self._collect_duplicates(_doc_)


    def _collect_duplicates(self, document):
        if self.context is ContextMark.Paragraph:
            doc = Text(document)
            for _ in doc.paragraphs.contents:
                for _s_ in _.sentences:
                    if _s_ not in self.contents:
                        self.contents[_s_] = []
                    self.contents[_s_].append(Statistics(doc.file_path,
                                                         _.sentences[_s_]))


    def display(self):
        if self.contents:
            for _ in self.contents:
                if len(self.contents[_]) > 1:
                    for _dupl_ in self.contents[_]:
                        text = _dupl_.sentence.text
                        if text.strip() and text[0].isalnum():
                            yield _dupl_.file_path, text[:32] + ' ' * padding



