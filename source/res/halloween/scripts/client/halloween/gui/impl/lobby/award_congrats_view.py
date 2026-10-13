# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/award_congrats_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from halloween.gui.impl.gen.view_models.views.lobby.award_congrats_view_model import AwardCongratsViewModel
from halloween.gui.impl.lobby.base_view import BaseView, HWLobbyWindow
from halloween.gui.impl.lobby.hw_helpers import fillRewardsCommon, getEndingToken
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import AwardCongratsWindowSounds
from helpers import dependency
from ids_generators import SequenceIDGenerator
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class AwardCongratsView(BaseView):
    __slots__ = ()
    layoutID = R.views.halloween.mono.lobby.award_congrats_screen()
    _MAX_BONUSES_IN_VIEW = 1
    _hwArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)

    def __init__(self, choiceID, layoutID=None):
        settings = ViewSettings(layoutID or self.layoutID, model=AwardCongratsViewModel())
        super(AwardCongratsView, self).__init__(settings)
        self._choiceID = choiceID
        self.__idGen = SequenceIDGenerator()

    @property
    def viewModel(self):
        return super(AwardCongratsView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(AwardCongratsView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(AwardCongratsView, self)._initialize()
        sound = AwardCongratsWindowSounds.ON_ENTER.get(self._choiceID)
        if sound:
            playSound(sound)

    def _onLoading(self):
        super(AwardCongratsView, self)._onLoading()
        bonuses = self._hwArtefactsCtrl.getQuest(getEndingToken(self._choiceID)).getBonuses()
        with self.viewModel.transaction() as tx:
            tx.setTitle('R.strings.halloween_lobby.storyChoiceAward.{}.title'.format(self._choiceID))
            rewards = tx.getBonuses()
            rewards.clear()
            self.__bonusCache = fillRewardsCommon(bonuses, rewards, self._MAX_BONUSES_IN_VIEW, self.__idGen)
            rewards.invalidate()

    def _subscribe(self):
        super(AwardCongratsView, self)._subscribe()
        self.viewModel.onClose += self.__onClose

    def _unsubscribe(self):
        super(AwardCongratsView, self)._unsubscribe()
        self.viewModel.onClose -= self.__onClose

    def __onClose(self):
        self.destroyWindow()


class AwardCongratsViewWindow(HWLobbyWindow):

    def __init__(self, layoutID, choiceID, parent=None):
        super(AwardCongratsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=AwardCongratsView(choiceID, layoutID=layoutID), parent=parent)
        self._args = (choiceID, layoutID)
