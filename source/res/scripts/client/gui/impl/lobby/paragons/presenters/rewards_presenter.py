# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/presenters/rewards_presenter.py
import logging
import typing
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.rewards_header_tooltip_model import RewardsHeaderTooltipModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillChapterModel
from gui.impl.lobby.paragons.paragons_window_events import showParagonsSelectRewardsWindow
from gui.impl.lobby.paragons.tooltips.branch_select_tooltip import BranchSelectTooltip
from gui.impl.lobby.paragons.tooltips.vehicle_select_tooltip import VehicleSelectTooltip
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import TabId
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from helpers import dependency
from skeletons.gui.game_control import IParagonsController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewModel

class RewardsPresenter(SubModelPresenter):
    __slots__ = SubModelPresenter.__slots__ + ('__tooltipData',)
    __paragonsController = dependency.descriptor(IParagonsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, parentView):
        super(RewardsPresenter, self).__init__(viewModel, parentView)
        self.__viewModel = viewModel
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(RewardsPresenter, self).getViewModel()

    @property
    def parentViewModel(self):
        return self.parentView.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onSelectVehicle, self.__onSelectVehicle),
         (self.__paragonsController.onProgressPointsChanged, self.__fillModel),
         (self.__paragonsController.onSelectedRewardTokenReceived, self.__fillModel),
         (self.__paragonsController.onSelectedRewardMarked, self.__fillModel))

    def initialize(self, *args, **kwargs):
        super(RewardsPresenter, self).initialize(*args, **kwargs)
        self.__fillModel()
        _logger.info('[Paragons]: rewards presenter inited')

    def finalize(self):
        super(RewardsPresenter, self).finalize()
        _logger.info('[Paragons]: rewards presenter finalized')

    @createBackportTooltipDecorator()
    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.paragons.tooltips.BranchSelectTooltip():
            tooltipData = self.getTooltipData(event)
            return BranchSelectTooltip(layoutID=R.views.lobby.paragons.tooltips.BranchSelectTooltip(), paragonsUnlockID=tooltipData.specialArgs[0])
        elif contentID == R.views.lobby.paragons.tooltips.VehicleSelectTooltip():
            return VehicleSelectTooltip(layoutID=R.views.lobby.paragons.tooltips.VehicleSelectTooltip())
        elif contentID == R.views.lobby.paragons.tooltips.RewardsHeaderTooltip():
            rewardsHeaderModel = RewardsHeaderTooltipModel()
            rewardsHeaderModel.setIsLevelAchieved(event.getArgument('isCompleted'))
            rewardsHeaderModel.setIsCurrentLevel(event.getArgument('isCurrentLevel'))
            settings = ViewSettings(layoutID=R.views.lobby.paragons.tooltips.RewardsHeaderTooltip(), model=rewardsHeaderModel)
            return ViewImpl(settings)
        else:
            return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    @args2params(int, str)
    def __onSelectVehicle(self, levelID, entCode):
        currentChapterID = self.__paragonsController.chapterID or self.__paragonsController.getFirstChapterWithAvailableRewards()
        showParagonsSelectRewardsWindow(chapterID=currentChapterID, levelID=levelID, entitlementID=entCode, parent=self.getParentWindow())

    def __fillModel(self, *_, **__):
        showChapterID = self.__paragonsController.chapterID or self.__paragonsController.getFirstChapterWithAvailableRewards()
        if showChapterID:
            with self.viewModel.transaction() as tx:
                fillChapterModel(tx.currentChapter, showChapterID, tooltipData=self.__tooltipData)
        else:
            self.parentViewModel.onTabChange({'tabId': TabId.PROGRESS})
