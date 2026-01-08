# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/prestige_progress.py
from constants import Configs
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.progression.prestige_progress_model import PrestigeProgressModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.pub.view_component import ViewComponent
from gui.prestige.prestige_helpers import fillPrestigeEmblemModel, hasVehiclePrestige, showPrestigeVehicleStats
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class PrestigeProgressPresenter(ViewComponent[PrestigeProgressModel], IProgressionCategoryPresenter):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, categoryProgressFilter, arenaUniqueID, *args, **kwargs):
        super(PrestigeProgressPresenter, self).__init__(model=PrestigeProgressModel)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__progress = None
        return

    @classmethod
    def getPathToResource(cls):
        return PrestigeProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.battle_results.progression.Prestige()

    @property
    def viewModel(self):
        return super(PrestigeProgressPresenter, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onNavigate, self.__onNavigate), (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingChanged))

    def _finalize(self):
        self.__progress = None
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        super(PrestigeProgressPresenter, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(PrestigeProgressPresenter, self)._onLoading(*args, **kwargs)
        self._updateProgress()
        if not self.__progress:
            return
        self._updateModel()
        plugins = self.getParentView().viewModel.getPathToPlugins()
        plugins.set(self.getViewAlias(), self.getPathToResource())

    def _updateProgress(self):
        battleResults = getBattleResults(self.__arenaUniqueID)
        if battleResults:
            self.__progress = self.__categoryProgressFilter(battleResults.reusable)

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            model.setVehCD(self.__progress.vehCD)
            model.setGainedXP(self.__progress.gainedXP)
            model.setOldLvl(self.__progress.oldLvl)
            model.setNewLvl(self.__progress.newLvl)
            model.setCurrentXP(self.__progress.currentXP)
            model.setCurrentNextLevelXP(self.__progress.currentNextLvlXP)
            model.setOldXP(self.__progress.oldXP)
            model.setOldNextLvlXP(self.__progress.oldNextLvlXP)
            fillPrestigeEmblemModel(model.currentPrestigeEmblemModel, self.__progress.newLvl, self.__progress.vehCD)
            fillPrestigeEmblemModel(model.oldPrestigeEmblemModel, self.__progress.oldLvl, self.__progress.vehCD)
            model.setIsNavigationEnabled(hasVehiclePrestige(self.__progress.vehCD, checkElite=True))

    @args2params(int)
    def __onNavigate(self, vehCD):
        showPrestigeVehicleStats(vehCD)

    def __onServerSettingChanged(self, diff):
        if Configs.PRESTIGE_CONFIG.value in diff and self.__progress:
            self.viewModel.setIsNavigationEnabled(hasVehiclePrestige(self.__progress.vehCD, checkElite=True))
