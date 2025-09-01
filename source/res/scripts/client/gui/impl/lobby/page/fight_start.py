# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/fight_start.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import _EXT_FIGHT_BUTTON_TOOLTIP_GETTERS
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getEpicBattlesOnlyVehicleTooltipData, getPreviewTooltipData
from gui.impl.gen.view_models.views.lobby.page.header.fight_start_model import FightStartModel
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController, IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext

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
        return ((events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__onFightButtonUpdateEventHandler, EVENT_BUS_SCOPE.LOBBY),)

    def __onFightButtonUpdateEventHandler(self, _):
        self._onFightButtonUpdate()

    def _onFightButtonUpdate(self):
        prbEntity, prbDispatcher = self.prbEntity, self.prbDispatcher
        pFuncState = prbDispatcher.getFunctionalState()
        pValidation = prbEntity.canPlayerDoAction()
        isNavigationEnabled = not pFuncState.isNavigationDisabled()
        controlsHelper = self.__hangarGuiCtrl.getLobbyHeaderHelper()
        isInSquad = any((pFuncState.isInUnit(prbType) for prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES))
        isButtonLocked = not pValidation.isValid
        tooltip, _ = '', False
        if isNavigationEnabled:
            if g_currentVehicle.isOnlyForEpicBattles() and (g_currentVehicle.isUnsuitableToQueue() or g_currentVehicle.isDisabledInRent()):
                tooltip = getEpicBattlesOnlyVehicleTooltipData(pValidation)
            else:
                tooltip = self.__findExtensionTooltip(pValidation)
            if tooltip is None and g_currentPreviewVehicle.isPresent():
                tooltip = getPreviewTooltipData()
        if not tooltip and controlsHelper is not None:
            tooltip, _ = controlsHelper.getFightControlTooltipData(pValidation, isInSquad, isButtonLocked, isNavigationEnabled)
        self.viewModel.setTooltip(tooltip)
        return

    def __findExtensionTooltip(self, pValidation):
        for getter in _EXT_FIGHT_BUTTON_TOOLTIP_GETTERS:
            tooltip = getter(pValidation)
            if tooltip is not None:
                return tooltip

        return
