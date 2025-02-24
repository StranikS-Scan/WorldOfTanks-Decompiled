# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/queue_view/queue_view.py
import typing
from PlayerEvents import g_playerEvents
from cosmic_event.gui.Scaleform.daapi.view.lobby.cosmic_battle_queue import CosmicEventQueueProvider
from cosmic_event.gui.impl.gen.view_models.views.lobby.queue_view.queue_view_model import QueueViewModel
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl.pub import ViewImpl
from gui.prb_control import prbEntityProperty
from gui.prb_control.dispatcher import _PreBattleDispatcher
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events, g_eventBus
from gui.shared.system_factory import collectBattleQueueProvider
from cosmic_event.cosmic_constants import OLD_VEHICLE_NAME, NEW_VEHICLE_NAME
from helpers import dependency
from cosmic_account_settings import getLastSelectedVehicleID
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.cosmic_lobby_view_model import RoverEnum

class QueueView(ViewImpl):
    __cosmicEventController = dependency.descriptor(ICosmicEventBattleController)

    def __init__(self, layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW):
        settings = ViewSettings(layoutID, flags, QueueViewModel())
        qType = self.prbEntity.getQueueType()
        providerClass = collectBattleQueueProvider(qType)
        self._queueProvider = providerClass(self, qType)
        vehicles = self.__cosmicEventController.getEventVehicles()
        data = {vehData['name']:vehData['vehCD'] for _, vehData in vehicles}
        self.__oldVehicleTypeCD = data[OLD_VEHICLE_NAME]
        self.__newVehicleTypeCD = data[NEW_VEHICLE_NAME]
        self.__selectedVehicleID = RoverEnum(getLastSelectedVehicleID())
        super(QueueView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(QueueView, self).getViewModel()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def setPlayersTypeCDs(self, vehTypeCompDescrs):
        oldVehiclesCount = vehTypeCompDescrs.get(self.__oldVehicleTypeCD, 0)
        newVehiclesCount = vehTypeCompDescrs.get(self.__newVehicleTypeCD, 0)
        with self.viewModel.transaction() as tx:
            tx.setNewRoverQueue(newVehiclesCount)
            tx.setOldRoverQueue(oldVehiclesCount)
            tx.setPlayersInQueue(oldVehiclesCount + newVehiclesCount)
            tx.setVehicle(self.__selectedVehicleID)

    def setSelectedVehicle(self):
        with self.viewModel.transaction() as tx:
            resource = self.__cosmicEventController.getResourceIconForSelectedVehicle()
            tx.setSelectedVehicleResource(resource)

    def _initialize(self, *args, **kwargs):
        super(QueueView, self)._initialize(*args, **kwargs)
        self.viewModel.onLeave += self._onLeave
        g_playerEvents.onArenaCreated += self._onArenaCreated
        self._setHangarVisibility(HeaderMenuVisibilityState.NOTHING)
        self._queueProvider.start()

    def _finalize(self):
        self.viewModel.onLeave -= self._onLeave
        g_playerEvents.onArenaCreated -= self._onArenaCreated
        self._setHangarVisibility(HeaderMenuVisibilityState.ALL)
        if self._queueProvider:
            self._queueProvider.stop()
            self._queueProvider = None
        super(QueueView, self)._finalize()
        return

    def _setHangarVisibility(self, state):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), EVENT_BUS_SCOPE.LOBBY)

    def _onLeave(self):
        self.prbEntity.exitFromQueue()
        self.destroy()

    def _onArenaCreated(self, *args, **kwargs):
        pass
