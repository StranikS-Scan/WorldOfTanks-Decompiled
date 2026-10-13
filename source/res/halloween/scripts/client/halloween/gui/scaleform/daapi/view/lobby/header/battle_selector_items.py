# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from halloween_common.halloween_constants import QUEUE_TYPE, PREBATTLE_TYPE
from halloween.gui.halloween_gui_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from halloween.gui.halloween_account_settings import AccountSettingsKeys, getSettings
from halloween.skeletons.halloween_controller import IHalloweenController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency

def addHalloweenType(items):
    items.append(_HalloweenItem(backport.text(R.strings.halloween_lobby.headerButtons.battle.types.halloween()), PREBATTLE_ACTION_NAME.HALLOWEEN, 2, SELECTOR_BATTLE_TYPES.HALLOWEEN))


def addHalloweenSquadType(items):
    items.append(HalloweenSquadItem('Halloween Squad Battle', PREBATTLE_ACTION_NAME.HALLOWEEN_SQUAD, 2))


class _HalloweenItem(battle_selector_items.SelectorItem):
    __halloweenCtrl = dependency.descriptor(IHalloweenController)

    def isShowEventIndication(self):
        return self.__halloweenCtrl.isAvailable()

    def hasSparksAnimation(self, isNewbie, hasEventIndication):
        return hasEventIndication

    def getSmallIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.halloween())

    def getLargerIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_64x64.halloween())

    def isRandomBattle(self):
        return True

    @property
    def squadIcon(self):
        return backport.image(R.images.halloween.gui.maps.icons.battleTypes.c_40x40.halloween_squad())

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.HALLOWEEN) or state.isQueueSelected(QUEUE_TYPE.HALLOWEEN_MEDIUM) or state.isQueueSelected(QUEUE_TYPE.HALLOWEEN_HARD)
        self._isVisible = self.__halloweenCtrl.isAvailable()

    def _isKnownBattleType(self):
        return not getSettings(AccountSettingsKeys.IS_EVENT_NEW)


class HalloweenSquadItem(battle_selector_items.SpecialSquadItem):
    __halloweenCtrl = dependency.descriptor(IHalloweenController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(HalloweenSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.HALLOWEEN
        self._isVisible = self.__halloweenCtrl.isAvailable()
        self._isSpecialBgIcon = True
        self._isDescription = False

    def getSmallIcon(self):
        return backport.image(R.images.halloween.gui.maps.icons.battleTypes.c_40x40.halloween_squad())

    def isShowEventIndication(self):
        return self.__halloweenCtrl.isAvailable()

    def hasSparksAnimation(self, isNewbie, hasEventIndication):
        return hasEventIndication

    def _update(self, state):
        super(HalloweenSquadItem, self)._update(state)
        self._isVisible = self.__halloweenCtrl.isAvailable()
        self._isSelected = state.isInUnit(self._prebattleType) or state.isQueueSelected(QUEUE_TYPE.HALLOWEEN) or state.isQueueSelected(QUEUE_TYPE.HALLOWEEN_MEDIUM) or state.isQueueSelected(QUEUE_TYPE.HALLOWEEN_HARD)

    def _isKnownBattleType(self):
        return not getSettings(AccountSettingsKeys.IS_EVENT_NEW)
