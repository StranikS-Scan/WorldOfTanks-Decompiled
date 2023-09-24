# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/prestige/global_onboarding_view.py
import typing
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.prestige.global_onboarding_view_model import GlobalOnboardingViewModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_vehicle_model import PrestigeVehicleModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.prestige.prestige_helpers import fillPrestigeEmblemModel, isOnboardingViewed, setOnboardingViewed, showPrestigeVehicleStats
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class GlobalOnboardingView(ViewImpl):
    __slots__ = ('__topPrestigeVehIntCD',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    _VEHICLE_PRESTIGE_TOP_COUNT = 3

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = GlobalOnboardingViewModel()
        self.__topPrestigeVehIntCD = None
        super(GlobalOnboardingView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(GlobalOnboardingView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onGoToVehicleStatistic, self.__onClose))

    def _onLoading(self, *args, **kwargs):
        super(GlobalOnboardingView, self)._onLoading(*args, **kwargs)
        self.__saveSettings()
        self.__updateModel()
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        super(GlobalOnboardingView, self)._finalize()

    def __updateModel(self):
        prestigeVehicles = list(self.__itemsCache.items.getAccountDossier().getPrestigeStats().getVehicles().items())
        prestigeVehicles.sort(key=lambda x: x[1][0], reverse=True)
        uniqLvlXp = set()
        sortedTopVehicles = []
        for vehCD, (level, remainingPts) in prestigeVehicles:
            if (level, remainingPts) not in uniqLvlXp and len(sortedTopVehicles) >= self._VEHICLE_PRESTIGE_TOP_COUNT:
                break
            uniqLvlXp.add((level, remainingPts))
            vehicle = self.__itemsCache.items.getItemByCD(vehCD)
            sortedTopVehicles.append((vehicle, (level, vehicle.level, vehicle.name.split(':')[1])))

        sortedTopVehicles.sort(key=lambda x: x[1])
        self.__topPrestigeVehIntCD = sortedTopVehicles[-1][0].intCD if sortedTopVehicles else g_currentVehicle.intCD
        with self.viewModel.transaction() as tx:
            tx.setEliteVehicleAmount(len(prestigeVehicles))
            vehiclesList = tx.getVehicles()
            vehiclesList.clear()
            for vehicle, (prestigeLevel, _, __) in sortedTopVehicles[-self._VEHICLE_PRESTIGE_TOP_COUNT:]:
                vehModel = PrestigeVehicleModel()
                fillVehicleModel(vehModel, vehicle)
                fillPrestigeEmblemModel(vehModel.emblem, prestigeLevel, vehicle.intCD)
                vehiclesList.addViewModel(vehModel)

            vehiclesList.invalidate()

    def __saveSettings(self):
        isFirstOpen = not isOnboardingViewed(settingsCore=self.__settingsCore)
        if isFirstOpen:
            setOnboardingViewed(settingsCore=self.__settingsCore)

    def __onClose(self):
        showPrestigeVehicleStats(self.__topPrestigeVehIntCD)
        self.destroyWindow()


class GlobalOnboardingWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(GlobalOnboardingWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=GlobalOnboardingView(R.views.lobby.prestige.views.GlobalOnboardingView()), layer=WindowLayer.TOP_WINDOW, parent=parent)
