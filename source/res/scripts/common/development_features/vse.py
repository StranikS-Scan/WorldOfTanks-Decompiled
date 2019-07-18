# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/development_features/vse.py
import logging
from functools import wraps
import BigWorld
from visual_script.general import TestCase, Assert
logger = logging.getLogger(__name__)
executors = {}
planObj = None

def wrapBlock(block, beforeExecution):

    def wrap(f):

        @wraps(f)
        def executeWrapper(self, *args, **kwargs):
            beforeExecution(*args, **kwargs)
            return f(self, *args, **kwargs)

        return executeWrapper

    executors.setdefault(block, block._execute)
    block._execute = wrap(executors[block])


def runTestPlan(planPath):
    global planObj
    if not planObj:
        planObj = BigWorld.PyPlan()
    activeCase = [None]

    def _logTestCase(name):
        activeCase[:] = [name]
        if name == 'StopSuite':
            logger.warn('-- VSE test plan finished: %s ', planPath)

    def _logAssert(value, msg):
        if not value:
            logger.error('[FAILED] VSE assert: %s: %s', activeCase[0], msg)
        else:
            logger.warn('[PASSED] VSE assert: %s: %s', activeCase[0], msg)

    wrapBlock(TestCase, _logTestCase)
    wrapBlock(Assert, _logAssert)
    logger.warn('-- running VSE test plan: %s ', planPath)
    planObj.load(planPath, ['CLIENT'])
    planObj.start()
    return
