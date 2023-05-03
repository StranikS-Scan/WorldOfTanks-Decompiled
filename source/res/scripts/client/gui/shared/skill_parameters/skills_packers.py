# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/skill_parameters/skills_packers.py
from typing import TYPE_CHECKING
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_booster_model import PerkImpactType
from gui.shared.skill_parameters import SKILLS, formatters
from items.tankmen import MAX_SKILL_LEVEL
if TYPE_CHECKING:
    from typing import List, Tuple, Union, Dict, Callable
    from items.readers.skills_readers import SkillDescrsArg

def packBase(descrArgs, skillLevel, customValues=None):
    keyArgs = {}
    kpiArgs = []
    for paramName, paramDescArgs in descrArgs:
        if customValues and paramName in customValues:
            paramValue = customValues[paramName](paramDescArgs, False)
            paraMaxValue = customValues[paramName](paramDescArgs, True)
        else:
            paramValue = paramDescArgs.value * skillLevel
            paraMaxValue = paramDescArgs.value * MAX_SKILL_LEVEL
        keyArgs[paramName] = formatters.getDescriptionValue(paramDescArgs, paramValue)
        if paramDescArgs.isKpiVisible:
            kpiArgs.append((formatters.getKpiValue(paramDescArgs, paraMaxValue), formatters.getKpiDescription(paramDescArgs), PerkImpactType.NEUTRAL.value if paramDescArgs.situational else PerkImpactType.POSITIVE.value))

    return {'keyArgs': keyArgs,
     'kpiArgs': kpiArgs}


def _packCommanderExpert(descrArgs, skillLevel, customValues=None):
    damageMonitoringDelayBase = 4.5
    damageMonitoringDelayMinimum = 0.5

    def _customValue(skillDescrArg, isKpi):
        if isKpi:
            delay = damageMonitoringDelayBase - abs(skillDescrArg.value * MAX_SKILL_LEVEL)
            return max(damageMonitoringDelayMinimum, delay)
        delay = damageMonitoringDelayBase - abs(skillDescrArg.value * skillLevel)
        return max(damageMonitoringDelayMinimum, delay)

    return packBase(descrArgs, skillLevel, {'damageMonitoringDelay': _customValue})


def _packEnemyShotPredictor(descrArgs, skillLevel, customValues=None):
    notificationDelayBase = 2.1
    notificationDelayMinimum = 0.1

    def _customValue(skillDescrArg, isKpi):
        if isKpi:
            delay = notificationDelayBase - abs(skillDescrArg.value * MAX_SKILL_LEVEL)
            return max(notificationDelayMinimum, delay)
        delay = notificationDelayBase - abs(skillDescrArg.value * skillLevel)
        return max(notificationDelayMinimum, delay)

    return packBase(descrArgs, skillLevel, {'artNotificationDelayFactor': _customValue})


def _packGunnerGunsmith(descrArgs, skillLevel, customValues=None):
    base = 0.25

    def _customValue(skillDescrArg, isKpi):
        return skillDescrArg.value * MAX_SKILL_LEVEL if isKpi else base - abs(skillDescrArg.value * skillLevel)

    return packBase(descrArgs, skillLevel, {'damageAndPiercingDistributionLowerBound': _customValue,
     'damageAndPiercingDistributionUpperBound': _customValue})


def _parkSixthSense(descrArgs, skillLevel, customValues=None):

    def _customValue(skillDescrArg, isKpi):
        if not isKpi:
            if customValues and skillDescrArg.name in customValues:
                booster = customValues[skillDescrArg.name]()
                if booster:
                    paramValue = getattr(booster, skillDescrArg.name)
                    if paramValue:
                        return paramValue
        return skillDescrArg.value

    return packBase(descrArgs, skillLevel, {'delay': _customValue})


g_skillPackers = {SKILLS.COMMANDER_EXPERT: _packCommanderExpert,
 SKILLS.COMMANDER_ENEMY_SHOT_PREDICTOR: _packEnemyShotPredictor,
 SKILLS.GUNNER_GUNSMITH: _packGunnerGunsmith,
 SKILLS.COMMANDER_SIXTH_SENSE: _parkSixthSense}
