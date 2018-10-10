# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_award_group.py
from gui.Scaleform.daapi.view.meta.AwardGroupsMeta import AwardGroupsMeta
import Event

class EventBoardsAwardGroup(AwardGroupsMeta):

    def __init__(self):
        super(EventBoardsAwardGroup, self).__init__()
        self.onShowRewardCategory = Event.Event()

    def showGroup(self, groupId):
        self.onShowRewardCategory(groupId)

    def setActiveRewardGroup(self, groupID):
        self.as_setSelectedS(groupID - 1, True)
