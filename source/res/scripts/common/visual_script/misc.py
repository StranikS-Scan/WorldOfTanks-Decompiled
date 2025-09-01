# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/misc.py
import typing
from debug_utils import LOG_ERROR, LOG_WARNING
if typing.TYPE_CHECKING:
    from typing import Dict, Union
    from ResMgr import DataSection
    from visual_script.block import Block
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


class EDITOR_CUSTOM_ICON(object):
    EVENT_DELAYED = 1


class BLOCK_MODE(object):
    NONE = 0
    UNIQUE = 32
    DEV = 64
    HIDE_FROM_LIB = 256
    CAN_BE_CONST_EXPR = 2048


def makePlanPath(planName):
    return 'vscript/plans/{}.xml'.format(planName)


def errorVScript(owner, msg):
    LOG_ERROR('[VScript]', str(owner.planName()), str(owner.blockId()), msg)
    owner._writeLog('%s:%s : %s' % (owner.planName(), owner.blockId(), msg))


def warningVScript(owner, msg):
    LOG_WARNING('[VScript]', str(owner.planName()), str(owner.blockId()), msg)
    owner._writeLog('%s:%s : %s' % (owner.planName(), owner.blockId(), msg))


def readVisualScriptPlanParams(section, commonParams={}):
    params = dict(commonParams.items())
    if section.has_key('params'):
        for name, subsection in section['params'].items():
            if subsection.has_key('item'):
                params[name] = [ value.asString for idx, value in subsection.items() ]
            params[name] = subsection.asString

    return params


def readVisualScriptPlan(section, commonParams={}):
    planDef = {}
    if section.has_key('name'):
        planDef['name'] = section['name'].asString
        planDef['params'] = readVisualScriptPlanParams(section, commonParams)
        planDef['plan_id'] = section['plan_id'].asString if section.has_key('plan_id') else ''
    else:
        planDef['name'] = section.asString
        planDef['params'] = dict(commonParams)
        planDef['plan_id'] = ''
    return planDef


def readVisualScriptPlans(section, commonParams={}):
    plans = []
    for name, subsection in section.items():
        if name == 'plan':
            plans.append(readVisualScriptPlan(subsection, commonParams))

    return plans


def readVisualScriptSection(section, aspects=None):
    if aspects is None:
        aspects = ASPECT.ALL
    if not aspects:
        return {}
    elif section.has_key(VisualScriptTag):
        vseSection = section[VisualScriptTag]
        commonParams = {}
        if vseSection.has_key('common'):
            commonParams = readVisualScriptPlanParams(vseSection['common'])
        return {aspect:_readVisualScriptAspect(vseSection, aspect.lower(), commonParams) for aspect in aspects}
    else:
        return {aspect:[] for aspect in aspects}


def _readVisualScriptAspect(section, aspect, commonParams):
    plans = []
    if section.has_key(aspect):
        plans = readVisualScriptPlans(section[aspect], commonParams)
    return plans
