# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/misc.py
import BigWorld
from constants import IS_CLIENT, IS_BOT
from debug_utils import LOG_ERROR
VisualScriptTag = 'visualScript'

class DeferredQueue(object):
    COMMON = 0
    SINGLE = 1


class ASPECT(object):
    SERVER = 'SERVER'
    CLIENT = 'CLIENT'
    ALL = [CLIENT, SERVER]


class EDITOR_TYPE(object):
    NONE = 0
    STR_KEY_SELECTOR = 1
    ENUM_SELECTOR = 2


def makePlanPath(planName):
    return 'vscript/plans/{}.xml'.format(planName)


def preloadPlanXml(func):

    def wrapper(self, planName, *args, **kwargs):
        if not IS_CLIENT and not IS_BOT:

            def onCallback(future):
                try:
                    future.get()
                except BigWorld.FutureNotReady:
                    LOG_ERROR("[VScript] Plan xml '%s' not pre-loaded." % planName)

                func(self, planName, *args, **kwargs)

            future = BigWorld.resMgr.fetchDataSection(makePlanPath(planName))
            future.then(onCallback)
        else:
            func(self, planName, *args, **kwargs)

    return wrapper


def errorVScript(owner, msg):
    LOG_ERROR('[VScript] %s : %s', owner.__class__.__name__, msg)
    owner._writeLog('%s : %s' % (owner.__class__.__name__, msg))
