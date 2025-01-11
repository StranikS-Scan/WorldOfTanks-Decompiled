# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pm_announce/tooltips/__init__.py
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_old_campaign_tooltip_rewards_model import RewardStatus

def getRewardStatusForOperation(operation):
    if operation.isCompleted():
        if operation.isAwardAchieved():
            return RewardStatus.COMPLETED
        return RewardStatus.AVAILABLE
    return RewardStatus.AVAILABLE if operation.isAvailable().isValid else RewardStatus.LOCKED
