# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/feature/tooltips/quests_preview_tooltip.py
from gui.server_events import events_helpers
from gui.server_events.events_helpers import isFunRandomQuest
from gui.shared.tooltips.quests import QuestsPreviewTooltipData
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunRandomQuestsPreviewTooltip(QuestsPreviewTooltipData):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def _getQuests(self, vehicle):
        if self.__funRandomCtrl.isSuitableVehicle(vehicle) is not None:
            return []
        else:
            quests = [ q for q in self._questController.getQuestForVehicle(vehicle) if isFunRandomQuest(q.getGroupID()) and q.shouldBeShown() and not q.isCompleted() ]
            return sorted(quests, key=events_helpers.questsSortFunc)

    def _isShowBottom(self, vehicle=None):
        return '' if self.__funRandomCtrl.isSuitableVehicle(vehicle) is not None else super(FunRandomQuestsPreviewTooltip, self)._isShowBottom()
