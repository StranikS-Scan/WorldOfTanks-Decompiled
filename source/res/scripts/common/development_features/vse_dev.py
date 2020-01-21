# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/development_features/vse_dev.py
import fnmatch
import logging
import os
from functools import wraps
import VSE
from visual_script.general import Assert
logger = logging.getLogger(__name__)
base_executors = {}
planObj = None

def wrapBlock(block, beforeExecution=None, execute=None, afterExecution=None):

    def wrap(f):

        @wraps(f)
        def executeWrapper(*args, **kwargs):
            if beforeExecution:
                beforeExecution(*args, **kwargs)
            if execute:
                result = execute(*args, **kwargs)
            else:
                result = f(*args, **kwargs)
            if afterExecution:
                afterExecution(*args, **kwargs)
            return result

        return executeWrapper

    base_executors.setdefault(block, block._execute)
    block._execute = wrap(base_executors[block])


def unwrapBlock(block):
    if block in base_executors:
        block._execute = base_executors[block]


def collectPlans(vseDir, testDir, include, exclude=None):
    collected = []
    for root, dirs, files in os.walk(os.path.join(vseDir, testDir)):
        for fn in files:
            relPath = os.path.relpath(os.path.join(root, fn), vseDir)
            included = any((fnmatch.fnmatch(relPath, '*' + p) for p in include))
            excluded = exclude and any((fnmatch.fnmatch(relPath, '*' + p) for p in exclude))
            if included and not excluded:
                collected.append(relPath)

    return collected


def runTestPlan(planPath):
    global planObj
    if not planObj:
        planObj = VSE.Plan()

    def _logAssert(self, *args, **kwargs):
        if not self._value.getValue():
            logger.error('[FAILED] VSE assert: %s', self._msg.getValue())
        else:
            logger.warn('[PASSED] VSE assert: %s', self._msg.getValue())

    wrapBlock(Assert, _logAssert)
    logger.warn('-- running VSE test plan: %s ', planPath)
    planObj.load(planPath, ['CLIENT'])
    planObj.start()
