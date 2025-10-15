# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.lobby.header.fight_btn_tooltips import getSquadFightBtnTooltipData
from portal_common.portal_constants import QUEUE_TYPE, PREBATTLE_TYPE
from portal.gui.portal_gui_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from portal.skeletons.portal_event_controller import IPortalEventController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages
from gui.shared.utils.functions import makeTooltip
_R_BATTLE_TYPES = R.strings.mode_selector.portal

def addPortalBattlesType(items):
    items.append(_PortalBattlesItem(backport.text(_R_BATTLE_TYPES.title()), PREBATTLE_ACTION_NAME.PORTAL_BATTLE, 2, SELECTOR_BATTLE_TYPES.PORTAL))


def addPortalSquadType(items):
    items.append(PortalSquadItem(backport.text(_R_BATTLE_TYPES.squadName()), PREBATTLE_ACTION_NAME.PORTAL_BATTLE_SQUAD, 2))


class _PortalBattlesItem(battle_selector_items._SelectorItem):
    _PORTAL_MODE_SELECTOR_ICON = 'portal_battle'
    __portalBattlesCtrl = dependency.descriptor(IPortalEventController)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def getSmallIcon(self):
        return backport.image(R.images.portal.gui.maps.icons.battleTypes.c_40x40.dyn(self._PORTAL_MODE_SELECTOR_ICON)())

    def getLargerIcon(self):
        return backport.image(R.images.portal.gui.maps.icons.battleTypes.c_64x64.dyn(self._PORTAL_MODE_SELECTOR_ICON)())

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return state.isInUnit(PREBATTLE_TYPE.PORTAL)

    def getFightButtonLabel(self, state, playerInfo):
        if self.__portalBattlesCtrl.isPortalMode():
            label = R.strings.portal_event.headerButtons.battle
            if not playerInfo.isCreator and state.isReadyActionSupported():
                label = R.strings.portal_event.headerButtons.notReady if playerInfo.isReady else R.strings.portal_event.headerButtons.ready
            return backport.text(label())
        return super(_PortalBattlesItem, self).getFightButtonLabel(state, playerInfo)

    def getDisabledFightButtonLabel(self, result):
        return backport.text(R.strings.portal_event.headerButtons.battle()) if self.__portalBattlesCtrl.isPortalMode() else super(_PortalBattlesItem, self).getDisabledFightButtonLabel(result)

    def getDisabledFightButtonTooltip(self, result):
        if self.__portalBattlesCtrl.isPortalMode():
            if self.__portalBattlesCtrl.prbEntity.isInQueue():
                return makeTooltip(body=backport.text(R.strings.portal_lobby.startButton.tooltip.queueNotReady()))
            items = battle_selector_items.getItems()
            state = self.__portalBattlesCtrl.prbDispatcher.getFunctionalState()
            selected = items.update(state)
            isInSquad = selected.isInSquad(state)
            if isInSquad:
                canPlayerDoActionResult = self.__portalBattlesCtrl.prbEntity.canPlayerDoAction()
                canDoMsg = canPlayerDoActionResult.restriction
                return getSquadFightBtnTooltipData(canDoMsg)
        return super(_PortalBattlesItem, self).getDisabledFightButtonTooltip(result)

    def hasDisabledFightButtonData(self, result):
        return True if self.__portalBattlesCtrl.isPortalMode() else super(_PortalBattlesItem, self).hasDisabledFightButtonData(result)

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.PORTAL)
        self._isVisible = self.__portalBattlesCtrl.isEnabled()


class PortalSquadItem(battle_selector_items.SpecialSquadItem):
    __portalBattlesCtrl = dependency.descriptor(IPortalEventController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(PortalSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.PORTAL
        self._isVisible = self.__portalBattlesCtrl.isEnabled()
        self._isSpecialBgIcon = True
        self._isDescription = False

    @property
    def squadIcon(self):
        return backport.image(R.images.portal.gui.maps.icons.battleTypes.c_40x40.dyn('portal_squad')())

    def _update(self, state):
        super(PortalSquadItem, self)._update(state)
        self._isVisible = self.__portalBattlesCtrl.isEnabled()
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.PORTAL)
