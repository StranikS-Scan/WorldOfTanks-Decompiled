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
from helpers import dependency

class QueueView(ViewImpl):
    __cosmicEventController = dependency.descriptor(ICosmicEventBattleController)

    def __init__(self, layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW):
        settings = ViewSettings(layoutID, flags, QueueViewModel())
        qType = self.prbEntity.getQueueType()
        providerClass = collectBattleQueueProvider(qType)
        self._queueProvider = providerClass(self, qType)
        super(QueueView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(QueueView, self).getViewModel()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def setPlayersCount(self, count):
        with self.viewModel.transaction() as tx:
            tx.setPlayersInQueue(count)

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
