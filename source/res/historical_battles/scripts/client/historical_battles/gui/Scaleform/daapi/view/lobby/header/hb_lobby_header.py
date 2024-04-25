# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/header/hb_lobby_header.py
from __future__ import absolute_import
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.platoon_config import SquadInfo
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.locale.PLATOON import PLATOON
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader, TOOLTIP_TYPES, HeaderMenuVisibilityState
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from historical_battles.gui.impl.lobby.platoon.platoon_helpers import getPlatoonSlotsData
from historical_battles_common.hb_constants import HB_GAME_PARAMS_KEY
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.lobby_context import ILobbyContext
from messenger.formatters import TimeFormatter
from gui.shared.formatters import text_styles
from gui.prb_control.settings import UNIT_RESTRICTION
HEADER_BUTTON_TOOLTIPS_SQUAD = '#historical_battles.hb_lobby:platoon/headerButton/tooltips/squad'
HEADER_BUTTON_TOOLTIPS_SQUAD_DISABLED = '#historical_battles.hb_lobby:platoon/headerButton/tooltips/disabled'
HB_SQUAD_BUTTON = 'hbSquad'

class HBLobbyHeader(LobbyHeader):
    _gameEventController = dependency.descriptor(IGameEventController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(HBLobbyHeader, self).__init__()
        self.__inEvent = False

    def onPrbEntitySwitched(self):
        self._populateButtons()
        super(HBLobbyHeader, self).onPrbEntitySwitched()
        self.__updateVisibilityOnEntitySwitched()

    def _addListeners(self):
        super(HBLobbyHeader, self)._addListeners()
        self._gameEventController.onSelectedFrontmanChanged += self.__onSelectedFrontmanChanged
        self._gameEventController.onFrontmanLockChanged += self.__onSelectedFrontmanChanged
        self._gameEventController.onSelectedFrontChanged += self.__onSelectedFrontmanChanged
        self._gameEventController.onFrontTimeStatusUpdated += self.__onSelectedFrontmanChanged
        self._gameEventController.onLobbyHeaderUpdate += self.__onLobbyHeaderUpdate
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged

    def _removeListeners(self):
        super(HBLobbyHeader, self)._removeListeners()
        self._gameEventController.onSelectedFrontmanChanged -= self.__onSelectedFrontmanChanged
        self._gameEventController.onFrontmanLockChanged -= self.__onSelectedFrontmanChanged
        self._gameEventController.onSelectedFrontChanged -= self.__onSelectedFrontmanChanged
        self._gameEventController.onFrontTimeStatusUpdated -= self.__onSelectedFrontmanChanged
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self._gameEventController.onLobbyHeaderUpdate -= self.__onLobbyHeaderUpdate

    def _getAvailableButtons(self, buttonsToExclude):
        if self._gameEventController.isHistoricalBattlesMode():
            return [ (button if button != self.BUTTONS.SQUAD else HB_SQUAD_BUTTON) for button in self.BUTTONS.ALL() if button not in buttonsToExclude ]
        return [ button for button in self.BUTTONS.ALL() if button not in buttonsToExclude ]

    def _disableFightBtn(self, header, body):
        self.as_disableFightButtonS(True)
        self.as_setFightBtnTooltipS(makeTooltip(backport.text(header) if header else None, backport.text(body)), False)
        return

    def __onLobbyHeaderUpdate(self):
        self._updatePrebattleControls()

    def _updatePrebattleControls(self, *_):
        super(HBLobbyHeader, self)._updatePrebattleControls(*_)
        if self._gameEventController.isHistoricalBattlesMode():
            self.as_doDisableNavigationS()
            frontman = self._gameEventController.frontController.getSelectedFrontman()
            front = self._gameEventController.frontController.getSelectedFront()
            r = R.strings.hb_lobby.hangar.startBtn
            if not self._gameEventController.isBattlesEnabled():
                self._disableFightBtn(r.notReady.header(), r.disabled.body())
                if self._isHeaderButtonPresent(HB_SQUAD_BUTTON):
                    state = self.prbDispatcher.getFunctionalState()
                    squadItems = battle_selector_items.getSquadItems()
                    squadSelected = squadItems.update(state)
                    self.as_doDisableHeaderButtonS(HB_SQUAD_BUTTON, False)
                    self.as_updateSquadS(False, HEADER_BUTTON_TOOLTIPS_SQUAD_DISABLED, TOOLTIP_TYPES.COMPLEX, False, squadSelected.squadIcon, False, self._buildExtendedSquadInfoVo()._asdict())
                return
            if frontman.isInBattle():
                self._disableFightBtn(r.notReady.header(), r.frontmanNotReady.body())
            elif not front.isEnabled() or not front.isAvailable() or not self._gameEventController.isEnabled():
                self._disableFightBtn(r.notReady.header(), r.notReady.body())
            elif self.prbEntity.isInQueue():
                self._disableFightBtn('', r.queueNotReady.body())
            elif self._gameEventController.isBanned:
                timeStr = text_styles.yellowText(TimeFormatter.getLongDatetimeFormat(self._gameEventController.banExpiryTime))
                body = backport.text(r.banned.body(), time=timeStr)
                self.as_disableFightButtonS(True)
                self.as_setFightBtnTooltipS(makeTooltip(backport.text(r.banned.header()), body), False)
            elif not self._gameEventController.canSelectedVehicleStartToBattle():
                self._disableFightBtn(r.vehicleNotInInventory.header(), r.vehicleNotInInventory.body())
            if self._isHeaderButtonPresent(HB_SQUAD_BUTTON):
                state = self.prbDispatcher.getFunctionalState()
                items = battle_selector_items.getItems()
                selected = items.update(state)
                if selected.isInSquad(state):
                    isInSquad = True
                    tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_INSQUAD
                    self.as_doDisableHeaderButtonS(HB_SQUAD_BUTTON, True)
                    result = self.prbEntity.canPlayerDoAction()
                    restrict = result.restriction
                    if restrict == UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED:
                        self._disableFightBtn(r.notReady.header(), r.squadNotReady.tooltipBody())
                else:
                    isInSquad = False
                    self.as_doDisableHeaderButtonS(HB_SQUAD_BUTTON, self.prbDispatcher.getEntity().getPermissions().canCreateSquad())
                    tooltip = HEADER_BUTTON_TOOLTIPS_SQUAD
                squadItems = battle_selector_items.getSquadItems()
                squadSelected = squadItems.update(state)
                self.as_updateSquadS(isInSquad, tooltip, TOOLTIP_TYPES.COMPLEX, False, squadSelected.squadIcon, False, self._buildExtendedSquadInfoVo()._asdict())

    def _buildExtendedSquadInfoVo(self):
        commanderIndex = 0
        squadManStates = []
        if not (self.prbDispatcher and self.prbEntity):
            return SquadInfo(self.platoonCtrl.getPlatoonStateForSquadVO().value, squadManStates, commanderIndex)
        else:
            if self.prbDispatcher.getFunctionalState().isInUnit():
                count = 0
                slots = getPlatoonSlotsData(self.prbEntity)
                for it in slots:
                    player = it['player']
                    role = it['role']
                    squadManStates.append(self.platoonCtrl.getSquadManStates(player, role))
                    if player is not None:
                        if player['isCommander']:
                            commanderIndex = count
                    count += 1

            return SquadInfo(self.platoonCtrl.getPlatoonStateForSquadVO().value, squadManStates, commanderIndex)

    def _isHeaderButtonPresent(self, buttonID):
        override = self._tutorialLoader.gui.lastHeaderMenuButtonsOverride
        return buttonID in override if override is not None else True

    def __onSelectedFrontmanChanged(self, *_):
        self._updatePrebattleControls()

    def __onSettingsChanged(self, diff):
        if HB_GAME_PARAMS_KEY not in diff:
            return
        self._updatePrebattleControls()

    def __updateVisibilityOnEntitySwitched(self):
        isEvent = self._gameEventController.isHistoricalBattlesMode()
        if isEvent != self.__inEvent:
            stateNothing = HeaderMenuVisibilityState.NOTHING
            stateAll = HeaderMenuVisibilityState.ALL
            state = stateNothing if isEvent else stateAll
            self.__toggleVisibilityMenu(state)
        self.__inEvent = isEvent

    def __toggleVisibilityMenu(self, state):
        self.menuVisibilityHelper.updateStates(state)
        activeState = self.menuVisibilityHelper.getActiveState()
        self.as_toggleVisibilityMenuS(activeState)
