# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/fight_start.py
from __future__ import absolute_import
import typing
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getEpicBattlesOnlyVehicleTooltipData, getPreviewTooltipData
from gui.impl.gen.view_models.views.lobby.page.header.fight_start_model import FightStartModel
from gui.impl.lobby.common.lobby_header_utils import findExtensionTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController, IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.lobby_state_machine.states import LobbyStateFlags

def isNotPBSPreview():
    lsm = getLobbyStateMachine()
    inPBS = any((s.getFlags() & LobbyStateFlags.POST_BATTLE_RESULTS for s in lsm.getNonEmptyEnteredStates(onlyLeaves=False)))
    return g_currentPreviewVehicle.isPresent() and not inPBS


class FightStartPresenter(ViewComponent[FightStartModel], IPrbListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)

    def __init__(self):
        super(FightStartPresenter, self).__init__(model=FightStartModel)

    @property
    def viewModel(self):
        return super(FightStartPresenter, self).getViewModel()

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self._onFightButtonUpdate), (g_currentPreviewVehicle.onChanged, self._onFightButtonUpdate))

    def _onLoading(self, *args, **kwargs):
        super(FightStartPresenter, self)._onLoading(*args, **kwargs)
        self._onFightButtonUpdate()

    def _getListeners(self):
        return ((events.LobbyHeaderMenuEvent.UPDATE_PREBATTLE_CONTROLS, self.__onUpdatePrbControls, EVENT_BUS_SCOPE.LOBBY), (events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__onUpdatePrbControls, EVENT_BUS_SCOPE.LOBBY))

    def __onUpdatePrbControls(self, _):
        self._onFightButtonUpdate()

    def __createTooltipText(self):
        prbEntity, prbDispatcher = self.prbEntity, self.prbDispatcher
        pFuncState = prbDispatcher.getFunctionalState()
        pValidation = prbEntity.canPlayerDoAction()
        isNavigationEnabled = not pFuncState.isNavigationDisabled()
        controlsHelper = self.__hangarGuiCtrl.currentGuiProvider.getLobbyHeaderHelper()
        isInSquad = any((pFuncState.isInUnit(prbType) for prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES))
        isButtonLocked = not pValidation.isValid
        if isNavigationEnabled:
            tooltip = None
            if g_currentVehicle.isOnlyForEpicBattles() and (g_currentVehicle.isUnsuitableToQueue() or g_currentVehicle.isDisabledInRent()):
                tooltip = getEpicBattlesOnlyVehicleTooltipData(pValidation)
            else:
                tooltip = findExtensionTooltip(pValidation)
            if tooltip is None and not g_currentVehicle.isPresent() and isNotPBSPreview():
                return getPreviewTooltipData()
        if controlsHelper is not None:
            tooltip, _ = controlsHelper.getFightControlTooltipData(pValidation, isInSquad, isButtonLocked, isNavigationEnabled)
            return tooltip
        else:
            return

    def _onFightButtonUpdate(self):
        self.viewModel.setTooltip(self.__createTooltipText())
