# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/manual/loggers.py
from uilogging.base.logger import BaseLogger
from uilogging.manual.constants import FEATURE

class ManualLogger(BaseLogger):

    def __init__(self, group):
        super(ManualLogger, self).__init__(FEATURE, group)
