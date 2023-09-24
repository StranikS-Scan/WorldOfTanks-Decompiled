# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/elite_window/elite_view.py
import SoundGroups
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.elite_window.elite_view_model import EliteViewModel
from gui.prestige.prestige_helpers import hasVehiclePrestige, fillPrestigeEmblemModel, getVehiclePrestige
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showVehPostProgressionView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.veh_post_progression.sounds import Sounds
from helpers import dependency
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache

class EliteView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('__vehicle',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.elite_window.EliteView())
        settings.model = EliteViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(EliteView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EliteView, self).getViewModel()

    def _onLoading(self, vehicleCD, *args, **kwargs):
        currentLevel, _ = getVehiclePrestige(vehicleCD, itemsCache=self.__itemsCache)
        with self.viewModel.transaction() as model:
            self.__vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
            fillVehicleInfo(model.vehicleInfo, self.__vehicle)
            self.__updateVehPostProgression(model=model)
            model.setIsPrestigeAvailable(hasVehiclePrestige(vehicleCD))
            fillPrestigeEmblemModel(model.prestigeEmblem, currentLevel, vehicleCD)
        super(EliteView, self)._onLoading(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        super(EliteView, self)._onLoaded(*args, **kwargs)
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.gui_reward_screen_general()))
        SoundGroups.g_instance.playSound2D(Sounds.ENTER_ELITE_VIEW)

    def _getEvents(self):
        return super(EliteView, self)._getEvents() + ((self.__itemsCache.onSyncCompleted, self.__onSyncCompleted), (self.viewModel.onClose, self.__onClose), (self.viewModel.onGoToPostProgression, self.__onGoToPostProgression))

    def __onClose(self):
        g_eventBus.handleEvent(events.CloseWindowEvent(events.CloseWindowEvent.ELITE_WINDOW_CLOSED))
        self.destroyWindow()

    def __onGoToPostProgression(self):

        def predicate(window):
            return window.content is not None and getattr(window.content, 'alias', None) == VIEW_ALIAS.LOBBY_RESEARCH

        window = first(self.__guiLoader.windowsManager.findWindows(predicate))
        if window is not None:
            window.content.goToPostProgression(self.__vehicle.intCD)
        else:
            g_eventBus.handleEvent(events.DestroyViewEvent(VIEW_ALIAS.VEH_POST_PROGRESSION), scope=EVENT_BUS_SCOPE.LOBBY)
            showVehPostProgressionView(self.__vehicle.intCD)
        self.__markAsVisitedHintInResearch()
        return

    def __markAsVisitedHintInResearch(self):
        self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.RESEARCH_POST_PROGRESSION_ENTRY_POINT_HINT: 1})

    def __onSyncCompleted(self, reason, diff):
        if GUI_ITEM_TYPE.VEH_POST_PROGRESSION in diff:
            self.__updateVehPostProgression()

    @replaceNoneKwargsModel
    def __updateVehPostProgression(self, model=None):
        model.setIsPostProgressionExists(self.__vehicle.postProgressionAvailability(unlockOnly=True).result)


class EliteWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, vehicleCD):
        super(EliteWindow, self).__init__(content=EliteView(vehicleCD=vehicleCD))
