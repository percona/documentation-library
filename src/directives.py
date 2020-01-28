#!/usr/bin/env python3

from collections import namedtuple
from os import path as os_path
from os import sep as os_sep
from shutil import copy as copy_file

from messages import Info

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
    def name(self):
        return self._rule_set.directive_value_sep.join([
            self.contents.name_space,
            self.contents.attribute])

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
                directive = line[1].partition(
                    self._rule_set.directive_name_space_sep)
                if len(line) >= len(directive):
                    name_space = directive[0]
                    attribute = directive[-1].partition(
                        self._rule_set.directive_value_sep)[0]
                    value = line[2:]
                    status = True
        return status and Directive(prefix,
                                    name_space,
                                    attribute,
                                    value)


class DirectiveBuffer:
    @staticmethod
    def doc_property(name_space, attribute, sep):
        return sep.join([name_space, attribute]).lower()


    def __init__(self, doc_file, rule_set):
        self._doc_file = doc_file
        self._rule_set = rule_set
        self.directives = self._inspect()
        

    def _inspect(self):
        collected = dict()
        for each in self._doc_file:
            d = DirectiveLine(each, self._rule_set)
            if d.is_valid:
                doc_property = DirectiveBuffer.doc_property(
                    name_space=d.name_space,
                    attribute=d.attribute,
                    sep=self._rule_set.directive_name_space_sep)
                if doc_property in collected:
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
        pass



class AutoAgent(DirectiveAgent):
    def __init__(self, env, file_name):
        super().__init__(env, file_name)
    def run(self, values):
        for each_v in values:
            target_path = self.file_name.name.rpartition(self.env.project_code)
            target_project = os_path.join(target_path[0], each_v.upper())
            target = os_path.join(target_project, target_path[-1].partition(os_sep)[-1])

            if self.env.project_code != each_v.upper():
                copy_file(self.file_name.name, target)



class ProductAgent(DirectiveAgent):
    def __init__(self, env, file_name):
        super().__init__(env, file_name)
    def run(self, values):
        Info.DEBUG('Found in file', self.file_name)
        Info.DEBUG('Product agent running',values)
        return None



class VersionAgent(DirectiveAgent):
    def __init__(self, env, file_name):
        super().__init__(env, file_name)
    def run(self, values):
        Info.DEBUG('Found in file', self.file_name)
        Info.DEBUG('Version agent running',values)
        return None
