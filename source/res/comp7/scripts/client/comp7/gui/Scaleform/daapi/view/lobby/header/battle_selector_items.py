# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from comp7.gui.comp7_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from comp7.gui.prb_control.entities import comp7_prb_helpers
from comp7_common.comp7_constants import PREBATTLE_TYPE
from constants import QUEUE_TYPE
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import SelectorItem, SpecialSquadItem, _getSeasonInfoStr
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.formatters import text_styles
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

def addComp7BattleType(items):
    items.append(_Comp7Item(backport.text(R.strings.menu.headerButtons.battle.types.comp7()), PREBATTLE_ACTION_NAME.COMP7, 1, SELECTOR_BATTLE_TYPES.COMP7))


def addComp7SquadType(items):
    items.append(_Comp7SquadItem(backport.text(R.strings.menu.headerButtons.battle.types.comp7Squad()), PREBATTLE_ACTION_NAME.COMP7_SQUAD, 1))


class _Comp7Item(SelectorItem):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def isRandomBattle(self):
        return True

    def select(self):
        comp7_prb_helpers.selectComp7()
        selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def getFormattedLabel(self):
        battleTypeName = super(_Comp7Item, self).getFormattedLabel()
        scheduleStr = self.__getScheduleStr()
        label = '{}\n{}'.format(battleTypeName, scheduleStr) if scheduleStr else battleTypeName
        return label

    def getSmallIcon(self):
        return backport.image(R.images.comp7.gui.maps.icons.battleTypes.c_40x40.dyn(self._data)())

    def getLargerIcon(self):
        return backport.image(R.images.comp7.gui.maps.icons.battleTypes.c_64x64.dyn(self._data)())

    def getSpecialBGIcon(self):
        return backport.image(R.images.gui.maps.icons.buttons.selectorRendererBGEvent()) if self.__comp7Controller.isAvailable() else ''

    def _update(self, state):
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.COMP7)
        self._isVisible = self.__comp7Controller.isEnabled()
        self._isDisabled = state.hasLockedState or self.__comp7Controller.isFrozen()

    @classmethod
    def __getScheduleStr(cls):
        previousSeason = cls.__comp7Controller.getPreviousSeason()
        currentSeason = cls.__comp7Controller.getCurrentSeason()
        nextSeason = cls.__comp7Controller.getNextSeason()
        if previousSeason is None and currentSeason is None and nextSeason is None:
            return ''
        else:
            return text_styles.main(backport.text(R.strings.menu.headerButtons.battle.types.comp7.extra.frozen())) if cls.__comp7Controller.isFrozen() else _getSeasonInfoStr(cls.__comp7Controller, SELECTOR_BATTLE_TYPES.COMP7)


class _Comp7SquadItem(SpecialSquadItem):
    __controller = dependency.descriptor(IComp7Controller)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_Comp7SquadItem, self).__init__(label, data, order, selectorType, isVisible)
        primeTimeStatus, _, _ = self.__controller.getPrimeTimeStatus()
        self._prebattleType = PREBATTLE_TYPE.COMP7
        self._isVisible = self.__controller.isEnabled() and self.__controller.isInPrimeTime()
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE

    def getSmallIcon(self):
        return backport.image(R.images.comp7.gui.maps.icons.battleTypes.c_40x40.comp7Squad())

    def _update(self, state):
        super(_Comp7SquadItem, self)._update(state)
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.COMP7)
        primeTimeStatus, _, _ = self.__controller.getPrimeTimeStatus()
        self._isVisible = self.__controller.isEnabled() and self.__controller.isInPrimeTime() and state.isInPreQueue(queueType=QUEUE_TYPE.COMP7)
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE
