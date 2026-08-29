# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/marathon/loggers.py
import json
from enum import Enum
from uilogging.base.logger import MetricsLogger
from wotdecorators import noexcept
from helpers import time_utils

class MarathonEvents(Enum):
    OPEN_PAGE = 'OpenPage'
    FLAG_CLICKED = 'FlagClicked'


class MarathonLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(MarathonLogger, self).__init__('marathon')

    @noexcept
    def logEnter(self, item):
        logTime = int(time_utils.getServerUTCTime())
        self.log(action='EnterMarathon', item=item, info=json.dumps(logTime))
