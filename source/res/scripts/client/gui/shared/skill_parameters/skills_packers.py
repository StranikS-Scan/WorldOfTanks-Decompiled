# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/skill_parameters/skills_packers.py
from typing import TYPE_CHECKING
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import Color
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_booster_model import PerkImpactType
from gui.shared.skill_parameters import SKILLS, formatters
from items.tankmen import MAX_SKILL_LEVEL
if TYPE_CHECKING:
    from typing import List, Tuple, Union, Dict, Callable, Any
    from items.readers.skills_readers import SkillDescrsArg

def packBase(descrArgs, skillLevel, *args, **kwargs):
    keyArgs = {}
    kpiArgs = []
    lowEfficiency = kwargs.get('lowEfficiency', False)
    isTmanTrainedVeh = kwargs.get('isTmanTrainedVeh', False)
    customValues = kwargs.get('customValues')
    isSkillAlreadyEarned = kwargs.get('isSkillAlreadyEarned')
    hasBooster = kwargs.get('hasBooster')
    for paramName, paramDescArgs in descrArgs:
        if customValues and paramName in customValues:
            paramValue = customValues[paramName](paramDescArgs, False)
            paraMaxValue = customValues[paramName](paramDescArgs, True)
        else:
            paramValue = paramDescArgs.value * skillLevel
            paraMaxValue = paramDescArgs.value * MAX_SKILL_LEVEL
        color = Color.RED.value if lowEfficiency and isTmanTrainedVeh and isSkillAlreadyEarned and not hasBooster else (Color.YELLOW.value if paramDescArgs.situational else Color.GREENBRIGHT.value)
        keyArgs[paramName] = {'value': formatters.getDescriptionValue(paramDescArgs, paramValue),
         'color': color}
        if paramDescArgs.isKpiVisible:
            kpiArgs.append((formatters.getKpiValue(paramDescArgs, paraMaxValue), formatters.getKpiDescription(paramDescArgs), PerkImpactType.NEUTRAL.value if paramDescArgs.situational else PerkImpactType.POSITIVE.value))

    return {'keyArgs': keyArgs,
     'kpiArgs': kpiArgs}


def _packCommanderExpert(descrArgs, skillLevel, *args, **kwargs):
    damageMonitoringDelayBase = 4.5
    damageMonitoringDelayMinimum = 0.5

    def _customValue(skillDescrArg, isKpi):
        if isKpi:
            delay = damageMonitoringDelayBase - abs(skillDescrArg.value * MAX_SKILL_LEVEL)
            return max(damageMonitoringDelayMinimum, delay)
        delay = damageMonitoringDelayBase - abs(skillDescrArg.value * skillLevel)
        return max(damageMonitoringDelayMinimum, delay)

    kwargs.update({'customValues': {'damageMonitoringDelay': _customValue}})
    return packBase(descrArgs, skillLevel, *args, **kwargs)


def _packEnemyShotPredictor(descrArgs, skillLevel, *args, **kwargs):
    notificationDelayBase = 2.1
    notificationDelayMinimum = 0.1

    def _customValue(skillDescrArg, isKpi):
        if isKpi:
            delay = notificationDelayBase - abs(skillDescrArg.value * MAX_SKILL_LEVEL)
            return max(notificationDelayMinimum, delay)
        delay = notificationDelayBase - abs(skillDescrArg.value * skillLevel)
        return max(notificationDelayMinimum, delay)

    kwargs.update({'customValues': {'artNotificationDelayFactor': _customValue}})
    return packBase(descrArgs, skillLevel, *args, **kwargs)


def _packGunnerGunsmith(descrArgs, skillLevel, *args, **kwargs):
    base = 0.25

    def _customValue(skillDescrArg, isKpi, skillEfficiency=kwargs.get('skillEfficiency', 1.0)):
        return skillDescrArg.value * MAX_SKILL_LEVEL if isKpi else base - abs(skillDescrArg.value * skillLevel)

    kwargs.update({'customValues': {'damageAndPiercingDistributionLowerBound': _customValue,
                      'damageAndPiercingDistributionUpperBound': _customValue}})
    return packBase(descrArgs, skillLevel, *args, **kwargs)


def _parkSixthSense(descrArgs, skillLevel, *args, **kwargs):

    def _customValue(skillDescrArg, isKpi, customValues=kwargs.get('customValues', {})):
        if not isKpi:
            if customValues and skillDescrArg.name in customValues:
                booster = customValues[skillDescrArg.name]()
                if booster:
                    paramValue = getattr(booster, skillDescrArg.name)
                    if paramValue:
                        return paramValue
        return skillDescrArg.value

    kwargs.update({'customValues': {'delay': _customValue}})
    return packBase(descrArgs, skillLevel, *args, **kwargs)


g_skillPackers = {SKILLS.COMMANDER_EXPERT: _packCommanderExpert,
 SKILLS.COMMANDER_ENEMY_SHOT_PREDICTOR: _packEnemyShotPredictor,
 SKILLS.GUNNER_GUNSMITH: _packGunnerGunsmith,
 SKILLS.COMMANDER_SIXTH_SENSE: _parkSixthSense}
