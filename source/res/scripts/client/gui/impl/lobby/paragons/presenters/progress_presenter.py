# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/presenters/progress_presenter.py
from functools import partial
import typing
from frameworks.wulf import ViewSettings, ViewModel
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import TabId
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.rewards_header_tooltip_model import RewardsHeaderTooltipModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.paragons.paragons_window_events import showParagonsSelectRewardsWindow
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillChapterModels
from gui.impl.lobby.paragons.paragons_helpers.paragons_helpers import onProgressionStylePreview
from gui.impl.lobby.paragons.paragons_window_events import showParagonsNavigationView
from gui.impl.lobby.paragons.sound_constants import PARAGONS_PREVIEW_SOUND_SPACE
from gui.impl.lobby.paragons.tooltips.branch_select_tooltip import BranchSelectTooltip
from gui.impl.lobby.paragons.tooltips.vehicle_select_tooltip import VehicleSelectTooltip
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showVehiclePreview
from helpers import dependency
from skeletons.gui.game_control import IParagonsController, IVehicleComparisonBasket
from gui.impl.gui_decorators import args2params
import logging
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.paragons.progression.progression_view_model import ProgressionViewModel

class ProgressPresenter(SubModelPresenter):
    __slots__ = SubModelPresenter.__slots__ + ('__tooltipData',)
    __paragonsController = dependency.descriptor(IParagonsController)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, viewModel, parentView):
        super(ProgressPresenter, self).__init__(viewModel, parentView)
        self.__viewModel = viewModel
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(ProgressPresenter, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onPreviewVehicle, self.__onPreviewVehicle),
         (self.viewModel.onPreviewStyle, self.__onProgressStylePreview),
         (self.viewModel.onCompareVehicle, self.__onCompareVehicle),
         (self.viewModel.onSelectVehicle, self.__onSelectVehicle),
         (self.__paragonsController.onProgressPointsChanged, self.__fillModel),
         (self.__paragonsController.onSelectedRewardTokenReceived, self.__fillModel),
         (self.__paragonsController.onSelectedRewardMarked, self.__fillModel))

    def initialize(self, *args, **kwargs):
        super(ProgressPresenter, self).initialize(*args, **kwargs)
        self.__fillModel()
        _logger.info('[Paragons]: progress presenter inited')

    def finalize(self):
        super(ProgressPresenter, self).finalize()
        _logger.info('[Paragons]: progress presenter finalized')

    @createBackportTooltipDecorator()
    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.paragons.tooltips.PointsTooltip():
            settings = ViewSettings(layoutID=R.views.lobby.paragons.tooltips.PointsTooltip(), model=ViewModel())
            return ViewImpl(settings)
        elif contentID == R.views.lobby.paragons.tooltips.BranchSelectTooltip():
            tooltipData = self.getTooltipData(event)
            return BranchSelectTooltip(layoutID=R.views.lobby.paragons.tooltips.BranchSelectTooltip(), paragonsUnlockID=tooltipData.specialArgs[0])
        elif contentID == R.views.lobby.paragons.tooltips.VehicleSelectTooltip():
            return VehicleSelectTooltip(layoutID=R.views.lobby.paragons.tooltips.VehicleSelectTooltip(), level=int(event.getArgument('level')), chapterID=int(event.getArgument('chapterID')), entitlementID=event.getArgument('entitlementID'))
        elif contentID == R.views.lobby.paragons.tooltips.RewardsHeaderTooltip():
            rewardsHeaderModel = RewardsHeaderTooltipModel()
            rewardsHeaderModel.setIsLevelAchieved(event.getArgument('isCompleted'))
            rewardsHeaderModel.setIsCurrentLevel(event.getArgument('isCurrentLevel'))
            rewardsHeaderModel.setHasSelectableRewards(event.getArgument('hasSelectableRewards'))
            rewardsHeaderModel.setIsParagonsPoints(event.getArgument('isParagonsPoints'))
            settings = ViewSettings(layoutID=R.views.lobby.paragons.tooltips.RewardsHeaderTooltip(), model=rewardsHeaderModel)
            return ViewImpl(settings)
        else:
            return None

    def __fillModel(self, *_, **__):
        with self.viewModel.transaction() as tx:
            fillChapterModels(tx.getStages(), tooltipData=self.__tooltipData)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    @args2params(int, int)
    def __onPreviewVehicle(self, vehicleCD, seasonID):
        _logger.info('[Paragons]: onPreviewVehicle, vehicleCD=%s, season=%s', vehicleCD, seasonID)
        showVehiclePreview(vehicleCD, previewBackCb=partial(self.__vehiclePreviewCallback, seasonID), previewAlias=VIEW_ALIAS.VEHICLE_PREVIEW, backBtnLabel=backport.text(R.strings.paragons.vehiclePreview.backButton()), soundSpace=PARAGONS_PREVIEW_SOUND_SPACE)

    @args2params(int, int, int)
    def __onProgressStylePreview(self, styleID, group, styleLevel):
        onProgressionStylePreview(styleID, group, styleLevel=styleLevel, previewCallback=self.__previewBackCallback, soundSpace=PARAGONS_PREVIEW_SOUND_SPACE)

    def __vehiclePreviewCallback(self, seasonID):
        currentSeasonID = seasonID or self.__paragonsController.chapterID
        tabID = TabId.PROGRESS if currentSeasonID else TabId.CHAPTERS
        showParagonsNavigationView(tabId=tabID, currentChapterID=currentSeasonID)

    @args2params(int)
    def __onCompareVehicle(self, vehicleCD):
        self.__comparisonBasket.addVehicle(vehicleCD)

    @args2params(int, str, int)
    def __onSelectVehicle(self, levelID, entCode, chapterID):
        showParagonsSelectRewardsWindow(chapterID=chapterID, levelID=levelID, entitlementID=entCode)

    def __previewBackCallback(self):
        currentSeasonID = self.__paragonsController.chapterID
        tabID = TabId.PROGRESS if currentSeasonID else TabId.CHAPTERS
        showParagonsNavigationView(tabId=tabID)
