# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/bootcamp.py
from __future__ import absolute_import
from gui.battle_results.components import base
from gui.battle_results.components.common import makeRegularFinishResultLabel
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui import makeHtmlString
from helpers.i18n import makeString
from helpers import dependency
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.BootcampConstants import BATTLE_STATS_RESULT_FIELDS, BATTLE_STATS_ICONS
from skeletons.gui.game_control import IBootcampController
from shared_utils import first
import BigWorld
_BG_FOLDER_PATH = '../maps/icons/bootcamp/battle_result/background/'
_BG_IMAGE_FORMATS = {PLAYER_TEAM_RESULT.WIN: 'bcVictoryBg_{0}.png',
 PLAYER_TEAM_RESULT.DEFEAT: 'bcDefeat.png',
 PLAYER_TEAM_RESULT.DRAW: 'bcDraw.png'}
_STAT_ICON_PATH = '../maps/icons/bootcamp/battle_result/{0}.png'
_STAT_ICON_TOOLTIP_PATH = '../maps/icons/bootcamp/battle_result/tooltip/{0}.png'

class BackgroundItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        teamResult = reusable.getPersonalTeamResult()
        lessonNum = g_bootcamp.getLessonNum() - 1
        value = _BG_FOLDER_PATH + _BG_IMAGE_FORMATS[teamResult].format(lessonNum)
        return value


class UnlocksAndMedalsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        if teamResult != PLAYER_TEAM_RESULT.WIN:
            return
        lessonNum = g_bootcamp.getLessonNum()
        lessonSpecificExtras = g_bootcamp.getBattleResultsExtra(lessonNum - 1)
        for val in lessonSpecificExtras['unlocks']:
            self.addNextComponent(base.DirectStatsItem('', val))

        for val in lessonSpecificExtras['medals']:
            self.addNextComponent(base.DirectStatsItem('', val))

        bootcampController = dependency.instance(IBootcampController)
        lastLessonNum = g_bootcamp.getContextIntParameter('lastLessonNum')
        showPremium = lessonNum == lastLessonNum and bootcampController.needAwarding()
        if showPremium:
            self.addNextComponent(base.DirectStatsItem('', {'id': 'premium',
             'label': makeString(BOOTCAMP.RESULT_AWARD_PREMIUM_LABEL),
             'description': makeString(BOOTCAMP.RESULT_AWARD_PREMIUM_TEXT),
             'icon': RES_ICONS.MAPS_ICONS_BOOTCAMP_REWARDS_BCPREMIUM,
             'iconTooltip': RES_ICONS.MAPS_ICONS_BOOTCAMP_REWARDS_TOOLTIPS_BCPREMIUM}))


class HasUnlocksFlag(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        teamResult = reusable.getPersonalTeamResult()
        if teamResult != PLAYER_TEAM_RESULT.WIN:
            return False
        lessonNum = g_bootcamp.getLessonNum()
        lessonSpecificExtras = g_bootcamp.getBattleResultsExtra(lessonNum - 1)
        val = bool(lessonSpecificExtras['unlocks'])
        return val


class StatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result['personal'])
        battleStats = g_bootcamp.getBattleStatsLesson()
        for statType in battleStats:
            statFieldName = BATTLE_STATS_RESULT_FIELDS[statType]
            statVal = info.__getattribute__(statFieldName)
            statVal = BigWorld.wg_getIntegralFormat(statVal)
            self.addNextComponent(base.DirectStatsItem('', {'id': statType,
             'label': makeString(BOOTCAMP.battle_result(statType)),
             'description': makeString(BOOTCAMP.battle_result_description(statType)),
             'value': statVal,
             'icon': _STAT_ICON_PATH.format(BATTLE_STATS_ICONS[statType]),
             'iconTooltip': _STAT_ICON_TOOLTIP_PATH.format(BATTLE_STATS_ICONS[statType])}))


class ResultTypeStrItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        teamResult = reusable.getPersonalTeamResult()
        val = makeHtmlString('html_templates:bootcamp/battle_results', teamResult)
        return val


class FinishReasonItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        teamResult = reusable.getPersonalTeamResult()
        val = makeRegularFinishResultLabel(reusable.common.finishReason, teamResult)
        return val


class ShowRewardsFlag(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        credits = reusable.personal.getBaseCreditsRecords().getRecord('credits')
        xp = reusable.personal.getBaseXPRecords().getRecord('xp')
        return credits != 0 or xp != 0


class PlayerVehicleBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        _, item = first(reusable.personal.getVehicleItemsIterator())
        self.addNextComponent(base.DirectStatsItem('name', item.userName))
        self.addNextComponent(base.DirectStatsItem('typeIcon', getTypeBigIconPath(item.type, False)))


class CreditsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        intVal = reusable.personal.getBaseCreditsRecords().getRecord('credits')
        strVal = BigWorld.wg_getGoldFormat(intVal)
        self.addNextComponent(base.DirectStatsItem('value', intVal))
        self.addNextComponent(base.DirectStatsItem('str', strVal))


class XPBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        intVal = reusable.personal.getBaseXPRecords().getRecord('xp')
        strVal = BigWorld.wg_getIntegralFormat(intVal)
        self.addNextComponent(base.DirectStatsItem('value', intVal))
        self.addNextComponent(base.DirectStatsItem('str', strVal))
