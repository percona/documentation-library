#!/usr/bin/env python3

import argparse

from messages import Help
from constants import (OperationName as op_name,
                       UIArgumentName as ui_name,
                       OptionInclude,
                       NameFactory)


class InterfaceType:
    class CLI: pass



class CLIArgumentFactory(NameFactory):
    def __init__(self, opt_sep_char, name_sep_char):
        super().__init__(name_sep_char)
        self._opt_sep = opt_sep_char[0]

    
    def make(self, attr_name):
        top_argument = super().make(attr_name)
        opt_name = super()._normalize(self._opt_sep, attr_name)
        opt_name = '--{}'.format(opt_name)

        class CLIArgument(top_argument.__class__):
            def __init__(self, name, option):
                super().__init__(name)
                self.option = option

        return CLIArgument(name=attr_name, option=opt_name)



class CLI:
    def __init__(self, option_sep_char, name_sep_char):
        self.arguments = dict()
        self.operation = None

        cli_attr = CLIArgumentFactory(opt_sep_char=option_sep_char,
                                      name_sep_char=name_sep_char)

        project_code = cli_attr.make(ui_name.project_code)
        source_dir = cli_attr.make(ui_name.source_dir)
        ticket_id = cli_attr.make(ui_name.ticket_id)
        include = cli_attr.make(ui_name.include)
        context = cli_attr.make(ui_name.context)
        target = cli_attr.make(ui_name.target)

        main_command = argparse.ArgumentParser()
        sub_commands = main_command.add_subparsers(dest=ui_name.operation)

        add_sc = sub_commands.add_parser(op_name.add,
                                              help=Help.register_project())
        add_sc.add_argument(project_code.option,
                            dest=project_code.name,
                            required=True)
        add_sc.add_argument(source_dir.option,
                            dest=source_dir.name,
                            required=True)

        checkout_sc = sub_commands.add_parser(op_name.checkout,
                                              help=Help.checkout_project())
        checkout_sc.add_argument(project_code.option,
                                 dest=project_code.name,
                                 required=True)
        checkout_sc.add_argument(ticket_id.option, dest=ticket_id.name,
                                 required=True)

        checkin_sc = sub_commands.add_parser(op_name.checkin,
                                             help=Help.checkin_project())
        checkin_sc.add_argument(project_code.option,
                                dest=project_code.name,
                                required=True)
        checkin_sc.add_argument(ticket_id.option,
                                dest=ticket_id.name,
                                required=True)

        merge_sc = sub_commands.add_parser(op_name.merge,
                                           help=Help.merge_project())
        merge_sc.add_argument(project_code.option,
                              dest=project_code.name,
                              required=True)
        merge_sc.add_argument(include.option,
                              choices=[OptionInclude.auto,
                                       OptionInclude.product,
                                       OptionInclude.version],
                              default=OptionInclude.auto,
                              dest=include.name,
                              required=False)

        detect_sc = sub_commands.add_parser(op_name.detect,
                                            help=Help.detect_project())
        detect_sc.add_argument(project_code.option,
                               dest=project_code.name,
                               required=True)
        detect_sc.add_argument(target.option,
                               dest=target.name,
                               required=False)
        detect_sc.add_argument(context.option,
                               dest=context.name,
                               required=False)

        self.arguments = vars(main_command.parse_args())



class CLIMessage:
    def __init__(self, title, prompt, text_width, legend=None, decoration_token=' '):
        self.title = title.title()
        self.text_width = int(text_width)
        self.decoration = str(decoration_token[0]) * self.text_width
        self.prompt = prompt
        if legend:
            self.legend = legend[:self.text_width]
        else:
            self.legend = ''


    def make(self):
        contents = {'title': self.title,
                    'legend': self.legend,
                    'prompt': self.prompt,
                    'decoration':self.decoration}
        message = ''
        if self.legend:
            message = '\n{title}\n{decoration}\n{legend}\n{decoration}\n{prompt}: '.format(**contents)
        else:
            message = '\n{title}\n{decoration}\n{prompt}: '.format(**contents)
        return message
