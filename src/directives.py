#!/usr/bin/env python3

from collections import namedtuple
from os import path as os_path
from os import sep as os_sep
from shutil import copy as copy_file


Directive = namedtuple('Directive', ['prefix',
                                     'name_space',
                                     'attribute',
                                     'value'])

class DirectiveLine:
    def __init__(self, line, rule_set):
        self._rule_set = rule_set
        line = line.strip().lower()
        self._contents = self._make(line.split())
        self._is_valid_directive = False
        if self._contents:
            self._is_valid_directive = True

    @property
    def is_valid(self):
        return self._is_valid_directive

    @property
    def contents(self):
        return self._contents
        
    @property
    def name_space(self):
        return self._contents.name_space

    @property
    def value(self):
        return self._contents.value

    @property
    def attribute(self):
        return self._contents.attribute

    def _make(self, line):
        status = None

        if len(line):
            prefix = line[0]

            if prefix == self._rule_set.directive_prefix:
                directive = line[1].partition(self._rule_set.directive_name_space_sep)

                if len(line) >= len(directive):
                    name_space = directive[0]
                    attribute = directive[-1].partition(self._rule_set.directive_value_sep)[0]
                    value = line[2:]
                    status = True
                else:
                    status = False
            else:
                status = False
        else:
            status = False

        return status and Directive(prefix,
                                    name_space,
                                    attribute,
                                    value)


class DirectiveBuffer:
    @staticmethod
    def doc_property(name_space, attribute, sep):
        return sep.join([name_space, attribute])

    def __init__(self, doc_file, rule_set):
        self._doc_file = doc_file
        self._rule_set = rule_set
        self.directives = self._inspect()
        

    def _inspect(self):
        collected = dict()
        for each in self._doc_file:
            d = DirectiveLine(each, self._rule_set)
            if d.is_valid:
                doc_property = DirectiveBuffer.doc_property(name_space=d.name_space,
                                                            attribute=d.attribute,
                                                            sep=self._rule_set.directive_name_space_sep)

                print('[Debug] Doc property: {}'.format(doc_property))

                if doc_property in collected:
                    print('[Debug] Doc property value: {}'.format(collected[doc_property]))
                    collected[doc_property].add(' '.join(d.value))
                else:
                    collected[doc_property] = set()
                    collected[doc_property].add(' '.join(d.value))

        return collected
            

class DirectiveAgent:
    def __init__(self, env, file_name):
        self.file_name = file_name
        self.env = env
    def run(self, values):
        print("Running with: {}".format(values))



class AutoAgent(DirectiveAgent):
    def __init__(self, env, file_name):
        super().__init__(env, file_name)
    def run(self, values):

        print('[DEBUG] Auto agent running! {}'.format(values))
        print('[DEBUG] Source file: {}'.format(self.file_name.name))
        for each_v in values:
            target_path = self.file_name.name.rpartition(self.env.project_code)
            target_project = os_path.join(target_path[0], each_v.upper())
            target = os_path.join(target_project, target_path[-1].partition(os_sep)[-1])

            print('[DEBUG] Target file: {}'.format(target))
            if self.env.project_code != each_v.upper():
                copy_file(self.file_name.name, target)
            

#            print('[DEBUG] Target file: {}'.format(os_path.join(self.env.workspace_dir_path,
#                                                                each_v.upper(),
#                                                                self.env.doc_source_dir_name)))

        return None



class ProductAgent(DirectiveAgent):
    def __init__(self, env, file_name):
        super().__init__(env, file_name)
    def run(self, values):
        print("Product agent running: {}".format(values))
        return None



class VersionAgent(DirectiveAgent):
    def __init__(self, env, file_name):
        super().__init__(env, file_name)
    def run(self, values):
        print("Version agent running: {}".format(values))
        return None
