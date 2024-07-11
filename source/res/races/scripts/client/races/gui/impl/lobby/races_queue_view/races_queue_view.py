# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/races_queue_view/races_queue_view.py
import typing
from races.gui.impl.gen.view_models.views.lobby.races_queue_view.races_queue_view_model import RacesQueueViewModel
from races.gui.prb_control.races_queue import RacesQueueProvider
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl.pub import ViewImpl
from gui.prb_control import prbEntityProperty
from gui.prb_control.dispatcher import _PreBattleDispatcher
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.system_factory import collectBattleQueueProvider

class RacesQueueView(ViewImpl):

    def __init__(self, layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW):
        settings = ViewSettings(layoutID, flags, RacesQueueViewModel())
        qType = self.prbEntity.getQueueType()
        providerClass = collectBattleQueueProvider(qType)
        self._queueProvider = providerClass(self, qType)
        super(RacesQueueView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RacesQueueView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onLeave, self._onLeave),)

    def _initialize(self, *args, **kwargs):
        super(RacesQueueView, self)._initialize(*args, **kwargs)
        self._setHangarVisibility(HeaderMenuVisibilityState.NOTHING)
        self._queueProvider.start()

    def _finalize(self):
        self._setHangarVisibility(HeaderMenuVisibilityState.ALL)
        if self._queueProvider:
            self._queueProvider.stop()
            self._queueProvider = None
        super(RacesQueueView, self)._finalize()
        return

    def _onLoading(self):
        super(RacesQueueView, self)._onLoading()
        self.setVehicle()

    def _setHangarVisibility(self, state):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), EVENT_BUS_SCOPE.LOBBY)

    @prbEntityProperty
    def prbEntity(self):
        return None

    def setPlayersCount(self, count):
        with self.viewModel.transaction() as tx:
            tx.setPlayersInQueue(count)

    def setVehicle(self):
        vehicle = g_currentVehicle.item.shortUserName
        with self.viewModel.transaction() as tx:
            tx.setVehicleName(vehicle)

    def _onLeave(self):
        self.prbEntity.exitFromQueue()
        self.destroy()
