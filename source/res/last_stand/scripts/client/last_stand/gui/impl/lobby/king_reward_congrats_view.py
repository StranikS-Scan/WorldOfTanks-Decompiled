# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/king_reward_congrats_view.py
import WWISE
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from last_stand.gui.impl.gen.view_models.views.lobby.king_reward_congrats_view_model import KingRewardCongratsViewModel
from last_stand.gui.impl.lobby.ls_helpers import fillRewards
from last_stand.gui.impl.lobby.base_view import BaseView
from last_stand.gui.shared.event_dispatcher import showLootBoxMainViewInQueue
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import KING_REWARD_WINDOW_ENTER, KING_REWARD_WINDOW_EXIT, KingRewardState
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from helpers import dependency
from ids_generators import SequenceIDGenerator
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class KingRewardCongratsView(BaseView):
    layoutID = R.views.last_stand.mono.lobby.king_reward_view()
    _MAX_BONUSES_IN_VIEW = 5
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID or self.layoutID, model=KingRewardCongratsViewModel())
        super(KingRewardCongratsView, self).__init__(settings)
        self.__idGen = SequenceIDGenerator()
        self.__bonusCache = {}

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(KingRewardCongratsView, self).createToolTip(event)

    @property
    def viewModel(self):
        return super(KingRewardCongratsView, self).getViewModel()

    def _onLoading(self):
        super(KingRewardCongratsView, self)._onLoading()
        with self.viewModel.transaction() as model:
            rewards = model.getRewards()
            rewards.clear()
            kingRewardArtefact = self.lsArtifactsCtrl.getKingRewardArtefact()
            model.setIsTransition(self.lsArtifactsCtrl.isArtefactHasLootBoxGift(kingRewardArtefact.artefactID))
            self.__bonusCache.update(fillRewards(kingRewardArtefact.bonusRewards, rewards, self._MAX_BONUSES_IN_VIEW, self.__idGen))
            rewards.invalidate()

    def _initialize(self, *args, **kwargs):
        super(KingRewardCongratsView, self)._initialize()
        playSound(KING_REWARD_WINDOW_ENTER)
        WWISE.WW_setState(KingRewardState.GROUP, KingRewardState.GENERAL_ON)

    def _finalize(self):
        playSound(KING_REWARD_WINDOW_EXIT)
        WWISE.WW_setState(KingRewardState.GROUP, KingRewardState.GENERAL_OFF)
        super(KingRewardCongratsView, self)._finalize()

    def _subscribe(self):
        super(KingRewardCongratsView, self)._subscribe()
        self.viewModel.onClose += self._onClose
        self.viewModel.onToOutroClick += self._onToOutro

    def _unsubscribe(self):
        super(KingRewardCongratsView, self)._unsubscribe()
        self.viewModel.onClose -= self._onClose
        self.viewModel.onToOutroClick -= self._onToOutro

    def _onToOutro(self):
        artefact = self.lsArtifactsCtrl.getKingRewardArtefact()
        if self.lsArtifactsCtrl.isArtefactHasLootBoxGift(artefact.artefactID):
            showLootBoxMainViewInQueue(self.lsCtrl.lootBoxesEvent)
        self.destroyWindow()


class KingRewardCongratsWindow(LobbyNotificationWindow):

    def __init__(self, layoutID, parent=None):
        super(KingRewardCongratsWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=KingRewardCongratsView(layoutID), parent=parent)
        self._args = (layoutID,)

    def isParamsEqual(self, *args):
        return self._args == args
