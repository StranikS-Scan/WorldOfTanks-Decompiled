# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from last_stand_common.last_stand_constants import QUEUE_TYPE, PREBATTLE_TYPE
from last_stand.gui.ls_gui_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from last_stand.gui.ls_account_settings import AccountSettingsKeys, getSettings
from last_stand.skeletons.ls_controller import ILSController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency

def addLastStandType(items):
    items.append(_LSItem(backport.text(R.strings.last_stand_lobby.headerButtons.battle.types.last_stand()), PREBATTLE_ACTION_NAME.LAST_STAND, 2, SELECTOR_BATTLE_TYPES.LAST_STAND))


def addLastStandSquadType(items):
    items.append(LSSquadItem('Last Stand Squad Battle', PREBATTLE_ACTION_NAME.LAST_STAND_SQUAD, 2))


class _LSItem(battle_selector_items.SelectorItem):
    lsCtrl = dependency.descriptor(ILSController)

    def isShowEventIndication(self):
        return self.lsCtrl.isAvailable()

    def hasSparksAnimation(self, isNewbie, hasEventIndication):
        return hasEventIndication

    def getSmallIcon(self):
        return backport.image(R.images.last_stand.gui.maps.icons.battleTypes.c_40x40.last_stand())

    def getLargerIcon(self):
        return backport.image(R.images.last_stand.gui.maps.icons.battleTypes.c_64x64.last_stand())

    def isRandomBattle(self):
        return True

    @property
    def squadIcon(self):
        return backport.image(R.images.last_stand.gui.maps.icons.battleTypes.c_40x40.last_stand_squad())

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.LAST_STAND) or state.isQueueSelected(QUEUE_TYPE.LAST_STAND_MEDIUM) or state.isQueueSelected(QUEUE_TYPE.LAST_STAND_HARD)
        self._isVisible = self.lsCtrl.isAvailable()

    def _isKnownBattleType(self):
        return not getSettings(AccountSettingsKeys.IS_EVENT_NEW)


class LSSquadItem(battle_selector_items.SpecialSquadItem):
    lsCtrl = dependency.descriptor(ILSController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(LSSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.LAST_STAND
        self._isVisible = self.lsCtrl.isAvailable()
        self._isSpecialBgIcon = True
        self._isDescription = False

    def getSmallIcon(self):
        return backport.image(R.images.last_stand.gui.maps.icons.battleTypes.c_40x40.last_stand_squad())

    def isShowEventIndication(self):
        return self.lsCtrl.isAvailable()

    def hasSparksAnimation(self, isNewbie, hasEventIndication):
        return hasEventIndication

    def _update(self, state):
        super(LSSquadItem, self)._update(state)
        self._isVisible = self.lsCtrl.isAvailable()
        self._isSelected = state.isInUnit(self._prebattleType) or state.isQueueSelected(QUEUE_TYPE.LAST_STAND) or state.isQueueSelected(QUEUE_TYPE.LAST_STAND_MEDIUM) or state.isQueueSelected(QUEUE_TYPE.LAST_STAND_HARD)

    def _isKnownBattleType(self):
        return not getSettings(AccountSettingsKeys.IS_EVENT_NEW)
