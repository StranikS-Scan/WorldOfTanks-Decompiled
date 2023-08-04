# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/collections/loggers.py
from uilogging.base.logger import MetricsLogger
from uilogging.collections.constants import FEATURE, CollectionsItem
from uilogging.constants import CommonLogActions

class CollectionsLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(CollectionsLogger, self).__init__(FEATURE)

    def handleRewardNotificationAction(self, collectionID):
        self.logOnce(action=CommonLogActions.CLICK, item=CollectionsItem.REWARD_NOTIFICATION, info=str(collectionID))

    def handleGameObjectClick(self, collectionID):
        self.log(action=CommonLogActions.CLICK, item=CollectionsItem.GAME_OBJECT, info=str(collectionID))
