# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_progression_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from fun_random.gui.feature.fun_sounds import FUN_PROGRESSION_SOUND_SPACE
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_progression_view_model import FunRandomProgressionViewModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import packAdditionalRewards, packProgressionCondition, packProgressionStages, packProgressionState
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showHangar
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
_DESTROY_ACTION_NAME = 'showHangar'

class FunRandomProgressionView(ViewImpl, LobbyHeaderVisibility, FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher):
    __slots__ = ('__tooltips',)
    _COMMON_SOUND_SPACE = FUN_PROGRESSION_SOUND_SPACE

    def __init__(self, *_, **__):
        settings = ViewSettings(layoutID=R.views.fun_random.lobby.feature.FunRandomProgression(), flags=ViewFlags.LOBBY_SUB_VIEW, model=FunRandomProgressionViewModel())
        self.__tooltips = {}
        super(FunRandomProgressionView, self).__init__(settings)

    @staticmethod
    def showHangar(*_):
        showHangar()

    @property
    def viewModel(self):
        return super(FunRandomProgressionView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(FunRandomProgressionView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            progression = self.getActiveProgression()
            showCount, stageIdx = int(event.getArgument('showCount')), int(event.getArgument('stageIdx'))
            packedRewards = packAdditionalRewards(progression, stageIdx, showCount) if progression else []
            if packedRewards:
                return AdditionalRewardsTooltip(packedRewards)
            return None
        else:
            return super(FunRandomProgressionView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def showInfoPage(self, *_):
        self.showCommonInfoPage()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.showHangar), (self.viewModel.onShowInfo, self.showInfoPage))

    def _initialize(self, *args, **kwargs):
        super(FunRandomProgressionView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader(self.uniqueID)

    def _finalize(self):
        self.__tooltips.clear()
        self.resumeLobbyHeader(self.uniqueID)
        self.stopProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)
        super(FunRandomProgressionView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(FunRandomProgressionView, self)._onLoading(*args, **kwargs)
        self.startProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)
        self.__invalidateAll()

    @hasActiveProgression(abortAction=_DESTROY_ACTION_NAME)
    def __invalidateAll(self, *_):
        self.__tooltips.clear()
        progression = self.getActiveProgression()
        with self.viewModel.transaction() as model:
            model.setAssetsPointer(self.getModeAssetsPointer())
            packProgressionStages(progression, model.getStages(), self.__tooltips)
            packProgressionCondition(progression, model.condition)
            packProgressionState(progression, model.state)

    @hasActiveProgression(abortAction=_DESTROY_ACTION_NAME)
    def __invalidateTimer(self, *_):
        self.viewModel.state.setResetTimer(self.getActiveProgression().condition.resetTimer)
