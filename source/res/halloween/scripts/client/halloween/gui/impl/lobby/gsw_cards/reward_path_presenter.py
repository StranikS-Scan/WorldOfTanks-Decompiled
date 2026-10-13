# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/gsw_cards/reward_path_presenter.py
from __future__ import absolute_import
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.pub.view_component import ViewComponent
from halloween.skeletons.halloween_twitch_con_controller import IHalloweenTwitchConController
from helpers import dependency
from halloween.gui.impl.gen.view_models.views.lobby.widgets.reward_path_card_view_model import RewardPathCardViewModel
from halloween.gui.impl.lobby.tooltips.tooltip_positioner import TooltipPositionerMixin
from halloween.gui.shared.event_dispatcher import showRewardPathView, showStoryChoiceWindow
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween_common.halloween_constants import HWStoryChoiceSettings
from skeletons.gui.shared import IItemsCache

class RewardPathCardPresenter(TooltipPositionerMixin, ViewComponent[RewardPathCardViewModel]):
    _hwArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _hwTwitchCtrl = dependency.descriptor(IHalloweenTwitchConController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(RewardPathCardPresenter, self).__init__(model=RewardPathCardViewModel)

    def _onLoading(self, *args, **kwargs):
        super(RewardPathCardPresenter, self)._onLoading()
        self.__fillMetaWidget()

    def _getEvents(self):
        return ((self._hwArtefactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated), (self.getViewModel().onClick, self.__onClick), (self._hwTwitchCtrl.onCertificateCountUpdated, self.__cerfCountUpdate))

    def _subscribe(self):
        super(RewardPathCardPresenter, self)._subscribe()
        g_clientUpdateManager.addCallbacks({'tokens': self.__handleTokensUpdate})

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RewardPathCardPresenter, self)._unsubscribe()

    def _isChoiceState(self):
        tokens = self.__itemsCache.items.tokens
        finalArtefactID = self._hwArtefactsCtrl.getFinalArtefact().artefactID
        hasFinalToken = self._hwArtefactsCtrl.isArtefactOpened(finalArtefactID)
        return hasFinalToken and all((not tokens.getTokenCount(opt) for opt in HWStoryChoiceSettings.ALL_OPTIONS))

    def __onClick(self):
        if not self._isChoiceState():
            showRewardPathView()
        else:
            self._hwArtefactsCtrl.setChoice(HWStoryChoiceSettings.OPTION_SKIP)
            showStoryChoiceWindow()

    def __fillMetaWidget(self):
        with self.getViewModel().transaction() as tx:
            maxProgress = self._hwArtefactsCtrl.getMaxArtefactsProgress()
            currentProgress = self._hwArtefactsCtrl.getCurrentArtefactProgress()
            tx.setMaxProgress(maxProgress)
            tx.setCurrentProgress(min(currentProgress, maxProgress))
            tx.setCertificates(self._hwTwitchCtrl.getCertificateCount())
            tx.setIsCompleted(currentProgress >= maxProgress)
            tx.setIsStoryChoiceState(self._isChoiceState())

    def __onArtefactStatusUpdated(self, _):
        self.__fillMetaWidget()

    def __cerfCountUpdate(self):
        self.getViewModel().setCertificates(self._hwTwitchCtrl.getCertificateCount())

    def __handleTokensUpdate(self, diff):
        if any((token in HWStoryChoiceSettings.ALL_OPTIONS for token in diff)):
            self.__fillMetaWidget()
