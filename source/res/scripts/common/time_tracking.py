# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/time_tracking.py
from constants import SERVER_TICK_LENGTH, IS_CLIENT, IS_BOT
from debug_utils import LOG_WARNING
import sys
from time import time
if not IS_CLIENT and not IS_BOT:
    from insights.common import incrTickOverspends
DEFAULT_TIME_LIMIT = 0.02
DEFAULT_TICK_LENGTH = SERVER_TICK_LENGTH

def LOG_TIME_WARNING(spentTime, context=None, tickLength=DEFAULT_TICK_LENGTH, *args):
    percent = round(spentTime / tickLength * 100)
    if context is None:
        context = sys._getframe(1).f_code.co_name
    LOG_WARNING(('Time is overspent in %s: %.4f sec, %d%% of %.2f sec tick' % (context,
     spentTime,
     percent,
     tickLength)), *args)
    return


class TimeTracker(object):

    def __init__(self, context=None, timeLimit=DEFAULT_TIME_LIMIT, tickLength=DEFAULT_TICK_LENGTH):
        self.context = context
        self.timeLimit = timeLimit
        self.tickLength = tickLength

    def __enter__(self):
        self.startTime = time()
        self.checkpoints = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        spentTime = time() - self.startTime
        if spentTime > self.timeLimit:
            if not IS_CLIENT and not IS_BOT:
                incrTickOverspends()
            context = self.context
            if context is None:
                context = sys._getframe(1).f_code.co_name
            checkpoints = self.checkpoints
            if checkpoints:
                startTime = self.startTime
                for checkpoint in checkpoints:
                    endTime = checkpoint[1]
                    checkpoint[1] -= startTime
                    startTime = endTime

                LOG_TIME_WARNING(spentTime, context, self.tickLength, checkpoints)
            else:
                LOG_TIME_WARNING(spentTime, context, self.tickLength)
        return

    def checkpoint(self, name):
        self.checkpoints.append([name, time()])


def timetracked(func=None, context=None, timeLimit=DEFAULT_TIME_LIMIT, tickLength=DEFAULT_TICK_LENGTH):

    def decorator(f):

        def wrapper(*args, **kwargs):
            startTime = time()
            try:
                return f(*args, **kwargs)
            finally:
                spentTime = time() - startTime
                if spentTime > timeLimit:
                    LOG_TIME_WARNING(spentTime, context if context is not None else f.__name__, tickLength)
                    if not IS_CLIENT and not IS_BOT:
                        incrTickOverspends()

            return

        return wrapper

    return decorator(func) if func is not None else decorator
