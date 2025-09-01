# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/optional_devices_assistant_presenter.py
from __future__ import absolute_import
import logging
import typing
import Event
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from frameworks.state_machine import BaseStateObserver, visitor
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_model import OptionalDevicesAssistantModel
from gui.impl.lobby.tank_setup.optional_devices_assistant.hangar import OptionalDevicesAssistantView
from gui.impl.lobby.tanksetup.tooltips.popular_loadouts_tooltip import PopularLoadoutsTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from frameworks.state_machine import State
    from typing import Optional
_logger = logging.getLogger(__name__)

class _OptionalDevicesObserver(BaseStateObserver):

    def __init__(self):
        super(_OptionalDevicesObserver, self).__init__()
        self.__manager = Event.EventManager()
        self.onEquipEntered = Event.Event(self.__manager)
        self.onEquipExited = Event.Event(self.__manager)

    def clear(self):
        super(_OptionalDevicesObserver, self).clear()
        self.__manager.clear()

    def isObservingState(self, state):
        from gui.impl.lobby.hangar.states import EquipmentLoadoutState
        lsm = state.getMachine()
        return visitor.isDescendantOf(state, lsm.getStateByCls(EquipmentLoadoutState)) or state.getStateID() == EquipmentLoadoutState.STATE_ID


class OptionalDevicesAssistantPresenter(ViewComponent[OptionalDevicesAssistantModel], IGlobalListener):
    _STATES_OBSERVER = _OptionalDevicesObserver
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _wotPlusController = dependency.descriptor(IWotPlusController)

    def __init__(self):
        self._optionalDevicesAssistant = None
        self.optionalDevicesAssistantObserver = self._STATES_OBSERVER()
        super(OptionalDevicesAssistantPresenter, self).__init__(model=OptionalDevicesAssistantModel, enabled=True)
        return

    def prepare(self):
        lsm = getLobbyStateMachine()
        lsm.connect(self.optionalDevicesAssistantObserver)

    @property
    def viewModel(self):
        return super(OptionalDevicesAssistantPresenter, self).getViewModel()

    def _getEvents(self):
        return ((self._wotPlusController.onEnabledStatusChanged, self.__onWotPlusDataChanged), (g_currentVehicle.onChanged, self.__onVehicleChanged))

    def _initialize(self, *args, **kwargs):
        super(OptionalDevicesAssistantPresenter, self)._initialize(*args, **kwargs)
        self._createOptionalDevicesAssistantPanel()

    def _finalize(self):
        super(OptionalDevicesAssistantPresenter, self)._finalize()
        self._optionalDevicesAssistant = None
        lsm = getLobbyStateMachine()
        lsm.disconnect(self.optionalDevicesAssistantObserver)
        self.__slotSelectionObserver = None
        return

    def _createOptionalDevicesAssistantPanel(self):
        if not g_currentVehicle.isPresent():
            return
        if not self.prbEntity:
            return
        queueType = self.prbEntity.getQueueType()
        if self._lobbyContext.getServerSettings().isOptionalDevicesAssistantEnabled() and self._wotPlusController.isEnabled() and queueType in (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.COMP7):
            self._optionalDevicesAssistant = OptionalDevicesAssistantView(self.viewModel, queueType)
            self._optionalDevicesAssistant.onLoading()

    def _removeOptionalDevicesAssistantPanel(self):
        if self._optionalDevicesAssistant is not None:
            self._optionalDevicesAssistant.finalize()
            self._optionalDevicesAssistant = None
        return

    def __onVehicleChanged(self):
        if self._optionalDevicesAssistant is not None:
            self._optionalDevicesAssistant.updateVehicle()
        return

    def createToolTipContent(self, event, contentID):
        return PopularLoadoutsTooltip(vehCompDescr=int(event.getArgument('sourceVehicleCompDescr', 0)), optionalDevicesResultType=int(event.getArgument('optionalDevicesResultType', 0))) if contentID == R.views.lobby.tanksetup.tooltips.PopularLoadoutsTooltip() else None

    def __onWotPlusDataChanged(self, isEnabledVal):
        if isEnabledVal is None:
            return
        else:
            if isEnabledVal:
                if not self._optionalDevicesAssistant:
                    self._createOptionalDevicesAssistantPanel()
                    if self._optionalDevicesAssistant:
                        self._optionalDevicesAssistant.initialize()
                else:
                    _logger.warning('Optional device assistant widget has already been created!')
            elif self._optionalDevicesAssistant is not None:
                self._optionalDevicesAssistant.showHiddenState()
                self._removeOptionalDevicesAssistantPanel()
            return
