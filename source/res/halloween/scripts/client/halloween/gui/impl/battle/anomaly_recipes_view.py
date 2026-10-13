# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/battle/anomaly_recipes_view.py
from __future__ import absolute_import
import logging
import typing
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.tooltips.simple_tooltip import createSimpleTooltip
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from halloween.gui.impl.common.anomalies_view_mixin import AnomaliesViewMixin
from halloween.gui.impl.gen.view_models.views.battle.anomaly_recipes_view_model import AnomalyRecipesViewModel
from halloween.gui.impl.gen.view_models.views.common.anomaly_model import AnomalyState
from halloween.gui.scaleform.daapi.view.battle.anomalies_utils import selectAnomaly, getKnownAnomaliesIDs
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import AnomaliesSounds
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import List
_logger = logging.getLogger(__name__)

class AnomalyRecipesView(AnomaliesViewMixin, ViewImpl):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.halloween.mono.battle.anomaly_recipes(), model=AnomalyRecipesViewModel())
        super(AnomalyRecipesView, self).__init__(settings)
        self._usedAnomalies = set()

    def getAnomalyState(self, anomalyData):
        anomalyID = anomalyData.id
        if anomalyID in self.upgradeOptions:
            return AnomalyState.AVAILABLE
        if anomalyID in self._usedAnomalies:
            return AnomalyState.ACQUIRED
        return AnomalyState.KNOWN if self.isAnomalyKnown(anomalyData) else AnomalyState.UNKNOWN

    @property
    def knownAnomaliesIDs(self):
        return getKnownAnomaliesIDs().union(self._usedAnomalies)

    @property
    def hwBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    @property
    def upgradeOptions(self):
        return self.hwBattleGuiCtrl.currentUpgradeOptions

    def createToolTip(self, event):
        if event.contentID == R.views.halloween.mono.lobby.tooltips.anomaly_tooltip():
            anomalyId = event.getArgument('id')
            locRes = R.strings.halloween_buffs.buffs.dyn(anomalyId)
            return createSimpleTooltip(self.getParentWindow(), event, backport.text(locRes.header()), backport.text(locRes.description.tabTooltip()))
        return super(AnomalyRecipesView, self).createToolTip(event)

    @property
    def viewModel(self):
        return super(AnomalyRecipesView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.matrix.onAnomalyClick, self.__onAnomalyClick),)

    def _subscribe(self):
        super(AnomalyRecipesView, self)._subscribe()
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl is not None:
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility += self.__onChangeAnomaliesViewVisibility
            hwBattleGuiCtrl.onUpdateUsedAnomalies += self.__onUpdateUsedAnomalies
            hwBattleGuiCtrl.onUpgradeOptionsUpdated += self.__onUpgradeOptionsUpdated
        return

    def _unsubscribe(self):
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl is not None:
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility -= self.__onChangeAnomaliesViewVisibility
            hwBattleGuiCtrl.onUpdateUsedAnomalies -= self.__onUpdateUsedAnomalies
            hwBattleGuiCtrl.onUpgradeOptionsUpdated -= self.__onUpgradeOptionsUpdated
        super(AnomalyRecipesView, self)._unsubscribe()
        return

    def __onChangeAnomaliesViewVisibility(self, isVisible):
        self.viewModel.setIsVisible(isVisible)
        sound = AnomaliesSounds.Battle.ENTER if isVisible else AnomaliesSounds.Battle.LEAVE
        playSound(sound)

    def __onAnomalyClick(self, args):
        selectAnomaly(anomalyID=args.get('id'))

    def __onUpdateUsedAnomalies(self, usedAnomalies):
        self._usedAnomalies = set(usedAnomalies[:])
        self.refreshMatrix()

    def __onUpgradeOptionsUpdated(self, _):
        self.refreshMatrix()
