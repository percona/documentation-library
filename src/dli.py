#!/usr/bin/env python3
'''The *main* module of the app (dli - documentation Library interface). Its job is
to load the key components and manage their interactions based on user's
requests.'''

from env import Environment
from lib import DocProject
from constants import OperationName as op_name
from messages import Help

e = Environment()
dp = DocProject(e)

if e.operation == op_name.add: dp.add()
elif e.operation == op_name.checkout: dp.checkout()
elif e.operation == op_name.checkin:  dp.checkin()
elif e.operation == op_name.merge: dp.merge()
elif e.operation == op_name.detect: dp.detect()
else:
    for _line_ in Help.no_operation(e.readme_path):
        print(_line_)
