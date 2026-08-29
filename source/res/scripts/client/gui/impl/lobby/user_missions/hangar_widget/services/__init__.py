# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/__init__.py
from __future__ import absolute_import
import typing
from gui.prb_control.entities.listener import IGlobalListener
if typing.TYPE_CHECKING:
    from typing import List
    from gui.impl.lobby.user_missions.hangar_widget.plugins import IUserMissionPlugin

class IBattlePassService(IGlobalListener):
    onBattlePassChanged = None

    def startListening(self):
        raise NotImplementedError

    def stopListening(self):
        raise NotImplementedError

    def isVisible(self):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError


class IEventsService(IGlobalListener):
    onEventsListChanged = None

    def startListening(self):
        raise NotImplementedError

    def stopListening(self):
        raise NotImplementedError

    def getEntries(self):
        raise NotImplementedError

    def getEntryData(self):
        raise NotImplementedError

    def updateEntries(self):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError

    @property
    def isAvailable(self):
        raise NotImplementedError


class IMissionsService(IGlobalListener):
    onMissionsChanged = None

    def startListening(self):
        raise NotImplementedError

    def stopListening(self):
        raise NotImplementedError

    def isVisible(self):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError


class IPersonalMissionsService(IMissionsService):
    onPersonalMissionsChanged = None
    onWidgetQuestIDMarkedAsNew = None
    onServicePMSyncCompleted = None

    def clearWidgetQuestIDMarkedAsNew(self):
        raise NotImplementedError

    def setWidgetQuestIDMarkedAsNew(self, questID, doUpdateWidget=True):
        raise NotImplementedError

    def getWidgetQuestIDMarkedAsNew(self):
        raise NotImplementedError


class IMissionsContainerService(IGlobalListener):
    onShowPlugin = None
    onHidePlugin = None

    def showPlugin(self, viewAlias):
        raise NotImplementedError

    def hidePlugin(self, viewAlias):
        raise NotImplementedError

    def getVisiblePlugins(self):
        raise NotImplementedError

    def isPluginVisible(self, viewAlias):
        raise NotImplementedError

    def getSelectedSlide(self, sliderId):
        raise NotImplementedError

    def onSlideChanged(self, selectedSlide):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError


class IUserMissionWidgetService(object):
    onVisibleGroupsChanged = None

    def setGroupVisibility(self, groupName, isVisible):
        raise NotImplementedError

    def getVisibleGroups(self):
        raise NotImplementedError

    def isGroupVisible(self, groupName):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError
