#!/usr/bin/env python3

from os import sep as path_sep
from re import split as re_split
from string import whitespace, punctuation

from jira import JIRA
from git import Repo
from messages import Alert
from signals import VerificationSignals, GitSignals, JIRASignals
from errors import JIRATicketNotFound, GitRepositoryNotFound


class GitConnector:
    def __init__(self, workspace_path):
        self._workspace_path = workspace_path
        self._repo = self._load_repository(self._workspace_path)


    def make_branch(self, product_id, ticket_summary, doc_source_dir_path):
        '''Creates a Git branch based on the provided JIRA ticket object'''
        git_index_file = self._repo.index
        git_index_file.add(path_sep.join([self._workspace_path,
                                          doc_source_dir_path]))
        git_index_file.commit(ticket_summary.ticket_id + ": " + ticket_summary.text)
        
        self._repo.create_head(ticket_summary.make_branch_name(product_id)).checkout()

        return GitSignals.RepositoryCreate.Ok


    def _load_repository(self, path):
        '''Attempts to create an instance of a Git repository under the provided path'''

        repo =  Repo.init(self._workspace_path)

        if not repo:
            print(Alert.git_repo_not_found(self.workspace_path))
        else:
            self._repo = repo

        return repo


    @property
    def repository(self):
        return self._repo


    @property
    def workspace_path(self):
        return self._workspace_path

    @workspace_path.setter
    def workspace_path(self, new_path):
        if self._load_repository(new_path):
            self._workspace_path = new_path
        

class JIRAConnector:
    def __init__(self, site_url):
        self.site_url = site_url
        self.connection = JIRA(self.site_url)

    def find_ticket(self, ticket_id, ticket_id_sep):
        class JIRATicketRequest:
            info = None
            status = None
        found = None
        requested_ticket = self.connection.issue(ticket_id)
        if requested_ticket:
            JIRATicketRequest.info = JIRATicketInfo(ticket_id,
                                                    requested_ticket.fields.summary,
                                                    ticket_id_sep)
            JIRATicketRequest.status = VerificationSignals.TicketCodeValid.Ok
        else:
            JIRATicketRequest.info = None
            JIRATicketRequest.status = VerificationSignals.TicketCodeValid.Failed
        return JIRATicketRequest



class JIRATicketInfo:
    def __init__(self, ticket_id, text, ticket_id_sep):
        self._ticket_id = ticket_id.upper()
        self._ticket_id_sep = ticket_id_sep
        self._text = ''
        self._normalized_text = ''
        self.text = text
        self.branch_name = None


    def update_summary(self, request_format):
        status = None
        if request_format:
            self.text = input(request_format.make()).strip()
            status = JIRASignals.TicketSummaryUpdate.Ok
        else:
            status = JIRASignals.TicketSummaryUpdate.Failed

        return status

    
    def make_branch_name(self, product_id):
        '''Combines the ticket information with the version component from product code
        to make a branch name; tokens are delimited by a configurable 'code
        separator'.'''

        product_version = product_id.rpartition(self._ticket_id_sep)[-1]
        self.branch_name = self._ticket_id_sep.join([self.ticket_id,
                                                     self.normalized_text,
                                                     product_version])
        return self.branch_name


    def _normalize(self, sep):
        '''Replaces whitespace and punctuation characters with a a configurable 'code
        separator'. Alphabetic characters are converted to upper case.
        '''

        pattern = '[{}{}]'.format(whitespace, punctuation)
        return sep.join(token
                        for token
                        in re_split(pattern, self.text)
                        if token).upper()

    @property
    def ticket_id(self):
        return self._ticket_id


    @property
    def normalized_text(self):
        return self._normalized_text


    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        if new_text.strip():
            self._text = new_text
            self._normalized_text = self._normalize(self._ticket_id_sep)
