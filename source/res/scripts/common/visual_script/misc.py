# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/misc.py
import BigWorld
from constants import IS_CLIENT
from debug_utils import LOG_ERROR
VisualScriptTag = 'visualScript'

class DeferredQueue(object):
    COMMON = 0
    SINGLE = 1


class ASPECT(object):
    SERVER = 'SERVER'
    CLIENT = 'CLIENT'


def makePlanPath(planName):
    return 'vscript/plans/{}.xml'.format(planName)


def preloadPlanXml(func):

    def wrapper(self, planName, *args, **kwargs):
        if not IS_CLIENT:

            def onCallback(future):
                try:
                    future.get()
                except BigWorld.FutureNotReady:
                    LOG_ERROR("Plan xml '%s' not pre-loaded." % planName)

                func(self, planName, *args, **kwargs)

            future = BigWorld.resMgr.fetchDataSection(makePlanPath(planName))
            future.then(onCallback)
        else:
            func(self, planName, *args, **kwargs)

    return wrapper


def errorVScript(owner, msg):
    LOG_ERROR('[VScript] %s : %s', owner.__class__.__name__, msg)
    owner._writeLog('%s : %s' % (owner.__class__.__name__, msg))
