# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/submodels/no_boxes.py
from gui.impl.gen.view_models.views.lobby.lootbox_system.main_view_model import SubViewID
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.no_boxes_view_model import NoBoxesViewModel
from gui.impl.lobby.lootbox_system.base.common import SubViewImpl
from gui.impl.lobby.lootbox_system.base.submodels.common import updateBoxesInfoModel
from gui.impl.lobby.lootbox_system.base.submodels.statistics import Statistics
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.base.common import ViewID, Views
from gui.lootbox_system.base.decorators import createTooltipContentDecorator
from gui.lootbox_system.base.utils import areUsedExternalTransitions, getPreferredBox, isShopVisible
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import ILootBoxSystemController

class NoBoxes(SubViewImpl):
    __slots__ = ('__category', '__stats', '__isResetCompleted', '__eventName', '__backCallback')
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, viewModel, parentView):
        super(NoBoxes, self).__init__(viewModel, parentView)
        self.__category = ''
        self.__stats = Statistics()
        self.__isResetCompleted = False
        self.__eventName = ''
        self.__backCallback = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(NoBoxes, self).createToolTip(event)

    def initialize(self, *args, **kwargs):
        super(NoBoxes, self).initialize(*args, **kwargs)
        self.__eventName = kwargs.get('eventName', '')
        self.__backCallback = kwargs.get('backCallback')
        self.__category = getPreferredBox(self.__eventName, kwargs.get('category')).getCategory()
        with self.viewModel.transaction() as vmTx:
            self.__updateData(model=vmTx)
            self.__updateStatistics(model=vmTx)

    def _getEvents(self):
        return ((self.viewModel.onInfoOpen, self.__showInfo),
         (self.viewModel.onBuyBoxes, self.__openShop),
         (self.viewModel.onClose, self.destroy),
         (self.viewModel.statistics.onReset, self.__onStatisticsReset),
         (self.viewModel.statistics.onUpdateResetState, self.__onUpdateResetState),
         (self.__lootBoxes.onBoxesCountChanged, self.__onCountChanged),
         (self.__lootBoxes.onStatusChanged, self.__onStatusChanged),
         (self.__lootBoxes.onBoxesUpdated, self.__updateStatistics),
         (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onStatusChanged))

    def _getListeners(self):
        return ((events.LootBoxSystemEvent.ON_STATISTICS_RESET, self.__onUpdateReset, EVENT_BUS_SCOPE.LOBBY),)

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        model.setEventName(self.__eventName)
        model.setUseExternal(areUsedExternalTransitions(self.__eventName))
        model.setIsShopVisible(isShopVisible(self.__eventName))
        updateBoxesInfoModel(self.__eventName, model.getBoxesInfo())

    @replaceNoneKwargsModel
    def __updateStatistics(self, model=None):
        useStats = self.__lootBoxes.useStats(self.__eventName)
        model.setUseStats(useStats)
        if useStats:
            self.__stats.update(model.statistics, findFirst(lambda b: b.getCategory() == self.__category, self.__lootBoxes.getActiveBoxes(self.__eventName)).getID(), self.__isResetCompleted, self.__eventName)

    def __onCountChanged(self):
        box = getPreferredBox(self.__eventName)
        if box.isEnabled() and box.getInventoryCount():
            Views.load(ViewID.MAIN, subViewID=SubViewID.HAS_BOXES, category=box.getCategory(), eventName=self.__eventName, backCallback=self.__backCallback)

    def __onUpdateResetState(self):
        self.__isResetCompleted = False
        self.viewModel.statistics.setIsResetCompleted(self.__isResetCompleted)

    def __onUpdateReset(self, event):
        self.__isResetCompleted = event.ctx['isCompleted']

    def __onStatisticsReset(self):
        self.__stats.reset()

    def __onStatusChanged(self):
        if self.__lootBoxes.isAvailable(self.__eventName) and self.__lootBoxes.getActiveBoxes(self.__eventName):
            box = getPreferredBox(self.__eventName)
            if box.isEnabled() and box.getInventoryCount():
                Views.load(ViewID.MAIN, subViewID=SubViewID.HAS_BOXES, category=box.getCategory(), eventName=self.__eventName, backCallback=self.__backCallback)
            else:
                self.__updateData()
                self.__updateStatistics()

    def __showInfo(self):
        Views.load(ViewID.INFO, previousWindow=ViewID.MAIN, eventName=self.__eventName, backCallback=self.__backCallback)

    def __openShop(self):
        Views.load(ViewID.SHOP, eventName=self.__eventName)
