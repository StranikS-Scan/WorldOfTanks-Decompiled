# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_summary_results.py
import logging
from frameworks.wulf import ViewFlags, WindowFlags, Window, WindowSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.framework.managers.loaders import ViewKey
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter, BATTLE_ROYALE_MODEL_PRESENTERS
from gui.impl.backport import createTooltipData, BackportTooltipWindow, TooltipData
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.battle_royale.BR_stats_renderer_model import BRStatsRendererModel
from gui.impl.gen.view_models.views.battle_royale.battle_royale_summary_results_view_model import BattleRoyaleSummaryResultsViewModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.pub import ViewImpl
from gui.prb_control import prbDispatcherProperty
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IBattleRoyaleController
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class BattleRoyaleSummaryResults(ViewImpl):
    battleRoyale = dependency.descriptor(IBattleRoyaleController)
    __slots__ = ('__inBattle', '__isInSquad', '__isWinner', '__statsList', '__rewardsList', '__namesList', '__isDataInit', '__chevronsDiff', '__items')

    def __init__(self, *args, **kwargs):
        layoutID = kwargs.pop('layoutID', None) or R.views.common.battle_royale.battle_summary_results.BattleRoyaleSummaryResults()
        super(BattleRoyaleSummaryResults, self).__init__(layoutID, ViewFlags.VIEW, BattleRoyaleSummaryResultsViewModel, *args, **kwargs)
        self.__isDataInit = False
        self.__items = {}
        self.__inBattle = False
        self.__isInSquad = False
        self.__isWinner = False
        self.__chevronsDiff = 0
        self.__statsList = None
        self.__rewardsList = None
        self.__namesList = None
        if kwargs.get('ctx'):
            self.setData(kwargs.get('ctx'))
        return

    def setData(self, data, updateModel=False):
        self.__inBattle = data.get('inBattle', False)
        self.__isInSquad = data.get('isInSquad', False)
        self.__isWinner = data.get('isWinner', False)
        self.__chevronsDiff = data.get('chevronsDiff', 0)
        self.__statsList = data.get('statsList', [])
        self.__rewardsList = data.get('rewardsList', [])
        self.__namesList = data.get('namesList', [])
        self.__isDataInit = True
        if updateModel:
            self.__updateViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(BattleRoyaleSummaryResults, self).createToolTip(event)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @property
    def viewModel(self):
        return super(BattleRoyaleSummaryResults, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(BattleRoyaleSummaryResults, self)._initialize()
        self.viewModel.onShowHangarBtnClick += self.__onShowHangarBtnClick
        if self.__isDataInit:
            self.__updateViewModel()

    def _finalize(self):
        self.viewModel.onShowHangarBtnClick -= self.__onShowHangarBtnClick
        self.__items.clear()
        super(BattleRoyaleSummaryResults, self)._finalize()

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        elif tooltipId in self.__items:
            return self.__items[tooltipId]
        else:
            if tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT:
                vehicleCD = _getVehicleCD(event.getArgument('vehicleCD'))
                if vehicleCD is not None:
                    return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_INFO, specialArgs=(vehicleCD, True))
            elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT_CONVERT_COUNT:
                vehicleCD = _getVehicleCD(event.getArgument('vehicleCD'))
                if vehicleCD is not None:
                    return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_CONVERT_INFO, specialArgs=[vehicleCD])
            return

    def __updateViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setInSquad(self.__isInSquad)
            vm.setIsWinner(self.__isWinner)
            vm.setChevronsDiff(self.__chevronsDiff)
            vm.setChevronsDiffTrigger(True)
            self.__updateStatsList(vm.getStatsList(), self.__statsList)
            self.__updateRewardsList(vm.getRewardsList(), self.__rewardsList)
            self.__updateNamesList(vm.getNamesList(), self.__namesList)

    def __updateStatsList(self, statsList, dataList):
        statsList.clear()
        for idx, item in enumerate(dataList):
            itemModel = BRStatsRendererModel()
            itemModel.setImage(item.get('image', R.invalid()))
            itemModel.setStatValue(item.get('value', 0))
            itemModel.setId(item.get('id', idx))
            itemModel.setTooltip(item.get('tooltip', ''))
            if idx == 0:
                itemModel.setTotalPlayersValue(item.get('totalValue', 0))
                itemModel.setWinner(self.__isWinner)
            if 'isSeparator' in item:
                itemModel.setIsSeparator(item['isSeparator'])
            statsList.addViewModel(itemModel)

        statsList.invalidate()

    def __updateRewardsList(self, rewardsList, dataList):
        rewardsList.clear()
        if dataList is None:
            dataList = []
        for index, reward in enumerate(dataList):
            formatter = getRewardRendererModelPresenter(reward, BATTLE_ROYALE_MODEL_PRESENTERS)
            rewardRender = formatter.getModel(reward, index, False)
            rewardsList.addViewModel(rewardRender)
            compensationReason = reward.get('compensationReason', None)
            ttTarget = compensationReason if compensationReason is not None else reward
            self.__items[index] = TooltipData(tooltip=ttTarget.get('tooltip', None), isSpecial=ttTarget.get('isSpecial', False), specialAlias=ttTarget.get('specialAlias', ''), specialArgs=ttTarget.get('specialArgs', None))

        rewardsList.invalidate()
        return

    def __updateNamesList(self, namesList, dataList):
        namesList.clear()
        for item in dataList:
            namesList.addString(item)

        namesList.invalidate()

    def __onShowHangarBtnClick(self):
        if self.__inBattle:
            self.__doExit()
        else:
            self.destroyWindow()

    def __doExit(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        sessionProvider.exit()


class BattleRoyaleSummaryResultsWindow(Window):
    appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        view = self.appLoader.getApp().containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
        if view is not None:
            parent = view.getParentWindow()
        else:
            parent = None
        settings = WindowSettings()
        settings.flags = WindowFlags.WINDOW
        settings.content = BattleRoyaleSummaryResults(*args, **kwargs)
        settings.parent = parent
        super(BattleRoyaleSummaryResultsWindow, self).__init__(settings)
        return


class BattleRoyaleSummaryResultsComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return BattleRoyaleSummaryResults(layoutID=R.views.common.battle_royale.hangar_summary_results.HangarBattleRoyaleSummaryResults())

    def setData(self, data):
        self.injectView.setData(data, updateModel=True)


def _getVehicleCD(value):
    try:
        vehicleCD = int(value)
    except ValueError:
        _logger.warning('Wrong vehicle compact descriptor: %s!', value)
        return None

    return vehicleCD
    return None
