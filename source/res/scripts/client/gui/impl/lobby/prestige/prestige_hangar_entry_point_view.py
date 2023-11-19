# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/prestige/prestige_hangar_entry_point_view.py
import logging
from CurrentVehicle import g_currentVehicle
from constants import Configs
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.prestige.prestige_hangar_entry_point_model import PrestigeHangarEntryPointModel
from gui.impl.pub import ViewImpl
from gui.prestige.prestige_helpers import getCurrentProgress, fillPrestigeEmblemModel, getVehiclePrestige, showPrestigeVehicleStats, DEFAULT_PRESTIGE
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class PrestigeHangarEntryPointView(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.prestige.views.PrestigeHangarEntryPoint(), flags=ViewFlags.VIEW, model=PrestigeHangarEntryPointModel())
        super(PrestigeHangarEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PrestigeHangarEntryPointView, self).getViewModel()

    def _getEvents(self):
        return super(PrestigeHangarEntryPointView, self)._getEvents() + ((self.viewModel.onShowInfo, self.__onShowInfoClick),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange),
         (g_currentVehicle.onChanged, self.__onCurrentVehicleChanged),
         (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted))

    def _onLoading(self, *args, **kwargs):
        super(PrestigeHangarEntryPointView, self)._onLoading()
        self.__updateModel()

    def __updateModel(self):
        currentLevel, remainingPts = getVehiclePrestige(g_currentVehicle.intCD, itemsCache=self.__itemsCache)
        if (currentLevel, remainingPts) == DEFAULT_PRESTIGE:
            return
        currentXP, nextLvlXP = getCurrentProgress(g_currentVehicle.intCD, currentLevel, remainingPts, lobbyContext=self.__lobbyContext)
        with self.viewModel.transaction() as tx:
            tx.setCurrentProgress(currentXP)
            tx.setMaxProgress(nextLvlXP)
            fillPrestigeEmblemModel(tx.emblem, currentLevel, g_currentVehicle.intCD)

    def __onShowInfoClick(self):
        showPrestigeVehicleStats(g_currentVehicle.intCD)

    def __onServerSettingsChange(self, diff):
        if Configs.PRESTIGE_CONFIG.value in diff:
            self.__updateModel()

    def __onCurrentVehicleChanged(self):
        self.__updateModel()

    def __onSyncCompleted(self, *args):
        self.__updateModel()
