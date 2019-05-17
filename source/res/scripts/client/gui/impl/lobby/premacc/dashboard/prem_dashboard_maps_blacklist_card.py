# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/prem_dashboard_maps_blacklist_card.py
from frameworks.wulf import ViewFlags
from constants import PremiumConfigs
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_maps_blacklist_card_model import PremDashboardMapsBlacklistCardModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_slot_states import MapsBlacklistSlotStates
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_widget_slot_model import MapsBlacklistWidgetSlotModel
from gui.impl.lobby.premacc.maps_blacklist_view import buildSlotsModels
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showMapsBlacklistView
from gui.shared.utils.scheduled_notifications import AcyclicNotifier, Notifiable
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext

class PremDashboardMapsBlacklistCard(ViewImpl):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __slots__ = ('__notifier',)

    def __init__(self, *args, **kwargs):
        super(PremDashboardMapsBlacklistCard, self).__init__(R.views.lobby.premacc.dashboard.prem_dashboard_maps_blacklist_card.PremDashboardMapsBlacklistCard(), ViewFlags.VIEW, PremDashboardMapsBlacklistCardModel, *args, **kwargs)
        self.__notifier = None
        return

    @property
    def viewModel(self):
        return super(PremDashboardMapsBlacklistCard, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PremDashboardMapsBlacklistCard, self)._initialize(*args, **kwargs)
        self.viewModel.onGoToMapsBlacklistView += self.__onOpenMapsBlackListView
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify += self.__updatePrem
        g_clientUpdateManager.addCallbacks({'preferredMaps': self.__onPreferredMapsChanged})
        self.__notifier = Notifiable()
        self.__notifier.addNotificator(AcyclicNotifier(lambda : ONE_MINUTE, self.__timerUpdate))
        self.__update()

    def _finalize(self):
        self.viewModel.onGoToMapsBlacklistView -= self.__onOpenMapsBlackListView
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify -= self.__updatePrem
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__notifier.clearNotification()
        super(PremDashboardMapsBlacklistCard, self)._finalize()

    def __onOpenMapsBlackListView(self, _=None):
        showMapsBlacklistView()
        self.__update()

    def __update(self):
        enabled = self.__lobbyContext.getServerSettings().isPreferredMapsEnabled()
        self.viewModel.setIsAvailable(enabled)
        if not enabled:
            return
        hasCooldown = False
        disabledMaps = self.viewModel.disabledMaps.getItems()
        disabledMaps.clear()
        for slotModel in buildSlotsModels(MapsBlacklistWidgetSlotModel):
            slotModel.setIsShowMode(True)
            disabledMaps.addViewModel(slotModel)
            if slotModel.getState() == MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN:
                hasCooldown = True

        disabledMaps.invalidate()
        if hasCooldown:
            self.__notifier.startNotification()
        else:
            self.__notifier.stopNotification()

    def __timerUpdate(self):
        self.__update()

    def __onServerSettingsChanged(self, diff):
        if PremiumConfigs.IS_PREFERRED_MAPS_ENABLED in diff or PremiumConfigs.PREFERRED_MAPS in diff:
            self.__update()

    def __onPreferredMapsChanged(self, _):
        self.__update()

    def __updatePrem(self, *_):
        self.__update()
