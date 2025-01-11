# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/chapter_rewards_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen.view_models.views.lobby.paragons.chapter_rewards_view_model import ChapterRewardsViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillChapterModel
from gui.impl.lobby.paragons.paragons_window_events import showParagonsSelectRewardsWindow
from gui.impl.lobby.paragons.tooltips.branch_select_tooltip import BranchSelectTooltip
from gui.impl.lobby.paragons.tooltips.vehicle_select_tooltip import VehicleSelectTooltip
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IParagonsController

class ChapterRewardsView(ViewImpl):
    __slots__ = ('__chapterID', '__tooltipData')
    __paragonsController = dependency.descriptor(IParagonsController)

    def __init__(self, layoutID, chapterID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = ChapterRewardsViewModel()
        self.__chapterID = chapterID
        self.__tooltipData = {}
        super(ChapterRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChapterRewardsView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onSelectVehicle, self.__onSelectVehicle),
         (self.__paragonsController.onProgressPointsChanged, self.__fillModel),
         (self.__paragonsController.onSelectedRewardTokenReceived, self.__fillModel),
         (self.__paragonsController.onSelectedRewardMarked, self.__fillModel))

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ChapterRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.paragons.tooltips.BranchSelectTooltip():
            tooltipData = self.getTooltipData(event)
            return BranchSelectTooltip(layoutID=R.views.lobby.paragons.tooltips.BranchSelectTooltip(), paragonsUnlockID=tooltipData.specialArgs[0])
        return VehicleSelectTooltip(layoutID=R.views.lobby.paragons.tooltips.VehicleSelectTooltip()) if contentID == R.views.lobby.paragons.tooltips.VehicleSelectTooltip() else super(ChapterRewardsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(ChapterRewardsView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def __onClose(self):
        self.destroyWindow()

    @args2params(int, str)
    def __onSelectVehicle(self, levelID, entCode):
        showParagonsSelectRewardsWindow(chapterID=self.__chapterID, levelID=levelID, entitlementID=entCode, parent=self.getParentWindow())

    def __fillModel(self, *_, **__):
        with self.viewModel.transaction() as tx:
            fillChapterModel(tx.currentChapter, self.__chapterID, tooltipData=self.__tooltipData)


class ChapterRewardsWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, chapterID, parent=None):
        super(ChapterRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ChapterRewardsView(R.views.lobby.paragons.ChapterRewardsView(), chapterID), parent=parent)
