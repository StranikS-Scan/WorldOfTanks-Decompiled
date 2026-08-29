# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/user_mission_widget_service.py
from __future__ import absolute_import
import Event
from gui.impl.lobby.user_missions.hangar_widget.services import IUserMissionWidgetService

class UserMissionWidgetService(IUserMissionWidgetService):

    def __init__(self):
        super(UserMissionWidgetService, self).__init__()
        self.onVisibleGroupsChanged = Event.Event()
        self.__visibleGroups = {}

    def setGroupVisibility(self, groupName, isVisible):
        if not groupName:
            return
        self.__visibleGroups[groupName] = isVisible
        self.onVisibleGroupsChanged(groupName, isVisible)

    def getVisibleGroups(self):
        return self.__visibleGroups

    def isGroupVisible(self, groupName):
        return self.__visibleGroups.get(groupName, False)

    def finalize(self):
        self.__visibleGroups.clear()
        self.onVisibleGroupsChanged.clear()
