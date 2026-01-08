# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/new_module_vehicle_progress.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.lobby.vehicle_hub.sub_presenters.modules_sub_presenter import ModulesTreeViewDumper
from gui.impl.lobby.hangar.presenters.utils import GUINode
from gui.impl.pub.view_component import ViewComponent
from gui.impl.gen.view_models.views.lobby.battle_results.progression.module_vehicle_progress_model import ModuleVehicleProgressModel
from gui.impl.gen.view_models.views.lobby.battle_results.progression.unlock_module_progress_model import UnlockModuleProgressModel
from gui.impl.gen.view_models.views.lobby.battle_results.progression.unlock_vehicle_progress_model import UnlockVehicleProgressModel
from gui.shared import event_dispatcher, events
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator

class NewModuleVehicleProgressPresenter(ViewComponent[ModuleVehicleProgressModel], IProgressionCategoryPresenter):

    def __init__(self, categoryProgressFilter, arenaUniqueID, *args, **kwargs):
        super(NewModuleVehicleProgressPresenter, self).__init__(model=ModuleVehicleProgressModel, enabled=False)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__vehicleIntCD = g_currentPreviewVehicle.intCD
        self.__progress = None
        return

    @classmethod
    def getPathToResource(cls):
        return ModuleVehicleProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.battle_results.progression.ModuleVehicleUnlocks()

    @property
    def viewModel(self):
        return super(NewModuleVehicleProgressPresenter, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(NewModuleVehicleProgressPresenter, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId in (TOOLTIPS_CONSTANTS.TECHTREE_MODULE, TOOLTIPS_CONSTANTS.TECHTREE_VEHICLE):
            itemCD = int(event.getArgument('itemCD', 0))
            if not itemCD:
                return None
            currentNode = self._data.getNodeByItemCD(itemCD)
            guiNode = GUINode(itemCD, currentNode.getState(), currentNode.getUnlockProps())
            return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(guiNode, self.__vehicleIntCD))
        else:
            return None

    def prepare(self):
        self._subscribe()
        self._updateProgress()
        if not self.__progress:
            return
        self.setEnabled(True)

    def finalize(self):
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__progress = None
        self.__vehicleIntCD = None
        self._data.clear()
        self._unsubscribe()
        super(NewModuleVehicleProgressPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onNavigate, self.__onNavigate),)

    def _getListeners(self):
        return ((events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onPremiumXpBonusChanged),)

    def _onLoading(self, *args, **kwargs):
        self._data = ResearchItemsData(ModulesTreeViewDumper())
        self._data.setRootCD(self.__vehicleIntCD)
        self._data.load()
        self._updateModel()
        plugins = self.getParentView().viewModel.getPathToPlugins()
        plugins.set(self.getViewAlias(), self.getPathToResource())

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            for unlockVehicles, unlockModules in self.__progress.values():
                unlockedVehicles = model.getUnlockedVehicles()
                unlockedVehicles.clear()
                for item in unlockVehicles:
                    vehicleModel = self.__createUnlockVehicle(*item)
                    unlockedVehicles.addViewModel(vehicleModel)

                unlockedVehicles.invalidate()
                unlockedModules = model.getUnlockedModule()
                unlockedModules.clear()
                for item in unlockModules:
                    moduleModel = self.__createUnlockModule(*item)
                    unlockedModules.addViewModel(moduleModel)

                unlockedModules.invalidate()

    def _updateProgress(self):
        battleResults = getBattleResults(self.__arenaUniqueID)
        if battleResults:
            self.__progress = self.__categoryProgressFilter(battleResults.reusable)

    def __onPremiumXpBonusChanged(self, event):
        isBonusApplied = event.ctx.get('isBonusApplied', True) if event.ctx is not None else True
        if not isBonusApplied:
            return
        else:
            self._updateProgress()
            if not self.__progress:
                return
            self.setEnabled(True)
            self._updateModel()
            return

    @args2params(int)
    def __onNavigate(self, vehicleCD):
        if not vehicleCD:
            vehicleCD = self.__progress.keys()[0]
        event_dispatcher.showVehicleHubModules(vehicleCD)

    def __createUnlockModule(self, item, unlockProps):
        model = UnlockModuleProgressModel()
        model.setUserName(item.userName)
        model.setItemTypeName(item.itemTypeName)
        model.setModuleId(item.intCD)
        model.setIconName(item.iconName)
        model.setLevel(item.level)
        model.price.setName(CURRENCIES_CONSTANTS.XP_COST)
        model.price.setValue(unlockProps.xpCost)
        return model

    def __createUnlockVehicle(self, item, unlockProps, avgBattlesTillUnlock):
        model = UnlockVehicleProgressModel()
        model.setUserName(item.userName)
        model.setNationName(item.nationName)
        model.setVehicleId(item.intCD)
        model.setVehicleIcon(item.name)
        model.setVehicleType(item.type)
        model.setLevel(item.level)
        model.setAvgBattlesTillUnlock(avgBattlesTillUnlock)
        model.price.setName(CURRENCIES_CONSTANTS.XP_COST)
        model.price.setValue(unlockProps.xpCost)
        return model
