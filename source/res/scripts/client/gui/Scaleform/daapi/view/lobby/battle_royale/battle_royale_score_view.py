# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_score_view.py
import logging
from gui.impl.gen.view_models.views.battle_royale.BR_score_background_model import BRScoreBackgroundModel
from gui.impl.gen.view_models.views.battle_royale.BR_score_item_renderer_base_model import BRScoreItemRendererBaseModel
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.impl.gen.resources import R
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IBattleRoyaleController
from frameworks.wulf import ViewFlags, WindowFlags, Window
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import ViewKey
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen.view_models.views.battle_royale.battle_royale_score_results_view_model import BattleRoyaleScoreResultsViewModel
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class BattleRoyaleScoreView(ViewImpl):
    battleRoyale = dependency.descriptor(IBattleRoyaleController)
    __slots__ = ('__isInSquad', '__inBattle', '__dataTable', '__dataUsers', '__namesList', '__isDataInit', '__isWinner')

    def __init__(self, *args, **kwargs):
        super(BattleRoyaleScoreView, self).__init__(R.views.common.battle_royale.score_results.BattleRoyaleScoreResults(), ViewFlags.VIEW, BattleRoyaleScoreResultsViewModel, *args, **kwargs)
        self.__isDataInit = False
        self.__inBattle = False
        self.__isWinner = False
        self.__isInSquad = False
        self.__dataTable = None
        self.__dataUsers = None
        self.__namesList = None
        if kwargs.get('ctx'):
            self.setData(kwargs.get('ctx'))
        return

    @property
    def viewModel(self):
        return super(BattleRoyaleScoreView, self).getViewModel()

    def setData(self, ctx, updateModel=False):
        self.__inBattle = ctx.get('inBattle', False)
        self.__isWinner = ctx.get('isWinner', False)
        self.__isInSquad = ctx.get('isInSquad', False)
        self.__dataTable = ctx.get('dataTable', [])
        self.__dataUsers = ctx.get('dataUsers', [])
        self.__namesList = ctx.get('namesList', [])
        self.__isDataInit = True
        if updateModel:
            self.__updateViewModel()

    def _initialize(self, *args, **kwargs):
        super(BattleRoyaleScoreView, self)._initialize()
        self.viewModel.onShowHangarBtnClick += self.__onShowHangarBtnClick
        if self.__isDataInit:
            self.__updateViewModel()

    def _finalize(self):
        self.viewModel.onShowHangarBtnClick -= self.__onShowHangarBtnClick

    def __updateViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setInSquad(self.__isInSquad)
            vm.setIsBattleState(self.__inBattle)
            vm.setIsWinner(self.__isWinner)
            self.__updateDataTable(vm.getTableData(), self.__dataTable)
            self.__updateDataUsers(vm.getUsersData(), self.__dataUsers)
            self.__updateNamesList(vm.getNamesList(), self.__namesList)

    def __updateDataTable(self, dataTable, dataList):
        for idx, item in enumerate(dataList):
            itemModel = BRScoreBackgroundModel()
            itemModel.setCountChevrones(item.get('countChevrones'))
            itemModel.setCount(item.get('count'))
            if idx == 0:
                itemModel.setIsWinner(True)
            dataTable.addViewModel(itemModel)

        dataTable.invalidate()

    def __updateDataUsers(self, dataUser, dataList):
        for item in dataList:
            itemModel = BRScoreItemRendererBaseModel()
            itemModel.setUserName(item.get('userName', []))
            itemModel.setUserPlace(item.get('userPlace', ''))
            itemModel.setUserCurrent(item.get('userCurrent', False))
            itemModel.setIsLeaver(item.get('isLeaver', False))
            itemModel.setIsWinner(item.get('isWinner', False))
            dataUser.addViewModel(itemModel)

        dataUser.invalidate()

    def __updateNamesList(self, namesList, dataList):
        namesList.clear()
        for item in dataList:
            namesList.addString(item)

        namesList.invalidate()

    def __onShowHangarBtnClick(self):
        self.destroyWindow()


class BattleRoyaleScoreWindow(Window):
    appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        view = self.appLoader.getApp().containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
        if view is not None:
            parent = view.getParentWindow()
        else:
            parent = None
        super(BattleRoyaleScoreWindow, self).__init__(content=BattleRoyaleScoreView(*args, **kwargs), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return


class BattleRoyaleScoreComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return BattleRoyaleScoreView()

    def setData(self, data):
        self.injectView.setData(data, updateModel=True)
