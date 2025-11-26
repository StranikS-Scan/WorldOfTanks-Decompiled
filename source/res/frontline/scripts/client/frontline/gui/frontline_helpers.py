# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/frontline_helpers.py
import BigWorld
from collections import defaultdict
from itertools import chain
import CommandMapping
import typing
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineState
from frontline_common.frontline_constants import RESERVES_MODIFIER_NAMES
from gui.Scaleform.daapi.view.common.keybord_helpers import getHotKeysInfo
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import createEpicParam
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import time_utils, dependency, i18n
from items import vehicles
from skeletons.gui.game_control import IEpicBattleMetaGameController

@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def geFrontlineState(withPrimeTime=False, epicController=None):
    now = time_utils.getCurrentLocalServerTimestamp()
    startDate, endDate = epicController.getSeasonTimeRange()
    if now > endDate:
        season = epicController.getCurrentSeason()
        endSeasonDate = season.getEndDate() if season else 0
        return (FrontlineState.FINISHED, endSeasonDate, int(endSeasonDate - now))
    if now < startDate:
        return (FrontlineState.ANNOUNCE, startDate, int(startDate - now))
    primeTimeStatus, timeLeft, _ = epicController.getPrimeTimeStatus()
    if primeTimeStatus is not PrimeTimeStatus.AVAILABLE:
        if withPrimeTime:
            return (FrontlineState.FROZEN, int(now + timeLeft), timeLeft)
        return (FrontlineState.FROZEN, endDate, int(endDate - now))
    return (FrontlineState.FINISHED, 0, 0) if not epicController.isEnabled() else (FrontlineState.ACTIVE, endDate, int(endDate - now))


def getStatesUnavailableForHangar():
    return [FrontlineState.FINISHED, FrontlineState.ANNOUNCE]


def getReserveIconPath(icon):
    return 'img://gui/maps/icons/artefact/{}.png'.format(icon)


def getHotKeyListCommands():
    return [CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_LEFT, CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_RIGHT]


def getHotKeyInfoListByIndex(index):
    commands = getHotKeyListCommands()
    return [ keyInfo.asDict() for keyInfo in getHotKeysInfo(commands[index]) ]


def isHangarAvailable():
    frontlineState, _, _ = geFrontlineState()
    return frontlineState not in getStatesUnavailableForHangar()


class FLBattleTypeDescription(object):

    @staticmethod
    def getDescription(reservesModifier=None):
        return FLBattleTypeDescription.__getDescription('description', reservesModifier)

    @staticmethod
    def getShortDescription(reservesModifier=None):
        return FLBattleTypeDescription.__getDescription('shortDescription', reservesModifier)

    @staticmethod
    def getTitle(reservesModifier=None):
        return FLBattleTypeDescription.__getDescription('title', reservesModifier)

    @staticmethod
    def getBattleTypeIconPath(reservesModifier=None, sizeFolder='c_136x136'):
        if reservesModifier is None:
            return ''
        else:
            modifier = RESERVES_MODIFIER_NAMES[reservesModifier]
            iconRes = FLBattleTypeDescription.__getRI().dyn(sizeFolder).dyn(modifier)
            return backport.image(iconRes()) if iconRes.exists() else ''

    @staticmethod
    def __getDescription(descriptionType, reservesModifier):
        if reservesModifier is None:
            return ''
        else:
            modifier = RESERVES_MODIFIER_NAMES[reservesModifier]
            descriptionRes = FLBattleTypeDescription.__getRS().dyn(descriptionType).dyn(modifier)
            return backport.text(descriptionRes()) if descriptionRes.exists() else ''

    @staticmethod
    def __getRS():
        return R.strings.fl_common.battleType

    @staticmethod
    def __getRI():
        return R.images.frontline.gui.maps.icons.battleTypes


class AbilitiesTemplates(object):

    def __init__(self, templateDir):
        self.__templateDir = templateDir

    @property
    def default(self):
        return self.__templateDir.default()

    @property
    def seconds(self):
        return self.__templateDir.seconds()

    @property
    def meters(self):
        return self.__templateDir.meters()

    @property
    def percents(self):
        return self.__templateDir.percents()

    @property
    def percentsBySecond(self):
        return self.__templateDir.percentsBySecond()

    @property
    def skillParams(self):
        templateDefault = self.default
        templateSeconds = self.seconds
        templateMeters = self.meters
        templatePercents = self.percents
        return {'FixedTextParam': templateDefault,
         'DirectNumericTextParam': templateDefault,
         'DirectSecondsTextParam': templateSeconds,
         'DirectMetersTextParam': templateMeters,
         'MulDirectPercentageTextParam': templatePercents,
         'AddDirectPercentageTextParam': self.percentsBySecond,
         'MulReciprocalPercentageTextParam': templatePercents,
         'AddReciprocalPercentageTextParam': templatePercents,
         'ShellStunSecondsTextParam': templateSeconds,
         'MultiMetersTextParam': templateMeters,
         'NestedMetersTextParam': templateMeters,
         'NestedSecondsTextParam': templateSeconds,
         'MulNestedPercentageTextParam': templatePercents,
         'AddNestedPercentageTextParam': templatePercents,
         'NestedShellStunSecondsTextParam': templateSeconds,
         'MulNestedPercentageTextTupleValueParam': templatePercents}


TEMPLATES = AbilitiesTemplates(R.strings.fl_battle_abilities_setup.infoPanel.param.valueTemplate)

def getSkillParams(skillLevelData):
    params = {}
    equipments = vehicles.g_cache.equipments()
    from frontline.constants.common import HIDDEN_PARAMS, SKILL_PARAM_SIGN
    from gui.shared.tooltips.battle_ability_tooltip_params import g_battleAbilityTooltipMgr
    for lvl, skillLevel in skillLevelData.levels.iteritems():
        curLvlEq = equipments[skillLevel.eqID]
        paramId = 0
        for tooltipIdentifier in curLvlEq.tooltipIdentifiers:
            if tooltipIdentifier in HIDDEN_PARAMS:
                continue
            param = createEpicParam(curLvlEq, tooltipIdentifier)
            if param:
                tooltipName, tooltipRenderer = g_battleAbilityTooltipMgr.getTooltipInfo(tooltipIdentifier)
                paramId += 1
                tooltipParams = params.setdefault(lvl, {}).setdefault(tooltipIdentifier, [])
                tooltipParams.append({'id': tooltipIdentifier,
                 'name': i18n.makeString(tooltipName) if i18n.isValidKey(tooltipName) else '',
                 'value': str(param),
                 'sign': SKILL_PARAM_SIGN.get(tooltipIdentifier, ''),
                 'isDynamic': False,
                 'valueTemplate': str(backport.text(TEMPLATES.default if isinstance(param, str) else TEMPLATES.skillParams.get(tooltipRenderer, TEMPLATES.default)))})

    paramsById = defaultdict(list)
    valuesById = defaultdict(set)
    for lvlDict in params.itervalues():
        for param in chain.from_iterable(lvlDict.itervalues()):
            pid = param['id']
            paramsById[pid].append(param)
            valuesById[pid].add(param['value'])

    for pid, values in valuesById.iteritems():
        if len(values) > 1:
            for param in paramsById[pid]:
                param['isDynamic'] = True

    return params


def becomeNonPlayerState():
    acount = BigWorld.player()
    result = acount.epicMetaGame.becomeNonPlayerState if acount else True
    return result


def isFinishedCycleState():
    frontlineState, _, _ = geFrontlineState()
    return frontlineState == FrontlineState.FINISHED
