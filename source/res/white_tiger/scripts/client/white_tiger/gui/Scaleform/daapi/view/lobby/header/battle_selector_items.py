# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from adisp import adisp_process
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.entities.base.ctx import PrbAction
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem, SpecialSquadItem
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from white_tiger_common import wt_constants
from white_tiger.gui import gui_constants
_R_BATTLE_TYPES = R.strings.menu.headerButtons.battle.types
_R_ICONS = R.images.gui.maps.icons

def addWhiteTigerBattlesType(items):
    items.append(_WhiteTigerBattlesItem(backport.text(_R_BATTLE_TYPES.whiteTiger()), gui_constants.PREBATTLE_ACTION_NAME.WHITE_TIGER, 2, gui_constants.SELECTOR_BATTLE_TYPES.WHITE_TIGER))


def addWhiteTigerBattleSquadsType(items):
    from gui.shared.formatters import text_styles
    items.append(_WhiteTigerBattleSquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.whiteTigerSquad())), gui_constants.PREBATTLE_ACTION_NAME.WHITE_TIGER_SQUAD, 2))


class _WhiteTigerBattlesItem(_SelectorItem):
    __wtController = dependency.descriptor(IWhiteTigerController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_WhiteTigerBattlesItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isVisible = self.__wtController.isAvailable()

    def getSmallIcon(self):
        return backport.image(R.images.white_tiger.gui.maps.icons.battleTypes.c_40x40.whiteTiger())

    def getLargerIcon(self):
        return backport.image(R.images.white_tiger.gui.maps.icons.battleTypes.c_64x64.whiteTiger())

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.buttons.selectorRendererBGEvent()) if self.__wtController.isAvailable() else ''

    @adisp_process
    def _doSelect(self, dispatcher):
        if self.__wtController.isModeActive():
            isSuccess = yield dispatcher.doSelectAction(PrbAction(self._data))
            if isSuccess:
                selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def _update(self, state):
        eventCtrl = self.__wtController
        self._isDisabled = state.hasLockedState or eventCtrl.isFrozen() or not eventCtrl.isModeActive()
        if self._isDisabled and self._isNew:
            self._isNew = False
        self._isSelected = state.isQueueSelected(wt_constants.QUEUE_TYPE.WHITE_TIGER)
        self._isVisible = eventCtrl.isEnabled()

    def isVisible(self):
        return self.__wtController.isAvailable() or self.__wtController.isFrozen()


class _WhiteTigerBattleSquadItem(SpecialSquadItem):
    __gameEventCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_WhiteTigerBattleSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = wt_constants.PREBATTLE_TYPE.WHITE_TIGER
        primeTimeStatus, _, _ = self.__gameEventCtrl.getPrimeTimeStatus()
        self._isVisible = self.__gameEventCtrl.isEnabled() and self.__gameEventCtrl.isInPrimeTime()
        self._isSpecialBgIcon = True
        self._isDescription = False
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE

    @property
    def squadIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.whiteTigerSquad())

    def _update(self, state):
        super(_WhiteTigerBattleSquadItem, self)._update(state)
        self._isSelected = state.isQueueSelected(wt_constants.QUEUE_TYPE.WHITE_TIGER)
        primeTimeStatus, _, _ = self.__gameEventCtrl.getPrimeTimeStatus()
        self._isVisible = self.__gameEventCtrl.isEnabled() and self.__gameEventCtrl.isInPrimeTime() and state.isInPreQueue(queueType=wt_constants.QUEUE_TYPE.WHITE_TIGER)
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE
