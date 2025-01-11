# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/presenters/chapters_presenter.py
import typing
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
import logging
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import TabId
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillChapterModels
from gui.impl.lobby.paragons.paragons_window_events import showChapterRewardsView
from helpers import dependency
from skeletons.gui.game_control import IParagonsController
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Dict
    from frameworks.wulf import View, ViewModel

class ChaptersPresenter(SubModelPresenter):
    __slots__ = SubModelPresenter.__slots__ + ('__tooltipData',)
    __paragonsController = dependency.descriptor(IParagonsController)

    def __init__(self, viewModel, parentView):
        super(ChaptersPresenter, self).__init__(viewModel, parentView)
        self.__viewModel = viewModel
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(ChaptersPresenter, self).getViewModel()

    @property
    def parentViewModel(self):
        return self.parentView.getViewModel()

    def initialize(self, *args, **kwargs):
        super(ChaptersPresenter, self).initialize(*args, **kwargs)
        self.__updateChapters()
        _logger.info('[Paragons]: chapters presenter inited')

    def finalize(self):
        _logger.info('[Paragons]: chapters presenter finalized')
        super(ChaptersPresenter, self).finalize()

    def createToolTipContent(self, event, contentID):
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _getEvents(self):
        return ((self.viewModel.onSelectChapter, self.__onSelectChapter),
         (self.viewModel.onToChapterRewards, self.__onToChapterRewards),
         (self.__paragonsController.onSettingsChanged, self.__onServerSettingsChanged),
         (self.__paragonsController.onProgressPointsChanged, self.__updateChapters))

    def __onSelectChapter(self, event):
        chapterId = int(event.get('id', 0))
        self.__paragonsController.setChapter(chapterId, self.__selectChapterCallback)

    def __selectChapterCallback(self, isSuccess):
        if isSuccess:
            self.__updateChapters()
            self.parentViewModel.onTabChange({'tabId': TabId.PROGRESS})

    def __updateChapters(self):
        with self.parentViewModel.progression.transaction() as tx:
            fillChapterModels(tx.getStages(), tooltipData=self.__tooltipData)

    def __onServerSettingsChanged(self, _):
        self.__updateChapters()

    def __onToChapterRewards(self, event):
        chapterId = int(event.get('id', 0))
        showChapterRewardsView(chapterId, self.getParentWindow())
