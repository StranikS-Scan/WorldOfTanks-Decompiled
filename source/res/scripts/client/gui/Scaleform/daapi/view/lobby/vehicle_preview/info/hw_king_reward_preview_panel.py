# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/hw_king_reward_preview_panel.py
from gui.Scaleform.daapi.view.meta.EventKingRewardMeta import EventKingRewardMeta
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from gui.shared.event_dispatcher import showMetaView
from gui.impl.gen.view_models.views.lobby.halloween.meta_view_model import PageTypeEnum

class VehiclePreviewEventKingRewardProgressionPanel(EventKingRewardMeta):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(VehiclePreviewEventKingRewardProgressionPanel, self).__init__()
        self.__eventRewardController = self._gameEventController.getEventRewardController()

    def _populate(self):
        super(VehiclePreviewEventKingRewardProgressionPanel, self)._populate()
        self._gameEventController.onRewardBoxUpdated += self._update
        self._update()

    def _dispose(self):
        self._gameEventController.onRewardBoxUpdated -= self._update
        super(VehiclePreviewEventKingRewardProgressionPanel, self)._dispose()

    def _update(self):
        currentProgress = self.__eventRewardController.getCurrentRewardProgress()
        maxProgress = self.__eventRewardController.getMaxRewardProgress()
        self.setData(currentProgress, maxProgress)

    def setData(self, currentProgress, maxProgress):
        rewardBoxProgressVO = {'current': currentProgress,
         'total': maxProgress,
         'taken': currentProgress >= maxProgress}
        self.as_setDataS(rewardBoxProgressVO)

    def onExitToRewardsClick(self):
        showMetaView(PageTypeEnum.FINAL_REWARD.value)
