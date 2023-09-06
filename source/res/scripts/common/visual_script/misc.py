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
    HANGAR = 'HANGAR'
    ALL = [CLIENT, SERVER, HANGAR]


class EDITOR_TYPE(object):
    NONE = 0
    STR_KEY_SELECTOR = 1
    ENUM_SELECTOR = 2
    COMPLEX_KEY_SELECTOR = 3
    VEHICLE_NAME_SELECTOR = 4
    VEHICLE_PRESET_SELECTOR = 5


class BLOCK_MODE(object):
    NONE = 0
    UNIQUE = 32
    DEV = 64
    HIDE_FROM_LIB = 256


def makePlanPath(planName):
    return 'vscript/plans/{}.xml'.format(planName)


def errorVScript(owner, msg):
    LOG_ERROR('[VScript]', owner.__class__.__name__, msg)
    owner._writeLog('%s : %s' % (owner.__class__.__name__, msg))


def readVisualScriptPlanParams(section, commonParams={}):
    params = dict(commonParams.items())
    if section.has_key('params'):
        for name, subsection in section['params'].items():
            if subsection.has_key('item'):
                params[name] = [ value.asString for idx, value in subsection.items() ]
            params[name] = subsection.asString

    return params


def readVisualScriptPlans(section, commonParams={}):
    plans = []
    for name, subsection in section.items():
        if name == 'plan':
            planDef = {}
            if subsection.has_key('name'):
                planDef['name'] = subsection['name'].asString
                planDef['params'] = readVisualScriptPlanParams(subsection, commonParams)
                planDef['plan_id'] = subsection['plan_id'].asString if subsection.has_key('plan_id') else ''
            else:
                planDef['name'] = subsection.asString
                planDef['params'] = dict(commonParams)
                planDef['plan_id'] = ''
            plans.append(planDef)

    return plans
