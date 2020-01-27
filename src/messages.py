#!/usr/bin/env python3

class Alert:

    @staticmethod
    def jira_ticket_not_found(ticket_id):
        return "JIRA ticket '{}' has not been found".format(ticket_id)
    
    @staticmethod
    def uncommitted_changes_exist(project_code):
        return "Some changes in project `{}` are not committed.".format(project_code)

    @staticmethod
    def project_code_exists(project_code):
        return "Project code '{}' already exists".project_code
    
    @staticmethod
    def project_has_unsaved_changes(project_code):
        return 'Project [{}] has uncommitted changes'.format(project_code)

    @staticmethod
    def project_code_not_in_jira_ticket(project_code, ticket_code):
        message = 'The current project code [{}] is different from JIRA ticket ID [{}]'
        return message.format(project_code, ticket_code)

    @staticmethod
    def git_repo_not_found(path):
        return "No Git repository has been detected under '{}'".format(path)

    @staticmethod
    def feature_branch_too_many(project_code, library):
        return 'More than one feature branch is detected for {} under [{}]'.format(project_code, library)



class Info:

    @staticmethod
    def project_created(project_name):
        return "Project '{}' has been created".format(project_name)

    @staticmethod
    def project_loaded(project_name):
        return "Project '{}' has been loaded".format(project_name)

    @staticmethod
    def commit_message(ticket_id):
        return "[MERGED] JIRA ticket '{}'".format(ticket_id)

    @staticmethod
    def work_offline():
        return 'Using offline resources ...'

    @staticmethod
    def DEBUG(mark, value):
        print('[DEBUG] {}: {}'.format(mark, value))

    
class Help:
    readme_path = '../README'

    @staticmethod
    def detect_project():
        return 'Detect specific issues in the given context'

    @staticmethod
    def register_project():
        return 'Register a new project based on the contents of an arbitrary directory'

    @staticmethod
    def checkout_project():
        return 'Load the project data from the library to the working space'

    @staticmethod
    def checkin_project():
        return 'Load the project data from the working space to the library'

    @staticmethod
    def merge_project():
        return 'Scan the project and reuse its assets in other projects'

    @staticmethod
    def no_operation(readme_file_path):
        with open(readme_file_path) as readme:
            for _line_ in readme:
                yield '\t{}'.format(_line_)
    
class Request:

    @staticmethod
    def ticket_summary(ticket_id):
        return 'Ticket summary [{}]'.format(ticket_id)

    @staticmethod
    def ticket_default_summary(existing_text):
        return "Default text '{}'".format(existing_text)

    @staticmethod
    def ticket_summary_prompt():
        return 'New summary (leave empty to keep the default)'
