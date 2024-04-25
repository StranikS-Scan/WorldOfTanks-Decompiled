# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem, SpecialSquadItem
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.performance_analyzer import PerformanceGroup
from historical_battles_common.hb_constants_extension import PREBATTLE_TYPE
from helpers import dependency
from helpers import time_utils
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
_R_LIBRARY = R.images.gui.maps.icons.library
_R_PERFORMANCE = R.strings.hb_mode_selector.mode.historicalBattles.performance

def addHistoricalBattlesType(items):
    items.append(HistoricalBattlesItem(backport.text(R.strings.hb_mode_selector.mode.historicalBattles.name()), PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES, 2, SELECTOR_BATTLE_TYPES.HISTORICAL_BATTLES))


def addHistoricalBattlesSquadType(items):
    items.append(HistoricalBattlesSquadItem(text_styles.middleTitle(backport.text(R.strings.hb_mode_selector.mode.historicalBattles.squadName())), PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES_SQUAD, 2))


class HistoricalBattlesItem(_SelectorItem):
    __gameEventController = dependency.descriptor(IGameEventController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def getSpecialBGIcon(self):
        return backport.image(R.images.gui.maps.icons.buttons.selectorRendererBGEvent()) if self.__gameEventController.isEnabled() else ''

    def getSmallIcon(self):
        return backport.image(R.images.historical_battles.gui.maps.icons.battleTypes.c_40x40.historicalBattles())

    def getLargerIcon(self):
        return backport.image(R.images.historical_battles.gui.maps.icons.battleTypes.c_64x64.historicalBattles())

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return state.isInUnit(PREBATTLE_TYPE.HISTORICAL_BATTLES)

    def getFormattedLabel(self):
        battleTypeName = super(HistoricalBattlesItem, self).getFormattedLabel()
        availabilityStr = self._getPerformanceAlarmStr() or self._getScheduleStr()
        return battleTypeName if availabilityStr is None else '%s\n%s' % (battleTypeName, availabilityStr)

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        front = self.__gameEventController.frontController.getSelectedFront()
        self._isSelected = state.isQueueSelected(front.getFrontQueueType()) if front else False
        self._isVisible = self.__gameEventController.isEnabled()

    def _getPerformanceAlarmStr(self):
        currPerformanceGroup = self.__gameEventController.getPerformanceGroup()
        attentionText, iconPath = (None, None)
        if currPerformanceGroup == PerformanceGroup.HIGH_RISK:
            attentionText = text_styles.error(backport.text(_R_PERFORMANCE.highRisk()))
            iconPath = backport.image(_R_LIBRARY.CancelIcon_1())
        elif currPerformanceGroup == PerformanceGroup.MEDIUM_RISK:
            attentionText = text_styles.alert(backport.text(_R_PERFORMANCE.mediumRisk()))
            iconPath = backport.image(_R_LIBRARY.alertIcon())
        return icons.makeImageTag(iconPath, vSpace=-3) + ' ' + attentionText if attentionText and iconPath else None

    def _getScheduleStr(self):
        timeLeft = self.__gameEventController.getEventFinishTime()
        rAvailability = R.strings.menu.headerButtons.battle.types.mapbox.availability
        if timeLeft < time_utils.ONE_HOUR:
            timeLeftStr = backport.text(rAvailability.lessThanHour())
        else:
            timeLeftStr = backport.backport_time_utils.getTillTimeStringByRClass(timeLeft, rAvailability)
        return text_styles.main(backport.text(R.strings.hb_mode_selector.headerButtons.historicalBattles.endsIn(), timeLeft=timeLeftStr))


class HistoricalBattlesSquadItem(SpecialSquadItem):
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(HistoricalBattlesSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.HISTORICAL_BATTLES
        self._isVisible = self.__gameEventController.isEnabled()
        self._isSpecialBgIcon = True
        self._isDescription = False

    @property
    def squadIcon(self):
        return backport.image(R.images.historical_battles.gui.maps.icons.battleTypes.c_40x40.squadHistoricalBattles())

    def _update(self, state):
        super(HistoricalBattlesSquadItem, self)._update(state)
        self._isVisible = self.__gameEventController.isEnabled()
        front = self.__gameEventController.frontController.getSelectedFront()
        self._isSelected = state.isQueueSelected(front.getFrontQueueType()) if front else False
